import os

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


def _database_status():
    """Cheap connectivity probe shared by the health and version endpoints."""
    try:
        User = get_user_model()
        User.objects.exists()
        return 'connected'
    except Exception as e:
        return f'error: {str(e)}'


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
    """
    commit = os.environ.get('RAILWAY_GIT_COMMIT_SHA', '') or ''
    return Response({
        'status': 'healthy',
        'service': 'imagi-backend',
        'role': settings.IMAGI_ROLE or 'unset',
        'commit': commit or 'unknown',
        'commit_short': commit[:7] if commit else 'unknown',
        'branch': os.environ.get('RAILWAY_GIT_BRANCH') or 'unknown',
        'deployment_id': os.environ.get('RAILWAY_DEPLOYMENT_ID') or 'unknown',
        'database': _database_status(),
    })
