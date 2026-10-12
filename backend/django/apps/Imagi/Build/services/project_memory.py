"""
A project's shared memory: what every thread and the coordinator know.

Each thread has its own conversation and nothing else, so anything decided in
one thread (a convention, a choice the user made, what a finished job built)
would otherwise reach the next only if the coordinator re-wrote it into a
brief. Project memory is the shared state instead: short keyed entries,
injected as a compact summary into every coordinator and thread prompt, with
the recall tool for anything the summary had to shorten.

Write discipline: the user and the coordinator write entries directly. A
thread proposes one (the remember tool, run from a thread), and the proposal
becomes an entry when that thread's work lands in the app; work that is
discarded takes its proposals with it. One entry per key: writing a key
again replaces it.

Freshness: a running thread re-reads the summary before each model call
(refresh_context), so an entry committed mid-run reaches it on its next step.
"""

import logging
from typing import Any, Dict, List, Optional

from django.db import transaction

logger = logging.getLogger(__name__)

KEY_MAX_CHARS = 80
VALUE_MAX_CHARS = 1000
# The summary every prompt carries: whole entries while they fit, shortened
# ones after that, and a pointer to recall for the rest.
SUMMARY_MAX_CHARS = 3000
SUMMARY_VALUE_CHARS = 240
MAX_ENTRIES_PER_PROJECT = 200


def _clean_key(key: str) -> str:
    key = ' '.join(str(key or '').split())[:KEY_MAX_CHARS]
    if not key:
        raise ValueError("A memory entry needs a short key naming what it is about")
    return key


def _clean_value(value: str) -> str:
    value = str(value or '').strip()[:VALUE_MAX_CHARS]
    if not value:
        raise ValueError("A memory entry needs a value")
    return value


def _active(user_id, project_id):
    from ..models import ProjectMemory

    return ProjectMemory.objects.filter(
        user_id=user_id, project_id=project_id, status='active'
    )


def write_entry(user_id, project_id, key, value, author='coordinator', source=None):
    """Write an active entry, replacing any active entry with the same key."""
    from ..models import ProjectMemory

    if project_id is None:
        raise ValueError("Project memory needs a project")
    key = _clean_key(key)
    value = _clean_value(value)
    with transaction.atomic():
        existing = _active(user_id, project_id).filter(key__iexact=key).order_by('id')
        entry = existing.first()
        if entry is not None:
            existing.exclude(id=entry.id).delete()
            entry.key = key
            entry.value = value
            entry.author = author
            entry.source = source
            entry.save(update_fields=['key', 'value', 'author', 'source', 'updated_at'])
            return entry
        if _active(user_id, project_id).count() >= MAX_ENTRIES_PER_PROJECT:
            raise ValueError(
                "Project memory is full; forget an entry that no longer holds first"
            )
        return ProjectMemory.objects.create(
            user_id=user_id, project_id=project_id, key=key, value=value,
            status='active', author=author, source=source,
        )


def propose_entry(thread, key, value):
    """A thread's entry, held until its work lands (one per key per thread)."""
    from ..models import ProjectMemory

    key = _clean_key(key)
    value = _clean_value(value)
    ProjectMemory.objects.filter(
        source=thread, status='proposed', key__iexact=key
    ).delete()
    return ProjectMemory.objects.create(
        user_id=thread.user_id, project_id=thread.project_id, key=key, value=value,
        status='proposed', author='thread', source=thread,
    )


def commit_proposals(thread) -> int:
    """The thread's work landed: its proposed entries become project memory."""
    from ..models import ProjectMemory

    committed = 0
    for proposal in ProjectMemory.objects.filter(source=thread, status='proposed').order_by('id'):
        try:
            write_entry(
                proposal.user_id, proposal.project_id, proposal.key, proposal.value,
                author='thread', source=thread,
            )
            committed += 1
        except ValueError as e:
            logger.info("Dropped memory proposal %s: %s", proposal.id, e)
        proposal.delete()
    return committed


def drop_proposals(thread) -> None:
    """The thread's work was discarded: so are its proposals."""
    from ..models import ProjectMemory

    ProjectMemory.objects.filter(source=thread, status='proposed').delete()


def edit_entry(entry, key, value):
    """The user editing an entry. An active one becomes theirs (and replaces
    any other active entry its new key collides with); a thread's proposal
    stays a proposal."""
    key = _clean_key(key)
    value = _clean_value(value)
    with transaction.atomic():
        if entry.status == 'active':
            _active(entry.user_id, entry.project_id).filter(
                key__iexact=key
            ).exclude(id=entry.id).delete()
            entry.author = 'user'
        entry.key = key
        entry.value = value
        entry.save(update_fields=['key', 'value', 'author', 'updated_at'])
    return entry


def forget_entry(user_id, project_id, key) -> bool:
    deleted, _ = _active(user_id, project_id).filter(key__iexact=_clean_key(key)).delete()
    return deleted > 0


def memory_summary(user_id, project_id) -> str:
    """The compact block every coordinator and thread prompt carries."""
    if project_id is None:
        return ''
    entries = list(_active(user_id, project_id).order_by('key', 'id'))
    if not entries:
        return ''
    lines = []
    used = 0
    shortened = False
    for entry in entries:
        value = ' '.join(entry.value.split())
        if len(value) > SUMMARY_VALUE_CHARS:
            value = value[:SUMMARY_VALUE_CHARS].rstrip() + '…'
            shortened = True
        line = f"- {entry.key}: {value}"
        if used + len(line) > SUMMARY_MAX_CHARS:
            shortened = True
            lines.append(f"- …and {len(entries) - len(lines)} more")
            break
        lines.append(line)
        used += len(line)
    text = "Project memory (shared by the coordinator and every thread):\n" + "\n".join(lines)
    if shortened:
        text += "\nUse recall for the full entries."
    return text


def recall(user_id, project_id, query: str = '') -> List[Dict[str, str]]:
    """Full entries whose key or value mentions the query (all, if empty)."""
    entries = _active(user_id, project_id)
    query = ' '.join((query or '').split())
    if query:
        from django.db.models import Q
        entries = entries.filter(Q(key__icontains=query) | Q(value__icontains=query))
    return [{'key': e.key, 'value': e.value} for e in entries.order_by('key', 'id')[:30]]


def serialize_entry(entry) -> Dict[str, Any]:
    source = entry.source
    return {
        'id': entry.id,
        'key': entry.key,
        'value': entry.value,
        'status': entry.status,
        'author': entry.author,
        'source': (
            {'id': source.id, 'title': (source.goal or source.title or '').strip()}
            if source is not None else None
        ),
        'updated_at': entry.updated_at.isoformat(),
    }


def project_entries(user, project_id) -> List[Dict[str, Any]]:
    """Active entries and pending proposals, for the workspace's memory panel."""
    from ..models import ProjectMemory

    rows = ProjectMemory.objects.filter(
        user=user, project_id=project_id,
    ).select_related('source').order_by('status', 'key', 'id')
    return [serialize_entry(e) for e in rows]


def refresh_context(context) -> Optional[str]:
    """Re-read the summary onto a run's context; return it when it changed."""
    user_id = getattr(context, 'user_id', None)
    project_id = getattr(context, 'project_id', None)
    if user_id is None or project_id is None:
        return None
    try:
        fresh = memory_summary(user_id, project_id)
    except Exception as e:  # pragma: no cover - best effort
        logger.warning(f"Could not refresh project memory: {e}")
        return None
    if fresh != getattr(context, 'project_memory', ''):
        context.project_memory = fresh
        return fresh
    return None
