"""
ASGI config for dog_20250203203036 project.
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dog_20250203203036.settings')
application = get_asgi_application()
