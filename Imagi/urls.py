from django.contrib import admin
from django.urls import path, include
from apps.Auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin interface
    path('builder/', include('apps.Builder.urls')),  # Builder app URLs
    path('auth/', include('apps.Auth.urls')),  # Auth app URLs
    path('login/', auth_views.login_view, name='login'),  # Login URL
    path('signup/', auth_views.signup_view, name='signup'),  # Add this line for signup URL
    path('', include('apps.Home.urls')),  # Home app URLs (including the landing page)
]
