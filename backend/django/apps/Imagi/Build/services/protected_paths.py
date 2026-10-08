"""
Files the build agents may not change: the prebuilt auth and payments.

Sign-in, registration and the auth API come from Imagi's maintained template
(codegen/prebuilt_apps/auth.py) so they are correct in every project. A model
rewriting them, even with good intentions, is how a project ends up with a
login that skips CSRF or a register endpoint without password validation, so
every file-writing tool refuses these paths, whatever the brief says.

Two auth files stay open, and they are the whole of the auth pages' look:
the stylesheet and the copy. That is enough to restyle the pages to any
design, which is all a business needs to change about them.

The prebuilt payments (Sell.services.payment_templates) follow the same
rule: the checkout flow and the server-side usage client are Imagi's, and
only their stylesheet and copy are open.

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

PAYMENTS_FRONTEND_DIR = 'frontend/vuejs/src/apps/payments'
PAYMENTS_BACKEND_DIR = 'backend/django/apps/payments'

# The payment files an agent may rewrite: how the pages look and what they say.
PAYMENTS_RESTYLE_PATHS = (
    f'{PAYMENTS_FRONTEND_DIR}/styles/payments.css',
    f'{PAYMENTS_FRONTEND_DIR}/brand.ts',
)

# Everything under these is maintained by Imagi, apart from the paths above.
PROTECTED_DIRS = (
    AUTH_FRONTEND_DIR, AUTH_BACKEND_DIR,
    PAYMENTS_FRONTEND_DIR, PAYMENTS_BACKEND_DIR,
)
OPEN_PATHS = AUTH_RESTYLE_PATHS + PAYMENTS_RESTYLE_PATHS

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

PAYMENTS_REFUSAL = (
    "'{path}' is part of the project's prebuilt payments, which Imagi maintains "
    "so they stay secure; agents cannot change it. To change how the payment "
    f"pages look, edit '{PAYMENTS_RESTYLE_PATHS[0]}' (every visual style) or "
    f"'{PAYMENTS_RESTYLE_PATHS[1]}' (the page copy). To charge for something, "
    "use the plans in 'frontend/vuejs/src/apps/payments/' as they are: link to "
    "'/pricing' or '/store', and from the backend call report_usage() or "
    "has_active_plan() from 'apps.payments'. Prices are set in the Sell console; "
    "anything else, tell the user plainly instead of working around it."
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
    if p in (allowed.lower() for allowed in OPEN_PATHS):
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
    p = _normalize(path)
    if any(_under(p.lower(), d.lower()) for d in (PAYMENTS_FRONTEND_DIR, PAYMENTS_BACKEND_DIR)):
        return PAYMENTS_REFUSAL.format(path=p)
    return REFUSAL.format(path=p)
