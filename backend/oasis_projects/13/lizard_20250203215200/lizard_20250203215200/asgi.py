"""
ASGI config for lizard_20250203215200 project.
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lizard_20250203215200.settings')
application = get_asgi_application()
