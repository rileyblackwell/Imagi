"""
The coordinator's schedule: units of work placed on threads.

The coordinator never does work itself. It places each job on a thread, and
the placement follows from what the job needs from work already under way:

- nothing: a new thread, running in parallel with everything else;
- another thread's result: that same thread, after its current work
  ('append' — a thread runs its tasks one at a time, so order is free);
- another thread's context but not its result: a fork of that thread, which
  starts from its conversation and runs in parallel ('fork');
- the results of other threads (fan-in, or a chain across threads): a new
  thread that waits until every one of them has landed in the app ('after').

Each placement is a ThreadTask row, so the schedule is explicit and
inspectable rather than implied by a prompt: the coordinator reads it back
every turn (tools.lead_task_roster), and the workspace shows it to the user.

A task is delivered through its thread's queued_prompt, the same staging
every thread run has always started from, so nothing about how threads run
changes. What tasks add is the hold: a task with dependencies is kept off
its thread until they land (release_waiting_tasks, called by the thread
scheduler each time it looks for work to start), and a dependency that
fails or is discarded blocks it instead of letting it run on a missing
foundation.
"""

import logging
from typing import Any, Dict, Iterable, List, Optional

from django.utils import timezone

logger = logging.getLogger(__name__)

# Task statuses that still have work ahead of them.
OPEN_STATUSES = ('waiting', 'blocked', 'queued', 'running', 'input', 'failed')
# Held back on the schedule, not yet on their thread.
HELD_STATUSES = ('waiting', 'blocked')
# A dependency in one of these will not land unless someone acts on it.
STUCK_STATUSES = ('failed', 'cancelled')

REASON_MAX_CHARS = 200
# How many tasks the schedule endpoint returns for one project.
SCHEDULE_MAX_TASKS = 60


def stage_on_thread(thread, text: str) -> None:
    """Put work on a thread as its next turn.

    A message already waiting there is joined rather than replaced, so the
    thread hears both. A finished or stopped thread is reopened so the thread
    scheduler picks it up; its run forks a fresh copy of the app as it is now
    and applies again when it finishes.
    """
    text = (text or '').strip()
    if not text:
        return
    queued = (thread.queued_prompt or '').strip()
    thread.queued_prompt = f"{queued}\n\n{text}" if queued else text
    fields = ['queued_prompt']
    if thread.review_status in ('accepted', 'failed'):
        thread.review_status = 'active'
        fields.append('review_status')
    thread.save(update_fields=fields + ['updated_at'])


def _latest_task(thread_id: int):
    """A thread's most recent live task — what depending on it means."""
    from ..models import ThreadTask

    return (
        ThreadTask.objects.filter(thread_id=thread_id)
        .exclude(status='cancelled')
        .order_by('-id')
        .first()
    )


def resolve_dependencies(user, lead, after_threads: Iterable, exclude_thread_id=None):
    """The tasks a new piece of work waits for, from the thread ids it names.

    Depending on a thread means depending on the work it has now. A thread
    whose work already landed adds nothing to wait for. Unknown ids are an
    error the coordinator can correct, rather than a silent no-op.
    """
    from ..models import AgentConversation

    deps = []
    seen = set()
    for raw in after_threads or ():
        try:
            thread_id = int(raw)
        except (TypeError, ValueError):
            raise ValueError(f"after takes thread numbers from your roster, not {raw!r}")
        if thread_id in seen or thread_id == exclude_thread_id:
            continue
        seen.add(thread_id)
        thread = AgentConversation.objects.filter(
            id=thread_id, user=user, kind='task', parent=lead
        ).first()
        if thread is None:
            raise ValueError(f"There is no thread {thread_id} under you to wait for.")
        task = _latest_task(thread_id)
        if task is not None:
            if task.status != 'done':
                deps.append(task)
        elif thread.review_status not in ('accepted',):
            # A thread from before the schedule existed has no task row;
            # give it one so there is something to wait on.
            deps.append(_adopt_untracked_thread(thread, lead))
    return deps


def _adopt_untracked_thread(thread, lead):
    from ..models import ThreadTask

    running = bool(thread.run_started_at)
    status = {
        'active': 'running' if running else 'queued',
        'input': 'input',
        'ready': 'input',
        'failed': 'failed',
        'dismissed': 'cancelled',
    }.get(thread.review_status, 'queued')
    return ThreadTask.objects.create(
        user=thread.user,
        project_id=thread.project_id,
        coordinator=lead,
        thread=thread,
        brief=thread.goal or thread.title or '',
        placement='new',
        status=status,
    )


def schedule_work(
    *, lead, thread, brief: str, placement: str = 'new', reason: str = '',
    depends_on: Optional[List] = None,
):
    """Record a unit of work on a thread, and stage it if nothing holds it.

    Returns the ThreadTask. With open dependencies it waits on the schedule
    and its thread stays idle; otherwise it is staged on the thread straight
    away, exactly as work always was.
    """
    from ..models import ThreadTask

    depends_on = list(depends_on or [])
    stuck = any(d.status in STUCK_STATUSES for d in depends_on)
    held = bool(depends_on)
    task = ThreadTask.objects.create(
        user=thread.user,
        project_id=thread.project_id,
        coordinator=lead,
        thread=thread,
        brief=brief,
        placement=placement,
        reason=' '.join((reason or '').split())[:REASON_MAX_CHARS],
        status=('blocked' if stuck else 'waiting') if held else 'queued',
    )
    if depends_on:
        task.depends_on.set(depends_on)
    else:
        stage_on_thread(thread, brief)
    return task


def release_waiting_tasks(user) -> int:
    """Stage every held task whose dependencies have all landed.

    Re-evaluates the held tasks: all dependencies done puts the task on its
    thread; any dependency failed or discarded blocks it; otherwise it keeps
    waiting (a blocked task whose dependency was retried goes back to
    waiting). Returns how many were staged.
    """
    from ..models import ThreadTask

    held = list(
        ThreadTask.objects.filter(user=user, status__in=HELD_STATUSES)
        .select_related('thread')
        .prefetch_related('depends_on')
    )
    staged = 0
    for task in held:
        thread = task.thread
        if thread.archived_at is not None or thread.review_status == 'dismissed':
            task.status = 'cancelled'
            task.finished_at = timezone.now()
            task.save(update_fields=['status', 'finished_at'])
            continue
        statuses = [d.status for d in task.depends_on.all()]
        if all(s == 'done' for s in statuses):
            stage_on_thread(thread, task.brief)
            task.status = 'queued'
            task.save(update_fields=['status'])
            staged += 1
            logger.info("Released task %s onto thread %s", task.id, thread.id)
        else:
            status = 'blocked' if any(s in STUCK_STATUSES for s in statuses) else 'waiting'
            if status != task.status:
                task.status = status
                task.save(update_fields=['status'])
    return staged


def task_run_started(thread, user_input: str) -> None:
    """A thread run is starting: the tasks it delivers are now running.

    That is every queued task whose brief is in this run's input, plus the
    task a question or a stop left parked — the run is its answer or retry.
    Work staged after the run was claimed stays queued for the next one.
    """
    from ..models import ThreadTask

    now = timezone.now()
    text = user_input or ''
    for task in ThreadTask.objects.filter(thread=thread, status__in=('queued', 'input', 'failed')):
        if task.status == 'queued' and task.brief.strip() not in text:
            continue
        task.status = 'running'
        task.started_at = task.started_at or now
        task.save(update_fields=['status', 'started_at'])


def task_run_ended(thread, outcome: str, summary: str = '', files=None) -> None:
    """A thread run ended: record how on the tasks it was running.

    outcome is 'done' (its work landed in the app), 'input' (it needs the
    user: a question, drafts to pick from, or work that could not go in) or
    'failed'. A finished task keeps a structured result the coordinator can
    read: its summary, the files it touched, and how it ended.
    """
    from ..models import ThreadTask

    now = timezone.now()
    running = ThreadTask.objects.filter(thread=thread, status='running')
    if outcome == 'done':
        result = {
            'outcome': 'done',
            'summary': (summary or '').strip()[:1200],
            'files': list(files or [])[:40],
        }
        running.update(status='done', finished_at=now, result=result)
    elif outcome in ('input', 'failed'):
        running.update(status=outcome)


def thread_landed(thread) -> None:
    """A thread's work went into the app outside a run's own ending (the user
    picked a draft): whatever it was waiting on the user for is done."""
    from ..models import ThreadTask

    ThreadTask.objects.filter(thread=thread, status__in=('running', 'input')).update(
        status='done', finished_at=timezone.now(),
    )


def cancel_thread_tasks(thread) -> None:
    """A thread was discarded: its open work will never land."""
    from ..models import ThreadTask

    ThreadTask.objects.filter(thread=thread, status__in=OPEN_STATUSES).update(
        status='cancelled', finished_at=timezone.now(),
    )


def thread_is_held(thread) -> bool:
    """Whether a thread's only pending work is held on the schedule."""
    from ..models import ThreadTask

    return ThreadTask.objects.filter(thread=thread, status__in=HELD_STATUSES).exists()


def _thread_label(thread) -> Dict[str, Any]:
    return {
        'id': thread.id,
        'title': (thread.goal or thread.title or '').strip(),
        'review_status': thread.review_status,
    }


def thread_schedule(thread) -> Optional[Dict[str, Any]]:
    """Where a thread stands on the schedule, for its card.

    The thread's current task (the oldest one still open, else its latest):
    how it was placed and why, and what it waits for. Plus where the thread
    was forked from. None for a thread with no schedule at all.
    """
    from ..models import ThreadTask

    tasks = list(ThreadTask.objects.filter(thread=thread).order_by('id'))
    current = next((t for t in tasks if t.status in OPEN_STATUSES), None)
    if current is None and tasks:
        current = tasks[-1]
    fork = getattr(thread, 'forked_from', None) if thread.forked_from_id else None
    if current is None and fork is None:
        return None
    data: Dict[str, Any] = {
        'task_id': current.id if current else None,
        'status': current.status if current else '',
        'placement': current.placement if current else 'fork',
        'reason': current.reason if current else '',
        'waits_on': [],
        'queued_after': 0,
        'forked_from': _thread_label(fork) if fork is not None else None,
    }
    if current is not None:
        for dep in current.depends_on.select_related('thread').order_by('id'):
            entry = _thread_label(dep.thread)
            entry['status'] = dep.status
            data['waits_on'].append(entry)
        # Work lined up on this thread behind the current task.
        data['queued_after'] = sum(
            1 for t in tasks if t.id > current.id and t.status in ('queued',) + HELD_STATUSES
        )
    return data


def serialize_task(task) -> Dict[str, Any]:
    return {
        'id': task.id,
        'thread_id': task.thread_id,
        'placement': task.placement,
        'reason': task.reason,
        'status': task.status,
        'depends_on': [d.id for d in task.depends_on.all()],
        'depends_on_threads': sorted({d.thread_id for d in task.depends_on.all()}),
        'result': task.result or {},
        'created_at': task.created_at.isoformat(),
        'started_at': task.started_at.isoformat() if task.started_at else None,
        'finished_at': task.finished_at.isoformat() if task.finished_at else None,
    }


def project_schedule(user, project_id) -> List[Dict[str, Any]]:
    """The project's schedule, newest work last: the task graph as data."""
    from ..models import ThreadTask

    tasks = list(
        ThreadTask.objects.filter(
            user=user, project_id=project_id, thread__archived_at__isnull=True,
        ).prefetch_related('depends_on').order_by('-id')[:SCHEDULE_MAX_TASKS]
    )
    tasks.reverse()
    return [serialize_task(t) for t in tasks]
