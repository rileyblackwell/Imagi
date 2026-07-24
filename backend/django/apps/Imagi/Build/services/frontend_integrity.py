"""
Static integrity checks for a generated project's Vue frontend.

Two failure modes are caught here, both of which take an app down while
compiling perfectly well, so neither a type-check nor ``vite build`` finds
them:

1. Dangling references. Vite resolves imports when a module is first
   requested, so a single import pointing at a file that was never written
   takes the whole preview down with a "Failed to resolve import ..."
   internal server error — the page the user was about to see is simply
   blank. An agent run that is cut short leaves exactly that state: a view or
   route referencing a component it did not get around to creating. The same
   applies to a template ``src`` naming an image that does not exist.

2. A broken app-router contract. Each app owns a ``router/index.ts`` that
   exports a ``routes`` array, and the project's root router globs those up
   into one route table. An agent that rewrites an app's router module as a
   standalone ``createRouter(...)`` breaks that contract silently and
   catastrophically: vue-router accepts the resulting value without
   complaint and resolves to NO routes at all, so every URL — including the
   home page — falls through to the 404 page.

3. Auth pages nothing links to. Every project is created with working
   sign-in and register pages and a home page linking to both; a first build
   that rewrites that home page can drop the links, leaving pages that exist
   but cannot be reached. This one is advisory rather than blocking — a good
   page with no sign-in link still beats the untouched scaffold — so it feeds
   a repair run, and the caller decides what an unrepaired one is worth.

Every scan runs without booting anything, so a run's output can be checked
before it reaches the tree the preview serves. They are deliberately
conservative: a clean project always scans clean, because a false positive
discards a build that was actually fine.
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

# Static asset references in a template: src="..." and poster="...". Vite
# compiles these into imports, so one naming a file that does not exist is the
# same dangling reference as a bad import statement — it renders as a broken
# image and fails the production build. Only the static attribute form is
# matched: a ':src'/'v-bind:src' binding is an expression, not a path.
_TEMPLATE_ASSET_RE = re.compile(
    r"""(?<![:\w.-])(?:src|poster)\s*=\s*["'](?P<asset>[^"']+)["']"""
)

# Specifiers that name a file in this project (everything else is an npm
# package, which the shared dependency store owns).
_LOCAL_PREFIXES = ('@/', './', '../')

# A root-absolute reference ('/images/hero.jpg') is resolved by Vite against
# the frontend's public/ directory, then its root. Generated projects ship no
# public/ directory at all, so these are the most common way an agent invents
# an asset that was never created.
_PUBLIC_DIR = os.path.join('frontend', 'vuejs', 'public')
_FRONTEND_ROOT = os.path.join('frontend', 'vuejs')

# References that are not a path into this project: real URLs, protocol-
# relative URLs, inline data, and template placeholders.
_NON_PATH_PREFIXES = ('http://', 'https://', '//', 'data:', 'blob:', 'mailto:', '#')

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


def _candidate_targets(spec, source_file, src_root, root):
    """Absolute paths Vite would try for a specifier, in resolution order."""
    if spec.startswith('@/'):
        return [os.path.join(src_root, spec[2:])]
    if spec.startswith('/'):
        # Root-absolute: public/ first (Vite serves it at the root), then the
        # frontend root itself.
        relative = spec.lstrip('/')
        return [
            os.path.join(root, _PUBLIC_DIR, relative),
            os.path.join(root, _FRONTEND_ROOT, relative),
        ]
    return [os.path.normpath(os.path.join(os.path.dirname(source_file), spec))]


def _resolves(spec, source_file, src_root, root):
    """Whether a specifier names a file that exists, as Vite resolves it."""
    for target in _candidate_targets(spec, source_file, src_root, root):
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


def _is_project_path(spec):
    """Whether a specifier points at a file this project is meant to contain.

    Excludes npm packages (bare specifiers), real URLs, inline data, and
    anything assembled at runtime — none of which a static check can or should
    judge.
    """
    if not spec or spec.startswith(_NON_PATH_PREFIXES):
        return False
    if any(marker in spec for marker in _DYNAMIC_MARKERS):
        return False
    return spec.startswith(_LOCAL_PREFIXES) or spec.startswith('/')


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
        specs = [
            match.group('static') or match.group('dynamic')
            for match in _IMPORT_RE.finditer(source)
        ]
        specs += [
            match.group('asset') for match in _TEMPLATE_ASSET_RE.finditer(source)
        ]
        for spec in specs:
            if not spec or spec in seen:
                continue
            seen.add(spec)
            if not _is_project_path(spec):
                continue
            if _resolves(spec, source_file, src_root, root):
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


# An app's router module must hand its routes to the root router as an array.
# `export { routes }` is the scaffolded form; `export default [...]` also works,
# since the root router accepts an array from either export.
_ROUTES_EXPORT_RE = re.compile(
    r"export\s+(?:const|let|var)\s+routes\b"      # export const routes = [...]
    r"|export\s*\{[^}]*\broutes\b[^}]*\}"          # export { routes }
    r"|export\s+default\s*\[",                     # export default [ ... ]
    re.MULTILINE,
)

# The specific rewrite that breaks the contract: an app router that builds its
# own Router instead of exporting route records.
_CREATE_ROUTER_RE = re.compile(r"\bcreateRouter\s*\(")


def find_router_contract_problems(root):
    """Find app router modules that no longer hand routes to the root router.

    Args:
        root: The project tree to scan (a project_path or a task worktree).

    Returns:
        list[dict]: ``{'file': <project-relative path>, 'detail': <what broke>}``
        in a stable order, empty when every app router still exports routes.
        A project with no apps directory yields [] — this check reports a broken
        contract, it does not require one to exist.
    """
    apps_root = os.path.join(root or '', FRONTEND_SRC, 'apps')
    if not os.path.isdir(apps_root):
        return []

    problems = []
    for app_name in sorted(os.listdir(apps_root)):
        router_dir = os.path.join(apps_root, app_name, 'router')
        if not os.path.isdir(router_dir):
            continue
        for filename in sorted(os.listdir(router_dir)):
            if not filename.startswith('index.') or not filename.endswith(
                ('.ts', '.js')
            ):
                continue
            path = os.path.join(router_dir, filename)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    source = f.read()
            except (OSError, UnicodeDecodeError) as e:
                logger.warning(f"Could not read {path} for router check: {e}")
                continue

            relative = os.path.relpath(path, root).replace(os.sep, '/')
            if _CREATE_ROUTER_RE.search(source):
                problems.append({
                    'file': relative,
                    'detail': (
                        "calls createRouter(), but an app router must only "
                        "export a 'routes' array — the project's root router "
                        "(frontend/vuejs/src/router) is the one that creates "
                        "the router. As written, the app contributes no routes "
                        "at all and every page 404s"
                    ),
                })
            elif not _ROUTES_EXPORT_RE.search(source):
                problems.append({
                    'file': relative,
                    'detail': (
                        "does not export a 'routes' array, so the root router "
                        "picks up no routes from this app and its pages 404"
                    ),
                })
    return problems


def describe_router_contract_problems(problems):
    """Render broken router contracts as a bulleted list for an agent prompt."""
    shown = problems[:MAX_REPORTED_PROBLEMS]
    lines = [f"- {p['file']} {p['detail']}" for p in shown]
    if len(problems) > len(shown):
        lines.append(f"- ... and {len(problems) - len(shown)} more")
    return "\n".join(lines)


# The routes the prebuilt auth app serves. The scaffolded home page ships
# linking to both, so a home app that references neither has lost them.
AUTH_LINK_PATHS = ('/auth/signin', '/auth/register')

# The app whose pages are the way into the auth pages: '/' lives here.
LANDING_APP = 'home'


def find_auth_link_problems(root, app_name=LANDING_APP):
    """Find prebuilt auth pages the landing app stopped linking to.

    Every project is created with a working sign-in and register page and a
    home page that links to both. A first build rewrites that home page
    wholesale, and a rewrite that drops the links leaves the founder an app
    whose auth pages exist but cannot be reached from anywhere. Nothing else
    notices: it compiles, loads, and looks finished.

    Unlike the two checks above, this one is advisory — see
    initial_build_service, which prefers shipping a page that fails it to
    handing the founder the untouched scaffold.

    Args:
        root: The project tree to scan (a project_path or a task worktree).
        app_name: The frontend app that owns the landing page.

    Returns:
        list[dict]: ``{'path': '/auth/...'}`` for each auth route the app's
        source no longer references anywhere, in a stable order. A project
        without an auth app, or without that landing app, yields [] — this
        reports a link that was lost, it does not require one to exist.
    """
    src_root = os.path.join(root or '', FRONTEND_SRC)
    auth_app = os.path.join(src_root, 'apps', 'auth')
    app_root = os.path.join(src_root, 'apps', app_name)
    if not os.path.isdir(auth_app) or not os.path.isdir(app_root):
        return []

    # Read the app whole: a link counts wherever it lives, so a build that
    # moved the header into a layout component is not reported.
    sources = []
    for source_file in _iter_source_files(app_root):
        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                sources.append(f.read())
        except (OSError, UnicodeDecodeError) as e:
            logger.warning(f"Could not read {source_file} for auth link check: {e}")
    if not sources:
        return []

    app_source = "\n".join(sources)
    return [
        {'path': path} for path in AUTH_LINK_PATHS if path not in app_source
    ]


def describe_auth_link_problems(problems):
    """Render lost auth links as a bulleted list for an agent prompt."""
    shown = problems[:MAX_REPORTED_PROBLEMS]
    lines = [
        f"- nothing links to '{p['path']}' any more" for p in shown
    ]
    if len(problems) > len(shown):
        lines.append(f"- ... and {len(problems) - len(shown)} more")
    return "\n".join(lines)
