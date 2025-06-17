from django.urls import path
from . import views

app_name = 'auth_api'

urlpatterns = [
    # Health Check and Debugging
    path('health/', views.HealthCheckView.as_view(), name='health-check'),
    
    # CSRF and Authentication
    path('csrf/', views.CSRFTokenView.as_view(), name='csrf-token'),
    path('init/', views.InitView.as_view(), name='init'),
    
    # Authentication endpoints
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    
    # User management
    path('user/', views.UserView.as_view(), name='user'),
]
