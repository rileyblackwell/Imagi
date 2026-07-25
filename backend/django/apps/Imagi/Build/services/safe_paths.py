"""Path containment for anything that turns a user-supplied path into a real one.

Every file path that reaches the Build services comes from the user — the REST
endpoints take it from the request body or from a ``<path:file_path>`` URL
segment, both of which happily carry ``..`` segments and absolute paths. Joining
one of those onto the project root escapes it (``os.path.join`` discards the root
entirely when the second argument is absolute), so each read, write and delete
resolves the path through :func:`resolve_within` first.
"""

import os


class UnsafePathError(ValueError):
    """A user-supplied path resolved outside the project directory."""


def resolve_within(project_path, file_path):
    """Resolve ``file_path`` against ``project_path`` and confine it there.

    Returns the absolute, symlink-resolved path. Raises :class:`UnsafePathError`
    when the result lands outside the project directory, whether by ``..``
    segments, an absolute path, or a symlink pointing out of the tree.
    """
    if not project_path:
        raise UnsafePathError('Project path is not set')

    root = os.path.realpath(project_path)
    full = os.path.realpath(os.path.join(root, file_path))
    if full != root and not full.startswith(root + os.sep):
        raise UnsafePathError(f"Path '{file_path}' is outside the project directory")
    return full


def resolve_safe(project_path, file_path):
    """:func:`resolve_within` for the REST services — rejects with a 400.

    The services let exceptions propagate to DRF, so raising ``ValidationError``
    here turns a traversal attempt into a plain bad request rather than a 500.
    """
    from rest_framework.exceptions import ValidationError

    try:
        return resolve_within(project_path, file_path)
    except UnsafePathError as exc:
        raise ValidationError(str(exc))
