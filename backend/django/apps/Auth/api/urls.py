from django.urls import path
from . import views

app_name = 'auth_api'

urlpatterns = [
    # Add CSRF endpoint
    path('csrf/', views.CSRFTokenView.as_view(), name='csrf-token'),
    
    # Add health check endpoint
    path('health/', views.health_check, name='health-check'),
    
    # Session initialization
    path('init/', views.InitView.as_view(), name='init'),
    
    # Authentication
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # User Management
    path('user/', views.UserDetailView.as_view(), name='user-detail'),
    path('user/password/', views.ChangePasswordView.as_view(), name='change-password'),
    
    # Password Reset
    path('password/reset/', views.PasswordResetRequestView.as_view(), name='password-reset'),
    path('password/reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    
    # Email Verification handled by allauth directly
]
