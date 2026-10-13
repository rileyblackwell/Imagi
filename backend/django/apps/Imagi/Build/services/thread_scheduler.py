"""
Starting threads on the server.

A thread's work is staged on its conversation (queued_prompt): the
coordinator's dispatch_task and message_task put it there, and so does a
person typing into a thread or answering its question. This module turns
staged work into running work — on the server, whether or not any browser
is open. Browsers only watch (detached_runs.watch_conversation).

It is called whenever a slot may have freed or new work may be waiting: the
coordinator dispatching, any run ending, a message arriving for a thread,
and a watcher waiting on a thread that has not started. The coordinator is
started here too, when the app reported errors for it (app_errors).

Every start is claimed with one conditional UPDATE on the run marker, so
two server processes (or two calls racing in one) can never start the same
thread twice.
"""

import logging
from datetime import timedelta
from typing import Any, Dict, List

from asgiref.sync import sync_to_async
from django.conf import settings
from django.db.models import Q
from django.utils import timezone

logger = logging.getLogger(__name__)

_BUILDER_SETTINGS = getattr(settings, 'IMAGI_BUILDER', {})
MAX_CONCURRENT_TASK_RUNS = _BUILDER_SETTINGS.get('MAX_CONCURRENT_TASK_RUNS', 5)

# Statuses a thread can be started from: working, waiting on the user, or
# finished and waiting for review (a follow-up re-opens it). A failed thread
# is the user's to retry; a dismissed one has no work left.
STARTABLE_STATUSES = ('active', 'input', 'ready')

# Matches the API's staleness window: a marker older than this is a run
# whose process died, not a run in progress.
RUN_STALENESS_WINDOW = timedelta(minutes=10)


def _claim_waiting_threads(user) -> Dict[str, Any]:
    """Claim as many waiting threads as this user has room for.

    Returns {'claimed': [...], 'blocked': None | 'usage'}; each claimed item
    is what the run needs to start.
    """
    from ..models import AgentConversation
    from .usage_limits import check_usage_allowed

    from .scheduling import release_waiting_tasks

    # Work held on the coordinator's schedule joins the queue the moment what
    # it waits for has landed — this runs on every pass, and a pass follows
    # every run's end.
    try:
        release_waiting_tasks(user)
    except Exception:  # pragma: no cover - best effort
        logger.exception("Could not release scheduled work")

    now = timezone.now()
    stale = now - RUN_STALENESS_WINDOW
    not_running = Q(run_started_at__isnull=True) | Q(run_started_at__lt=stale)

    waiting = list(
        AgentConversation.objects.filter(
            user=user, kind='task', archived_at__isnull=True,
            review_status__in=STARTABLE_STATUSES,
        ).exclude(queued_prompt='').filter(not_running).order_by('id')
    )
    if not waiting:
        return {'claimed': [], 'blocked': None}

    allowed, _payload = check_usage_allowed(user)
    if not allowed:
        return {'claimed': [], 'blocked': 'usage'}

    running = AgentConversation.objects.filter(
        user=user, kind='task', run_started_at__gt=stale
    ).count()
    room = MAX_CONCURRENT_TASK_RUNS - running

    claimed: List[Dict[str, Any]] = []
    for task in waiting:
        if room <= 0:
            break
        brief = task.queued_prompt
        if not brief.strip():
            continue
        won = AgentConversation.objects.filter(
            id=task.id, queued_prompt=brief
        ).filter(not_running).update(run_started_at=now, cancel_requested_at=None)
        if not won:
            continue  # someone else started it
        room -= 1
        claimed.append({
            'conversation_id': task.id,
            'brief': brief,
            'model': task.model_name,
            'project_id': task.project_id,
        })
    return {'claimed': claimed, 'blocked': None}


def _release_unstarted(conversation_id: int, note: str) -> None:
    """A claimed thread whose run never got going: clear its claim and say so."""
    from ..models import AgentConversation
    from .base_agent import ImagiAgentService

    conversation = AgentConversation.objects.filter(id=conversation_id).first()
    if conversation is None:
        return
    conversation.run_started_at = None
    conversation.save(update_fields=['run_started_at'])
    ImagiAgentService()._park_failed_task(conversation, note)


def _thread_events(user, item: Dict[str, Any]):
    """The run for one claimed thread, guarding the claim if it never starts."""
    from .base_agent import ImagiAgentService
    from ..api.views import resolve_model

    async def events():
        model = resolve_model(item['model'])
        service = ImagiAgentService(model=model)
        started = False
        failure = ''
        try:
            async for event in service.process_stream(
                user_input=item['brief'],
                user=user,
                model=model,
                project_id=item['project_id'],
                conversation_id=item['conversation_id'],
            ):
                if event.get('type') == 'start':
                    started = True
                elif event.get('type') == 'error' and not started:
                    failure = event.get('error') or ''
                yield event
        finally:
            if not started:
                await sync_to_async(_release_unstarted)(
                    item['conversation_id'],
                    "This thread could not start"
                    + (f": {failure[:300]}" if failure else ".")
                    + " Try it again to pick the job back up.",
                )

    return events()


def _claim_waiting_coordinators(user) -> List[Dict[str, Any]]:
    """Claim coordinators with staged work ([App error] messages) whose
    project has no coordinator or chat run going.

    A coordinator edits nothing itself, but its run holds the project's one
    canonical-tree slot, so it waits for that slot like a message the user
    sends would, and for the user's allowance.
    """
    from ..models import AgentConversation
    from ..api.views import (
        CANONICAL_TREE_KINDS,
        MAX_CONCURRENT_CANONICAL_RUNS_PER_USER,
        _project_has_running_conversation,
        _user_running_run_count,
    )
    from .usage_limits import check_usage_allowed

    waiting = list(
        AgentConversation.objects.filter(
            user=user, kind='lead', archived_at__isnull=True,
        ).exclude(queued_prompt='').order_by('id')
    )
    if not waiting:
        return []
    allowed, _payload = check_usage_allowed(user)
    if not allowed:
        return []
    room = MAX_CONCURRENT_CANONICAL_RUNS_PER_USER - _user_running_run_count(
        user, kinds=CANONICAL_TREE_KINDS,
    )
    now = timezone.now()
    stale = now - RUN_STALENESS_WINDOW
    not_running = Q(run_started_at__isnull=True) | Q(run_started_at__lt=stale)
    claimed: List[Dict[str, Any]] = []
    for lead in waiting:
        if room <= 0:
            break
        prompt = lead.queued_prompt
        if not prompt.strip() or _project_has_running_conversation(user, lead.project_id):
            continue
        won = AgentConversation.objects.filter(
            id=lead.id, queued_prompt=prompt,
        ).filter(not_running).update(
            queued_prompt='', run_started_at=now, cancel_requested_at=None,
        )
        if not won:
            continue
        room -= 1
        claimed.append({
            'conversation_id': lead.id,
            'prompt': prompt,
            'model': lead.model_name,
            'project_id': lead.project_id,
        })
    return claimed


def _release_unstarted_coordinator(conversation_id: int, prompt: str) -> None:
    """A claimed coordinator whose run never got going: free it, and put its
    work back for the next pass."""
    from ..models import AgentConversation

    conversation = AgentConversation.objects.filter(id=conversation_id).first()
    if conversation is None:
        return
    queued = (conversation.queued_prompt or '').strip()
    conversation.queued_prompt = f"{prompt}\n\n{queued}" if queued else prompt
    conversation.run_started_at = None
    conversation.save(update_fields=['queued_prompt', 'run_started_at'])


def _coordinator_events(user, item: Dict[str, Any]):
    """The coordinator's run on staged work. The message it reads is marked
    as the app's, so the chat shows it as such rather than as the user's."""
    from .base_agent import ImagiAgentService
    from ..api.views import resolve_model

    async def events():
        model = resolve_model(item['model'])
        service = ImagiAgentService(model=model)
        service.user_message_metadata = {'app_error': True}
        started = False
        try:
            async for event in service.process_stream(
                user_input=item['prompt'],
                user=user,
                model=model,
                project_id=item['project_id'],
                conversation_id=item['conversation_id'],
            ):
                if event.get('type') == 'start':
                    started = True
                yield event
        finally:
            if not started:
                await sync_to_async(_release_unstarted_coordinator)(
                    item['conversation_id'], item['prompt'],
                )

    return events()


async def start_waiting_threads(user) -> Dict[str, Any]:
    """Start every thread that has staged work and a free slot, on this
    server, and every coordinator with app errors waiting for it.

    Returns {'started': n, 'blocked': None | 'usage'}.
    """
    from .detached_runs import start_detached_run

    outcome = await sync_to_async(_claim_waiting_threads)(user)
    for item in outcome['claimed']:
        logger.info("Starting thread %s on the server", item['conversation_id'])
        start_detached_run(
            lambda item=item: _thread_events(user, item),
            user=user,
            conversation_id=item['conversation_id'],
        )
    coordinators = await sync_to_async(_claim_waiting_coordinators)(user)
    for item in coordinators:
        logger.info("Starting coordinator %s on app errors", item['conversation_id'])
        start_detached_run(
            lambda item=item: _coordinator_events(user, item),
            user=user,
            conversation_id=item['conversation_id'],
        )
    return {'started': len(outcome['claimed']), 'blocked': outcome['blocked']}
