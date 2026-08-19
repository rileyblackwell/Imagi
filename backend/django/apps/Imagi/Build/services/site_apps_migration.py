"""
Fold a project's one-page site apps back into its ``home`` app.

Imagi's scaffold used to give each page of the marketing front — about,
contact — its own top-level app, so the workspace's folder menu read as
three one-page folders and the nameplate as "about/about". The scaffold now
puts them where they belong (``apps/home/views/{Home,About,Contact}View.vue``
behind one router), but every project created before that still carries the
old shape on disk.

This migrates those projects in place, once, the next time their workspace
opens: each stray site app's view files move into ``apps/home/views/``, its
routes are merged into the home router with their paths and metadata intact,
and the emptied app directory goes away. The root router discovers app
routers by glob, so the routes keep serving across the move.

It is deliberately timid. An app is only migrated when it still has the
shape the old scaffold gave it — views and a router that imports only those
views, no components of its own, and nothing that would collide with what
home already has. Anything an agent has grown beyond that is left alone,
because a project that still navigates matters more than a tidy menu.
"""

import logging
import os
import re
import shutil

from .project_files_service import ensure_workspace_tier, record_file, remove_directory

logger = logging.getLogger(__name__)

APPS_SUBDIR = os.path.join('frontend', 'vuejs', 'src', 'apps')
HOME_APP = 'home'

# App directories that hold what is really a page of the home site. Named
# rather than guessed: 'store' and 'pricing' are the Sell workspace's
# prebuilt checkout apps and 'auth' is the sign-in app, none of which belong
# to the marketing front even though they are equally small.
SITE_APP_NAMES = frozenset({
    'about', 'aboutus', 'about-us', 'about_us',
    'contact', 'contactus', 'contact-us', 'contact_us',
    'faq', 'faqs', 'terms', 'privacy',
})

_VIEW_IMPORT_RE = re.compile(
    r"^\s*import\s+(?P<name>\w+)\s+from\s+(?P<q>['\"])\.\./views/(?P<file>[\w.-]+\.vue)(?P=q)\s*;?\s*$"
)
_TYPE_IMPORT_RE = re.compile(r"^\s*import\s+type\s+")
_IMPORT_LINE_RE = re.compile(r"^\s*import\s+")
_ROUTES_ARRAY_RE = re.compile(r"const\s+routes\s*(?::[^=]+)?=\s*\[")
_ROUTE_PATH_RE = re.compile(r"path:\s*(['\"])(?P<path>[^'\"]*)\1")


def regroup_site_apps(project) -> list:
    """Merge legacy one-page site apps into ``home``. Returns the apps moved."""
    # Checked before anything moves: on the web tier of a split deployment the
    # working copy is ephemeral, so a merge there would rearrange files that
    # are about to vanish and leave the volume's real copy untouched.
    ensure_workspace_tier('regroup a project\'s site apps')
    apps_root = os.path.join(project.project_path or '', APPS_SUBDIR)
    home_dir = os.path.join(apps_root, HOME_APP)
    if not os.path.isdir(apps_root) or not os.path.isdir(home_dir):
        return []

    merged = []
    for app_name in sorted(os.listdir(apps_root)):
        if app_name not in SITE_APP_NAMES:
            continue
        app_dir = os.path.join(apps_root, app_name)
        if not os.path.isdir(app_dir):
            continue
        try:
            if _merge_app_into_home(project, apps_root, app_name):
                merged.append(app_name)
        except Exception as e:
            # A half-merged app is the one outcome worse than an untidy menu,
            # so failures are logged and the app is left exactly as it was.
            logger.warning(
                f"Could not fold '{app_name}' into home for project {project.id}: {e}"
            )
    if merged:
        logger.info(
            f"Project {project.id}: folded {', '.join(merged)} into the home app"
        )
    return merged


def _merge_app_into_home(project, apps_root, app_name) -> bool:
    app_dir = os.path.join(apps_root, app_name)
    home_dir = os.path.join(apps_root, HOME_APP)
    app_views = os.path.join(app_dir, 'views')
    home_views = os.path.join(home_dir, 'views')
    app_router = os.path.join(app_dir, 'router', 'index.ts')
    home_router = os.path.join(home_dir, 'router', 'index.ts')

    if not (os.path.isdir(app_views) and os.path.isdir(home_views)):
        return False
    if not (os.path.isfile(app_router) and os.path.isfile(home_router)):
        return False

    # Every .vue file the app owns must be a view. Components of its own would
    # have to move too, and their names collide across apps by design.
    view_files = sorted(f for f in os.listdir(app_views) if f.endswith('.vue'))
    if not view_files:
        return False
    for root, dirs, filenames in os.walk(app_dir):
        dirs[:] = [d for d in dirs if d != 'views']
        if any(f.endswith('.vue') for f in filenames):
            return False

    # Nothing may already exist under the name it would take in home.
    if any(os.path.exists(os.path.join(home_views, f)) for f in view_files):
        return False

    # A view reaching out of views/ — into its app's stores, its components,
    # itself by alias — would be reaching into a directory that is about to
    # stop existing. Leave those where their imports still resolve.
    outward = re.compile(rf"""['"](?:\.\./|@/apps/{re.escape(app_name)}/)""")
    for filename in view_files:
        with open(os.path.join(app_views, filename), 'r', encoding='utf-8') as f:
            if outward.search(f.read()):
                return False

    with open(app_router, 'r', encoding='utf-8') as f:
        app_router_src = f.read()
    with open(home_router, 'r', encoding='utf-8') as f:
        home_router_src = f.read()

    imports, entries = _parse_router(app_router_src)
    if not imports or not entries.strip():
        return False
    # Only the views being moved may be imported; anything else would dangle.
    if {file for _, file in imports} - set(view_files):
        return False
    if any(re.search(rf"\b{re.escape(name)}\b", home_router_src) for name, _ in imports):
        return False
    home_paths = {m.group('path') for m in _ROUTE_PATH_RE.finditer(home_router_src)}
    if home_paths & {m.group('path') for m in _ROUTE_PATH_RE.finditer(entries)}:
        return False

    merged_router = _merge_router(home_router_src, imports, entries)

    # Disk first, then the database mirror — the same order every other file
    # service uses, so a crash leaves the mirror stale rather than ahead.
    for filename in view_files:
        shutil.move(os.path.join(app_views, filename), os.path.join(home_views, filename))
    _write(home_router, merged_router)
    barrel = os.path.join(home_views, 'index.ts')
    barrel_updated = _update_barrel(barrel, view_files)
    shutil.rmtree(app_dir)

    rel_home = _rel(APPS_SUBDIR, HOME_APP)
    for filename in view_files:
        record_file(project, f'{rel_home}/views/{filename}')
    record_file(project, f'{rel_home}/router/index.ts')
    if barrel_updated:
        record_file(project, f'{rel_home}/views/index.ts')
    remove_directory(project, _rel(APPS_SUBDIR, app_name))
    return True


def _parse_router(source):
    """Return ([(identifier, view filename)], route-entry text) from a router."""
    imports = []
    for line in source.splitlines():
        match = _VIEW_IMPORT_RE.match(line)
        if match:
            imports.append((match.group('name'), match.group('file')))
        elif _IMPORT_LINE_RE.match(line) and not _TYPE_IMPORT_RE.match(line):
            # An import of anything but the views (a store, a layout, a
            # component) would not resolve from home. Leave the app alone.
            return [], ''
    return imports, _routes_body(source)


def _routes_body(source) -> str:
    """The text between the brackets of the router's `routes` array."""
    match = _ROUTES_ARRAY_RE.search(source)
    if not match:
        return ''
    start = match.end()
    depth = 1
    for i in range(start, len(source)):
        char = source[i]
        if char in '[{':
            depth += 1
        elif char in ']}':
            depth -= 1
            if depth == 0:
                return source[start:i]
    return ''


def _merge_router(home_source, imports, entries) -> str:
    """Add the moved views' imports and routes to the home router's source."""
    lines = home_source.splitlines()
    last_import = max(
        (i for i, line in enumerate(lines) if _IMPORT_LINE_RE.match(line)), default=-1
    )
    new_imports = [f"import {name} from '../views/{file}'" for name, file in imports]
    lines[last_import + 1:last_import + 1] = new_imports
    source = '\n'.join(lines) + ('\n' if home_source.endswith('\n') else '')

    body = _routes_body(source)
    start = source.index(body)
    existing = body.rstrip()
    if existing and not existing.endswith(','):
        existing += ','
    merged = existing + '\n' + entries.strip('\n').rstrip() + '\n'
    return source[:start] + merged + source[start + len(body):]


def _update_barrel(barrel_path, view_files) -> bool:
    """Re-export the moved views from home's views barrel, if it has one."""
    if not os.path.isfile(barrel_path):
        return False
    with open(barrel_path, 'r', encoding='utf-8') as f:
        source = f.read()
    additions = [
        f"export {{ default as {os.path.splitext(f)[0]} }} from './{f}'"
        for f in view_files
        if f"from './{f}'" not in source
    ]
    if not additions:
        return False
    _write(barrel_path, source.rstrip('\n') + '\n' + '\n'.join(additions) + '\n')
    return True


def _write(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def _rel(*parts) -> str:
    return os.path.join(*parts).replace(os.sep, '/')
