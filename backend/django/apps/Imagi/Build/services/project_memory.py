"""
A project's shared memory: what the coordinator and every thread know.

Each thread has its own conversation and nothing else, so anything decided in
one place (something the user chose, a convention, what a finished job built)
would otherwise reach later work only if the coordinator re-wrote it into a
brief. Project memory is that shared state: one short markdown document with
a few fixed sections, carried whole in every coordinator and thread prompt
and re-read before each model call (refresh_context), so a line saved
mid-run reaches work already running.

It keeps itself current. After each coordinator turn, and when a thread's
work lands in the app, a capture pass on a small model reads what just
happened beside the current memory and adds, rewrites or removes lines: the
pattern ChatGPT's automatic memory and Anthropic's memory consolidation use,
with the merging done as it goes so the document stays short. The agents can
also save a line on purpose (the remember tool), and the user can read and
edit the whole document.

Write discipline: the user, the coordinator and the capture pass write
directly. A thread's own notes wait on the thread until its work lands, and
its work is only captured then; work that is discarded leaves nothing behind.

Every write is recorded as a ProjectMemoryChange (who, which lines), so the
user can see where a line came from and undo it.
"""

import logging
import re
import threading
from typing import Any, Dict, Iterable, List, Optional, Tuple

from django.conf import settings
from django.db import close_old_connections, transaction
from django.utils import timezone

logger = logging.getLogger(__name__)

_BUILDER_SETTINGS = getattr(settings, 'IMAGI_BUILDER', {})

# The document's sections, in order. Fixed, so every agent knows where a
# line goes and the user always finds the same shape.
SECTIONS = (
    'About the app',
    'Decisions',
    "How it's built",
    'How the user likes to work',
)
DEFAULT_SECTION = 'Decisions'

# What every prompt carries. The capture pass is asked to keep the document
# under this, merging and pruning as it goes; anything past it is cut from
# the prompt (never from the document).
MEMORY_MAX_CHARS = 6000
# What the user may save by hand.
EDIT_MAX_CHARS = 20000
LINE_MAX_CHARS = 400
# A thread's notes waiting for its work to land.
MAX_THREAD_NOTES = 30
CHANGES_SHOWN = 20

# The capture pass: on by default, off with IMAGI_BUILDER['MEMORY_CAPTURE'].
CAPTURE_ENABLED = _BUILDER_SETTINGS.get('MEMORY_CAPTURE', True)
# How much of a turn it reads: the newest messages, up to this many chars.
CAPTURE_TRANSCRIPT_CHARS = 12000
CAPTURE_MESSAGE_CHARS = 2500
CAPTURE_MAX_TOKENS = 2000

CAPTURE_SYSTEM = f"""You keep the shared memory of an app being built in Imagi, where people build web apps by chatting with AI agents: a coordinator the user talks to, and threads that each do one job in the code. Every agent reads this memory before it works, so it holds what later work should know and nothing else.

Given the current memory and what just happened, call update_memory with the changes worth keeping: what the user decided or asked for that should keep holding, what the app is and does, how it's built (conventions, structure, where things live, what broke and how it was fixed), and how the user likes to work. Each line is one short, self-contained fact in plain words. Skip progress updates, small talk, guesses, anything already in memory, and anything that only mattered in the moment. When something new contradicts or refines a line, remove that line (quote it exactly) and add the new one. Keep the whole memory under {MEMORY_MAX_CHARS} characters, merging or dropping the least useful lines as it nears that. Most turns change nothing: then send an empty list."""

CAPTURE_TOOL = {
    'name': 'update_memory',
    'description': 'Apply changes to the project memory; an empty list when nothing should change.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'changes': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'action': {'type': 'string', 'enum': ['add', 'remove']},
                        'section': {'type': 'string', 'enum': list(SECTIONS)},
                        'text': {
                            'type': 'string',
                            'description': 'The line to add, or the existing line to remove, quoted exactly.',
                        },
                    },
                    'required': ['action', 'section', 'text'],
                },
            },
        },
        'required': ['changes'],
    },
}


class MemoryConflict(Exception):
    """The user's edit was made against an older copy of the memory."""


# --- The document -------------------------------------------------------------

_HEADING_RE = re.compile(r'^##\s+(.*\S)\s*$')
_BULLET_RE = re.compile(r'^\s*(?:[-*+]|\d+[.)])\s+')


def _norm(text: str) -> str:
    """A line as compared: no bullet, one space, any case, no end stop."""
    text = _BULLET_RE.sub('', str(text or ''))
    return ' '.join(text.split()).lower().rstrip('.')


def _clean_line(text: str) -> str:
    text = ' '.join(_BULLET_RE.sub('', str(text or '')).split())[:LINE_MAX_CHARS]
    if not text:
        raise ValueError("A memory line needs some text")
    return text


def section_for(name: Optional[str]) -> str:
    """The fixed section a name means (any case), else the default."""
    wanted = ' '.join(str(name or '').split()).lower()
    for section in SECTIONS:
        if section.lower() == wanted:
            return section
    return DEFAULT_SECTION


def _parse(content: str) -> Tuple[List[str], List[List[Any]]]:
    """(lines before the first section, [[heading, lines], ...])."""
    head: List[str] = []
    sections: List[List[Any]] = []
    for raw in (content or '').splitlines():
        match = _HEADING_RE.match(raw)
        if match:
            sections.append([match.group(1), []])
        elif sections:
            sections[-1][1].append(raw.rstrip())
        else:
            head.append(raw.rstrip())
    return head, sections


def _render(head: List[str], sections: List[List[Any]]) -> str:
    parts = []
    preamble = '\n'.join(head).strip()
    if preamble:
        parts.append(preamble)
    for heading, lines in sections:
        body = '\n'.join(lines).strip('\n')
        parts.append(f"## {heading}\n{body}" if body.strip() else f"## {heading}")
    return '\n\n'.join(parts).strip() + '\n'


def blank_document() -> str:
    return _render([], [[s, []] for s in SECTIONS])


def _find_section(sections: List[List[Any]], name: str) -> List[Any]:
    for section in sections:
        if section[0].strip().lower() == name.lower():
            return section
    # A fixed section that was deleted comes back in its place in the order.
    created = [name, []]
    if name in SECTIONS:
        later = SECTIONS[SECTIONS.index(name) + 1:]
        for i, section in enumerate(sections):
            if section[0] in later:
                sections.insert(i, created)
                return created
    sections.append(created)
    return created


def _add(content: str, section: str, text: str) -> Optional[str]:
    """The document with a line added, or None when it already holds it."""
    head, sections = _parse(content or blank_document())
    wanted = _norm(text)
    for _, lines in sections:
        if any(_norm(line) == wanted for line in lines if line.strip()):
            return None
    lines = _find_section(sections, section)[1]
    while lines and not lines[-1].strip():
        lines.pop()
    lines.append(f"- {text}")
    return _render(head, sections)


def _remove(content: str, text: str) -> Optional[Tuple[str, str, str]]:
    """(document, section, line) with one line removed, or None.

    An exact match (bullets, spacing and case aside) wins; otherwise the one
    line that contains the text, when exactly one does."""
    head, sections = _parse(content)
    wanted = _norm(text)
    if not wanted:
        return None
    candidates = []
    for section in sections:
        for i, line in enumerate(section[1]):
            if line.strip() and _norm(line) == wanted:
                candidates = [(section, i)]
                break
        else:
            continue
        break
    if not candidates:
        candidates = [
            (section, i)
            for section in sections
            for i, line in enumerate(section[1])
            if line.strip() and wanted in _norm(line)
        ]
    if len(candidates) != 1:
        return None
    section, i = candidates[0]
    removed = _BULLET_RE.sub('', section[1].pop(i)).strip()
    return _render(head, sections), section[0], removed


def _lines_by_section(content: str) -> List[Tuple[str, str]]:
    """Every non-blank line under a section, as (section, text)."""
    _, sections = _parse(content)
    return [
        (heading, _BULLET_RE.sub('', line).strip())
        for heading, lines in sections
        for line in lines
        if line.strip()
    ]


def prompt_view(content: str) -> str:
    """The document as prompts carry it: sections with nothing in them left out."""
    head, sections = _parse(content)
    kept = [s for s in sections if any(line.strip() for line in s[1])]
    if not kept and not '\n'.join(head).strip():
        return ''
    return _render(head, kept).strip()


# --- Reading and writing --------------------------------------------------------

def _document(user_id, project_id, lock: bool = False):
    from ..models import ProjectMemoryDocument

    rows = ProjectMemoryDocument.objects
    if lock:
        rows = rows.select_for_update()
    doc = rows.filter(user_id=user_id, project_id=project_id).first()
    if doc is None and lock:
        doc, _ = ProjectMemoryDocument.objects.get_or_create(
            user_id=user_id, project_id=project_id,
            defaults={'content': blank_document()},
        )
    return doc


def read_document(user_id, project_id) -> str:
    doc = _document(user_id, project_id)
    return doc.content if doc is not None else ''


def apply_changes(user_id, project_id, changes: Iterable[Dict[str, Any]],
                  author: str, source=None):
    """Apply add/remove changes to the current document, atomically.

    Each change is matched against the document as it is now, not as the
    writer saw it, so concurrent writers (the capture pass, a thread landing,
    the user) never undo one another; a removal whose line is gone is
    skipped. Returns the recorded ProjectMemoryChange, or None when nothing
    changed."""
    from ..models import ProjectMemoryChange

    if project_id is None:
        raise ValueError("Project memory needs a project")
    with transaction.atomic():
        doc = _document(user_id, project_id, lock=True)
        content = doc.content or blank_document()
        applied: List[Dict[str, str]] = []
        for change in changes or []:
            op = (change or {}).get('action') or (change or {}).get('op')
            text = (change or {}).get('text') or ''
            try:
                if op == 'add':
                    line = _clean_line(text)
                    section = section_for(change.get('section'))
                    updated = _add(content, section, line)
                    if updated is not None:
                        content = updated
                        applied.append({'op': 'add', 'section': section, 'text': line})
                elif op == 'remove':
                    result = _remove(content, text)
                    if result is not None:
                        content, section, line = result
                        applied.append({'op': 'remove', 'section': section, 'text': line})
            except ValueError:
                continue
        if not applied:
            return None
        doc.content = content
        doc.version += 1
        doc.save(update_fields=['content', 'version', 'updated_at'])
        return ProjectMemoryChange.objects.create(
            user_id=user_id, project_id=project_id, author=author,
            source=source, lines=applied,
        )


def remember(user_id, project_id, text: str, section: Optional[str] = None,
             author: str = 'coordinator', source=None):
    """Save one line now."""
    return apply_changes(
        user_id, project_id,
        [{'action': 'add', 'section': section, 'text': _clean_line(text)}],
        author=author, source=source,
    )


def forget(user_id, project_id, text: str, author: str = 'coordinator', source=None):
    """Remove the line that matches (exactly, or the one line containing it)."""
    return apply_changes(
        user_id, project_id, [{'action': 'remove', 'text': text}],
        author=author, source=source,
    )


def _line_diff(before: str, after: str) -> List[Dict[str, str]]:
    """Which lines an edit removed and added, by section."""
    old = _lines_by_section(before)
    new = _lines_by_section(after)
    old_norms = {_norm(t) for _, t in old}
    new_norms = {_norm(t) for _, t in new}
    return [
        {'op': 'remove', 'section': s, 'text': t} for s, t in old if _norm(t) not in new_norms
    ] + [
        {'op': 'add', 'section': s, 'text': t} for s, t in new if _norm(t) not in old_norms
    ]


def save_document(user_id, project_id, content: str, base_version: int,
                  base_content: Optional[str] = None):
    """The user's own edit of the whole document.

    Saved as written when nothing changed since the copy they edited. When
    the capture pass or a thread saved lines meanwhile, their edit is merged
    instead: the lines they removed and added (against base_content, the
    copy they started from) are applied to the memory as it is now, so
    neither side's lines are lost. Without base_content that case is refused
    (MemoryConflict). Recorded as which lines they added and removed."""
    from ..models import ProjectMemoryChange

    content = (content or '').replace('\r\n', '\n')
    if len(content) > EDIT_MAX_CHARS:
        raise ValueError(f"Project memory is limited to {EDIT_MAX_CHARS:,} characters")
    content = content.strip() + '\n' if content.strip() else blank_document()
    with transaction.atomic():
        doc = _document(user_id, project_id, lock=True)
        if int(base_version) != doc.version:
            if base_content is None:
                raise MemoryConflict()
            edits = _line_diff(base_content, content)
            apply_changes(
                user_id, project_id,
                [{'action': e['op'], 'section': e['section'], 'text': e['text']} for e in edits],
                author='user',
            )
            return _document(user_id, project_id)
        if content == doc.content:
            return doc
        lines = _line_diff(doc.content, content)
        doc.content = content
        doc.version += 1
        doc.save(update_fields=['content', 'version', 'updated_at'])
        if lines:
            ProjectMemoryChange.objects.create(
                user_id=user_id, project_id=project_id, author='user', lines=lines,
            )
        return doc


def undo_change(change) -> None:
    """Put the lines one change touched back the way they were."""
    if change.undone_at is not None:
        raise ValueError("That change was already undone")
    inverse = [
        {'action': 'remove', 'text': line['text']} if line.get('op') == 'add'
        else {'action': 'add', 'section': line.get('section'), 'text': line['text']}
        for line in reversed(change.lines or [])
    ]
    with transaction.atomic():
        # Applied without a record of its own: the undone change is the record.
        from ..models import ProjectMemoryChange

        recorded = apply_changes(
            change.user_id, change.project_id, inverse, author='user',
        )
        if recorded is not None:
            ProjectMemoryChange.objects.filter(id=recorded.id).delete()
        change.undone_at = timezone.now()
        change.save(update_fields=['undone_at'])


def memory_summary(user_id, project_id) -> str:
    """The block every coordinator and thread prompt carries."""
    if project_id is None:
        return ''
    text = prompt_view(read_document(user_id, project_id))
    if not text:
        return ''
    if len(text) > MEMORY_MAX_CHARS:
        text = text[:MEMORY_MAX_CHARS].rstrip() + '\n…'
    return "Project memory, shared by the coordinator and every thread:\n" + text


def refresh_context(context) -> Optional[str]:
    """Re-read the memory onto a run's context; return it when it changed."""
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


# --- Threads -------------------------------------------------------------------

def add_thread_note(thread, text: str, section: Optional[str] = None) -> None:
    """A thread's remember: held on the thread until its work lands."""
    from ..models import AgentConversation

    line = _clean_line(text)
    with transaction.atomic():
        row = AgentConversation.objects.select_for_update().get(pk=thread.pk)
        notes = [n for n in (row.memory_notes or []) if _norm(n.get('text')) != _norm(line)]
        notes.append({'section': section_for(section), 'text': line})
        row.memory_notes = notes[-MAX_THREAD_NOTES:]
        row.save(update_fields=['memory_notes'])
    thread.memory_notes = row.memory_notes


def thread_landed(thread, capture: bool = True) -> None:
    """The thread's work is in the app: its notes are saved, and what it did
    is read for anything else worth keeping."""
    from ..models import AgentConversation

    notes = list(
        AgentConversation.objects.filter(pk=thread.pk).values_list('memory_notes', flat=True).first()
        or []
    )
    AgentConversation.objects.filter(pk=thread.pk).update(memory_notes=[])
    thread.memory_notes = []
    if notes and thread.project_id is not None:
        apply_changes(
            thread.user_id, thread.project_id,
            [{'action': 'add', 'section': n.get('section'), 'text': n.get('text')} for n in notes],
            author='thread', source=thread,
        )
    if capture:
        schedule_capture(thread.pk)


def thread_discarded(thread) -> None:
    """The thread's work will never land: neither do its notes, and nothing it
    said up to now is captured later."""
    from ..models import AgentConversation

    last = thread.messages.order_by('-id').values_list('id', flat=True).first() or 0
    AgentConversation.objects.filter(pk=thread.pk).update(memory_notes=[], memory_cursor=last)
    thread.memory_notes = []


def pending_notes(user, project_id) -> List[Dict[str, Any]]:
    """Threads' notes still waiting for their work to land."""
    from ..models import AgentConversation

    rows = AgentConversation.objects.filter(
        user=user, project_id=project_id, kind='task',
    ).exclude(memory_notes=[]).order_by('id')
    return [
        {
            'thread': {'id': row.id, 'title': (row.goal or row.title or '').strip()},
            'notes': row.memory_notes,
        }
        for row in rows
        if row.memory_notes
    ]


# --- Automatic capture ------------------------------------------------------------

def schedule_capture(conversation_id: int) -> None:
    """Read the conversation's newest messages for memory, in the background:
    nothing the user waits on depends on it."""
    from .api_keys import read_api_key

    # Without a key there is no model to read with (the test runner drops it).
    if not CAPTURE_ENABLED or not conversation_id or not read_api_key('ANTHROPIC_KEY'):
        return

    def run():
        try:
            capture(conversation_id)
        except Exception as e:
            logger.warning(f"Memory capture for conversation {conversation_id} failed: {e}")
        finally:
            close_old_connections()

    threading.Thread(target=run, name=f'memory-capture-{conversation_id}', daemon=True).start()


def _turn_transcript(conversation, messages) -> str:
    """What the capture pass reads: the user's words and the agents' replies,
    newest kept when it is long. Thread reports and app errors are left to
    the threads they came from, which are captured when their work lands."""
    parts: List[str] = []
    if conversation.kind == 'task' and conversation.goal:
        parts.append(f"The thread's job: {conversation.goal.strip()}")
    # A thread's first message is the coordinator's brief, not the user.
    brief_id = (
        messages[0].id
        if conversation.kind == 'task' and conversation.memory_cursor == 0 and messages
        else None
    )
    files: List[str] = []
    for message in messages:
        metadata = message.metadata if isinstance(message.metadata, dict) else {}
        content = (message.content or '').strip()
        if not content or metadata.get('task_report') or content.startswith('[App error]'):
            continue
        if len(content) > CAPTURE_MESSAGE_CHARS:
            content = content[:CAPTURE_MESSAGE_CHARS] + ' …'
        if message.role == 'user':
            speaker = 'Brief from the coordinator' if message.id == brief_id else 'User'
        elif message.role == 'assistant':
            speaker = 'Thread' if conversation.kind == 'task' else 'Coordinator'
            for path in metadata.get('files_changed') or []:
                if isinstance(path, str) and path not in files:
                    files.append(path)
        else:
            continue
        parts.append(f"{speaker}: {content}")
    if files:
        parts.append("Files the thread changed: " + ', '.join(files[:40]))
    text = '\n\n'.join(parts)
    if len(text) > CAPTURE_TRANSCRIPT_CHARS:
        text = '…' + text[-CAPTURE_TRANSCRIPT_CHARS:]
    return text


def _call_capture_model(memory: str, where: str, transcript: str, client=None):
    """(changes, usage) from the capture model."""
    from .api_keys import read_api_key
    from .helper_tools import HELPER_MODEL
    from .models_service import compute_cost_usd, get_backend_model_id

    model = _BUILDER_SETTINGS.get('MEMORY_MODEL', HELPER_MODEL)
    if client is None:
        api_key = read_api_key('ANTHROPIC_KEY')
        if not api_key:
            return [], None
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=get_backend_model_id(model),
        max_tokens=CAPTURE_MAX_TOKENS,
        system=CAPTURE_SYSTEM,
        tools=[CAPTURE_TOOL],
        tool_choice={'type': 'tool', 'name': CAPTURE_TOOL['name']},
        messages=[{
            'role': 'user',
            'content': (
                f"Current project memory:\n<memory>\n{memory or '(empty)'}\n</memory>\n\n"
                f"What just happened, {where}:\n<transcript>\n{transcript}\n</transcript>"
            ),
        }],
    )
    changes: List[Dict[str, Any]] = []
    for block in response.content or []:
        if getattr(block, 'type', '') == 'tool_use':
            raw = (getattr(block, 'input', None) or {}).get('changes') or []
            changes = [c for c in raw if isinstance(c, dict)]
    reading = getattr(response, 'usage', None)
    cache_read = getattr(reading, 'cache_read_input_tokens', 0) or 0
    cache_write = getattr(reading, 'cache_creation_input_tokens', 0) or 0
    input_tokens = (getattr(reading, 'input_tokens', 0) or 0) + cache_read + cache_write
    output_tokens = getattr(reading, 'output_tokens', 0) or 0
    usage = {
        'model': model,
        'input_tokens': input_tokens,
        'output_tokens': output_tokens,
        'cost_usd': compute_cost_usd(model, input_tokens, output_tokens, cache_read),
    }
    return changes, usage


def capture(conversation_id: int, client=None):
    """Read what is new in a coordinator chat or a landed thread and save
    what later work should know. Returns the recorded change, if any."""
    from ..models import AgentConversation

    conversation = AgentConversation.objects.filter(id=conversation_id).first()
    if conversation is None or conversation.project_id is None:
        return None
    if conversation.kind not in ('lead', 'task'):
        return None
    messages = list(
        conversation.messages.filter(id__gt=conversation.memory_cursor).order_by('id')
    )
    if not messages:
        return None
    # Claim the messages first, so two passes never read the same turn.
    claimed = AgentConversation.objects.filter(
        pk=conversation.pk, memory_cursor=conversation.memory_cursor,
    ).update(memory_cursor=messages[-1].id)
    if not claimed:
        return None
    # A coordinator turn that carried nothing from the user (a thread report,
    # an app error) has nothing of the user's to keep.
    if conversation.kind == 'lead' and not any(
        m.role == 'user' and not (m.content or '').lstrip().startswith('[App error]')
        for m in messages
    ):
        return None
    transcript = _turn_transcript(conversation, messages)
    if not transcript.strip():
        return None
    where = (
        "a thread's work that just landed in the app"
        if conversation.kind == 'task' else "the user's latest turn with the coordinator"
    )
    memory = prompt_view(read_document(conversation.user_id, conversation.project_id))
    changes, usage = _call_capture_model(memory, where, transcript, client=client)
    if usage:
        _meter(conversation, usage)
    if not changes:
        return None
    return apply_changes(
        conversation.user_id, conversation.project_id, changes,
        author='auto', source=conversation,
    )


def _meter(conversation, usage: Dict[str, Any]) -> None:
    """Charge the pass to the user's allowance, like any helper call."""
    if not (usage.get('input_tokens') or usage.get('output_tokens')):
        return
    try:
        from .usage_limits import record_usage
        record_usage(
            conversation.user, usage['model'],
            usage['input_tokens'], usage['output_tokens'],
            cost_usd=usage.get('cost_usd'), conversation_id=conversation.id,
        )
    except Exception as e:  # metering must never fail the pass
        logger.warning(f"Could not record memory capture usage: {e}")


# --- What the workspace shows --------------------------------------------------------

def serialize_change(change) -> Dict[str, Any]:
    source = change.source
    return {
        'id': change.id,
        'author': change.author,
        'source': (
            {
                'id': source.id,
                'kind': source.kind,
                'title': (source.goal or source.title or '').strip(),
            }
            if source is not None else None
        ),
        'lines': change.lines or [],
        'created_at': change.created_at.isoformat(),
        'undone': change.undone_at is not None,
    }


def workspace_view(user, project_id) -> Dict[str, Any]:
    """The memory, its recent changes, and threads' notes not yet saved."""
    from ..models import ProjectMemoryChange

    doc = _document(user.id, project_id)
    changes = ProjectMemoryChange.objects.filter(
        user=user, project_id=project_id,
    ).select_related('source').order_by('-id')[:CHANGES_SHOWN]
    return {
        'content': doc.content if doc is not None else blank_document(),
        'version': doc.version if doc is not None else 0,
        'updated_at': doc.updated_at.isoformat() if doc is not None else None,
        'sections': list(SECTIONS),
        'max_chars': MEMORY_MAX_CHARS,
        'changes': [serialize_change(c) for c in changes],
        'pending': pending_notes(user, project_id),
    }
