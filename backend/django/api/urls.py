from django.urls import include, path

urlpatterns = [
    path('home/', include('apps.Home.api.urls')),
    path('auth/', include('apps.Auth.api.urls')),
]
