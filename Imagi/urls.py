from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin interface
    path('builder/', include('apps.Builder.urls')),  # Builder app URLs
    path('', include('apps.Home.urls')),  # Home app URLs (including the landing page)
]
