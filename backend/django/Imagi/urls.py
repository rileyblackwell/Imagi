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
    
    # API endpoints - version 1
    path('api/v1/', include([
        path('', include('apps.ProjectManager.api.urls')),
        path('auth/', include('apps.Auth.api.urls', namespace='auth_api')),
        path('builder/', include('apps.Builder.api.urls')),
        path('payments/', include('apps.Payments.api.urls')),
        path('agents/', include('apps.Agents.api.urls')),
    ])),
    
    # App URLs (for server-rendered pages if needed)
    path('builder/', include('apps.Builder.urls')),
    path('', include('apps.Home.urls')),
    path('payments/', include('apps.Payments.urls')),
    path('agents/', include('apps.Agents.urls')),
    
    # Favicon
    path('favicon.ico', favicon_view),
]

# Debug toolbar in development
if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
    ]
