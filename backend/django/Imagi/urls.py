from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.views.decorators.http import require_GET
from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

@require_GET
def favicon_view(request):
    return HttpResponse(status=204)

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include('api.urls')),
    
    # App URLs
    path('builder/', include('apps.Builder.urls')),  # Builder app URLs
    path('auth/', include('apps.Auth.urls')),  # Auth app URLs
    path('', include('apps.Home.urls')),  # Home app URLs
    path('payments/', include('apps.Payments.urls')),  # Payments app URLs
    path('agents/', include('apps.Agents.urls')),  # Agents app URLs
    
    # Authentication views
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    # Favicon
    path('favicon.ico', favicon_view),
]

# Add CORS headers to all responses
from django.conf import settings
if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
    ]
