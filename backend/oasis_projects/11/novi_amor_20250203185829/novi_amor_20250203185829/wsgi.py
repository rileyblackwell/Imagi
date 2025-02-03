"""
WSGI config for novi_amor_20250203185829 project.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'novi_amor_20250203185829.settings')
application = get_wsgi_application()
