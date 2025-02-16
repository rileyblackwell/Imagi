"""
URL configuration for the Agents app.
All routes are handled by the API.
"""

from django.urls import path, include

app_name = 'agents'

urlpatterns = [
    # All routes are API routes
    path('api/', include('apps.Agents.api.urls')),
]
