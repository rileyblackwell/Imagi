from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.views.decorators.http import require_GET

@require_GET
def favicon_view(request):
    return HttpResponse(status=204)

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin interface
    path('builder/', include('apps.Builder.urls')),  # Builder app URLs
    path('auth/', include('apps.Auth.urls')),  # Auth app URLs
    path('', include('apps.Home.urls')),  # Home app URLs
    path('payments/', include('apps.Payments.urls')),  # Payments app URLs
    path('favicon.ico', favicon_view),
]
