from django.urls import path
from . import views

urlpatterns = [
    # CSRF Token
    path('csrf/', views.CSRFTokenView.as_view(), name='api-csrf-token'),
    
    # Authentication
    path('register/', views.RegisterView.as_view(), name='api-register'),
    path('login/', views.LoginView.as_view(), name='api-login'),
    path('logout/', views.LogoutView.as_view(), name='api-logout'),
    
    # User Management
    path('me/', views.UserDetailView.as_view(), name='api-user-detail'),
    path('change-password/', views.ChangePasswordView.as_view(), name='api-change-password'),
    
    # Password Reset
    path('password/reset/', views.PasswordResetRequestView.as_view(), name='api-password-reset-request'),
    path('password/reset/confirm/', views.PasswordResetConfirmView.as_view(), name='api-password-reset-confirm'),
]
