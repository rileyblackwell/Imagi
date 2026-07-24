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
    describe_router_contract_problems,
    describe_unresolved_imports,
    find_router_contract_problems,
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

    def _write_public(self, rel_path, content=''):
        path = os.path.join(self.root, 'frontend', 'vuejs', 'public', rel_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)
        return path

    def test_missing_template_image_is_reported(self):
        # Observed in a real first build: the agent wrote a hero <img> pointing
        # at an image file it could not create. Vite compiles a template src
        # into an import, so this renders broken and fails the production
        # build — exactly the class of dangling reference this gate exists for.
        self._write(
            'apps/home/views/HomeView.vue',
            '<template>\n'
            '  <img src="/images/coffee-hero.jpg" alt="Pouring coffee" />\n'
            '</template>\n',
        )
        self.assertEqual(self._imports(), [{
            'file': 'frontend/vuejs/src/apps/home/views/HomeView.vue',
            'import': '/images/coffee-hero.jpg',
        }])

    def test_template_image_present_in_public_resolves(self):
        self._write_public('images/hero.jpg', 'jpegbytes')
        self._write(
            'apps/home/views/HomeView.vue',
            '<template><img src="/images/hero.jpg" /></template>\n',
        )
        self.assertEqual(self._imports(), [])

    def test_relative_template_image_is_checked(self):
        self._write(
            'apps/home/views/HomeView.vue',
            '<template><img src="./logo.svg" /></template>\n',
        )
        self.assertEqual([p['import'] for p in self._imports()], ['./logo.svg'])

    def test_bound_src_expressions_are_skipped(self):
        # ':src' / 'v-bind:src' hold an expression, not a path — the value is
        # decided at runtime, so a static check must not judge it.
        self._write(
            'apps/home/views/HomeView.vue',
            '<template>\n'
            '  <img :src="product.imageUrl" />\n'
            '  <img v-bind:src="heroSrc" />\n'
            '</template>\n',
        )
        self.assertEqual(self._imports(), [])

    def test_remote_and_inline_sources_are_skipped(self):
        self._write(
            'apps/home/views/HomeView.vue',
            '<template>\n'
            '  <img src="https://cdn.example.com/a.jpg" />\n'
            '  <img src="//cdn.example.com/b.jpg" />\n'
            '  <img src="data:image/svg+xml;base64,PHN2Zz48L3N2Zz4=" />\n'
            '</template>\n',
        )
        self.assertEqual(self._imports(), [])

    def test_root_absolute_import_is_checked(self):
        self._write('apps/home/views/HomeView.vue', "import logo from '/logo.png'\n")
        self.assertEqual([p['import'] for p in self._imports()], ['/logo.png'])

    def test_scaffolded_app_router_is_accepted(self):
        self._write(
            'apps/home/router/index.ts',
            "import type { RouteRecordRaw } from 'vue-router'\n"
            "import HomeView from '../views/HomeView.vue'\n"
            "\n"
            "const routes: RouteRecordRaw[] = [\n"
            "  { path: '/', name: 'home-view', component: HomeView }\n"
            "]\n"
            "\n"
            "export { routes }\n",
        )
        self.assertEqual(find_router_contract_problems(self.root), [])

    def test_default_exported_route_array_is_accepted(self):
        # The root router takes an array from either export.
        self._write(
            'apps/home/router/index.ts',
            "import HomeView from '../views/HomeView.vue'\n"
            "export default [\n"
            "  { path: '/', component: HomeView }\n"
            "]\n",
        )
        self.assertEqual(find_router_contract_problems(self.root), [])

    def test_app_router_rewritten_as_a_real_router_is_reported(self):
        # Observed in a real first build. This compiles, type-checks, and passes
        # `vite build` — then vue-router silently resolves to zero routes, so
        # every page including home 404s. Nothing else catches it.
        self._write(
            'apps/home/router/index.ts',
            "import { createRouter, createWebHistory } from 'vue-router'\n"
            "import HomeView from '../views/HomeView.vue'\n"
            "\n"
            "const routes = [{ path: '/', component: HomeView }]\n"
            "const router = createRouter({ history: createWebHistory(), routes })\n"
            "export default router\n",
        )
        problems = find_router_contract_problems(self.root)
        self.assertEqual(
            [p['file'] for p in problems],
            ['frontend/vuejs/src/apps/home/router/index.ts'],
        )
        self.assertIn('createRouter', problems[0]['detail'])

    def test_app_router_without_a_routes_export_is_reported(self):
        self._write(
            'apps/home/router/index.ts',
            "import HomeView from '../views/HomeView.vue'\n"
            "const routes = [{ path: '/', component: HomeView }]\n",
        )
        problems = find_router_contract_problems(self.root)
        self.assertIn('does not export', problems[0]['detail'])

    def test_every_app_router_is_checked(self):
        self._write('apps/home/router/index.ts', "export { routes }\n")
        self._write(
            'apps/shop/router/index.ts',
            "import { createRouter } from 'vue-router'\n"
            "export default createRouter({ routes: [] })\n",
        )
        self.assertEqual(
            [p['file'] for p in find_router_contract_problems(self.root)],
            ['frontend/vuejs/src/apps/shop/router/index.ts'],
        )

    def test_project_without_apps_has_no_router_problems(self):
        self.assertEqual(find_router_contract_problems(self.root), [])

    def test_router_problem_description_names_the_file(self):
        described = describe_router_contract_problems(
            [{'file': 'apps/home/router/index.ts', 'detail': 'calls createRouter()'}]
        )
        self.assertIn('apps/home/router/index.ts', described)
        self.assertIn('createRouter', described)

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
