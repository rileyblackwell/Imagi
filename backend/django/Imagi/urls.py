"""
URL configuration for Imagi project.
"""

from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.views.decorators.http import require_GET
from django.conf import settings

@require_GET
def favicon_view(request):
    return HttpResponse(status=204)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include([
        path('project-manager/', include('apps.Products.Oasis.ProjectManager.api.urls')),
        path('auth/', include('apps.Auth.api.urls')),
        path('builder/', include('apps.Products.Oasis.Builder.api.urls')),
        path('payments/', include('apps.Payments.api.urls')),
        path('agents/', include('apps.Products.Oasis.Agents.api.urls')),
    ])),
    
    # App URLs (for server-rendered pages if needed)
    path('builder/', include('apps.Products.Oasis.Builder.urls')),
    path('', include('apps.Home.urls')),
    path('payments/', include('apps.Payments.urls')),
    path('agents/', include('apps.Products.Oasis.Agents.urls')),
    
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
