"""
WSGI config for doji_art_20250203190631 project.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doji_art_20250203190631.settings')
application = get_wsgi_application()
