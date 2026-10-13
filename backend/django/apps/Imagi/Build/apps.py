import os
import sys
import threading

from django.apps import AppConfig


class BuildConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.Imagi.Build'
    label = 'Build'

    def ready(self):
        # The first project created after a deploy used to wait seconds on
        # the agent stack's imports. A server imports them as it starts
        # instead, off the request path; management commands and tests skip it.
        if os.path.basename(sys.argv[0] if sys.argv else '') == 'manage.py':
            return
        threading.Thread(target=_warm_agent_imports, name='warm-imports', daemon=True).start()


def _warm_agent_imports():
    try:
        from .services import base_agent, coding_agent, head_start  # noqa: F401
        from apps.Imagi.ProjectManager.services import quick_home  # noqa: F401
    except Exception:  # pragma: no cover - only ever a head start
        pass
