"""
ASGI config for nova_amor_20250203185543 project.
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nova_amor_20250203185543.settings')
application = get_asgi_application()
