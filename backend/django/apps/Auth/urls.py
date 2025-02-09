"""
URL configuration for Auth app.
Includes all authentication-related URLs, including password reset views.
"""

from django.urls import path, include

app_name = 'auth'

urlpatterns = [
    # API endpoints
    path('api/v1/auth/', include(('apps.Auth.api.urls', 'auth_api'))),
    
    # Include allauth URLs
    path('', include('allauth.urls')),
]
