"""
Tests for the Builder app.

Covers the Builder models, the CreateFileService, and the current Builder DRF
API (file creation/content, auth gating and project ownership).

Note: the previous server-rendered view/service tests (`builder:landing_page`,
`process_builder_mode_input`, ...) were removed. Those exercised a legacy
template UI and pre-SDK agent helpers that no longer exist — the workspace is
now a Vue SPA talking to the DRF API exercised below.
"""

import os
import shutil
import tempfile
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from apps.Imagi.ProjectManager.models import Project as PMProject
from apps.Imagi.Build.services.browser_preview_service import (
    BrowserPreviewService,
    CdpError,
)
from apps.Imagi.Build.services.create_app_service import CreateAppService
from apps.Imagi.Build.services.create_file_service import CreateFileService
from apps.Imagi.Build.services.codegen.prebuilt_apps import PREBUILT_MAP


class DefaultAppsTests(TestCase):
    """The default scaffold must not include the legacy payments app —
    payment pages come from the Sell workspace's prebuilt templates."""

    def test_payments_is_not_a_prebuilt_app(self):
        self.assertNotIn('payments', PREBUILT_MAP)
        self.assertEqual(set(PREBUILT_MAP), {'home', 'auth'})

    def test_prebuilt_auth_backend_is_registrable_and_migratable(self):
        """The auth app must declare a non-conflicting label (its default,
        'auth', collides with django.contrib.auth) and ship a migrations
        package so `manage.py makemigrations` works if models are added."""
        from apps.Imagi.Build.services.codegen.prebuilt_apps import (
            generate_prebuilt_app_files,
        )

        files = {f['name']: f['content'] for f in generate_prebuilt_app_files('auth')}

        self.assertIn("label = 'user_auth'", files['backend/django/apps/auth/apps.py'])
        self.assertIn('backend/django/apps/auth/migrations/__init__.py', files)

    def test_prebuilt_auth_api_covers_the_frontend_contract(self):
        """Every endpoint the generated frontend calls must exist: the auth
        app's own service hits csrf/signin/register/logout/user, and the
        scaffold's shared auth store bootstraps via init/."""
        from apps.Imagi.Build.services.codegen.prebuilt_apps import (
            generate_prebuilt_app_files,
        )

        files = {f['name']: f['content'] for f in generate_prebuilt_app_files('auth')}
        urls = files['backend/django/apps/auth/api/urls.py']

        for route in ('csrf/', 'signin/', 'register/', 'logout/', 'init/', 'user/'):
            self.assertIn(f"path('{route}'", urls)

    def test_prebuilt_auth_mirrors_imagi_auth_module(self):
        """The generated auth code must stay a verbatim copy of Imagi's own
        auth module: same hardened signin/register views (generic invalid
        credential message, Django password validators) and a frontend that
        rides the shared api client instead of a bespoke axios instance."""
        from apps.Imagi.Build.services.codegen.prebuilt_apps import (
            generate_prebuilt_app_files,
        )

        files = {f['name']: f['content'] for f in generate_prebuilt_app_files('auth')}

        views = files['backend/django/apps/auth/api/views.py']
        # Generic message: no username-enumeration via distinct errors.
        self.assertIn('Invalid username or password.', views)
        self.assertNotIn('No account found with this username', views)

        serializers = files['backend/django/apps/auth/api/serializers.py']
        # Full Django password validation, not just a length check.
        self.assertIn('validate_password', serializers)

        service = files['frontend/vuejs/src/apps/auth/services/api.ts']
        self.assertIn("import api from '@/shared/services/api'", service)
        self.assertNotIn('axios.create', service)

        store = files['frontend/vuejs/src/apps/auth/stores/index.ts']
        self.assertIn("from '@/shared/stores/auth'", store)

    def test_prebuilt_home_page_links_to_sign_in(self):
        from apps.Imagi.Build.services.codegen.prebuilt_apps import (
            generate_prebuilt_app_files,
        )

        files = {f['name']: f['content'] for f in generate_prebuilt_app_files('home')}
        home_view = files['frontend/vuejs/src/apps/home/views/HomeView.vue']

        self.assertIn('/auth/signin', home_view)
        self.assertIn('/auth/register', home_view)

    def test_ensure_default_apps_skips_payments(self):
        user = User.objects.create_user(username='founder', password='testpass123')
        project_root = tempfile.mkdtemp(prefix='builder_default_apps_')
        self.addCleanup(lambda: shutil.rmtree(project_root, ignore_errors=True))
        project = PMProject.objects.create(
            user=user, name='Fresh Project', project_path=project_root
        )

        result = CreateAppService(user=user).ensure_default_apps(project_id=str(project.id))
        self.assertTrue(result['success'])

        apps_dir = os.path.join(project_root, 'frontend', 'vuejs', 'src', 'apps')
        self.assertTrue(os.path.isdir(os.path.join(apps_dir, 'home')))
        self.assertTrue(os.path.isdir(os.path.join(apps_dir, 'auth')))
        self.assertFalse(os.path.isdir(os.path.join(apps_dir, 'payments')))


class BuilderModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')

        self.project_root = tempfile.mkdtemp(prefix='builder_model_')
        self.project = PMProject.objects.create(
            user=self.user, name="Test Project", project_path=self.project_root
        )
        self.addCleanup(lambda: shutil.rmtree(self.project_root, ignore_errors=True))

    def test_project_creation(self):
        self.assertEqual(str(self.project), "Test Project (testuser)")
        self.assertEqual(self.project.slug, "test-project")


class BuilderAPITests(APITestCase):
    """The current Builder REST API (replaces the legacy view tests)."""

    def setUp(self):
        self.user = User.objects.create_user(username='builder', password='testpass123')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        self.project_root = tempfile.mkdtemp(prefix='builder_api_')
        self.project = PMProject.objects.create(
            user=self.user, name="API Project", project_path=self.project_root
        )
        self.addCleanup(lambda: shutil.rmtree(self.project_root, ignore_errors=True))

    def test_builder_api_requires_auth(self):
        self.client.credentials()  # drop auth
        resp = self.client.post(
            reverse('api-create-file', args=[self.project.id]),
            {'path': 'frontend/vuejs/src/apps/blog/views/Nope.vue', 'content': 'x'},
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_file_writes_to_disk(self):
        relative_path = 'frontend/vuejs/src/apps/blog/views/About.vue'
        resp = self.client.post(
            reverse('api-create-file', args=[self.project.id]),
            {'path': relative_path, 'content': 'hello world'},
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['path'], relative_path)
        self.assertTrue(os.path.exists(os.path.join(self.project_root, relative_path)))

    def test_create_file_accepts_form_encoded_data(self):
        # Regression: form posts arrive as an immutable QueryDict; the view must
        # copy it before deriving name/type instead of raising (which surfaced
        # as a 500). Note the default (non-json) client format is multipart.
        relative_path = 'frontend/vuejs/src/apps/blog/views/Form.vue'
        resp = self.client.post(
            reverse('api-create-file', args=[self.project.id]),
            {'path': relative_path, 'content': 'form body'},
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(os.path.exists(os.path.join(self.project_root, relative_path)))

    def test_create_file_requires_path_or_name(self):
        resp = self.client.post(
            reverse('api-create-file', args=[self.project.id]),
            {'content': 'x'}, format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_file_on_other_users_project_returns_404(self):
        other = User.objects.create_user(username='intruder', password='testpass123')
        other_root = tempfile.mkdtemp(prefix='builder_other_')
        self.addCleanup(lambda: shutil.rmtree(other_root, ignore_errors=True))
        other_project = PMProject.objects.create(
            user=other, name="Their Project", project_path=other_root
        )
        relative_path = 'frontend/vuejs/src/x.vue'
        resp = self.client.post(
            reverse('api-create-file', args=[other_project.id]),
            {'path': relative_path, 'content': 'x'}, format='json',
        )
        # Another user's project is not visible, so the caller gets a clean 404
        # (not a 500), and nothing is written into their directory.
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(os.path.exists(os.path.join(other_root, relative_path)))

    def test_file_content_of_other_users_project_returns_404(self):
        other = User.objects.create_user(username='snoop', password='testpass123')
        other_root = tempfile.mkdtemp(prefix='builder_snoop_')
        self.addCleanup(lambda: shutil.rmtree(other_root, ignore_errors=True))
        other_project = PMProject.objects.create(
            user=other, name="Snoop Project", project_path=other_root
        )
        resp = self.client.get(
            reverse('api-file-content', args=[other_project.id, 'a/b.vue'])
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    @patch('apps.Imagi.Build.api.views.CreateFileService')
    def test_unexpected_service_error_returns_safe_500(self, mock_service_cls):
        # An unexpected service failure must surface as a generic 500 handled by
        # the central exception handler — not a leaked internal error string.
        mock_service_cls.return_value.create_file.side_effect = Exception(
            'sensitive detail: /srv/secret/path'
        )
        resp = self.client.post(
            reverse('api-create-file', args=[self.project.id]),
            {'path': 'frontend/vuejs/src/x.vue', 'content': 'y'},
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('error', resp.data)
        self.assertNotIn('sensitive detail', str(resp.data))

    def test_file_content_round_trip(self):
        relative_path = 'frontend/vuejs/src/apps/blog/views/Home.vue'
        self.client.post(
            reverse('api-create-file', args=[self.project.id]),
            {'path': relative_path, 'content': 'the content'},
            format='json',
        )
        resp = self.client.get(
            reverse('api-file-content', args=[self.project.id, relative_path])
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['content'], 'the content')


class CreateFileServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='fileserviceuser', password='testpass123'
        )
        self.project_root = tempfile.mkdtemp(prefix='imagi_file_service_')
        self.project = PMProject.objects.create(
            user=self.user, name='File Service Project', project_path=self.project_root
        )
        self.service = CreateFileService(project=self.project)

    def tearDown(self):
        shutil.rmtree(self.project_root, ignore_errors=True)

    def test_creates_default_view_when_content_blank(self):
        relative_path = 'frontend/vuejs/src/apps/blog/views/NewAbout.vue'
        result = self.service.create_file({
            'name': relative_path,
            'type': 'vue',
            'content': '   '  # simulate blank content coming from UI
        })

        expected_path = os.path.join(self.project_root, relative_path)
        self.assertTrue(os.path.exists(expected_path))
        self.assertEqual(result['path'], relative_path)
        self.assertEqual(result['type'], 'vue')

        with open(expected_path, 'r', encoding='utf-8') as created_file:
            created_content = created_file.read()

        self.assertIn('<template>', created_content)
        self.assertIn('Welcome to NewAbout', created_content)
        self.assertIn("defineOptions({ name: 'NewAbout' })", created_content)

    def test_creates_default_component_when_content_empty(self):
        relative_path = 'frontend/vuejs/src/components/atoms/PrimaryButton.vue'
        result = self.service.create_file({
            'name': relative_path,
            'type': 'vue',
            'content': '\n'
        })

        expected_path = os.path.join(self.project_root, relative_path)
        self.assertTrue(os.path.exists(expected_path))
        self.assertEqual(result['path'], relative_path)

        with open(expected_path, 'r', encoding='utf-8') as created_file:
            created_content = created_file.read()

        self.assertIn('<!-- Atom: PrimaryButton -->', created_content)
        self.assertIn('.primarybutton-component', created_content)
        self.assertIn("defineOptions({ name: 'PrimaryButton' })", created_content)


class FakeCdpConnection:
    """Stands in for CdpConnection: records calls, serves canned replies."""

    def __init__(self, console_buffer=None, evaluate_result=None):
        self.applied_viewport = None
        self.console_watch_registered = False
        self.calls = []
        # evaluate_result overrides the default well-formed reply; an
        # Exception instance is raised instead of returned.
        if evaluate_result is None:
            evaluate_result = {'result': {'type': 'object', 'value': console_buffer or []}}
        self._evaluate_result = evaluate_result

    def call(self, method, params=None):
        self.calls.append((method, params or {}))
        if method == 'Page.getNavigationHistory':
            return {
                'currentIndex': 0,
                'entries': [{'id': 1, 'url': 'http://127.0.0.1:5174/', 'title': 'App'}],
            }
        if method == 'Runtime.evaluate':
            if isinstance(self._evaluate_result, Exception):
                raise self._evaluate_result
            return self._evaluate_result
        return {}


class PreviewConsoleWatchTests(TestCase):
    """console_errors in the frame/status payload (contract: level/text/ts,
    last 5, never fails a frame)."""

    def setUp(self):
        self.user = User.objects.create_user(username='consolewatch', password='pw123456')
        projects_root = tempfile.mkdtemp(prefix='preview_root_')
        self.addCleanup(lambda: shutil.rmtree(projects_root, ignore_errors=True))
        overrides = override_settings(PROJECTS_ROOT=projects_root)
        overrides.enable()
        self.addCleanup(overrides.disable)

        project_path = tempfile.mkdtemp(prefix='preview_proj_')
        self.addCleanup(lambda: shutil.rmtree(project_path, ignore_errors=True))
        self.project = PMProject.objects.create(
            user=self.user, name='Console Project', project_path=project_path
        )
        self.service = BrowserPreviewService(self.project)
        self.state = {'app_url': 'http://127.0.0.1:5174', 'viewport': [1280, 800]}

    def test_status_payload_reports_console_errors(self):
        conn = FakeCdpConnection(
            console_buffer=[{'level': 'error', 'text': 'Boom', 'ts': 123}]
        )
        payload = self.service._status_payload(conn, self.state)
        self.assertEqual(
            payload['console_errors'],
            [{'level': 'error', 'text': 'Boom', 'ts': 123}],
        )

    def test_collector_is_registered_once_per_connection(self):
        conn = FakeCdpConnection()
        self.service._status_payload(conn, self.state)
        self.service._status_payload(conn, self.state)
        registrations = [
            m for m, _ in conn.calls if m == 'Page.addScriptToEvaluateOnNewDocument'
        ]
        self.assertEqual(len(registrations), 1)

    def test_page_supplied_buffer_is_sanitized(self):
        # The page can overwrite window.__imagiErrors with anything, so the
        # backend re-validates: non-dicts and empty texts drop, text is
        # capped, a junk ts becomes 0, and level is forced to 'error'.
        conn = FakeCdpConnection(console_buffer=[
            'nonsense',
            {'text': ''},
            {'level': 'warning', 'text': 'x' * 1000, 'ts': 'NaN'},
            {'text': 'ok', 'ts': 5},
        ])
        errors = self.service._collect_console_errors(conn)
        self.assertEqual(len(errors), 2)
        self.assertEqual(errors[0]['level'], 'error')
        self.assertEqual(len(errors[0]['text']), 500)
        self.assertEqual(errors[0]['ts'], 0)
        self.assertEqual(errors[1], {'level': 'error', 'text': 'ok', 'ts': 5})

    def test_buffer_is_capped_to_last_five(self):
        conn = FakeCdpConnection(console_buffer=[
            {'text': f'err {i}', 'ts': i} for i in range(7)
        ])
        errors = self.service._collect_console_errors(conn)
        self.assertEqual([e['text'] for e in errors], [f'err {i}' for i in range(2, 7)])

    def test_collection_failure_never_fails_the_frame(self):
        for bad in (
            CdpError('Runtime.evaluate: blocked'),
            {'exceptionDetails': {'text': 'page threw'}},
            {'result': {'type': 'string', 'value': 'not a list'}},
        ):
            conn = FakeCdpConnection(evaluate_result=bad)
            self.assertEqual(self.service._collect_console_errors(conn), [])


class PreviewEndpointTests(APITestCase):
    """The async preview endpoints: auth, method handling, and error shapes."""

    def setUp(self):
        self.user = User.objects.create_user(username='previewapi', password='pw123456')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        # A private PROJECTS_ROOT so no stale state files make the service
        # think a browser is running.
        projects_root = tempfile.mkdtemp(prefix='preview_api_root_')
        self.addCleanup(lambda: shutil.rmtree(projects_root, ignore_errors=True))
        overrides = override_settings(PROJECTS_ROOT=projects_root)
        overrides.enable()
        self.addCleanup(overrides.disable)

        project_path = tempfile.mkdtemp(prefix='preview_api_proj_')
        self.addCleanup(lambda: shutil.rmtree(project_path, ignore_errors=True))
        self.project = PMProject.objects.create(
            user=self.user, name='Preview API Project', project_path=project_path
        )

    def test_requires_token_auth(self):
        self.client.credentials()  # drop auth
        resp = self.client.get(reverse('api-preview-frame', args=[self.project.id]))
        self.assertEqual(resp.status_code, 401)

    def test_session_auth_alone_is_rejected(self):
        # These views are csrf_exempt, so honouring cookie sessions would
        # let any origin drive the preview (same reasoning as agent_stream).
        self.client.credentials()
        self.client.force_login(self.user)
        resp = self.client.get(reverse('api-preview-frame', args=[self.project.id]))
        self.assertEqual(resp.status_code, 401)

    def test_frame_reports_browser_not_running_as_409(self):
        resp = self.client.get(reverse('api-preview-frame', args=[self.project.id]))
        self.assertEqual(resp.status_code, 409)
        body = resp.json()
        self.assertFalse(body['running'])
        self.assertIn('error', body)

    def test_input_reports_browser_not_running_as_409(self):
        resp = self.client.post(
            reverse('api-preview-input', args=[self.project.id]),
            data='{"events": []}', content_type='application/json',
        )
        self.assertEqual(resp.status_code, 409)
        self.assertFalse(resp.json()['running'])

    def test_navigate_and_resize_report_browser_not_running_as_409(self):
        for name, body in (
            ('api-preview-navigate', '{"action": "reload"}'),
            ('api-preview-resize', '{"width": 800, "height": 600}'),
        ):
            resp = self.client.post(
                reverse(name, args=[self.project.id]),
                data=body, content_type='application/json',
            )
            self.assertEqual(resp.status_code, 409)

    def test_input_rejects_oversized_batch(self):
        # BrowserPreviewError surfaces as a 400, exactly like the DRF views.
        events = ','.join(['{}'] * 65)
        resp = self.client.post(
            reverse('api-preview-input', args=[self.project.id]),
            data='{"events": [%s]}' % events, content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn('error', resp.json())

    def test_input_rejects_invalid_json(self):
        resp = self.client.post(
            reverse('api-preview-input', args=[self.project.id]),
            data='not json', content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['error'], 'Invalid JSON body')

    def test_wrong_methods_are_405(self):
        resp = self.client.post(
            reverse('api-preview-frame', args=[self.project.id]),
            data='{}', content_type='application/json',
        )
        self.assertEqual(resp.status_code, 405)
        resp = self.client.get(reverse('api-preview-input', args=[self.project.id]))
        self.assertEqual(resp.status_code, 405)

    def test_other_users_project_is_404(self):
        other = User.objects.create_user(username='previewother', password='pw123456')
        other_path = tempfile.mkdtemp(prefix='preview_api_other_')
        self.addCleanup(lambda: shutil.rmtree(other_path, ignore_errors=True))
        other_project = PMProject.objects.create(
            user=other, name='Their Preview', project_path=other_path
        )
        resp = self.client.get(reverse('api-preview-frame', args=[other_project.id]))
        self.assertEqual(resp.status_code, 404)
