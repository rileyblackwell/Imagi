"""
URL configuration for the Build app.
All routes are handled by the API; see api/urls.py.
"""
from django.urls import path, include

app_name = 'build'

urlpatterns = [
    # All routes are API routes
    path('api/', include('apps.Imagi.Build.api.urls')),
]
