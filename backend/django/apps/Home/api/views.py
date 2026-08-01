import logging
import os
import shutil

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

logger = logging.getLogger(__name__)

# External programs the build workspace shells out to, and what breaks without
# each. Every one of these is present on a developer's machine and has to be
# installed into the image on purpose (backend/django/Dockerfile), which is
# exactly the kind of gap that survives code review and passing tests.
#
# This list exists because 'git' once did not: generated projects are git repos
# and every subagent builds in a worktree of one, so its absence in production
# made dispatched subagents die the instant they started — visible only as
# threads that never said anything, three layers below the UI. Presence here is
# a PATH lookup, so a missing binary is one curl away instead of a log dig.
REQUIRED_BINARIES = (
    # Generated projects are git repos; each subagent run forks a worktree.
    ('git', None),
    # Generated projects run their own Vite + Django dev servers for preview.
    ('node', None),
    ('npm', None),
    # Headless render of the preview for the workspace UI. Path is pinned by
    # env var (BROWSER_PREVIEW_EXECUTABLE) rather than found on PATH.
    ('chromium', 'BROWSER_PREVIEW_EXECUTABLE'),
)


def _binary_status():
    """Which of the workspace's external programs this container actually has.

    Returns {name: path-or-None}. Cheap enough to serve on every request: a
    PATH scan (or a stat, for the env-pinned entries), never a subprocess —
    asking each binary for its version would turn a diagnostic into four
    process spawns.
    """
    found = {}
    for name, env_var in REQUIRED_BINARIES:
        pinned = os.environ.get(env_var) if env_var else None
        if pinned:
            found[name] = pinned if os.path.exists(pinned) else None
        else:
            found[name] = shutil.which(name)
    return found


def _database_status():
    """Cheap connectivity probe shared by the health and version endpoints.

    Both callers are AllowAny, so the driver's exception text never reaches the
    response: a libpq connection failure names the internal database host, its
    address, port and role, which is exactly what an attacker wants and exactly
    when they can get it. The detail goes to the logs instead, matching the
    policy imagi.exception_handler enforces everywhere else.
    """
    try:
        User = get_user_model()
        User.objects.exists()
        return 'connected'
    except Exception:
        logger.exception("Database connectivity probe failed")
        return 'error'


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint for monitoring and Railway health checks."""
    return Response({
        'status': 'healthy',
        'service': 'imagi-backend',
        'database': _database_status(),
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def version_info(request):
    """Report which build THIS process is running, for the split deployment.

    The web and workspace tiers are the same Django image deployed as two
    Railway services (see settings.IMAGI_ROLE), so they can drift onto
    different commits when one redeploys and the other does not — the usual
    cause of "my change isn't live in prod". This view reports the running
    tier's role and deployed commit; it is mounted at a web-routed path AND a
    workspace-routed path (see api/ops_urls.py + the nginx $api_upstream map),
    so you can hit both and compare `commit`:

        curl https://<app>/api/v1/ops/web/version/
        curl https://<app>/api/v1/ops/workspace/version/

    Matching commits => the tiers are in sync. Different => the stale tier
    needs a redeploy. Values come from Railway's injected build vars.

    It also reports the external programs the build workspace shells out to
    (REQUIRED_BINARIES). `missing_binaries` is the field to read: non-empty
    means this container cannot do part of its job no matter how current its
    commit is, which looks nothing like a deploy problem from the UI. It
    matters most on the workspace tier, but both tiers run the same image, so
    both answer.
    """
    commit = os.environ.get('RAILWAY_GIT_COMMIT_SHA', '') or ''
    binaries = _binary_status()
    return Response({
        'status': 'healthy',
        'service': 'imagi-backend',
        'role': settings.IMAGI_ROLE or 'unset',
        'commit': commit or 'unknown',
        'commit_short': commit[:7] if commit else 'unknown',
        'branch': os.environ.get('RAILWAY_GIT_BRANCH') or 'unknown',
        'deployment_id': os.environ.get('RAILWAY_DEPLOYMENT_ID') or 'unknown',
        'database': _database_status(),
        'binaries': binaries,
        'missing_binaries': sorted(
            name for name, path in binaries.items() if not path
        ),
    })
