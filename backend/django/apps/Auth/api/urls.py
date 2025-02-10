from django.urls import path
from . import views

app_name = 'auth_api'

urlpatterns = [
    # CSRF and Health Check
    path('csrf/', views.CSRFTokenView.as_view(), name='csrf-token'),
    path('health/', views.health_check, name='health-check'),
    
    # Session initialization
    path('init/', views.InitView.as_view(), name='init'),
    
    # Core Authentication
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # User Management
    path('user/', views.UserDetailView.as_view(), name='user-detail'),
]
