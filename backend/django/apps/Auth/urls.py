from django.urls import path, include

app_name = 'auth'

urlpatterns = [
    # API endpoints
    path('api/v1/auth/', include(('apps.Auth.api.urls', 'auth_api'))),
]
