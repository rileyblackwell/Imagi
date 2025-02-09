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
    # Admin interface
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/builder/', include('apps.Builder.api.urls')),  # Builder API endpoints
    path('api/payments/', include('apps.Payments.api.urls')),  # Payments API endpoints
    path('api/agents/', include('apps.Agents.api.urls')),  # Agents API endpoints
    path('api/projectmanager/', include('apps.ProjectManager.urls')),  # ProjectManager API endpoints
    
    # App URLs (for server-rendered pages if needed)
    path('builder/', include('apps.Builder.urls')),
    path('', include('apps.Home.urls')),
    path('payments/', include('apps.Payments.urls')),
    path('agents/', include('apps.Agents.urls')),
    
    # Favicon
    path('favicon.ico', favicon_view),
    
    # Auth URLs - make sure this is included
    path('api/v1/auth/', include('apps.Auth.api.urls', namespace='auth_api')),
]

# Debug toolbar in development
if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
    ]
