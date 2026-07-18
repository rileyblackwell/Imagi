"""
Project file repository: keeps the database copy of a user's project files
in sync with the working copy on disk.

Design
------
- The directory at ``project.project_path`` (under PROJECTS_ROOT) is the
  SOURCE OF TRUTH. Everything runs from disk in both development and
  production: the agent's tools, the preview server, and git version
  control all operate on these files directly.
- The database (ProjectFile rows) is a mirror of the disk copy, kept for
  development/debugging — it makes a user's project files browsable from
  the Build module — and as a backup for rehydrating a working copy that
  has gone missing (e.g. a redeployed production host with an empty
  PROJECTS_ROOT). When disk and database disagree, disk wins.
- Every mutation touches disk first, then writes through to the mirror:
  the file services and agent tools call ``record_file`` / ``remove_file``
  / ``remove_directory`` after touching disk.
- ``import_project_from_disk`` refreshes the mirror from disk (backfills,
  or re-syncs after a git reset rewrites the working copy);
  ``hydrate_project`` goes the other way, and is only used to restore a
  missing working copy — it never overwrites files already on disk unless
  explicitly asked.
"""

import logging
import os

from django.db import transaction

from apps.Imagi.Build.models import ProjectFile

logger = logging.getLogger(__name__)

# Only text files with these extensions are stored in the database.
# Everything else (images, binaries, lockfiles we don't care about) lives
# on disk only.
SYNCED_EXTENSIONS = {
    '.vue', '.ts', '.tsx', '.js', '.jsx', '.css', '.json',
    '.html', '.py', '.md', '.txt', '.env', '.cfg', '.toml', '.yaml', '.yml',
}

# Never sync files inside these directories
SKIP_DIRS = {
    'node_modules', '__pycache__', '.git', 'dist', 'build',
    'staticfiles', 'media', '.venv', 'venv',
}

# Refuse to store files larger than this in the database
MAX_SYNCED_FILE_BYTES = 1_000_000

_EXT_TYPE_MAP = {
    '.html': 'html', '.css': 'css', '.js': 'javascript', '.jsx': 'javascript',
    '.json': 'json', '.py': 'python', '.md': 'markdown', '.txt': 'text',
    '.vue': 'vue', '.ts': 'typescript', '.tsx': 'typescript',
}


def _normalize_rel_path(rel_path: str) -> str:
    """Normalize a project-relative path to POSIX separators, no leading slash."""
    return rel_path.replace(os.sep, '/').strip().lstrip('/')


def _file_type_for(rel_path: str) -> str:
    return _EXT_TYPE_MAP.get(os.path.splitext(rel_path)[1].lower(), '')


def is_syncable_path(rel_path: str) -> bool:
    """Whether a project-relative path should have a database copy."""
    rel_path = _normalize_rel_path(rel_path)
    parts = rel_path.split('/')
    if any(p in SKIP_DIRS or p.startswith('.') for p in parts[:-1]):
        return False
    filename = parts[-1]
    if filename.startswith('.') and os.path.splitext(filename)[1].lower() not in SYNCED_EXTENSIONS:
        return False
    ext = os.path.splitext(filename)[1].lower()
    return ext in SYNCED_EXTENSIONS


# ---------------------------------------------------------------------------
# Write-through primitives (called after every disk mutation)
# ---------------------------------------------------------------------------

def record_file(project, rel_path: str, content: str = None):
    """Upsert the database copy of a project file.

    Reads the content from disk when not provided. Returns the ProjectFile
    row, or None when the path is not syncable (binary/ignored/too large).
    """
    rel_path = _normalize_rel_path(rel_path)
    if not is_syncable_path(rel_path):
        return None

    if content is None:
        full_path = os.path.join(project.project_path, rel_path)
        try:
            if os.path.getsize(full_path) > MAX_SYNCED_FILE_BYTES:
                logger.warning(f"Skipping DB sync for oversized file: {rel_path}")
                return None
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except (OSError, UnicodeDecodeError) as e:
            logger.warning(f"Could not read {rel_path} for DB sync: {e}")
            return None

    if len(content.encode('utf-8', errors='ignore')) > MAX_SYNCED_FILE_BYTES:
        logger.warning(f"Skipping DB sync for oversized content: {rel_path}")
        return None

    row, _created = ProjectFile.objects.update_or_create(
        project=project,
        path=rel_path,
        defaults={
            'content': content,
            'file_type': _file_type_for(rel_path),
            'size': len(content.encode('utf-8', errors='ignore')),
        },
    )
    return row


def remove_file(project, rel_path: str) -> int:
    """Delete the database copy of a project file. Returns rows deleted."""
    rel_path = _normalize_rel_path(rel_path)
    deleted, _ = ProjectFile.objects.filter(project=project, path=rel_path).delete()
    return deleted


def remove_directory(project, rel_dir: str) -> int:
    """Delete database copies of every file under a directory prefix."""
    rel_dir = _normalize_rel_path(rel_dir).rstrip('/')
    if not rel_dir:
        raise ValueError("Refusing to remove database files for the project root")
    deleted, _ = ProjectFile.objects.filter(
        project=project, path__startswith=rel_dir + '/'
    ).delete()
    return deleted


def get_db_content(project, rel_path: str):
    """Return the database copy's content for a file, or None if absent."""
    rel_path = _normalize_rel_path(rel_path)
    row = ProjectFile.objects.filter(project=project, path=rel_path).only('content').first()
    return row.content if row else None


# ---------------------------------------------------------------------------
# Bulk sync (DB -> disk and disk -> DB)
# ---------------------------------------------------------------------------

def hydrate_project(project, overwrite: bool = False) -> dict:
    """Materialize the working copy on disk from the database rows.

    Writes each ProjectFile to ``project.project_path``. Files already on
    disk are left alone unless ``overwrite`` is set, so a development
    checkout with newer local edits is never clobbered by accident.
    """
    project_root = project.project_path
    written = 0
    skipped = 0

    for row in ProjectFile.objects.filter(project=project).iterator():
        full_path = os.path.join(project_root, row.path.replace('/', os.sep))
        if os.path.exists(full_path) and not overwrite:
            skipped += 1
            continue
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(row.content)
        written += 1

    logger.info(f"Hydrated project {project.id}: {written} files written, {skipped} already present")
    return {'written': written, 'skipped': skipped}


def import_project_from_disk(project, prune: bool = True) -> dict:
    """Import/refresh the database copy from the working copy on disk.

    Used to backfill existing projects and to re-sync after operations that
    rewrite the working copy wholesale (e.g. a git version reset). When
    ``prune`` is set, rows whose files no longer exist on disk are deleted.
    """
    project_root = project.project_path
    if not project_root or not os.path.isdir(project_root):
        raise ValueError(f"Project {project.id} has no directory on disk to import from")

    seen = set()
    synced = 0
    # Batch every per-file upsert into a single transaction. Without this each
    # record_file() auto-commits on its own — one fsync per file — which makes
    # importing a freshly scaffolded project (hundreds of files) needlessly
    # slow, especially on SQLite. One commit at the end instead of hundreds.
    with transaction.atomic():
        for root, dirs, filenames in os.walk(project_root):
            dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not d.startswith('.'))
            for filename in sorted(filenames):
                abs_path = os.path.join(root, filename)
                rel_path = _normalize_rel_path(os.path.relpath(abs_path, project_root))
                if not is_syncable_path(rel_path):
                    continue
                if record_file(project, rel_path) is not None:
                    seen.add(rel_path)
                    synced += 1

        pruned = 0
        if prune:
            stale = ProjectFile.objects.filter(project=project).exclude(path__in=seen)
            pruned, _ = stale.delete()

    logger.info(f"Imported project {project.id} from disk: {synced} files synced, {pruned} stale rows pruned")
    return {'synced': synced, 'pruned': pruned}


def ensure_working_copy(project) -> bool:
    """Make sure the project's working copy exists on disk.

    If the project directory is missing or empty but the database has file
    rows (a production cold start, or a fresh development environment),
    hydrate it from the database. Returns True when a hydration ran.
    """
    project_root = project.project_path
    if not project_root:
        return False

    has_disk_files = False
    if os.path.isdir(project_root):
        for _root, dirs, filenames in os.walk(project_root):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith('.')]
            if any(not f.startswith('.') for f in filenames):
                has_disk_files = True
                break

    if has_disk_files:
        return False

    if not ProjectFile.objects.filter(project=project).exists():
        return False

    os.makedirs(project_root, exist_ok=True)
    hydrate_project(project)
    return True
