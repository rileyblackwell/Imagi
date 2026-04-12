"""
URL Configuration for the ProjectManager app.

Note: All API URLs are defined in api/urls.py
"""

from django.urls import path, include

app_name = 'projectmanager'

urlpatterns = [
    # Include API URLs from the api directory
    path('api/', include('apps.Products.Imagi.ProjectManager.api.urls', namespace='api')),
    
    # Add any non-API URLs here if needed in the future
]