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


def start_detached_run(make_events: Callable[[], AsyncIterator[Dict[str, Any]]]) -> DetachedRun:
    """Start a run in the background and return the handle to listen to it.

    make_events builds the run's event generator (process_stream). It is
    called inside the driver so the generator's whole life — including the
    cleanup in its finally blocks — belongs to the driver task, not to the
    request.
    """
    run = DetachedRun()

    async def drive():
        # The request's thread-sensitive executor is shut down when the
        # request ends; the run's ORM calls need one that lives as long as
        # the run does.
        async with ThreadSensitiveContext():
            events = make_events()
            watcher = None
            try:
                async for event in events:
                    if (
                        watcher is None
                        and event.get('type') == 'start'
                        and event.get('conversation_id')
                    ):
                        run.conversation_id = event['conversation_id']
                        watcher = asyncio.create_task(_watch(run))
                    run._emit(event)
            except asyncio.CancelledError:
                # Handled here, so the task is no longer being cancelled —
                # the awaits in the cleanup below must still run.
                task = asyncio.current_task()
                if task is not None:
                    task.uncancel()
                # A Stop. The generator's own cleanup has already run on the
                # way out (partial reply kept, marker cleared); the listener,
                # if any, is told plainly.
                run._emit({
                    'type': 'error',
                    'code': 'stopped',
                    'error': 'Stopped.',
                    'conversation_id': run.conversation_id,
                })
            except Exception as e:  # pragma: no cover - defensive
                logger.exception("Detached agent run failed")
                run._emit({'type': 'error', 'error': str(e), 'conversation_id': run.conversation_id})
            finally:
                try:
                    await events.aclose()
                except Exception:  # pragma: no cover - best effort
                    pass
                if watcher is not None:
                    watcher.cancel()
                run._emit(_END)
                # This thread's database connection goes with its executor.
                await sync_to_async(connections.close_all)()

    task = asyncio.get_running_loop().create_task(drive())
    run.task = task
    _running.add(task)
    task.add_done_callback(_running.discard)
    return run
