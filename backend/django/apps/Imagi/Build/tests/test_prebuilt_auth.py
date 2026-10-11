"""
Tests for the prebuilt auth every generated project ships with.

Three promises are pinned here:

* The template's sign-in flow is Imagi's own auth, file for file, so a fix to
  Imagi's auth reaches new projects in the same change (the parity tests).
* The pages' look lives entirely in one stylesheet, so a restyle never needs
  to touch the markup or the flow (the stylesheet contract).
* The build agents cannot change the flow, only the stylesheet and the copy
  (protected paths and the file tools).

The end-to-end check, the template's own suite passing inside a freshly
generated project, is ScaffoldWiringTests in ProjectManager's tests.
"""

import ast
import json
import os
import re
import shutil
import tempfile
from unittest import skipUnless
from unittest.mock import patch

from asgiref.sync import async_to_sync
from django.conf import settings
from django.contrib.auth.models import User
from django.test import SimpleTestCase, TransactionTestCase

from apps.Imagi.Build.services.codegen.prebuilt_apps import generate_prebuilt_app_files
from apps.Imagi.Build.services.codegen.prebuilt_apps.auth import (
    auth_app_files,
    template_files,
)
from apps.Imagi.Build.services.protected_paths import (
    AUTH_RESTYLE_PATHS,
    is_protected_directory,
    is_protected_path,
)

BACKEND_ROOT = settings.BASE_DIR
REPO_ROOT = os.path.dirname(os.path.dirname(BACKEND_ROOT))
IMAGI_FRONTEND_AUTH = os.path.join(REPO_ROOT, 'frontend', 'vuejs', 'src', 'apps', 'auth')
IMAGI_BACKEND_AUTH = os.path.join(BACKEND_ROOT, 'apps', 'Auth')

TEMPLATE_FRONTEND = 'frontend/vuejs/src/apps/auth/'
TEMPLATE_BACKEND = 'backend/django/apps/auth/'

# The flow itself: copies of Imagi's auth module, kept identical.
SHARED_FRONTEND_FILES = (
    'index.ts',
    'types/auth.ts',
    'types/form.ts',
    'plugins/validation.ts',
    'services/api.ts',
    'stores/index.ts',
    'composables/useAuth.ts',
    'composables/useSignInForm.ts',
    'composables/useRegisterForm.ts',
    'utils/redirect.ts',
)
SHARED_BACKEND_FILES = (
    'api/serializers.py',
    'api/views.py',
    'api/throttles.py',
    'api/urls.py',
)


def _read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def _test_methods(source):
    """{TestCase class name: sorted test method names} for a tests module."""
    found = {}
    for node in ast.parse(source).body:
        if isinstance(node, ast.ClassDef) and node.name.endswith('Tests'):
            found[node.name] = sorted(
                n.name for n in node.body
                if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')
            )
    return found


class TemplateParityTests(SimpleTestCase):
    """The template's flow is Imagi's auth, byte for byte."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.files = template_files()

    @skipUnless(os.path.isdir(IMAGI_FRONTEND_AUTH), 'needs the full repository checkout')
    def test_frontend_flow_files_match_imagi(self):
        for rel in SHARED_FRONTEND_FILES:
            with self.subTest(file=rel):
                self.assertEqual(
                    self.files[TEMPLATE_FRONTEND + rel],
                    _read(os.path.join(IMAGI_FRONTEND_AUTH, rel)),
                    f'{rel} drifted from Imagi; copy the change into the template',
                )

    def test_backend_api_files_match_imagi(self):
        for rel in SHARED_BACKEND_FILES:
            with self.subTest(file=rel):
                self.assertEqual(
                    self.files[TEMPLATE_BACKEND + rel],
                    _read(os.path.join(IMAGI_BACKEND_AUTH, rel)),
                    f'{rel} drifted from Imagi; copy the change into the template',
                )

    def test_backend_tests_cover_what_imagi_tests(self):
        # The template's suite is Imagi's, minus the dev-account command that
        # only Imagi has.
        imagi = _test_methods(_read(os.path.join(IMAGI_BACKEND_AUTH, 'tests.py')))
        imagi.pop('SeedDevUserCommandTests')
        template = _test_methods(self.files[TEMPLATE_BACKEND + 'tests.py'])
        self.assertEqual(template, imagi)

    def test_template_tests_target_the_generated_app(self):
        tests = self.files[TEMPLATE_BACKEND + 'tests.py']
        self.assertNotIn('apps.Auth', tests)
        self.assertIn('from apps.auth.api', tests)

    def test_the_app_label_does_not_collide_with_django_auth(self):
        apps_py = self.files[TEMPLATE_BACKEND + 'apps.py']
        self.assertIn("name = 'apps.auth'", apps_py)
        self.assertIn("label = 'user_auth'", apps_py)
        self.assertIn(TEMPLATE_BACKEND + 'migrations/__init__.py', self.files)


class TemplateOutputTests(SimpleTestCase):
    """What auth_app_files hands the scaffold."""

    def test_every_template_file_is_generated(self):
        generated = {f['name'] for f in auth_app_files('Beanline')}
        self.assertEqual(generated, set(template_files()))

    def test_the_business_name_is_stamped_as_a_safe_string_literal(self):
        files = {f['name']: f['content'] for f in auth_app_files("Joe's \"Best\" Pizza")}
        brand = files[TEMPLATE_FRONTEND + 'brand.ts']
        self.assertIn('name: "Joe\'s \\"Best\\" Pizza"', brand)
        self.assertNotIn('__BUSINESS_NAME__', brand)

    def test_a_missing_name_falls_back_to_a_neutral_one(self):
        files = {f['name']: f['content'] for f in auth_app_files(None)}
        self.assertIn('name: "Your Business"', files[TEMPLATE_FRONTEND + 'brand.ts'])

    def test_the_prebuilt_map_passes_the_project_name_through(self):
        files = {f['name']: f['content'] for f in generate_prebuilt_app_files('auth', None, 'Beanline')}
        self.assertIn('"Beanline"', files[TEMPLATE_FRONTEND + 'brand.ts'])

    def test_no_imagi_branding_or_design_tokens_leak_into_projects(self):
        for path, content in template_files().items():
            if not path.endswith(('.vue', '.css')):
                continue
            with self.subTest(file=path):
                # Comments may say who maintains the file; the pages may not.
                if path.endswith('.vue'):
                    self.assertFalse('Imagi' in content.split('<script', 1)[0])
                for leak in ('--sl-', '@/shared/styles', '@/shared/components', 'ImagiLogo'):
                    self.assertFalse(leak in content, leak)


class StylesheetContractTests(SimpleTestCase):
    """Every look-and-feel decision is in styles/auth.css.

    A restyle rewrites that file alone, so the markup may only use classes it
    defines (plus Tailwind's sr-only), and no inline styles or utility classes
    that the stylesheet cannot reach.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        files = template_files()
        cls.css = files[TEMPLATE_FRONTEND + 'styles/auth.css']
        cls.markup = {
            path: content for path, content in files.items()
            if path.startswith(TEMPLATE_FRONTEND) and path.endswith('.vue')
        }

    def test_markup_uses_only_classes_the_stylesheet_defines(self):
        defined = set(re.findall(r'\.(auth-[a-z0-9-]+)', self.css))
        for path, content in self.markup.items():
            template = content.split('<script', 1)[0]
            used = set()
            for attr in re.findall(r'\sclass="([^"]*)"', template):
                used.update(attr.split())
            for expr in re.findall(r":class=\"([^\"]*)\"", template):
                used.update(re.findall(r"'(auth-[a-z0-9-]+)'", expr))
            with self.subTest(file=path):
                self.assertEqual(used - defined - {'sr-only'}, set())

    def test_markup_has_no_inline_or_scoped_styles(self):
        for path, content in self.markup.items():
            with self.subTest(file=path):
                self.assertNotIn(' style="', content)
                self.assertNotIn('<style', content)

    def test_the_layout_loads_the_stylesheet(self):
        layout = self.markup[TEMPLATE_FRONTEND + 'layouts/AuthLayout.vue']
        self.assertIn("import '../styles/auth.css'", layout)

    def test_the_restyle_paths_are_real_template_files(self):
        for path in AUTH_RESTYLE_PATHS:
            self.assertIn(path, template_files())


class ProtectedPathTests(SimpleTestCase):
    def test_every_template_file_but_the_look_is_protected(self):
        for path in template_files():
            with self.subTest(path=path):
                self.assertEqual(is_protected_path(path), path not in AUTH_RESTYLE_PATHS)

    def test_the_shared_auth_plumbing_is_protected(self):
        self.assertTrue(is_protected_path('frontend/vuejs/src/shared/stores/auth.ts'))
        self.assertTrue(is_protected_path('frontend/vuejs/src/shared/services/api.ts'))

    def test_new_files_inside_auth_are_protected_too(self):
        self.assertTrue(is_protected_path('frontend/vuejs/src/apps/auth/views/Bypass.vue'))
        self.assertTrue(is_protected_path('backend/django/apps/auth/api/backdoor.py'))

    def test_path_tricks_do_not_get_past(self):
        for path in (
            '/frontend/vuejs/src/apps/auth/services/api.ts',
            'frontend/vuejs/src/apps/home/../auth/services/api.ts',
            'frontend\\vuejs\\src\\apps\\auth\\services\\api.ts',
            'Frontend/VueJS/src/apps/Auth/services/api.ts',
            'backend/django/apps/auth/./api/views.py',
        ):
            with self.subTest(path=path):
                self.assertTrue(is_protected_path(path))

    def test_other_project_files_are_open(self):
        for path in (
            'frontend/vuejs/src/apps/home/views/HomeView.vue',
            'frontend/vuejs/src/apps/authors/views/Index.vue',
            'frontend/vuejs/src/shared/stores/cart.ts',
            'backend/django/apps/authors/models.py',
        ):
            with self.subTest(path=path):
                self.assertFalse(is_protected_path(path))

    def test_directories_holding_auth_cannot_be_deleted(self):
        for path in (
            'frontend/vuejs/src/apps/auth',
            'frontend/vuejs/src/apps/auth/styles',
            'frontend/vuejs/src/apps',
            'backend/django/apps',
            'frontend',
            '',
        ):
            with self.subTest(path=path):
                self.assertTrue(is_protected_directory(path))
        self.assertFalse(is_protected_directory('frontend/vuejs/src/apps/home'))


class ProtectedToolTests(TransactionTestCase):
    """The file tools refuse the prebuilt auth, invoked as the SDK invokes them."""

    def setUp(self):
        from apps.Imagi.ProjectManager.models import Project

        self.root = tempfile.mkdtemp(prefix='prebuilt_auth_tools_')
        self.addCleanup(lambda: shutil.rmtree(self.root, ignore_errors=True))
        self.user = User.objects.create_user(username='guarded', password='testpass123')
        self.project = Project.objects.create(
            user=self.user, name='Guarded', project_path=self.root
        )
        for f in auth_app_files('Guarded'):
            full = os.path.join(self.root, f['name'])
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, 'w', encoding='utf-8') as out:
                out.write(f['content'])
        self.api_ts = 'frontend/vuejs/src/apps/auth/services/api.ts'
        self.original = _read(os.path.join(self.root, self.api_ts))

    def _invoke(self, tool, **args):
        from agents.tool_context import ToolContext
        from apps.Imagi.Build.services.base_agent import AgentContext

        context = AgentContext(
            user_id=self.user.id, project_id=self.project.id, project_path=self.root
        )
        tool_ctx = ToolContext(
            context=context, tool_name=tool.name, tool_call_id='call_1',
            tool_arguments=json.dumps(args),
        )
        return json.loads(async_to_sync(tool.on_invoke_tool)(tool_ctx, json.dumps(args)))

    def _assert_refused(self, result):
        self.assertFalse(result['success'], result)
        self.assertIn('prebuilt sign-in', result['error'])
        # The refusal points at the way to restyle instead.
        self.assertIn('styles/auth.css', result['error'])

    def test_writes_to_the_flow_are_refused_and_leave_it_untouched(self):
        from apps.Imagi.Build.services.tools import (
            create_file, delete_directory, delete_file, edit_file, update_file,
        )

        self._assert_refused(self._invoke(
            edit_file, file_path=self.api_ts, old_string='API_PATH', new_string='X',
        ))
        self._assert_refused(self._invoke(update_file, file_path=self.api_ts, content='x'))
        self._assert_refused(self._invoke(delete_file, file_path=self.api_ts))
        self._assert_refused(self._invoke(
            create_file, file_path='backend/django/apps/auth/api/extra.py', content='x',
        ))
        self._assert_refused(self._invoke(delete_directory, dir_path='frontend/vuejs/src/apps'))

        self.assertEqual(_read(os.path.join(self.root, self.api_ts)), self.original)
        self.assertFalse(os.path.exists(
            os.path.join(self.root, 'backend/django/apps/auth/api/extra.py')
        ))

    def test_the_stylesheet_and_copy_stay_writable(self):
        from apps.Imagi.Build.services.tools import edit_file, update_file

        css, brand = AUTH_RESTYLE_PATHS
        result = self._invoke(update_file, file_path=css, content='.auth-theme { --auth-bg: #000; }\n')
        self.assertTrue(result['success'], result)
        result = self._invoke(
            edit_file, file_path=brand, old_string='Welcome back', new_string='Good to see you',
        )
        self.assertTrue(result['success'], result)
        self.assertIn('Good to see you', _read(os.path.join(self.root, brand)))


class AuthRestyleServiceTests(TransactionTestCase):
    """The background thread that restyles the auth pages after the home page."""

    def setUp(self):
        from apps.Imagi.ProjectManager.models import Project

        self.user = User.objects.create_user(username='restyler', password='testpass123')
        self.project = Project.objects.create(
            user=self.user, name='Beanline',
            description='A small-batch coffee roastery that ships beans weekly.',
        )

    def _lead(self):
        from apps.Imagi.Build.models import AgentConversation

        return AgentConversation.objects.create(
            user=self.user, project_id=self.project.pk, kind='lead',
            model_name='claude-opus-5-5', title='Main thread', mode='agent',
        )

    def test_brief_matches_the_home_page_through_the_two_open_files(self):
        from apps.Imagi.ProjectManager.services.auth_restyle_service import (
            HOME_VIEW_PATH,
            build_restyle_brief,
        )

        brief = build_restyle_brief('Beanline', 'Coffee, roasted weekly.', 'Warm and earthy')
        self.assertIn(HOME_VIEW_PATH, brief)
        for path in AUTH_RESTYLE_PATHS:
            self.assertIn(path, brief)
        self.assertIn('Beanline', brief)
        self.assertIn('Warm and earthy', brief)

    def test_queues_a_thread_under_the_main_thread_on_the_everyday_model(self):
        from apps.Imagi.Build.models import AgentConversation
        from apps.Imagi.ProjectManager.services import auth_restyle_service

        lead = self._lead()
        with patch.object(auth_restyle_service, '_start_threads') as start:
            task = auth_restyle_service.queue_auth_restyle(self.project.pk, self.user.pk)

        self.assertIsNotNone(task)
        task = AgentConversation.objects.get(pk=task.pk)
        self.assertEqual(task.kind, 'task')
        self.assertEqual(task.parent_id, lead.id)
        self.assertEqual(task.model_name, settings.IMAGI_BUILDER['DEFAULT_MODEL'])
        # Normal speed: only the first build's home page runs in fast mode.
        self.assertFalse(task.fast_mode)
        self.assertIn('styles/auth.css', task.queued_prompt)
        self.assertIsNone(task.run_started_at)
        start.assert_called_once()

        # The main thread shows it with a card, like any other dispatch.
        message = lead.messages.get()
        self.assertEqual(message.role, 'assistant')
        self.assertEqual(
            message.metadata['dispatched_tasks'][0]['conversation_id'], task.id
        )

    def test_no_main_thread_means_no_restyle(self):
        from apps.Imagi.Build.models import AgentConversation
        from apps.Imagi.ProjectManager.services import auth_restyle_service

        with patch.object(auth_restyle_service, '_start_threads'):
            self.assertIsNone(
                auth_restyle_service.queue_auth_restyle(self.project.pk, self.user.pk)
            )
        self.assertFalse(AgentConversation.objects.filter(kind='task').exists())

    def test_never_raises_into_the_build(self):
        from apps.Imagi.ProjectManager.services import auth_restyle_service

        self.assertIsNone(auth_restyle_service.queue_auth_restyle(999999, self.user.pk))
