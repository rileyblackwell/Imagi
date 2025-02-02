"""
URL configuration for the Payments app.
All routes are handled by the API.
"""

from django.urls import path, include

app_name = 'payments'

urlpatterns = [
    # All routes are API routes
    path('api/', include('apps.Payments.api.urls')),
] 