"""
Static integrity check for a generated project's Vue frontend.

Vite resolves imports when a module is first requested, so a single import
pointing at a file that was never written takes the whole preview down with
an "Failed to resolve import ..." internal server error — the page the user
was about to see is simply blank. An agent run that is cut short (turn or
cost cap) leaves exactly that state: a view or route referencing a component
it did not get around to creating.

This module finds those dangling references without booting anything, so a
run's output can be checked before it reaches the tree the preview serves.
The scan is deliberately conservative — it only follows import specifiers
that name a file inside the project (``@/...`` alias or a relative path) and
resolves them the way Vite's resolver does, so a clean project always scans
clean.
"""

import logging
import os
import re

logger = logging.getLogger(__name__)

FRONTEND_SRC = os.path.join('frontend', 'vuejs', 'src')

# Files whose import graph Vite serves.
SCANNED_EXTENSIONS = ('.vue', '.ts', '.tsx', '.js', '.jsx', '.mjs')

# Extensions Vite's resolver appends when an import omits one. Order does not
# matter here — we only care whether *some* file answers the specifier.
RESOLVED_EXTENSIONS = (
    '.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs', '.vue', '.json',
    '.css', '.scss', '.sass', '.svg', '.png', '.jpg', '.jpeg', '.webp', '.gif',
)

# Directories that never hold project source.
SKIPPED_DIRS = {'node_modules', 'dist', '.vite-cache', '.git', '__pycache__'}

# `import x from '...'`, `export { x } from '...'`, bare `import '...'`, and
# dynamic `import('...')`. Anchored on a word boundary before the keyword so a
# CSS `@import` (or an identifier ending in "import") is not mistaken for one.
_IMPORT_RE = re.compile(
    r"(?:^|[\s;{}()])(?:import|export)\s+(?:[\w*{}$,\s]+\s+from\s+)?"
    r"['\"](?P<static>[^'\"]+)['\"]"
    r"|(?:^|[^\w.$])import\s*\(\s*['\"](?P<dynamic>[^'\"]+)['\"]\s*\)",
    re.MULTILINE,
)

# Specifiers that name a file in this project (everything else is an npm
# package, which the shared dependency store owns).
_LOCAL_PREFIXES = ('@/', './', '../')

# A specifier built at runtime is not statically resolvable, and neither is a
# glob — never report those.
_DYNAMIC_MARKERS = ('*', '?', '${')

# Bound on what a single report hands back to the agent, so a badly broken
# tree can't blow up a prompt.
MAX_REPORTED_PROBLEMS = 25


def _iter_source_files(src_root):
    """Yield every frontend source file Vite would serve, as absolute paths."""
    for dirpath, dirnames, filenames in os.walk(src_root):
        dirnames[:] = [d for d in dirnames if d not in SKIPPED_DIRS]
        for filename in filenames:
            if filename.endswith(SCANNED_EXTENSIONS):
                yield os.path.join(dirpath, filename)


def _resolves(spec, source_file, src_root):
    """Whether an import specifier names a file that exists, as Vite resolves it."""
    if spec.startswith('@/'):
        target = os.path.join(src_root, spec[2:])
    else:
        target = os.path.normpath(os.path.join(os.path.dirname(source_file), spec))

    if os.path.isfile(target):
        return True
    for ext in RESOLVED_EXTENSIONS:
        if os.path.isfile(target + ext):
            return True
    # A directory import resolves to its index file.
    for ext in RESOLVED_EXTENSIONS:
        if os.path.isfile(os.path.join(target, 'index' + ext)):
            return True
    return False


def find_unresolved_imports(root):
    """Find imports in a project's frontend that point at files that don't exist.

    Args:
        root: The project tree to scan (a project_path or a task worktree).

    Returns:
        list[dict]: ``{'file': <project-relative path>, 'import': <specifier>}``
        in a stable order, empty when the frontend's import graph is whole.
        An unreadable or absent frontend yields [] — this check exists to catch
        broken references, not to police project layout.
    """
    src_root = os.path.join(root or '', FRONTEND_SRC)
    if not os.path.isdir(src_root):
        return []

    problems = []
    for source_file in sorted(_iter_source_files(src_root)):
        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                source = f.read()
        except (OSError, UnicodeDecodeError) as e:
            logger.warning(f"Could not read {source_file} for import check: {e}")
            continue

        seen = set()
        for match in _IMPORT_RE.finditer(source):
            spec = match.group('static') or match.group('dynamic')
            if not spec or spec in seen:
                continue
            seen.add(spec)
            if not spec.startswith(_LOCAL_PREFIXES):
                continue
            if any(marker in spec for marker in _DYNAMIC_MARKERS):
                continue
            if _resolves(spec, source_file, src_root):
                continue
            problems.append({
                'file': os.path.relpath(source_file, root).replace(os.sep, '/'),
                'import': spec,
            })
    return problems


def describe_unresolved_imports(problems):
    """Render unresolved imports as a bulleted list for an agent prompt."""
    shown = problems[:MAX_REPORTED_PROBLEMS]
    lines = [f"- {p['file']} imports '{p['import']}', which does not exist" for p in shown]
    if len(problems) > len(shown):
        lines.append(f"- ... and {len(problems) - len(shown)} more")
    return "\n".join(lines)
