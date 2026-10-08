"""
Files the build agents may not change: the prebuilt auth.

Sign-in, registration and the auth API come from Imagi's maintained template
(codegen/prebuilt_apps/auth.py) so they are correct in every project. A model
rewriting them, even with good intentions, is how a project ends up with a
login that skips CSRF or a register endpoint without password validation, so
every file-writing tool refuses these paths, whatever the brief says.

Two auth files stay open, and they are the whole of the auth pages' look:
the stylesheet and the copy. That is enough to restyle the pages to any
design, which is all a business needs to change about them.

This binds the agents only. A founder editing their own code by hand is
editing their own code.
"""
from __future__ import annotations

import posixpath

AUTH_FRONTEND_DIR = 'frontend/vuejs/src/apps/auth'
AUTH_BACKEND_DIR = 'backend/django/apps/auth'

# The auth files an agent may rewrite: how the pages look and what they say.
AUTH_RESTYLE_PATHS = (
    f'{AUTH_FRONTEND_DIR}/styles/auth.css',
    f'{AUTH_FRONTEND_DIR}/brand.ts',
)

# Everything under these is the maintained auth, apart from the paths above.
PROTECTED_DIRS = (AUTH_FRONTEND_DIR, AUTH_BACKEND_DIR)

# The scaffold's shared auth plumbing: token storage and the API client that
# attaches the token and the CSRF header to every request.
PROTECTED_FILES = (
    'frontend/vuejs/src/shared/stores/auth.ts',
    'frontend/vuejs/src/shared/services/api.ts',
)

REFUSAL = (
    "'{path}' is part of the project's prebuilt sign-in and registration, which "
    "Imagi maintains so it stays secure; agents cannot change it. To change how "
    "the sign-in and register pages look, edit "
    f"'{AUTH_RESTYLE_PATHS[0]}' (every visual style) or '{AUTH_RESTYLE_PATHS[1]}' "
    "(the business name and page copy). Anything else about sign-in is not "
    "available yet: tell the user plainly instead of working around it."
)


def _normalize(path: str) -> str:
    path = (path or '').strip().replace('\\', '/').lstrip('/')
    path = posixpath.normpath(path) if path else ''
    return '' if path == '.' else path


def _under(path: str, directory: str) -> bool:
    return path == directory or path.startswith(directory + '/')


def is_protected_path(path: str) -> bool:
    """Whether an agent is barred from writing or deleting this file.

    ``path`` is project-relative, as the file tools see it after
    normalize_file_path. Matching is case-insensitive, so 'Apps/Auth' on a
    case-insensitive disk cannot slip past.
    """
    p = _normalize(path).lower()
    if not p:
        return False
    if p in (allowed.lower() for allowed in AUTH_RESTYLE_PATHS):
        return False
    if p in (f.lower() for f in PROTECTED_FILES):
        return True
    return any(_under(p, d.lower()) for d in PROTECTED_DIRS)


def is_protected_directory(path: str) -> bool:
    """Whether deleting this directory would delete protected files.

    True for the protected directories, anything inside them, and any
    ancestor of them (deleting 'frontend/vuejs/src/apps' takes auth with it).
    """
    p = _normalize(path).lower()
    if not p:
        # The project root itself holds everything.
        return True
    protected = [d.lower() for d in PROTECTED_DIRS] + [f.lower() for f in PROTECTED_FILES]
    return any(_under(p, d) or _under(d, p) for d in protected)


def refusal(path: str) -> str:
    return REFUSAL.format(path=_normalize(path))
