"""
URL configuration for Imagi project.
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_GET
from django.conf import settings

@require_GET
def favicon_view(request):
    return HttpResponse(status=204)

@require_GET
def health_check_view(request):
    """Global health check endpoint for monitoring and Railway health checks."""
    from django.contrib.auth import get_user_model
    try:
        # Quick database connectivity check
        User = get_user_model()
        User.objects.exists()
        db_status = 'connected'
    except Exception as e:
        db_status = f'error: {str(e)}'
    
    return JsonResponse({
        'status': 'healthy',
        'service': 'imagi-backend',
        'database': db_status,
        'timestamp': request.META.get('HTTP_DATE', 'unknown')
    }, status=200)


urlpatterns = [
    path('admin/', admin.site.urls),
    # Global health check endpoint (before api/v1/ routes)
    path('api/v1/health/', health_check_view, name='health-check'),
    path('api/v1/', include([
        path('project-manager/', include('apps.Products.Imagi.ProjectManager.api.urls')),
        path('auth/', include('apps.Auth.api.urls')),
        path('builder/', include('apps.Products.Imagi.Builder.api.urls')),
        path('payments/', include('apps.Payments.api.urls')),
        path('agents/', include('apps.Products.Imagi.Agents.api.urls')),
    ])),
    
    # App URLs (for server-rendered pages if needed)
    path('builder/', include('apps.Products.Imagi.Builder.urls')),
    path('', include('apps.Home.urls')),
    path('payments/', include('apps.Payments.urls')),
    path('agents/', include('apps.Products.Imagi.Agents.urls')),
    
    # Favicon
    path('favicon.ico', favicon_view),
]

# Debug toolbar in development
if settings.DEBUG:
    try:
        urlpatterns += [
            path('__debug__/', include('debug_toolbar.urls')),
        ]
    except ImportError:
        # debug_toolbar not installed, skip
        pass
