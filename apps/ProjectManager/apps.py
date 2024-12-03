from django.apps import AppConfig
import os
from django.conf import settings


class ProjectManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ProjectManager'

    def ready(self):
        # Ensure projects directory exists
        os.makedirs(settings.PROJECTS_ROOT, exist_ok=True)
