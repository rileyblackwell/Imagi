"""Run a project's preview under a dedicated unprivileged user.

The preview exists to run each project's *own* code — the generated Django
backend under ``runserver``, its Vite dev server, ``npm`` lifecycle scripts, and
a headless Chromium rendering the result. All of that is written by the user
(directly through the file API, or by the agent on their behalf), so it is
untrusted, and :func:`preview_service.child_env` already keeps Imagi's secrets
out of its environment.

What ``child_env`` cannot do is stop the code *reading* secrets another way.
Imagi's own server process holds every deployment secret in its environment and
holds a live database connection; while the preview children run as the same
user as that server (root, in the container image), they can read
``/proc/<imagi-pid>/environ`` and recover all of it — the API keys, the
database URL, ``DJANGO_SECRET_KEY`` — regardless of ``child_env``. On Linux a
process may read another's ``environ`` only when it shares the owning uid (or is
root), so running the preview children as a *different, unprivileged* user
closes that path: the Imagi server stays as it is, and the preview can no longer
see into it, into other users' working copies it doesn't own, or reach anything
only the server's identity is trusted for.

This is deliberately a per-deployment opt-in (``settings.PREVIEW_SANDBOX_USER``):
it only works when the Imagi process runs as root (so it can drop privileges for
a child) and when that user exists and owns — or shares a group with — the
project tree. When it is unset, or the process is not root, every helper here is
inert and spawning behaves exactly as before, so development and the test suite
are unaffected. See ``docs/preview-sandbox.md`` for the rollout steps.

Scope / what this does NOT do yet: all previews share one unprivileged user, so
it isolates the preview from the Imagi server but not one project's preview from
another's files. Per-project users (or a stronger sandbox) and network-egress
limits are the next step; they are tracked separately.
"""

import grp
import logging
import os
import pwd

from django.conf import settings

logger = logging.getLogger(__name__)

# Files and directories the preview writes are created group-writable so the
# Imagi server (root) and the preview user can both manage them through the
# shared group. 0o002 clears only "other" write.
SANDBOX_UMASK = 0o002

_IDENTITY_SENTINEL = object()
_identity_cache = _IDENTITY_SENTINEL


def _resolve_identity():
    """(uid, gid, name) for the configured sandbox user, or None when inactive.

    None — meaning "do not drop privileges" — is returned when the setting is
    unset, when the Imagi process is not root (only root can hand a child a
    different uid, so attempting it would raise), or when the named user does
    not exist in this image. Each of those is a normal state (local dev, tests,
    an image built before the user was added), not an error, so they log at most
    once and fall back to today's behaviour.
    """
    name = (getattr(settings, 'PREVIEW_SANDBOX_USER', '') or '').strip()
    if not name:
        return None
    if not hasattr(os, 'geteuid') or os.geteuid() != 0:
        logger.warning(
            "PREVIEW_SANDBOX_USER is set but Imagi is not running as root; "
            "preview processes will not be deprivileged."
        )
        return None
    try:
        entry = pwd.getpwnam(name)
    except KeyError:
        logger.error(
            "PREVIEW_SANDBOX_USER=%r does not exist in this image; "
            "preview processes will not be deprivileged.",
            name,
        )
        return None
    return (entry.pw_uid, entry.pw_gid, entry.pw_name)


def sandbox_identity():
    """Cached :func:`_resolve_identity`. ``(uid, gid, name)`` or None."""
    global _identity_cache
    if _identity_cache is _IDENTITY_SENTINEL:
        _identity_cache = _resolve_identity()
    return _identity_cache


def is_active():
    return sandbox_identity() is not None


def child_privilege_kwargs():
    """Keyword arguments for ``subprocess.Popen``/``run`` to drop privileges.

    ``{'user', 'group', 'umask'}`` when the sandbox is active, otherwise an
    empty dict — so a call site spreads ``**child_privilege_kwargs()`` and
    behaves exactly as before when the sandbox is off.
    """
    identity = sandbox_identity()
    if identity is None:
        return {}
    uid, gid, _name = identity
    return {'user': uid, 'group': gid, 'umask': SANDBOX_UMASK}


# Directories not worth descending into when preparing a project tree: the
# dependency store is reached through a symlink and is read-only to the preview,
# git metadata is off limits to the preview anyway, and these are the large ones.
_PREPARE_SKIP_DIRS = frozenset({'node_modules', '.git', '.vite', '__pycache__'})


def prepare_tree_recursive(path):
    """:func:`prepare_tree` over ``path`` and everything under it.

    Used on a project's working copy at preview start so files created before
    the sandbox was switched on — root-owned and not group-writable — become
    readable and writable by the deprivileged preview, without a separate
    migration step. Symlinks are never followed (so it won't wander into the
    shared dependency store), and the big/managed directories above are skipped.
    No-op when the sandbox is off; best-effort, never raises into the preview.
    """
    if not is_active() or not path or not os.path.isdir(path):
        return
    prepare_tree(path)
    for current, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in _PREPARE_SKIP_DIRS]
        for name in dirs:
            prepare_tree(os.path.join(current, name))
        for name in files:
            full = os.path.join(current, name)
            if os.path.islink(full):
                continue
            try:
                st = os.lstat(full)
                os.chown(full, -1, sandbox_identity()[1])
                os.chmod(full, (st.st_mode & 0o7777) | 0o660)
            except OSError:
                pass


def prepare_tree(path):
    """Make ``path`` writable by the sandbox user through the shared group.

    Sets the directory's group to the sandbox group and turns on the setgid bit
    plus group read/write/execute, so files the Imagi server creates inside it
    inherit that group and (with the server's umask) stay group-writable — which
    is what lets the deprivileged preview read and overwrite them. Best-effort
    and a no-op when the sandbox is off; never raises into the preview path.
    """
    identity = sandbox_identity()
    if identity is None or not path:
        return
    _uid, gid, _name = identity
    try:
        os.chown(path, -1, gid)
        current = os.stat(path).st_mode & 0o7777
        os.chmod(path, current | 0o2775)
    except OSError as exc:
        logger.warning("Could not prepare %s for the preview sandbox: %s", path, exc)
