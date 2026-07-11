"""
Function tools for the Imagi coding agent.

The tool surface follows the design of modern coding-agent harnesses
(Claude Code, OpenAI Codex CLI):

- Discovery:  get_project_tree, list_project_files, glob_files, grep_files
- Reading:    read_file (line-numbered, supports offset/limit)
- Editing:    edit_file (targeted string replacement), write_file-style
              update_file/create_file, delete_file, directory tools
- Planning:   update_plan (Codex-style step list surfaced to the UI)

Each tool is a thin wrapper around a plain implementation function so the
behavior can be unit-tested without the Agents SDK runtime.
"""

import fnmatch
import json
import logging
import os
import re
from typing import List, Optional
from typing_extensions import TypedDict

from agents import RunContextWrapper, function_tool

from apps.Imagi.Build.ProjectManager.models import Project
from apps.Imagi.Build.Builder.services.view_file_service import ViewFileService
from apps.Imagi.Build.Builder.services.create_file_service import CreateFileService
from apps.Imagi.Build.Builder.services.delete_file_service import DeleteFileService
from apps.Imagi.Build.Builder.services.directory_service import DirectoryService

logger = logging.getLogger(__name__)

# Directories that are never searched, read, or listed
SKIP_DIRS = {
    'node_modules', '__pycache__', '.git', 'dist', 'build',
    'staticfiles', 'media', '.venv', 'venv',
}

# Limits that keep tool output within a sane context budget
READ_DEFAULT_LIMIT = 2000        # lines returned by read_file by default
READ_MAX_LINE_CHARS = 500        # long lines are truncated
GREP_MAX_RESULTS = 50
GLOB_MAX_RESULTS = 200
GREP_MAX_FILE_BYTES = 1_000_000  # skip files larger than ~1MB when searching

# File extension to type mapping (for CreateFileService)
_EXT_TYPE_MAP = {
    '.vue': 'vue', '.ts': 'typescript', '.tsx': 'typescript',
    '.js': 'javascript', '.jsx': 'javascript', '.css': 'css',
    '.html': 'html', '.py': 'python', '.json': 'json',
    '.md': 'markdown', '.txt': 'text',
}

# Patterns indicating a frontend file path
_FRONTEND_PATH_PREFIXES = (
    'src/', 'public/', 'package.json', 'vite.config', 'tsconfig',
    'tailwind.config', 'postcss.config', 'index.html', 'env.d.ts',
)
_FRONTEND_EXTENSIONS = {'.vue', '.ts', '.tsx', '.jsx'}

# Patterns indicating a backend file path
_BACKEND_PATH_PREFIXES = (
    'templates/', 'static/', 'apps/', 'api/', 'manage.py', 'Pipfile',
)


class PlanStep(TypedDict):
    """One step of the agent's working plan (Codex update_plan style)."""
    step: str
    status: str  # 'pending' | 'in_progress' | 'completed'


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _is_dual_stack(project) -> bool:
    """Check if project has both frontend/vuejs and backend/django directories."""
    pp = project.project_path
    return (
        os.path.isdir(os.path.join(pp, 'frontend', 'vuejs'))
        and os.path.isdir(os.path.join(pp, 'backend', 'django'))
    )


def normalize_file_path(project, file_path: str) -> str:
    """Normalize a file path for dual-stack projects.

    The LLM may omit the 'frontend/vuejs/' or 'backend/django/' prefix.
    This function detects that and adds the correct prefix so files are
    written to the location that the project scanners actually see.
    """
    file_path = file_path.strip().lstrip('/')

    if not _is_dual_stack(project):
        return file_path

    # Already has the correct prefix — leave it alone
    if file_path.startswith('frontend/') or file_path.startswith('backend/'):
        return file_path

    ext = os.path.splitext(file_path)[1].lower()
    if any(file_path.startswith(p) for p in _FRONTEND_PATH_PREFIXES) or ext in _FRONTEND_EXTENSIONS:
        normalized = f'frontend/vuejs/{file_path}'
        logger.info(f"Path normalized (frontend): '{file_path}' -> '{normalized}'")
        return normalized

    if any(file_path.startswith(p) for p in _BACKEND_PATH_PREFIXES) or ext == '.py':
        normalized = f'backend/django/{file_path}'
        logger.info(f"Path normalized (backend): '{file_path}' -> '{normalized}'")
        return normalized

    return file_path


def resolve_safe_path(project, file_path: str) -> str:
    """Resolve a project-relative path to an absolute path inside the project.

    Raises ValueError when the path escapes the project root (e.g. via '..'
    segments or absolute paths), so tools can never read or write outside the
    user's project directory.
    """
    root = os.path.realpath(project.project_path)
    full = os.path.realpath(os.path.join(root, file_path))
    if full != root and not full.startswith(root + os.sep):
        raise ValueError(f"Path '{file_path}' is outside the project directory")
    return full


def infer_file_type(file_path: str) -> str:
    """Infer file type from extension for CreateFileService."""
    ext = os.path.splitext(file_path)[1].lower()
    return _EXT_TYPE_MAP.get(ext, '')


def _error_result(message: str) -> str:
    """Build a JSON error result that instructs the LLM to report failure."""
    return json.dumps({
        "success": False,
        "error": message,
        "instruction": "Tell the user this operation FAILED. Do NOT say the file was created or updated.",
    })


def _get_project(ctx):
    """Resolve the Project model from agent context."""
    try:
        return Project.objects.get(id=ctx.project_id, user_id=ctx.user_id, is_active=True)
    except Project.DoesNotExist:
        raise ValueError(f"Project {ctx.project_id} not found for user {ctx.user_id}")


def _iter_project_files(project_path: str):
    """Yield (abs_path, rel_path) for every non-hidden file, pruning skip dirs."""
    for root, dirs, filenames in os.walk(project_path):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not d.startswith('.'))
        for filename in sorted(filenames):
            if filename.startswith('.'):
                continue
            abs_path = os.path.join(root, filename)
            yield abs_path, os.path.relpath(abs_path, project_path)


# ---------------------------------------------------------------------------
# Implementation functions (plain, unit-testable)
# ---------------------------------------------------------------------------

def read_file_impl(project, file_path: str, offset: int = 1, limit: int = READ_DEFAULT_LIMIT) -> str:
    """Read a file returning `cat -n` style line-numbered output.

    Supports reading a slice of large files via offset (1-based) and limit.
    """
    file_path = normalize_file_path(project, file_path)
    full_path = resolve_safe_path(project, file_path)

    if os.path.isdir(full_path):
        entries = sorted(os.listdir(full_path))
        dirs = [e for e in entries if os.path.isdir(os.path.join(full_path, e)) and not e.startswith('.')]
        files = [e for e in entries if os.path.isfile(os.path.join(full_path, e)) and not e.startswith('.')]
        return json.dumps({
            "error": f"'{file_path}' is a directory, not a file. Use get_project_tree to browse directories.",
            "directory_contents": {"dirs": dirs, "files": files},
        })

    if not os.path.isfile(full_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(full_path, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()

    total = len(lines)
    offset = max(1, offset)
    if offset > total and total > 0:
        raise ValueError(f"offset {offset} is past the end of the file ({total} lines)")
    limit = max(1, limit)
    window = lines[offset - 1:offset - 1 + limit]

    numbered = []
    for i, line in enumerate(window, start=offset):
        if len(line) > READ_MAX_LINE_CHARS:
            line = line[:READ_MAX_LINE_CHARS] + '… [line truncated]'
        numbered.append(f"{i}\t{line}")

    header = f"[file: {file_path} | lines {offset}-{offset + len(window) - 1} of {total}]"
    if offset - 1 + limit < total:
        header += " (more lines below — call read_file again with a higher offset)"
    return header + "\n" + "\n".join(numbered)


def edit_file_impl(
    project,
    file_path: str,
    old_string: str,
    new_string: str,
    replace_all: bool = False,
) -> dict:
    """Perform an exact string replacement in a file (Claude Code Edit tool).

    old_string must match the file content exactly and, unless replace_all is
    set, must be unique in the file.
    """
    if old_string == new_string:
        raise ValueError("new_string must be different from old_string")
    if not old_string:
        raise ValueError("old_string must not be empty (use create_file for new files)")

    file_path = normalize_file_path(project, file_path)
    full_path = resolve_safe_path(project, file_path)
    if not os.path.isfile(full_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()

    count = content.count(old_string)
    if count == 0:
        raise ValueError(
            "old_string not found in file. Read the file first and copy the exact "
            "text to replace, including whitespace and indentation."
        )
    if count > 1 and not replace_all:
        raise ValueError(
            f"old_string appears {count} times in the file. Provide a longer, unique "
            "snippet (include surrounding lines) or set replace_all=true."
        )

    if replace_all:
        new_content = content.replace(old_string, new_string)
        replacements = count
    else:
        new_content = content.replace(old_string, new_string, 1)
        replacements = 1

    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return {"success": True, "path": file_path, "replacements": replacements}


def grep_impl(
    project,
    pattern: str,
    path: str = '',
    include: Optional[str] = None,
    max_results: int = GREP_MAX_RESULTS,
) -> dict:
    """Search project file contents with a regular expression.

    Returns matches as {file, line, text} entries, capped at max_results.
    """
    regex = re.compile(pattern)
    search_root = resolve_safe_path(project, path) if path else os.path.realpath(project.project_path)
    if not os.path.isdir(search_root):
        raise ValueError(f"Search path '{path}' is not a directory in the project")

    project_root = os.path.realpath(project.project_path)
    matches = []
    files_scanned = 0
    truncated = False

    for abs_path, _ in _iter_project_files(search_root):
        rel_to_project = os.path.relpath(abs_path, project_root)
        if include and not fnmatch.fnmatch(os.path.basename(abs_path), include) \
                and not fnmatch.fnmatch(rel_to_project, include):
            continue
        try:
            if os.path.getsize(abs_path) > GREP_MAX_FILE_BYTES:
                continue
            with open(abs_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except (OSError, UnicodeDecodeError):
            continue

        files_scanned += 1
        for lineno, line in enumerate(text.splitlines(), start=1):
            if regex.search(line):
                snippet = line.strip()
                if len(snippet) > READ_MAX_LINE_CHARS:
                    snippet = snippet[:READ_MAX_LINE_CHARS] + '…'
                matches.append({"file": rel_to_project, "line": lineno, "text": snippet})
                if len(matches) >= max_results:
                    truncated = True
                    break
        if truncated:
            break

    return {
        "matches": matches,
        "match_count": len(matches),
        "files_scanned": files_scanned,
        "truncated": truncated,
    }


def glob_impl(project, pattern: str, max_results: int = GLOB_MAX_RESULTS) -> dict:
    """Find project files whose relative path matches a glob pattern.

    Supports '**' for recursive matching (e.g. 'frontend/**/*.vue', '*.py').
    """
    project_root = os.path.realpath(project.project_path)
    # fnmatch has no native '**'; translate it to match any path segment run.
    regex = _glob_to_regex(pattern)

    results = []
    truncated = False
    for abs_path, rel_path in _iter_project_files(project_root):
        rel_posix = rel_path.replace(os.sep, '/')
        if regex.match(rel_posix) or fnmatch.fnmatch(os.path.basename(abs_path), pattern):
            results.append(rel_posix)
            if len(results) >= max_results:
                truncated = True
                break

    return {"files": results, "count": len(results), "truncated": truncated}


def _glob_to_regex(pattern: str) -> re.Pattern:
    """Translate a glob pattern with '**' support into a compiled regex."""
    out = []
    i = 0
    while i < len(pattern):
        c = pattern[i]
        if c == '*':
            if pattern[i:i + 2] == '**':
                out.append('.*')
                i += 2
                if i < len(pattern) and pattern[i] == '/':
                    i += 1
                continue
            out.append('[^/]*')
        elif c == '?':
            out.append('[^/]')
        else:
            out.append(re.escape(c))
        i += 1
    return re.compile('^' + ''.join(out) + '$')


def set_plan(context, steps: List[PlanStep]) -> dict:
    """Validate and store the agent's plan on the run context."""
    valid_statuses = {'pending', 'in_progress', 'completed'}
    plan = []
    for step in steps:
        text = (step.get('step') or '').strip()
        status = (step.get('status') or 'pending').strip()
        if not text:
            continue
        if status not in valid_statuses:
            status = 'pending'
        plan.append({'step': text, 'status': status})
    context.plan = plan
    return {"success": True, "steps": len(plan)}


# ---------------------------------------------------------------------------
# Function tools (Agents SDK surface)
# ---------------------------------------------------------------------------

@function_tool
def get_project_tree(ctx: RunContextWrapper) -> str:
    """Get the directory tree of the user's project. Shows all directories and files organised hierarchically.

    Call this first when you need an overview of where views, routers, components, and other files live.
    """
    try:
        project = _get_project(ctx.context)
        service = ViewFileService(project=project)
        tree = service.get_directory_tree()
        return json.dumps(tree, indent=2)
    except Exception as e:
        logger.error(f"Error getting project tree: {e}")
        return _error_result(str(e))


@function_tool
def list_project_files(ctx: RunContextWrapper) -> str:
    """List all files in the user's project (both frontend and backend). Returns file paths and types."""
    try:
        project = _get_project(ctx.context)
        service = ViewFileService(project=project)
        files = service.list_all_project_files()
        file_list = [{"path": f["path"], "type": f.get("type", "unknown")} for f in files]
        return json.dumps(file_list, indent=2)
    except Exception as e:
        logger.error(f"Error listing project files: {e}")
        return _error_result(str(e))


@function_tool
def glob_files(ctx: RunContextWrapper, pattern: str) -> str:
    """Find files whose path matches a glob pattern. Faster and cheaper than listing every file.

    Args:
        pattern: Glob pattern matched against project-relative paths. Supports '**'
            for recursive matching (e.g. 'frontend/**/*.vue', '**/router/index.ts', '*.py').
    """
    try:
        project = _get_project(ctx.context)
        return json.dumps(glob_impl(project, pattern))
    except Exception as e:
        logger.error(f"Error globbing files with pattern {pattern}: {e}")
        return _error_result(str(e))


@function_tool
def grep_files(ctx: RunContextWrapper, pattern: str, path: str = "", include: str = "") -> str:
    """Search file contents across the project with a regular expression. Returns matching lines with file paths and line numbers.

    Use this to find where something is defined or referenced before reading whole files.

    Args:
        pattern: Regular expression to search for (e.g. 'createRouter', 'class\\s+\\w+View').
        path: Optional project-relative directory to limit the search (e.g. 'frontend/vuejs/src').
        include: Optional glob to filter which files are searched (e.g. '*.vue', '*.py').
    """
    try:
        project = _get_project(ctx.context)
        result = grep_impl(project, pattern, path=path, include=include or None)
        return json.dumps(result)
    except re.error as e:
        return _error_result(f"Invalid regular expression: {e}")
    except Exception as e:
        logger.error(f"Error searching files for pattern {pattern}: {e}")
        return _error_result(str(e))


@function_tool
def read_file(ctx: RunContextWrapper, file_path: str, offset: int = 1, limit: int = READ_DEFAULT_LIMIT) -> str:
    """Read a file from the user's project. Output is line-numbered like `cat -n` ("N<TAB>content" per line).

    Always read a file before editing it. For large files, read a slice with offset/limit.
    When copying text for edit_file, strip the leading line numbers and tab.

    Args:
        file_path: The relative path to the file within the project (e.g. 'frontend/vuejs/src/App.vue').
        offset: 1-based line number to start reading from (default 1).
        limit: Maximum number of lines to return (default 2000).
    """
    try:
        project = _get_project(ctx.context)
        return read_file_impl(project, file_path, offset=offset, limit=limit)
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return _error_result(str(e))


@function_tool
def edit_file(
    ctx: RunContextWrapper,
    file_path: str,
    old_string: str,
    new_string: str,
    replace_all: bool = False,
) -> str:
    """Make a targeted edit to an existing file by exact string replacement. PREFER this over update_file for small changes — it is safer and cannot clobber unrelated code.

    old_string must match the current file content exactly (including whitespace and
    indentation) and must be unique in the file unless replace_all is set. Read the
    file first and copy the exact text (without the line-number prefixes).

    Args:
        file_path: The relative path to the file within the project.
        old_string: The exact existing text to replace.
        new_string: The replacement text.
        replace_all: Replace every occurrence instead of requiring old_string to be unique.
    """
    try:
        project = _get_project(ctx.context)
        result = edit_file_impl(project, file_path, old_string, new_string, replace_all)
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error editing file {file_path}: {e}")
        return _error_result(str(e))


@function_tool
def update_file(ctx: RunContextWrapper, file_path: str, content: str) -> str:
    """Overwrite an existing file with entirely new content. Use edit_file for small changes; use this only for full rewrites.

    Args:
        file_path: The relative path to the file within the project.
        content: The complete new content for the file.
    """
    try:
        project = _get_project(ctx.context)
        file_path = normalize_file_path(project, file_path)
        full_path = resolve_safe_path(project, file_path)
        service = ViewFileService(project=project)
        result = service.update_file(file_path, content)

        if not os.path.isfile(full_path):
            return _error_result(f"update_file appeared to succeed but file not found at {file_path}")

        return json.dumps({"success": True, "path": file_path, "message": result.get("message", "File updated successfully")})
    except Exception as e:
        logger.error(f"Error updating file {file_path}: {e}")
        return _error_result(str(e))


@function_tool
def create_file(ctx: RunContextWrapper, file_path: str, content: str) -> str:
    """Create a new file in the user's project.

    Args:
        file_path: The relative path for the new file within the project (e.g. 'frontend/vuejs/src/components/MyComponent.vue').
        content: The content for the new file.
    """
    try:
        project = _get_project(ctx.context)
        file_path = normalize_file_path(project, file_path)
        resolve_safe_path(project, file_path)
        file_type = infer_file_type(file_path)
        service = CreateFileService(project=project)
        result = service.create_file({"name": file_path, "content": content, "type": file_type})

        full_path = os.path.join(project.project_path, file_path)
        if not os.path.isfile(full_path):
            return _error_result(f"create_file appeared to succeed but file not found at {file_path}")

        actual_path = result.get("path", file_path)
        return json.dumps({"success": True, "path": actual_path, "message": f"File created at {actual_path}"})
    except Exception as e:
        logger.error(f"Error creating file {file_path}: {e}")
        return _error_result(str(e))


@function_tool
def delete_file(ctx: RunContextWrapper, file_path: str) -> str:
    """Delete a file from the user's project.

    Args:
        file_path: The relative path to the file within the project (e.g. 'frontend/vuejs/src/components/OldComponent.vue').
    """
    try:
        project = _get_project(ctx.context)
        file_path = normalize_file_path(project, file_path)
        full_path = resolve_safe_path(project, file_path)
        service = DeleteFileService(project=project)
        service.delete_file(file_path)

        if os.path.isfile(full_path):
            return _error_result(f"delete_file appeared to succeed but file still exists at {file_path}")

        return json.dumps({"success": True, "path": file_path, "message": "File deleted successfully"})
    except Exception as e:
        logger.error(f"Error deleting file {file_path}: {e}")
        return _error_result(str(e))


@function_tool
def create_directory(ctx: RunContextWrapper, dir_path: str) -> str:
    """Create a new directory in the user's project.

    Args:
        dir_path: The relative path for the new directory within the project (e.g. 'frontend/vuejs/src/components/NewFeature').
    """
    try:
        project = _get_project(ctx.context)
        dir_path = normalize_file_path(project, dir_path)
        resolve_safe_path(project, dir_path)
        service = DirectoryService(project=project)
        result = service.create_directory(dir_path)
        return json.dumps({"success": True, "path": dir_path, "message": result.get("message", "Directory created successfully")})
    except Exception as e:
        logger.error(f"Error creating directory {dir_path}: {e}")
        return _error_result(str(e))


@function_tool
def delete_directory(ctx: RunContextWrapper, dir_path: str) -> str:
    """Delete a directory from the user's project. This will recursively delete the directory and all its contents.

    Args:
        dir_path: The relative path to the directory within the project (e.g. 'frontend/vuejs/src/components/OldFeature').
    """
    try:
        project = _get_project(ctx.context)
        dir_path = normalize_file_path(project, dir_path)
        resolve_safe_path(project, dir_path)
        service = DirectoryService(project=project)
        result = service.delete_directory(dir_path, recursive=True)
        return json.dumps({"success": True, "path": dir_path, "message": result.get("message", "Directory deleted successfully")})
    except Exception as e:
        logger.error(f"Error deleting directory {dir_path}: {e}")
        return _error_result(str(e))


@function_tool
def update_plan(ctx: RunContextWrapper, steps: List[PlanStep]) -> str:
    """Create or update your working plan for a multi-step task. The plan is shown live to the user, so keep it current.

    Call this when a task needs 3 or more distinct steps: once up front with all steps
    ('pending'), then again whenever a step starts ('in_progress') or finishes
    ('completed'). Exactly one step should be 'in_progress' at a time. Skip planning
    for trivial single-step requests.

    Args:
        steps: The full plan as a list of {step, status} objects, where status is
            'pending', 'in_progress', or 'completed'.
    """
    try:
        result = set_plan(ctx.context, steps)
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error updating plan: {e}")
        return _error_result(str(e))


# All tools exposed to the coding agent, in the order they appear in its prompt.
CODING_AGENT_TOOLS = [
    update_plan,
    get_project_tree,
    list_project_files,
    glob_files,
    grep_files,
    read_file,
    edit_file,
    update_file,
    create_file,
    delete_file,
    create_directory,
    delete_directory,
]
