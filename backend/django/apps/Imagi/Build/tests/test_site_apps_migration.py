"""
Tests for site_apps_migration: folding legacy one-page site apps into 'home'.

Projects scaffolded before the home app owned about/contact carry them as
apps of their own, which the workspace shows as a folder per page. This
migration merges them back — but only when the app still has the shape the
old scaffold gave it.
"""

import os
import shutil
import tempfile

from django.contrib.auth.models import User
from django.test import TestCase

from apps.Imagi.ProjectManager.models import Project as PMProject
from apps.Imagi.Build.models import ProjectFile
from apps.Imagi.Build.services.pages_service import list_app_pages
from apps.Imagi.Build.services.site_apps_migration import regroup_site_apps

APPS = 'frontend/vuejs/src/apps'

HOME_ROUTER = """import type { RouteRecordRaw } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home-view',
    component: HomeView,
    meta: { requiresAuth: false, title: 'Home' }
  }
]

export { routes }
"""

ABOUT_ROUTER = """import type { RouteRecordRaw } from 'vue-router'
import AboutView from '../views/AboutView.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/about',
    name: 'about-view',
    component: AboutView,
    meta: { requiresAuth: false, title: 'About' }
  }
]

export { routes }
"""


class SiteAppsMigrationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='regroupuser', password='testpass123')
        self.project_root = tempfile.mkdtemp(prefix='site_apps_')
        self.project = PMProject.objects.create(
            user=self.user, name='Regroup Project', project_path=self.project_root
        )
        self.addCleanup(lambda: shutil.rmtree(self.project_root, ignore_errors=True))

    def _write(self, rel_path, content):
        full = os.path.join(self.project_root, rel_path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, 'w', encoding='utf-8') as f:
            f.write(content)
        ProjectFile.objects.update_or_create(
            project=self.project, path=rel_path, defaults={'content': content}
        )

    def _read(self, rel_path):
        with open(os.path.join(self.project_root, rel_path), encoding='utf-8') as f:
            return f.read()

    def _legacy_layout(self):
        self._write(f'{APPS}/home/views/HomeView.vue', '<template><main>Home</main></template>')
        self._write(f'{APPS}/home/views/index.ts', "export { default as HomeView } from './HomeView.vue'\n")
        self._write(f'{APPS}/home/router/index.ts', HOME_ROUTER)
        self._write(f'{APPS}/about/views/AboutView.vue', '<template><main>About us</main></template>')
        self._write(f'{APPS}/about/views/index.ts', "export { default as AboutView } from './AboutView.vue'\n")
        self._write(f'{APPS}/about/router/index.ts', ABOUT_ROUTER)
        self._write(f'{APPS}/about/index.ts', "export * from './router'\n")

    def test_legacy_about_app_moves_into_home(self):
        self._legacy_layout()

        self.assertEqual(regroup_site_apps(self.project), ['about'])

        self.assertFalse(os.path.exists(os.path.join(self.project_root, APPS, 'about')))
        self.assertEqual(
            self._read(f'{APPS}/home/views/AboutView.vue'),
            '<template><main>About us</main></template>',
        )
        # One folder holding both pages is what the workspace menu reads from.
        apps = list_app_pages(self.project)
        self.assertEqual([a['name'] for a in apps], ['home'])
        self.assertEqual(
            [(p['title'], p['path']) for p in apps[0]['pages']],
            [('Home', '/'), ('About', '/about')],
        )

    def test_merged_router_keeps_the_route_intact(self):
        self._legacy_layout()

        regroup_site_apps(self.project)

        router = self._read(f'{APPS}/home/router/index.ts')
        self.assertIn("import AboutView from '../views/AboutView.vue'", router)
        self.assertIn("name: 'about-view'", router)
        self.assertIn("meta: { requiresAuth: false, title: 'About' }", router)
        self.assertIn(
            "export { default as AboutView } from './AboutView.vue'",
            self._read(f'{APPS}/home/views/index.ts'),
        )

    def test_database_mirror_follows_the_move(self):
        self._legacy_layout()

        regroup_site_apps(self.project)

        paths = set(ProjectFile.objects.filter(project=self.project).values_list('path', flat=True))
        self.assertIn(f'{APPS}/home/views/AboutView.vue', paths)
        self.assertFalse({p for p in paths if p.startswith(f'{APPS}/about/')})

    def test_running_twice_changes_nothing(self):
        self._legacy_layout()
        regroup_site_apps(self.project)
        router = self._read(f'{APPS}/home/router/index.ts')

        self.assertEqual(regroup_site_apps(self.project), [])
        self.assertEqual(self._read(f'{APPS}/home/router/index.ts'), router)

    def test_app_with_its_own_components_is_left_alone(self):
        # An agent has grown this past the scaffold's shape; moving its views
        # would leave the component behind and dangle the import.
        self._legacy_layout()
        self._write(f'{APPS}/about/components/TeamGrid.vue', '<template><div /></template>')

        self.assertEqual(regroup_site_apps(self.project), [])
        self.assertTrue(os.path.exists(os.path.join(self.project_root, APPS, 'about')))

    def test_router_importing_beyond_its_views_is_left_alone(self):
        self._legacy_layout()
        self._write(
            f'{APPS}/about/router/index.ts',
            ABOUT_ROUTER.replace(
                "import AboutView from '../views/AboutView.vue'",
                "import AboutView from '../views/AboutView.vue'\nimport { useAboutStore } from '../stores/about'",
            ),
        )

        self.assertEqual(regroup_site_apps(self.project), [])
        self.assertTrue(os.path.exists(os.path.join(self.project_root, APPS, 'about')))

    def test_colliding_view_name_is_left_alone(self):
        self._legacy_layout()
        self._write(f'{APPS}/home/views/AboutView.vue', '<template><main>Home already has one</main></template>')

        self.assertEqual(regroup_site_apps(self.project), [])
        self.assertTrue(os.path.exists(os.path.join(self.project_root, APPS, 'about')))

    def test_auth_and_prebuilt_apps_are_never_folded_in(self):
        self._legacy_layout()
        self._write(f'{APPS}/auth/views/SignInView.vue', '<template><main>Sign in</main></template>')
        self._write(f'{APPS}/auth/router/index.ts', ABOUT_ROUTER.replace('About', 'SignIn').replace('/about', '/auth/signin'))

        regroup_site_apps(self.project)

        self.assertTrue(os.path.exists(os.path.join(self.project_root, APPS, 'auth')))

    def test_view_reaching_into_its_own_app_is_left_alone(self):
        self._legacy_layout()
        self._write(
            f'{APPS}/about/views/AboutView.vue',
            "<script setup lang=\"ts\">\nimport { useAboutStore } from '../stores/about'\n</script>",
        )

        self.assertEqual(regroup_site_apps(self.project), [])
        self.assertTrue(os.path.exists(os.path.join(self.project_root, APPS, 'about')))
