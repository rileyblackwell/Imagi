from django.apps import AppConfig


class AuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.auth'
    # Explicit label: the default ('auth') collides with django.contrib.auth
    label = 'user_auth'
