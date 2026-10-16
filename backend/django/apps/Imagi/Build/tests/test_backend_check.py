"""
Threads check a project's Django backend before trying it (backend_check).
"""

import json
import os
import shutil
import tempfile
from unittest.mock import patch

from django.core.management import call_command
from django.test import SimpleTestCase, TransactionTestCase

from apps.Imagi.Build.services import backend_check, live_apply
from apps.Imagi.Build.tests.test_live_apply import LiveApplyRepoMixin

SHOP_MODELS = """from django.db import models


class Order(models.Model):
    name = models.CharField(max_length=100)
"""


class BackendCheckTests(SimpleTestCase):
    """A project shaped like the ones Imagi creates: backend/django holding a
    Django project and its apps under apps/."""

    def setUp(self):
        self.root = tempfile.mkdtemp(prefix='imagi-check-test-')
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        self.backend = os.path.join(self.root, 'backend', 'django')
        os.makedirs(self.backend)
        call_command('startproject', 'site_20261016', self.backend)
        self._write('apps/__init__.py', '')
        self._write('apps/shop/__init__.py', '')
        self._write('apps/shop/migrations/__init__.py', '')
        self._write('apps/shop/apps.py', (
            "from django.apps import AppConfig\n\n\n"
            "class ShopConfig(AppConfig):\n"
            "    name = 'apps.shop'\n"
            "    default_auto_field = 'django.db.models.BigAutoField'\n"
        ))
        self._write('apps/shop/models.py', SHOP_MODELS)
        settings_path = os.path.join(self.backend, 'site_20261016', 'settings.py')
        with open(settings_path) as f:
            settings = f.read()
        with open(settings_path, 'w') as f:
            f.write(settings.replace(
                '"django.contrib.staticfiles",',
                '"django.contrib.staticfiles",\n    "apps.shop",',
            ))

    def _write(self, relative, content):
        path = os.path.join(self.backend, relative)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)

    def test_makes_the_migrations_then_checks_and_applies_them_to_a_scratch_database(self):
        result = backend_check.check_backend(self.root)

        self.assertTrue(result['ok'], result)
        self.assertEqual(
            [step['command'] for step in result['steps']],
            ['manage.py makemigrations --noinput', 'manage.py check', 'manage.py migrate --noinput'],
        )
        self.assertEqual(
            result['new_migrations'], ['backend/django/apps/shop/migrations/0001_initial.py']
        )
        self.assertTrue(os.path.isfile(
            os.path.join(self.backend, 'apps', 'shop', 'migrations', '0001_initial.py')
        ))
        self.assertIn('Every migration applies', result['steps'][2]['output'])
        # The project's own database is never created or touched.
        self.assertFalse(os.path.exists(os.path.join(self.backend, 'db.sqlite3')))

    def test_a_model_change_django_cannot_migrate_by_itself_comes_back_to_fix(self):
        self.assertTrue(backend_check.check_backend(self.root)['ok'])
        self._write('apps/shop/models.py', SHOP_MODELS + (
            "    total = models.DecimalField(max_digits=8, decimal_places=2)\n"
        ))

        result = backend_check.check_backend(self.root)

        self.assertFalse(result['ok'])
        self.assertEqual(len(result['steps']), 1)
        self.assertIn('non-nullable', result['steps'][0]['output'])
        self.assertEqual(result['new_migrations'], [])

    def test_a_broken_url_is_reported_with_its_error(self):
        with open(os.path.join(self.backend, 'site_20261016', 'urls.py'), 'a') as f:
            f.write("\nfrom django.urls import include\nurlpatterns += [path('shop/', include('apps.shop.api.urls'))]\n")

        result = backend_check.check_backend(self.root)

        self.assertFalse(result['ok'])
        self.assertIn("No module named 'apps.shop.api'", result['steps'][-1]['output'])

    def test_a_project_without_a_backend_says_so(self):
        result = backend_check.check_backend(tempfile.gettempdir())
        self.assertFalse(result['ok'])
        self.assertIn('manage.py', result['error'])


class CheckBackendToolTests(LiveApplyRepoMixin, TransactionTestCase):
    """The tool a thread calls: the migrations Django writes reach the app the
    preview serves, like any file the thread writes."""

    def setUp(self):
        super().setUp()
        from django.contrib.auth.models import User
        from apps.Imagi.Build.services.base_agent import AgentContext
        from apps.Imagi.ProjectManager.models import Project

        user = User.objects.create_user(username='checker', password='pw123456')
        project = Project.objects.create(user=user, name='P', project_path=self.repo, is_active=True)
        self.ctx = AgentContext(
            user_id=user.id, project_id=project.id, conversation_id=5,
            project_path=self.repo, effective_project_path=self.worktree, live_apply=True,
        )

    def test_new_migrations_reach_the_app_and_are_applied_there(self):
        import asyncio
        from agents.tool_context import ToolContext
        from apps.Imagi.Build.services import live_preview_service, tools

        migration = 'backend/django/apps/shop/migrations/0001_initial.py'

        def fake_check(root):
            self.assertEqual(root, self.worktree)
            self._write(root, migration, '# made by Django')
            return {'ok': True, 'steps': [], 'new_migrations': [migration], 'changed_migrations': []}

        with patch.object(backend_check, 'check_backend', fake_check), \
                patch.object(live_preview_service, 'schedule_migrate') as migrate:
            result = json.loads(asyncio.run(tools.check_backend.on_invoke_tool(
                ToolContext(context=self.ctx, tool_name='check_backend', tool_call_id='1',
                            tool_arguments='{}'),
                '{}',
            )))

        self.assertTrue(result['ok'], result)
        self.assertEqual(self._read(self.repo, migration), '# made by Django')
        migrate.assert_called_once()

    def test_threads_have_the_tool(self):
        from apps.Imagi.Build.services.tools import CODING_AGENT_TOOLS

        self.assertIn('check_backend', [t.name for t in CODING_AGENT_TOOLS])
