"""
WSGI config for nova_amor_20250203185748 project.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nova_amor_20250203185748.settings')
application = get_wsgi_application()
