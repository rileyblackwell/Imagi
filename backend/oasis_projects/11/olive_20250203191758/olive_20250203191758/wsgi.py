"""
WSGI config for olive_20250203191758 project.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'olive_20250203191758.settings')
application = get_wsgi_application()
