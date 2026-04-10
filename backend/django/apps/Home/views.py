from django.conf import settings
from django.http import HttpResponseRedirect, HttpRequest, JsonResponse
import logging
from django.shortcuts import render
from django.views.decorators.http import require_GET

from .constants import FrontendRoutes

logger = logging.getLogger(__name__)


@require_GET
def health_check(request):
    """Health check endpoint for monitoring and Railway health checks."""
    from django.contrib.auth import get_user_model
    try:
        User = get_user_model()
        User.objects.exists()
        db_status = 'connected'
    except Exception as e:
        db_status = f'error: {str(e)}'

    return JsonResponse({
        'status': 'healthy',
        'service': 'imagi-backend',
        'database': db_status,
    })

def get_frontend_url(path: str) -> str:
    """Constructs frontend URL with proper error handling."""
    base_url = getattr(settings, 'FRONTEND_URL', '')
    if not base_url:
        logger.error("FRONTEND_URL not configured in settings")
        return path
    return f"{base_url.rstrip('/')}{path}"

def frontend_redirect(request: HttpRequest, path: str) -> HttpResponseRedirect:
    """Generic frontend redirect handler with logging."""
    target_url = get_frontend_url(path)
    logger.debug(f"Redirecting to frontend: {target_url}")
    return HttpResponseRedirect(target_url)

@require_GET
def landing_page(request):
    return render(request, 'home/landing.html')

def about_page(request: HttpRequest) -> HttpResponseRedirect:
    """Redirect to frontend about page."""
    return frontend_redirect(request, FrontendRoutes.ABOUT)

def privacy_page(request: HttpRequest) -> HttpResponseRedirect:
    return frontend_redirect(request, FrontendRoutes.PRIVACY)

def terms_page(request: HttpRequest) -> HttpResponseRedirect:
    return frontend_redirect(request, FrontendRoutes.TERMS)

def contact_page(request: HttpRequest) -> HttpResponseRedirect:
    return frontend_redirect(request, FrontendRoutes.CONTACT)

def cookie_policy(request: HttpRequest) -> HttpResponseRedirect:
    return frontend_redirect(request, FrontendRoutes.COOKIE_POLICY)

