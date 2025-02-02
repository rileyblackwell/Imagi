from django.urls import path, include

urlpatterns = [
    # API v1 endpoints
    path('v1/', include('api.v1.urls')),
]
