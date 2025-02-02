from django.urls import path, include

app_name = 'auth'

urlpatterns = [
    # All routes are API routes, handled by the api/ directory
    path('', include('apps.Auth.api.urls')),
]
