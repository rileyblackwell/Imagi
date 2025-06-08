"""
Core business logic for the Auth app.
All API endpoints are handled in the api/ directory.
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def csrf_failure(request, reason=""):
    """
    Custom CSRF failure view for better debugging in production.
    This view provides detailed information about CSRF failures
    which is especially useful for Railway proxy architecture.
    """
    logger.error(f"CSRF failure: {reason}")
    logger.error(f"Request headers: {dict(request.headers)}")
    logger.error(f"Request method: {request.method}")
    logger.error(f"Request path: {request.path}")
    logger.error(f"Origin: {request.META.get('HTTP_ORIGIN', 'None')}")
    logger.error(f"Referer: {request.META.get('HTTP_REFERER', 'None')}")
    
    return JsonResponse({
        'error': 'CSRF verification failed',
        'reason': reason,
        'detail': 'CSRF token missing or incorrect',
        'debug_info': {
            'method': request.method,
            'path': request.path,
            'origin': request.META.get('HTTP_ORIGIN'),
            'referer': request.META.get('HTTP_REFERER'),
        } if hasattr(request, 'user') and request.user.is_superuser else None
    }, status=403)
