"""
Tests for the frontend import-integrity check.

The check gates what reaches the tree the preview serves, so both directions
matter: it must catch a reference to a file that was never written, and it
must never flag a project that is actually fine — a false positive would
discard a perfectly good build.
"""

import os
import shutil
import tempfile

from django.test import TestCase

from apps.Imagi.Build.services.frontend_integrity import (
    describe_unresolved_imports,
    find_unresolved_imports,
)


class FrontendIntegrityTests(TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix='imagi-integrity-')
        self.src = os.path.join(self.root, 'frontend', 'vuejs', 'src')
        os.makedirs(self.src)
        self.addCleanup(shutil.rmtree, self.root, True)

    def _write(self, rel_path, content):
        path = os.path.join(self.src, rel_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)
        return path

    def _imports(self):
        return find_unresolved_imports(self.root)

    def test_no_frontend_is_not_a_problem(self):
        self.assertEqual(find_unresolved_imports(tempfile.mkdtemp()), [])

    def test_missing_aliased_file_is_reported(self):
        self._write(
            'apps/home/views/HomeView.vue',
            "<script setup lang=\"ts\">\n"
            "import SiteHeader from '@/shared/components/SiteHeader.vue'\n"
            "</script>\n",
        )
        self.assertEqual(self._imports(), [{
            'file': 'frontend/vuejs/src/apps/home/views/HomeView.vue',
            'import': '@/shared/components/SiteHeader.vue',
        }])

    def test_missing_relative_file_is_reported(self):
        self._write('apps/home/views/HomeView.vue', "import X from './Missing.vue'\n")
        self.assertEqual(
            [p['import'] for p in self._imports()], ['./Missing.vue']
        )

    def test_missing_lazy_route_component_is_reported(self):
        # The most common shape a cut-short build leaves behind: a route
        # pointing at a page the agent never got around to writing.
        self._write(
            'apps/home/router/index.ts',
            "const routes = [\n"
            "  { path: '/pricing', component: () => import('../views/Pricing.vue') },\n"
            "]\n",
        )
        self.assertEqual(
            [p['import'] for p in self._imports()], ['../views/Pricing.vue']
        )

    def test_resolved_imports_are_not_reported(self):
        self._write('shared/components/SiteHeader.vue', '<template><header /></template>\n')
        self._write('apps/home/views/Pricing.vue', '<template><div /></template>\n')
        self._write('apps/home/stores/index.ts', "export const useHome = () => {}\n")
        self._write('assets/css/main.css', 'body { margin: 0; }\n')
        self._write(
            'apps/home/views/HomeView.vue',
            "<script setup lang=\"ts\">\n"
            "import SiteHeader from '@/shared/components/SiteHeader.vue'\n"
            "import { useHome } from '../stores'\n"  # directory -> index.ts
            "const Pricing = () => import('./Pricing.vue')\n"
            "</script>\n",
        )
        self._write('main.ts', "import './assets/css/main.css'\n")
        self.assertEqual(self._imports(), [])

    def test_package_imports_are_ignored(self):
        # npm packages live in the shared dependency store, not the project.
        self._write(
            'main.ts',
            "import { createApp } from 'vue'\n"
            "import axios from 'axios'\n"
            "import { faUser } from '@fortawesome/free-solid-svg-icons'\n",
        )
        self.assertEqual(self._imports(), [])

    def test_extensionless_and_index_imports_resolve(self):
        self._write('shared/services/api.ts', 'export default {}\n')
        self._write('shared/stores/index.ts', 'export const s = 1\n')
        self._write(
            'apps/home/views/HomeView.vue',
            "import api from '@/shared/services/api'\n"
            "import { s } from '@/shared/stores'\n",
        )
        self.assertEqual(self._imports(), [])

    def test_css_at_import_is_not_treated_as_a_module_import(self):
        self._write(
            'apps/home/views/HomeView.vue',
            "<style>\n@import './nowhere.css';\n</style>\n",
        )
        self.assertEqual(self._imports(), [])

    def test_dynamic_specifiers_are_skipped(self):
        # A runtime-built path can't be checked statically; reporting it would
        # discard a build over something that may well be fine.
        self._write(
            'apps/home/views/HomeView.vue',
            "const load = (n) => import(`../views/${n}.vue`)\n",
        )
        self.assertEqual(self._imports(), [])

    def test_node_modules_is_not_scanned(self):
        self._write('../node_modules/pkg/index.js', "import x from './missing.js'\n")
        self.assertEqual(self._imports(), [])

    def test_each_broken_specifier_is_reported_once_per_file(self):
        self._write(
            'apps/home/views/HomeView.vue',
            "import A from './Missing.vue'\n"
            "import B from './Missing.vue'\n",
        )
        self.assertEqual(len(self._imports()), 1)

    def test_description_lists_every_problem(self):
        problems = [
            {'file': 'a.vue', 'import': './x.vue'},
            {'file': 'b.vue', 'import': '@/y.vue'},
        ]
        described = describe_unresolved_imports(problems)
        self.assertIn('a.vue', described)
        self.assertIn('./x.vue', described)
        self.assertIn('@/y.vue', described)

    def test_description_truncates_a_badly_broken_tree(self):
        problems = [{'file': f'{i}.vue', 'import': './x.vue'} for i in range(40)]
        described = describe_unresolved_imports(problems)
        self.assertIn('and 15 more', described)
