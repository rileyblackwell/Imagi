"""
Tests for pages_service: the app/page tree behind the workspace preview's
nameplate and its folder menu.

The nameplate reads "folder/page" — the app directory a page lives in, then
the page's own route segment — so what this service groups is exactly what the
user sees at the top of their preview.
"""

import os
import shutil
import tempfile

from django.contrib.auth.models import User
from django.test import TestCase

from apps.Imagi.ProjectManager.models import Project as PMProject
from apps.Imagi.Build.services.codegen.prebuilt_apps import home_app_files
from apps.Imagi.Build.services.pages_service import list_app_pages


class PagesServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='pageuser', password='testpass123')
        self.project_root = tempfile.mkdtemp(prefix='pages_service_')
        self.project = PMProject.objects.create(
            user=self.user, name='Pages Project', project_path=self.project_root
        )
        self.addCleanup(lambda: shutil.rmtree(self.project_root, ignore_errors=True))

    def _write(self, rel_path, content):
        full = os.path.join(self.project_root, rel_path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, 'w', encoding='utf-8') as f:
            f.write(content)

    def _scaffold_home(self):
        for f in home_app_files():
            self._write(f['name'], f['content'])

    def test_home_app_carries_all_three_public_pages(self):
        # One folder, three pages: what makes the nameplate read 'home/about'
        # rather than an 'about' folder holding a single page.
        self._scaffold_home()

        apps = list_app_pages(self.project)

        self.assertEqual([a['name'] for a in apps], ['home'])
        self.assertEqual(
            [(p['title'], p['path']) for p in apps[0]['pages']],
            [('Home', '/'), ('About', '/about'), ('Contact', '/contact')],
        )

    def test_apps_without_a_router_are_skipped(self):
        self._scaffold_home()
        self._write('frontend/vuejs/src/apps/scratch/views/ScratchView.vue', '<template />')

        self.assertEqual([a['name'] for a in list_app_pages(self.project)], ['home'])

    def test_missing_apps_directory_yields_nothing(self):
        self.assertEqual(list_app_pages(self.project), [])
