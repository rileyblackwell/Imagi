"""Shared frontend dependency store for generated projects.

Every generated Imagi project ships the *same* frontend ``package.json`` (a
fixed scaffold — only the ``name`` differs), so installing a private
``node_modules`` per project duplicates hundreds of megabytes and costs
minutes each time, both at project creation and again on every production
container rebuild (the on-disk projects tree is ephemeral there).

This module installs each unique dependency set exactly once into a shared,
content-addressed store and points every project's ``node_modules`` at it with
a symlink. Consequences:

- Project creation and preview start become effectively instant — no install,
  just a symlink — once the store is warm.
- The store is keyed by a hash of the dependency set, so all identical
  projects share one install and a project that ever diverges transparently
  gets (and shares) its own slot.
- The store lives at ``settings.FRONTEND_DEP_STORE_ROOT``, a path independent
  of ``PROJECTS_ROOT``. In production the Docker image prewarms it at build
  time (see the ``warm_frontend_deps`` management command), so it is baked
  into the image and survives every redeploy instead of being reinstalled.

Callers that cannot link (npm missing, install failure, a project whose
``node_modules`` is already a real directory) fall back to the existing
per-project ``npm install``; linking is a fast path, never a hard dependency.
"""

import hashlib
import json
import logging
import os
import shutil
import subprocess

from django.conf import settings

from .preview_service import NPM_INSTALL_TIMEOUT, npm_install_lock

logger = logging.getLogger(__name__)

# Bump when the on-disk layout of a store slot changes in a way that makes
# existing slots unusable, so old slots are ignored instead of relinked.
_STORE_SCHEMA = 'v1'

# package.json sections that determine what npm actually installs. Everything
# else (name, version, scripts, ...) is irrelevant to the resolved tree, so two
# projects differing only there still share one install.
_DEP_SECTIONS = (
    'dependencies',
    'devDependencies',
    'optionalDependencies',
    'peerDependencies',
    'overrides',
    'resolutions',
)


def store_root():
    """Root directory that holds every content-addressed dependency slot."""
    return getattr(settings, 'FRONTEND_DEP_STORE_ROOT', None) or os.path.join(
        settings.PROJECTS_ROOT, '.frontend-deps'
    )


def dependency_signature(package_json):
    """Return a stable hash of the dependency-affecting parts of a package.json.

    Projects whose installed tree would be identical hash the same, so they
    share a single store slot regardless of name/version/script differences.
    """
    canonical = {
        section: dict(sorted((package_json.get(section) or {}).items()))
        for section in _DEP_SECTIONS
    }
    payload = json.dumps(canonical, sort_keys=True, separators=(',', ':'))
    digest = hashlib.sha256(payload.encode('utf-8')).hexdigest()[:32]
    return f"{_STORE_SCHEMA}-{digest}"


def _read_package_json(package_json_path):
    try:
        with open(package_json_path, 'r') as f:
            return json.load(f)
    except (OSError, ValueError) as e:
        logger.warning(f"Could not read package.json at {package_json_path}: {e}")
        return None


def ensure_store(package_json_path):
    """Ensure the shared node_modules for this package.json exists.

    Returns the absolute path to the installed shared ``node_modules``, or
    ``None`` if it could not be built (npm missing, install failed). Installs
    at most once per unique dependency set; concurrent callers serialize on a
    per-slot lock.
    """
    package_json = _read_package_json(package_json_path)
    if package_json is None:
        return None

    signature = dependency_signature(package_json)
    slot = os.path.join(store_root(), signature)
    node_modules = os.path.join(slot, 'node_modules')

    # Fast path: already installed.
    if os.path.isdir(node_modules):
        return node_modules

    npm = shutil.which('npm')
    if not npm:
        logger.warning("npm not found on PATH - cannot build shared dependency store")
        return None

    try:
        os.makedirs(slot, exist_ok=True)
    except OSError as e:
        logger.warning(f"Could not create dependency store slot {slot}: {e}")
        return None

    with npm_install_lock(slot):
        # Re-check under the lock: another installer may have finished while we
        # waited.
        if os.path.isdir(node_modules):
            return node_modules

        # Install from a copy of the project's package.json so the store slot
        # is self-describing and a stray future `npm install` there stays
        # consistent. package-lock is intentionally not carried across.
        try:
            shutil.copyfile(package_json_path, os.path.join(slot, 'package.json'))
        except OSError as e:
            logger.warning(f"Could not stage package.json into {slot}: {e}")
            return None

        logger.info(f"Building shared frontend dependency store: {slot}")
        try:
            result = subprocess.run(
                [npm, 'install', '--no-audit', '--no-fund'],
                cwd=slot,
                capture_output=True,
                text=True,
                timeout=NPM_INSTALL_TIMEOUT,
            )
        except subprocess.TimeoutExpired:
            logger.error(f"Shared store npm install timed out in {slot}")
            return None

        if result.returncode != 0:
            tail = (result.stderr or result.stdout or '').strip()[-2000:]
            logger.error(f"Shared store npm install failed in {slot}: {tail}")
            # Leave no half-populated node_modules that a linker would trust.
            shutil.rmtree(node_modules, ignore_errors=True)
            return None

    logger.info(f"Shared frontend dependency store ready: {node_modules}")
    return node_modules


def link_frontend_dependencies(frontend_path):
    """Point ``frontend_path/node_modules`` at the shared store via a symlink.

    Returns True when the frontend ends up with usable dependencies (freshly
    linked, already linked, or an existing real install left untouched), and
    False when the caller should fall back to a per-project ``npm install``
    (no package.json, npm missing, or the store could not be built).
    """
    package_json_path = os.path.join(frontend_path, 'package.json')
    if not os.path.exists(package_json_path):
        return False

    node_modules = os.path.join(frontend_path, 'node_modules')

    if os.path.islink(node_modules):
        # A symlink pointing at a live store slot is already what we want; a
        # dangling one (store slot pruned/rebuilt) is replaced below.
        if os.path.isdir(node_modules):
            return True
        try:
            os.unlink(node_modules)
        except OSError:
            pass
    elif os.path.isdir(node_modules):
        # A real, previously-installed node_modules: leave it alone rather than
        # risk disturbing a running dev server. It already has dependencies.
        return True

    store_node_modules = ensure_store(package_json_path)
    if not store_node_modules:
        return False

    # Atomic swap: build the symlink under a temp name, then rename over any
    # leftover, so a concurrent reader never sees a missing node_modules.
    tmp_link = f"{node_modules}.linktmp.{os.getpid()}"
    try:
        if os.path.lexists(tmp_link):
            os.unlink(tmp_link)
        os.symlink(store_node_modules, tmp_link)
        os.replace(tmp_link, node_modules)
    except OSError as e:
        logger.warning(f"Could not link {node_modules} -> {store_node_modules}: {e}")
        try:
            if os.path.lexists(tmp_link):
                os.unlink(tmp_link)
        except OSError:
            pass
        return False

    logger.info(f"Linked {node_modules} -> {store_node_modules}")
    return True
