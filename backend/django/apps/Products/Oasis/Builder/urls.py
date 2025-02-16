"""
URL configuration for the Builder app.
All routes are handled by the API.
"""
from django.urls import path, include

app_name = 'builder'

urlpatterns = [
    # All routes are API routes
    path('api/', include('apps.Products.Oasis.Builder.api.urls')),
]
