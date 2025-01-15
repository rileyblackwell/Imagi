from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # CSRF endpoint
    path('api/auth/csrf/', views.get_csrf_token, name='get_csrf_token'),
    
    # API endpoints
    path('api/auth/register/', views.register_user, name='api_register'),
    path('api/auth/login/', views.login_user, name='api_login'),
    path('api/auth/logout/', views.logout_user, name='api_logout'),
    path('api/auth/user/', views.get_user, name='api_get_user'),
    path('api/auth/change-password/', views.change_password, name='api_change_password'),
    path('api/auth/reset-password/', views.request_password_reset, name='api_request_password_reset'),
    path('api/auth/reset-password/confirm/', views.password_reset_confirm, name='api_password_reset_confirm'),
    
    # Traditional form-based auth endpoints
    path('register/', views.signup_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Password reset URLs
    path('password_reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='auth/password_reset.html',
             email_template_name='auth/password_reset_email.html',
             subject_template_name='auth/password_reset_subject.txt'
         ),
         name='password_reset'),
    path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='auth/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='auth/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='auth/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]
