"""
Agent runs that outlive the request that started them.

A run used to live inside its HTTP response: the agent advanced only while
the browser read the stream, so anything that closed the connection — a
network blip, an iPad backgrounding the tab, a proxy cutting a long request
(Railway's edge ends any request at 15 minutes, and drops one that sends no
bytes for 5) — killed the run mid-work and parked it as "cut off".

Here the run is its own asyncio task on the server's event loop, and the
response only listens to it. A listener that goes away detaches; the run
carries on, persists its reply, routes its outcome to the main thread, and
clears its run marker exactly as it would have with someone watching. The
workspace picks the finished result up from the conversation API (its
resync poll) instead of from the stream.

What still stops a run: the user pressing Stop (the cancel endpoint sets
cancel_requested_at, which the watcher below turns into a task cancel), any
of the run's own bounds (turns, cost), a provider error, or the process going
away (a redeploy) — the stranded-task sweep reports that last one.
"""

import asyncio
import logging
import time
from typing import Any, AsyncIterator, Callable, Dict, Optional

from asgiref.sync import ThreadSensitiveContext, sync_to_async
from django.db import connections
from django.utils import timezone

logger = logging.getLogger(__name__)

# Seconds between SSE comment lines while a run is silent. A model thinking
# through a hard step, or writing a whole page into one tool call, can go
# minutes without emitting an event; proxies and mobile browsers close a
# response that quiet. Comments are ignored by the client's frame parser.
KEEPALIVE_INTERVAL = 15

# How often the watcher checks for a Stop, and refreshes the run marker so a
# run that is quiet (a long tool call) never looks stale to the busy guards.
WATCH_INTERVAL = 3
MARKER_REFRESH_INTERVAL = 60

KEEPALIVE_FRAME = ': keepalive\n\n'

# Strong references to running drivers: the event loop only keeps weak ones,
# and a run whose listener left has nothing else holding it.
_running = set()

_END = object()


class DetachedRun:
    """One agent run driven in the background, with at most one listener."""

    def __init__(self):
        self._queue: asyncio.Queue = asyncio.Queue()
        self._listening = True
        self.task: Optional[asyncio.Task] = None
        self.conversation_id: Optional[int] = None

    def _emit(self, item: Any) -> None:
        # Nobody reads a detached run's events; buffering them would only
        # grow memory for the rest of the run.
        if self._listening:
            self._queue.put_nowait(item)

    def detach(self) -> None:
        """The listener is gone. The run keeps going without it."""
        self._listening = False
        while not self._queue.empty():
            self._queue.get_nowait()

    async def frames(
        self, encode: Callable[[Dict[str, Any]], str],
        keepalive: float = KEEPALIVE_INTERVAL,
    ) -> AsyncIterator[str]:
        """The run's events as SSE frames, with keepalives while it is quiet.

        Leaving this generator (the client disconnecting, or the response
        being closed) detaches the listener; it never stops the run.
        """
        try:
            while True:
                try:
                    item = await asyncio.wait_for(self._queue.get(), keepalive)
                except asyncio.TimeoutError:
                    yield KEEPALIVE_FRAME
                    continue
                if item is _END:
                    return
                yield encode(item)
        finally:
            self.detach()


def _poll_conversation(conversation_id: int, refresh_marker: bool) -> bool:
    """One watcher tick: True when a Stop was requested for this run.

    The marker refresh is conditional on the marker still being set, so a run
    finishing (which clears it) can never be marked running again by a late
    tick.
    """
    from ..models import AgentConversation

    if refresh_marker:
        AgentConversation.objects.filter(
            id=conversation_id, run_started_at__isnull=False
        ).update(run_started_at=timezone.now())
    return AgentConversation.objects.filter(
        id=conversation_id, cancel_requested_at__isnull=False
    ).exists()


async def _watch(run: DetachedRun) -> None:
    """Turn a requested Stop into a cancel of the run's task; keep it fresh."""
    last_refresh = time.monotonic()
    while run.task is not None and not run.task.done():
        await asyncio.sleep(WATCH_INTERVAL)
        refresh = time.monotonic() - last_refresh >= MARKER_REFRESH_INTERVAL
        if refresh:
            last_refresh = time.monotonic()
        try:
            stop = await sync_to_async(_poll_conversation)(run.conversation_id, refresh)
        except Exception as e:  # pragma: no cover - best effort
            logger.warning("Run watcher could not read conversation %s: %s", run.conversation_id, e)
            continue
        if stop and run.task is not None and not run.task.done():
            logger.info("Stopping run for conversation %s at the user's request", run.conversation_id)
            run.task.cancel(msg='stopped')
            return


class _EventLog:
    """Writes a run's events to AgentRunEvent as the run goes, in batches.

    Every event gets a "seq" (1, 2, 3… within the run) before it reaches any
    listener, so a watcher that lost its connection can resume after the last
    one it saw. Writes are batched — a model streams many small deltas — and
    flushed at once for the events a watcher is waiting on.
    """

    URGENT = ('start', 'done', 'error', 'task_dispatch', 'title')

    def __init__(self, conversation_id: Optional[int] = None):
        self.conversation_id = conversation_id
        self.seq = 0
        self._pending: list = []
        self._cleared = False

    def add(self, event: Dict[str, Any]) -> Dict[str, Any]:
        self.seq += 1
        event = {**event, 'seq': self.seq}
        self._pending.append(event)
        return event

    def _write(self, conversation_id: int, events: list, clear: bool) -> None:
        from ..models import AgentRunEvent

        if clear:
            # Only the latest run's events are kept.
            AgentRunEvent.objects.filter(conversation_id=conversation_id).delete()
        if events:
            AgentRunEvent.objects.create(
                conversation_id=conversation_id,
                seq_end=events[-1]['seq'],
                events=events,
            )

    async def flush(self) -> None:
        if self.conversation_id is None or (self._cleared and not self._pending):
            return
        events, self._pending = self._pending, []
        clear = not self._cleared
        self._cleared = True
        try:
            await sync_to_async(self._write)(self.conversation_id, events, clear)
        except Exception as e:  # pragma: no cover - best effort
            # Watching is best effort; the run itself must not fail over it.
            logger.warning("Could not record run events for %s: %s", self.conversation_id, e)


# How often buffered events are written while a run streams.
EVENT_FLUSH_INTERVAL = 0.5


def start_detached_run(
    make_events: Callable[[], AsyncIterator[Dict[str, Any]]],
    *,
    user=None,
    conversation_id: Optional[int] = None,
) -> DetachedRun:
    """Start a run in the background and return the handle to listen to it.

    make_events builds the run's event generator (process_stream). It is
    called inside the driver so the generator's whole life — including the
    cleanup in its finally blocks — belongs to the driver task, not to the
    request.

    conversation_id, when the caller knows it, clears the conversation's
    previous run's events before this one starts, so nobody watching sees the
    old run as if it were the new one. user lets the run start the threads it
    dispatches, and the next waiting ones when it ends (thread_scheduler).
    """
    run = DetachedRun()
    log = _EventLog(conversation_id)

    async def drive():
        # The request's thread-sensitive executor is shut down when the
        # request ends; the run's ORM calls need one that lives as long as
        # the run does.
        async with ThreadSensitiveContext():
            await log.flush()
            events = make_events()
            watcher = None
            flusher = None

            async def flush_periodically():
                while True:
                    await asyncio.sleep(EVENT_FLUSH_INTERVAL)
                    await log.flush()

            def record(event):
                event = log.add(event)
                run._emit(event)
                return event

            try:
                async for event in events:
                    if (
                        watcher is None
                        and event.get('type') == 'start'
                        and event.get('conversation_id')
                    ):
                        run.conversation_id = event['conversation_id']
                        log.conversation_id = run.conversation_id
                        watcher = asyncio.create_task(_watch(run))
                        flusher = asyncio.create_task(flush_periodically())
                    event = record(event)
                    if event.get('type') in _EventLog.URGENT:
                        await log.flush()
                    if event.get('type') == 'task_dispatch' and user is not None:
                        # The coordinator handed work to threads: start them
                        # now, here on the server, whoever is watching.
                        await _kick_threads(user)
            except asyncio.CancelledError:
                # Handled here, so the task is no longer being cancelled —
                # the awaits in the cleanup below must still run.
                task = asyncio.current_task()
                if task is not None:
                    task.uncancel()
                # A Stop. The generator's own cleanup has already run on the
                # way out (partial reply kept, marker cleared); watchers are
                # told plainly.
                record({
                    'type': 'error',
                    'code': 'stopped',
                    'error': 'Stopped.',
                    'conversation_id': run.conversation_id,
                })
            except Exception as e:  # pragma: no cover - defensive
                logger.exception("Detached agent run failed")
                record({'type': 'error', 'error': str(e), 'conversation_id': run.conversation_id})
            finally:
                try:
                    await events.aclose()
                except Exception:  # pragma: no cover - best effort
                    pass
                if watcher is not None:
                    watcher.cancel()
                if flusher is not None:
                    flusher.cancel()
                await log.flush()
                run._emit(_END)
                if user is not None:
                    # A slot is free, and a follow-up may have been staged
                    # for a thread while it was busy: start what is waiting.
                    await _kick_threads(user)
                # This thread's database connection goes with its executor.
                await sync_to_async(connections.close_all)()

    task = asyncio.get_running_loop().create_task(drive())
    run.task = task
    _running.add(task)
    task.add_done_callback(_running.discard)
    return run


async def _kick_threads(user) -> None:
    from .thread_scheduler import start_waiting_threads

    try:
        await start_waiting_threads(user)
    except Exception:  # pragma: no cover - best effort
        logger.exception("Could not start waiting threads")


# How often a watcher reads new events, and how long it waits on a run that
# has ended without a final event (a redeploy killed it) before saying so.
WATCH_POLL_INTERVAL = 0.75
WATCH_ENDED_GRACE = 3.0
# How often a watcher waiting on a thread that has not started yet asks the
# scheduler to start it (it may be waiting for a free slot).
WATCH_KICK_INTERVAL = 5.0

TERMINAL_EVENTS = ('done', 'error')


def _watch_state(conversation_id: int) -> Dict[str, Any]:
    """What a watcher needs to know about a conversation, in one read."""
    from ..models import AgentConversation, AgentRunEvent
    from ..api.views import RUN_STALENESS_WINDOW  # noqa: avoid an import cycle at load

    conversation = AgentConversation.objects.filter(id=conversation_id).values(
        'run_started_at', 'queued_prompt', 'review_status', 'archived_at',
    ).first()
    if conversation is None:
        return {'exists': False}
    started = conversation['run_started_at']
    last_row = AgentRunEvent.objects.filter(conversation_id=conversation_id).order_by('-id').first()
    return {
        'exists': True,
        'running': bool(started and timezone.now() - started < RUN_STALENESS_WINDOW),
        'staged': bool((conversation['queued_prompt'] or '').strip()),
        'review_status': conversation['review_status'],
        'archived': conversation['archived_at'] is not None,
        'last_row_id': last_row.id if last_row else 0,
        'logged_run_ended': bool(
            last_row and last_row.events
            and (last_row.events[-1] or {}).get('type') in TERMINAL_EVENTS
        ),
    }


def _rows_after(conversation_id: int, row_id: int) -> list:
    from ..models import AgentRunEvent

    return list(
        AgentRunEvent.objects.filter(conversation_id=conversation_id, id__gt=row_id)
        .order_by('id').values('id', 'events')
    )


def _not_started_note(conversation_id: int) -> str:
    from ..models import AgentCheckIn

    pending = AgentCheckIn.objects.filter(
        conversation_id=conversation_id, status='pending'
    ).order_by('-id').values_list('body', flat=True).first()
    return pending or "This thread isn't running. Try it again to pick the job back up."


async def watch_conversation(
    conversation_id: int,
    user,
    encode: Callable[[Dict[str, Any]], str],
    after: Optional[int] = None,
    keepalive: float = KEEPALIVE_INTERVAL,
) -> AsyncIterator[str]:
    """Follow a conversation's run as SSE frames, from any tab or process.

    after=None follows "the current run": the one in progress, or the one
    about to start when work is staged for it (a dispatched thread waiting
    for a slot), or else the run that last finished. after=N resumes the
    current run after event N — what a tab does when its connection dropped.

    Ends after the run's final event. A run that ended without one (its
    process went away) is reported as an error rather than waited on forever.
    """
    state = await sync_to_async(_watch_state)(conversation_id)
    if not state['exists']:
        yield encode({'type': 'error', 'error': 'Conversation not found', 'code': 'not_found'})
        return

    # Staged work whose run has not begun logging yet (not claimed, or claimed
    # a moment ago): whatever is logged belongs to the previous run, so only
    # rows written from here on count. Staged work behind a run still going
    # (a follow-up waiting its turn) leaves that run to be followed.
    waiting_for_next = after is None and state['staged'] and (
        not state['running'] or state['logged_run_ended']
    )
    row_floor = state['last_row_id'] if waiting_for_next else 0
    min_seq = after or 0
    last_frame = time.monotonic()
    last_kick = 0.0
    idle_since: Optional[float] = None

    while True:
        rows = await sync_to_async(_rows_after)(conversation_id, row_floor)
        for row in rows:
            row_floor = row['id']
            for event in row['events'] or []:
                seq = event.get('seq') or 0
                if event.get('type') == 'start' and seq <= min_seq and after is None:
                    min_seq = 0  # a new run began; its seq counts from 1 again
                if seq <= min_seq:
                    continue
                min_seq = seq
                yield encode(event)
                last_frame = time.monotonic()
                if event.get('type') in TERMINAL_EVENTS:
                    return
        if rows:
            idle_since = None
            continue

        state = await sync_to_async(_watch_state)(conversation_id)
        now = time.monotonic()
        if state['running']:
            idle_since = None
        elif state['staged'] and state['review_status'] in ('active', 'input', 'ready') \
                and not state['archived']:
            # Waiting for the scheduler — a free slot, or a nudge after a
            # restart lost the one that was coming.
            idle_since = None
            if now - last_kick >= WATCH_KICK_INTERVAL:
                last_kick = now
                from .thread_scheduler import start_waiting_threads
                outcome = await start_waiting_threads(user)
                if outcome.get('blocked') == 'usage':
                    yield encode({
                        'type': 'error', 'code': 'usage_limit_exceeded',
                        'error': (
                            "Usage allowance spent — this thread starts when it "
                            "frees up, or upgrade your plan for more."
                        ),
                    })
                    return
        else:
            # Not running, nothing staged, no final event read: give a run
            # that is just finishing a moment to write it, then report.
            if idle_since is None:
                idle_since = now
            elif now - idle_since >= WATCH_ENDED_GRACE:
                note = await sync_to_async(_not_started_note)(conversation_id)
                yield encode({
                    'type': 'error', 'code': 'run_ended', 'error': note,
                    'conversation_id': conversation_id,
                })
                return

        if now - last_frame >= keepalive:
            yield KEEPALIVE_FRAME
            last_frame = now
        await asyncio.sleep(WATCH_POLL_INTERVAL)
