"""
URL configuration for Auth app.
Includes all authentication-related URLs, including password reset views.
"""

from django.urls import path, include
from django.contrib.auth import views as auth_views

app_name = 'auth'

urlpatterns = [
    # API endpoints
    path('api/', include('apps.Auth.api.urls')),
    
    # Password reset views
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
