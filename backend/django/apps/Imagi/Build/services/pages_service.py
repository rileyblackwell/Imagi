"""
Derive the navigable pages of a generated project from its Vue routers.

The workspace preview shows an app/page menu. It used to guess route paths
from view-component filenames, which breaks as soon as a router maps a view
somewhere unconventional. This service reads each app's actual
``router/index.ts`` from the project's working copy instead, so the menu
always reflects the routes the running app really serves.

The router files are TypeScript, but the generated (and agent-edited) ones
are formulaic enough that a small brace-depth scanner recovers the route
tree without a real parser: ``path:`` entries nested more deeply than a
previous entry are children and get joined onto their parent's path, exactly
as vue-router does.
"""

import logging
import os
import re

logger = logging.getLogger(__name__)

APPS_SUBDIR = os.path.join('frontend', 'vuejs', 'src', 'apps')

_TOKEN_RE = re.compile(
    r"(?P<open>\{)"
    r"|(?P<close>\})"
    r"|path:\s*(?P<pq>['\"])(?P<path>[^'\"]*)(?P=pq)"
    r"|component:\s*(?P<component>[^,\n}]+)"
)
_IMPORT_RE = re.compile(r"import\s+(\w+)\s+from\s+['\"]([^'\"]+)['\"]")


def list_app_pages(project):
    """Return [{name, title, pages: [{title, path}]}] for every app with routes."""
    apps_root = os.path.join(project.project_path or '', APPS_SUBDIR)
    if not os.path.isdir(apps_root):
        return []

    apps = []
    for app_name in sorted(os.listdir(apps_root)):
        router_file = os.path.join(apps_root, app_name, 'router', 'index.ts')
        if not os.path.isfile(router_file):
            continue
        try:
            with open(router_file, 'r', encoding='utf-8') as f:
                source = f.read()
            pages = _parse_router(source)
        except Exception as e:
            logger.warning(f"Could not parse router for app '{app_name}': {e}")
            continue
        if pages:
            apps.append({
                'name': app_name,
                'title': _humanize(app_name),
                'pages': pages,
            })
    return apps


def _parse_router(source):
    """Extract concrete leaf routes (path + display title) from router source."""
    imports = dict(_IMPORT_RE.findall(source))

    depth = 0
    stack = []   # [(depth, full_path)] of enclosing route entries
    entries = []  # [{'path': ..., 'component': None|str}] in document order

    for token in _TOKEN_RE.finditer(source):
        if token.group('open'):
            depth += 1
        elif token.group('close'):
            depth -= 1
        elif token.group('path') is not None:
            while stack and stack[-1][0] >= depth:
                stack.pop()
            parent = stack[-1][1] if stack else ''
            full = _join_paths(parent, token.group('path'))
            stack.append((depth, full))
            entries.append({'path': full, 'component': None})
        elif token.group('component') and entries and entries[-1]['component'] is None:
            entries[-1]['component'] = token.group('component').strip()

    pages = []
    seen = set()
    for entry in entries:
        path = entry['path']
        component = entry['component'] or ''
        # Only routes that render a view are navigable pages: this skips
        # layout-only parents (whose component lives outside views/) and
        # grouping entries with no component at all.
        source_ref = imports.get(component, component)
        if 'views/' not in source_ref.replace('\\', '/'):
            continue
        # Dynamic segments and catch-alls aren't directly addressable.
        if ':' in path or '*' in path:
            continue
        # Stripe return pages (from the Sell payment templates) only make
        # sense mid-checkout; don't offer them as navigable pages.
        if 'CheckoutReturn' in source_ref:
            continue
        if path in seen:
            continue
        seen.add(path)
        pages.append({'title': _page_title(path), 'path': path})
    return pages


def _join_paths(parent, child):
    """Join a nested route path onto its parent the way vue-router does."""
    if child.startswith('/'):
        return child or '/'
    if not child:
        return parent or '/'
    return (parent.rstrip('/') or '') + '/' + child


def _page_title(path):
    segment = path.rstrip('/').rsplit('/', 1)[-1]
    if not segment:
        return 'Home'
    return _humanize(segment)


def _humanize(value):
    spaced = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', value)
    spaced = re.sub(r'[-_]+', ' ', spaced).strip()
    return ' '.join(word.capitalize() for word in spaced.split())
