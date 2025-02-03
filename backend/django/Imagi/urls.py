"""
URL configuration for Imagi project.
"""

from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.views.decorators.http import require_GET

@require_GET
def favicon_view(request):
    return HttpResponse(status=204)

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/auth/', include('apps.Auth.api.urls')),  # Auth API endpoints
    path('api/builder/', include('apps.Builder.api.urls')),  # Builder API endpoints
    path('api/payments/', include('apps.Payments.api.urls')),  # Payments API endpoints
    path('api/agents/', include('apps.Agents.api.urls')),  # Agents API endpoints
    path('api/projectmanager/', include('apps.ProjectManager.urls')),  # ProjectManager API endpoints
    
    # App URLs (for server-rendered pages if needed)
    path('auth/', include('apps.Auth.urls')),  # Auth app URLs (including password reset)
    path('builder/', include('apps.Builder.urls')),
    path('', include('apps.Home.urls')),
    path('payments/', include('apps.Payments.urls')),
    path('agents/', include('apps.Agents.urls')),
    
    # Favicon
    path('favicon.ico', favicon_view),
]

# Debug toolbar in development
from django.conf import settings
if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
    ]
