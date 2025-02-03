"""
URL configuration for the Payments app.
All routes are handled by the API, frontend is handled by Vue.js.
"""

from django.urls import path, include

app_name = 'payments'

urlpatterns = [
    # API routes
    path('api/', include('apps.Payments.api.urls')),
] 