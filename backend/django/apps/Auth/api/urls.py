from django.urls import path

from .views import (
    csrf_view,
    init_view,
    logout_view,
    register_view,
    signin_view,
    user_update_view,
)

app_name = 'auth_api'

urlpatterns = [
    path('csrf/', csrf_view, name='csrf'),
    path('signin/', signin_view, name='signin'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('init/', init_view, name='init'),
    path('user/', user_update_view, name='user-update'),
]
