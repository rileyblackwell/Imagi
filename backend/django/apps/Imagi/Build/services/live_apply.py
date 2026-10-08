"""
Threads' edits, applied to the app as they are written.

A thread still works in its own git worktree, so its history stays separate
and it still merges when it finishes. But each file it writes is also copied
straight into the project the preview serves. The preview's dev servers
reload on their own (Vite hot-swaps the frontend, Django's runserver restarts
on backend edits), so the user, and the thread through its browser tools, see
the change at once. The thread and the preview make one live loop.

Two threads must not overwrite each other through this copy, so a file is
copied only when the project still holds what the thread had there before its
edit: the file as the thread forked it, or the thread's own last copy. If
anyone else changed it since, the copy is skipped and the thread's version
waits for the merge at the end, where git reconciles the two.

After a copy, the preview gets a moment to reload, and any new console error
or dev-server error is handed back in the thread's own tool result. An error
an edit causes therefore reaches the thread that made it, while it can still
fix it.

Drafts (several threads on one job, for the user to pick between) and the
first build's page threads are not copied: drafts would overwrite each other,
and a first-build page is checked before it is allowed into the project.
"""

import logging
import os
import re
import subprocess
import time
from typing import Dict, List, Optional

from django.conf import settings

logger = logging.getLogger(__name__)

_BUILDER = getattr(settings, 'IMAGI_BUILDER', {})
ENABLED = _BUILDER.get('LIVE_APPLY_THREAD_EDITS', True)
# How long the preview gets to reload before its errors are read.
SETTLE_SECONDS = _BUILDER.get('LIVE_APPLY_SETTLE_S', 1.5)
# Dev-server log lines worth a thread's attention.
_LOG_ERROR_RE = re.compile(
    r'(error|traceback|exception|failed to (?:resolve|load|compile))', re.IGNORECASE
)
MAX_LOG_LINES = 12
MAX_REPORTED_ERRORS = 6


def applies_to(context) -> bool:
    """Whether this run's file edits are copied into the project live."""
    return bool(
        ENABLED
        and getattr(context, 'live_apply', False)
        and getattr(context, 'project_path', None)
        and getattr(context, 'effective_project_path', None)
        and os.path.normpath(context.project_path)
        != os.path.normpath(context.effective_project_path)
    )


def _read(path: str) -> Optional[bytes]:
    try:
        with open(path, 'rb') as f:
            return f.read()
    except (FileNotFoundError, IsADirectoryError, NotADirectoryError):
        return None


def snapshot(context, file_path: str) -> Optional[bytes]:
    """The thread's copy of a file just before it edits it (None: no file)."""
    if not applies_to(context):
        return None
    return _read(os.path.join(context.effective_project_path, file_path))


class Mark:
    """Where the preview's error sources stood just before an edit."""

    def __init__(self, context):
        self.started_ms = int(time.time() * 1000)
        self.logs = {}
        for path in _log_files(context):
            try:
                self.logs[path] = os.path.getsize(path)
            except OSError:
                pass


def mirror(context, file_path: str, previous: Optional[bytes]) -> Dict:
    """Copy the thread's file into the project if no one else changed it.

    Returns {'live': True} when copied, {'live': False, 'reason': ...} when it
    was held back for the merge, and {} when live apply does not apply.
    """
    if not applies_to(context):
        return {}
    from .version_control_service import canonical_repo_lock

    source = os.path.join(context.effective_project_path, file_path)
    target = os.path.join(context.project_path, file_path)
    content = _read(source)
    try:
        # The repo lock keeps the copy out of the middle of a merge.
        with canonical_repo_lock(context.project_path):
            current = _read(target)
            if current == content:
                return {'live': True}
            if current != previous:
                return {
                    'live': False,
                    'reason': (
                        'Someone else changed this file in the app while you '
                        'were working, so your version goes in when you finish.'
                    ),
                }
            if content is None:
                if current is not None:
                    os.remove(target)
            else:
                os.makedirs(os.path.dirname(target), exist_ok=True)
                tmp = f'{target}.imagi-live'
                with open(tmp, 'wb') as f:
                    f.write(content)
                os.replace(tmp, target)
    except OSError as e:
        logger.warning("Could not apply %s to the project live: %s", file_path, e)
        return {'live': False, 'reason': 'It could not be copied into the app; it goes in when you finish.'}
    from .app_errors import record_live_edit

    record_live_edit(
        getattr(context, 'project_id', None), getattr(context, 'conversation_id', None), file_path,
    )
    return {'live': True}


def apply_edit(context, file_path: str, previous: Optional[bytes], mark: Optional[Mark]) -> Dict:
    """Mirror one edit and read back what the preview made of it.

    The result is merged into the tool's own JSON answer: 'applied_to_app'
    says whether the preview now shows the edit, and 'preview_errors' lists
    anything that went wrong in the app right after it.
    """
    outcome = mirror(context, file_path, previous)
    if not outcome:
        return {}
    result = {'applied_to_app': outcome['live']}
    if not outcome['live']:
        result['note'] = outcome['reason']
        return result
    errors = preview_errors(context, mark) if mark else []
    if errors:
        result['preview_errors'] = errors
        result['instruction'] = (
            'The app reported these errors right after this edit. If your change '
            'caused them, fix them before moving on.'
        )
    return result


def _log_files(context) -> List[str]:
    try:
        from apps.Imagi.ProjectManager.models import Project
        from .preview_service import PreviewService

        project = Project.objects.get(id=context.project_id)
        service = PreviewService(project)
        return [service.frontend_log_file, service.backend_log_file]
    except Exception:
        return []


def _new_log_errors(path: str, offset: int) -> List[str]:
    try:
        with open(path, 'rb') as f:
            f.seek(offset)
            tail = f.read(64 * 1024).decode('utf-8', errors='replace')
    except OSError:
        return []
    lines = [line.strip() for line in tail.splitlines() if line.strip()]
    hits = [line for line in lines if _LOG_ERROR_RE.search(line)]
    return hits[:MAX_LOG_LINES]


def preview_errors(context, mark: Mark, settle: Optional[float] = None) -> List[str]:
    """New errors from the preview since ``mark``: the page's console and the
    dev servers' logs. Never starts the preview, and never raises."""
    wait = SETTLE_SECONDS if settle is None else settle
    if wait:
        time.sleep(wait)
    errors: List[str] = []
    for path, offset in mark.logs.items():
        source = 'frontend server' if path.endswith('_frontend.log') else 'backend server'
        errors += [f'[{source}] {line}' for line in _new_log_errors(path, offset)]
    try:
        errors += [f'[browser console] {e}' for e in _console_errors_since(context, mark.started_ms)]
    except Exception as e:  # pragma: no cover - diagnostics are best effort
        logger.debug("Could not read preview console errors: %s", e)
    return errors[:MAX_REPORTED_ERRORS]


def _console_errors_since(context, since_ms: int) -> List[str]:
    from apps.Imagi.ProjectManager.models import Project
    from .browser_preview_service import BrowserPreviewService

    project = Project.objects.get(id=context.project_id)
    service = BrowserPreviewService(project)
    state = service._load_state()
    if not state or not service._browser_alive(state):
        return []

    def body(conn, _page):
        return service._collect_console_errors(conn)

    errors = service._with_page(state, body)
    return [e['text'] for e in errors if int(e.get('ts') or 0) >= since_ms]


# --- Discarding a thread --------------------------------------------------------

def revert(conversation, project_path: str, worktree_path: str) -> List[str]:
    """Take a discarded thread's live edits back out of the project.

    For each file the thread changed, the project's copy is put back as it was
    when the thread forked, but only where the project still holds the
    thread's version; anything changed since by someone else is left alone.
    Returns the paths restored.
    """
    from .version_control_service import canonical_repo_lock, task_base_ref

    if not (project_path and worktree_path and os.path.isdir(worktree_path)):
        return []

    def git(*args, cwd=project_path):
        return subprocess.run(['git', *args], cwd=cwd, capture_output=True)

    base = git('rev-parse', '--verify', '--quiet', task_base_ref(conversation.id))
    if base.returncode != 0:
        return []
    fork = base.stdout.decode().strip()
    changed = git('diff', '--name-only', fork, cwd=worktree_path)
    if changed.returncode != 0:
        return []
    untracked = git('ls-files', '--others', '--exclude-standard', cwd=worktree_path)
    paths = set(changed.stdout.decode().split('\n')) | set(untracked.stdout.decode().split('\n'))
    restored = []
    with canonical_repo_lock(project_path):
        for rel in sorted(p for p in paths if p):
            target = os.path.join(project_path, rel)
            if _read(target) != _read(os.path.join(worktree_path, rel)):
                continue  # not the thread's version (anymore)
            original = git('show', f'{fork}:{rel}')
            try:
                if original.returncode == 0:
                    with open(target, 'wb') as f:
                        f.write(original.stdout)
                elif os.path.exists(target):
                    os.remove(target)
            except OSError as e:
                logger.warning("Could not take %s back out of the project: %s", rel, e)
                continue
            restored.append(rel)
    return restored
