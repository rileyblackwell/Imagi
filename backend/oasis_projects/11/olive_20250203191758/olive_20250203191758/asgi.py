"""
ASGI config for olive_20250203191758 project.
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'olive_20250203191758.settings')
application = get_asgi_application()
