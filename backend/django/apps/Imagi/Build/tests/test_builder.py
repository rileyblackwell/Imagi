"""
Tests for the Builder app.

Covers the CreateFileService and the current Builder DRF
API (file creation/content, auth gating and project ownership).

Note: the previous server-rendered view/service tests (`builder:landing_page`,
`process_builder_mode_input`, ...) were removed. Those exercised a legacy
template UI and pre-SDK agent helpers that no longer exist — the workspace is
now a Vue SPA talking to the DRF API exercised below.
"""

import json
import os
import re
import shutil
import tempfile
import threading
import time
from unittest import mock
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from apps.Imagi.ProjectManager.models import Project as PMProject
from apps.Imagi.Build.services.browser_preview_service import (
    BACKDROP_PNG_BUDGET_B64,
    FRAME_PNG_BUDGET_B64,
    BrowserPreviewError,
    BrowserPreviewService,
    CdpError,
)
from apps.Imagi.Build.services.create_app_service import CreateAppService
from apps.Imagi.Build.services.create_file_service import CreateFileService
from apps.Imagi.Build.services.preview_service import child_env, sidecar_stem


class DefaultAppsTests(TestCase):
    """The default scaffold must not include the legacy payments app —
    payment pages come from the Sell workspace's prebuilt templates."""

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


class FilePathContainmentTests(APITestCase):
    """Paths from the request body and the URL stay inside the project.

    Owning a project must not be a licence to reach the rest of the filesystem:
    both the create-file body's `path` and the `<path:file_path>` URL segment
    are attacker-controlled, and `<path:...>` matches `..` segments verbatim.
    """

    def setUp(self):
        self.user = User.objects.create_user(username='pathuser', password='testpass123')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        self.sandbox = tempfile.mkdtemp(prefix='builder_sandbox_')
        self.addCleanup(lambda: shutil.rmtree(self.sandbox, ignore_errors=True))
        self.project_root = os.path.join(self.sandbox, 'project')
        os.makedirs(self.project_root)
        self.project = PMProject.objects.create(
            user=self.user, name="Path Project", project_path=self.project_root
        )

        # A file belonging to nobody in particular, next to the project
        self.outsider = os.path.join(self.sandbox, 'outside.txt')
        with open(self.outsider, 'w', encoding='utf-8') as f:
            f.write('original')

    def test_create_file_rejects_traversal_in_path(self):
        resp = self.client.post(
            reverse('api-create-file', args=[self.project.id]),
            {'path': '../outside.txt', 'content': 'pwned'},
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        with open(self.outsider, encoding='utf-8') as f:
            self.assertEqual(f.read(), 'original')

    def test_create_file_rejects_absolute_path(self):
        # os.path.join drops the project root entirely for an absolute path
        target = os.path.join(self.sandbox, 'absolute.txt')
        resp = self.client.post(
            reverse('api-create-file', args=[self.project.id]),
            {'path': target, 'content': 'pwned'},
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(os.path.exists(target))

    def test_file_content_write_rejects_traversal(self):
        resp = self.client.post(
            reverse('api-file-content', args=[self.project.id, '../outside.txt']),
            {'content': 'pwned'},
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        with open(self.outsider, encoding='utf-8') as f:
            self.assertEqual(f.read(), 'original')

    def test_file_content_read_rejects_traversal(self):
        resp = self.client.get(
            reverse('api-file-content', args=[self.project.id, '../outside.txt'])
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_file_rejects_traversal(self):
        resp = self.client.delete(
            reverse('api-delete-file', args=[self.project.id, '../outside.txt'])
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(os.path.exists(self.outsider))

    def test_traversal_that_lands_back_inside_is_allowed(self):
        # Containment is about where the path resolves, not whether it is tidy
        relative_path = 'frontend/../src/App.vue'
        resp = self.client.post(
            reverse('api-create-file', args=[self.project.id]),
            {'path': relative_path, 'content': 'fine'},
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(os.path.exists(os.path.join(self.project_root, 'src/App.vue')))

    def _make_git_config(self):
        git_dir = os.path.join(self.project_root, '.git')
        os.makedirs(os.path.join(git_dir, 'hooks'))
        config = os.path.join(git_dir, 'config')
        with open(config, 'w', encoding='utf-8') as f:
            f.write('[core]\n')
        return config

    def test_file_content_write_rejects_git_metadata(self):
        # A write to .git/config could set core.fsmonitor, which the backend's
        # own `git status` would then execute with the server's environment.
        config = self._make_git_config()
        resp = self.client.post(
            reverse('api-file-content', args=[self.project.id, '.git/config']),
            {'content': '[core]\n\tfsmonitor = touch /tmp/pwned\n'},
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        with open(config, encoding='utf-8') as f:
            self.assertEqual(f.read(), '[core]\n')

    def test_create_file_rejects_git_hooks(self):
        self._make_git_config()
        for path in ('.git/hooks/pre-commit', 'frontend/../.GIT/hooks/post-merge'):
            with self.subTest(path=path):
                resp = self.client.post(
                    reverse('api-create-file', args=[self.project.id]),
                    {'path': path, 'content': '#!/bin/sh\n'},
                    format='json',
                )
                self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(os.listdir(os.path.join(self.project_root, '.git', 'hooks')), [])

    def test_delete_file_rejects_git_metadata(self):
        config = self._make_git_config()
        resp = self.client.delete(
            reverse('api-delete-file', args=[self.project.id, '.git/config'])
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(os.path.exists(config))

    def test_names_that_only_contain_git_are_allowed(self):
        # The guard matches the .git path segment, not any name containing it.
        for path in ('.gitignore', 'docs/.github/workflow.yml', 'src/my.git.notes.txt'):
            with self.subTest(path=path):
                resp = self.client.post(
                    reverse('api-create-file', args=[self.project.id]),
                    {'path': path, 'content': 'ok'},
                    format='json',
                )
                self.assertEqual(resp.status_code, status.HTTP_201_CREATED)


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
        self.assertIn("defineOptions({ name: 'NewAbout' })", created_content)


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
        # What the page reports for the scroll-metrics probe.
        self.scroll_metrics = {
            'x': 0, 'y': 640, 'width': 1000, 'height': 4000,
            'viewport_width': 1000, 'viewport_height': 800,
            'background': 'rgb(255, 255, 255)',
        }

    def call(self, method, params=None):
        self.calls.append((method, params or {}))
        if method == 'Page.getNavigationHistory':
            return {
                'currentIndex': 0,
                'entries': [{'id': 1, 'url': 'http://127.0.0.1:5174/', 'title': 'App'}],
            }
        if method == 'Page.getLayoutMetrics':
            return {'cssVisualViewport': {'pageX': 0, 'pageY': 640}}
        if method == 'Page.captureScreenshot':
            return {'data': 'ZnJhbWU='}
        if method == 'Runtime.evaluate':
            if 'scrollingElement' in (params or {}).get('expression', ''):
                return {'result': {'type': 'object', 'value': self.scroll_metrics}}
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


class PreviewMotionFrameTests(TestCase):
    """Mid-gesture frames on a HiDPI session are captured at 1x CSS pixels."""

    def setUp(self):
        self.user = User.objects.create_user(username='motionframe', password='pw123456')
        projects_root = tempfile.mkdtemp(prefix='preview_root_')
        self.addCleanup(lambda: shutil.rmtree(projects_root, ignore_errors=True))
        overrides = override_settings(PROJECTS_ROOT=projects_root)
        overrides.enable()
        self.addCleanup(overrides.disable)
        project_path = tempfile.mkdtemp(prefix='preview_proj_')
        self.addCleanup(lambda: shutil.rmtree(project_path, ignore_errors=True))
        self.project = PMProject.objects.create(
            user=self.user, name='Motion Project', project_path=project_path
        )
        self.service = BrowserPreviewService(self.project)

    def _shot_params(self, conn):
        return [p for m, p in conn.calls if m == 'Page.captureScreenshot'][-1]

    def test_motion_frame_at_2x_is_clipped_to_the_scrolled_viewport_at_1x(self):
        conn = FakeCdpConnection()
        state = {'viewport': [1000, 800], 'device_scale_factor': 2}
        self.service._attach_frame(conn, {}, None, quality=55, motion_state=state)
        clip = self._shot_params(conn)['clip']
        self.assertEqual(clip, {'x': 0.0, 'y': 640.0, 'width': 1000, 'height': 800, 'scale': 0.5})

    def test_idle_frame_and_1x_sessions_capture_full_frames(self):
        conn = FakeCdpConnection()
        self.service._attach_frame(conn, {}, None)
        self.assertNotIn('clip', self._shot_params(conn))
        conn = FakeCdpConnection()
        state = {'viewport': [1000, 800], 'device_scale_factor': 1}
        self.service._attach_frame(conn, {}, None, quality=55, motion_state=state)
        self.assertNotIn('clip', self._shot_params(conn))
        self.assertNotIn('Page.getLayoutMetrics', [m for m, _ in conn.calls])

    def test_frames_at_rest_are_lossless_png(self):
        conn = FakeCdpConnection()
        payload = {}
        self.service._attach_frame(conn, payload, None)
        self.assertEqual(self._shot_params(conn)['format'], 'png')
        self.assertEqual(payload['frame_type'], 'png')
        # Mid-gesture frames stay JPEG.
        conn = FakeCdpConnection()
        payload = {}
        state = {'viewport': [1000, 800], 'device_scale_factor': 2}
        self.service._attach_frame(conn, payload, None, quality=55, motion_state=state)
        self.assertEqual(self._shot_params(conn)['format'], 'jpeg')
        self.assertEqual(payload['frame_type'], 'jpeg')

    def test_a_png_over_budget_is_replaced_by_jpeg_for_a_while(self):
        class HeavyPage(FakeCdpConnection):
            def call(self, method, params=None):
                reply = super().call(method, params)
                if method == 'Page.captureScreenshot' and params.get('format') == 'png':
                    return {'data': 'A' * (FRAME_PNG_BUDGET_B64 + 1)}
                return reply

        conn = HeavyPage()
        payload = {}
        self.service._attach_frame(conn, payload, None)
        shot = self._shot_params(conn)
        self.assertEqual((shot['format'], shot['quality']), ('jpeg', 90))
        self.assertEqual(payload['frame'], 'ZnJhbWU=')
        # The next frame of this view skips the wasted PNG encode.
        conn.calls.clear()
        self.service._attach_frame(conn, {}, None)
        self.assertEqual([p['format'] for m, p in conn.calls if m == 'Page.captureScreenshot'], ['jpeg'])

    def _dispatch(self, events):
        conn = FakeCdpConnection()
        entry = {'conn': conn, 'page': {}, 'lock': threading.Lock()}
        state = {'app_url': 'http://127.0.0.1:5174', 'viewport': [1000, 800],
                 'device_scale_factor': 2, 'cdp_port': 9999}
        with mock.patch.object(self.service, '_require_state', return_value=state), \
                mock.patch('apps.Imagi.Build.services.browser_preview_service._pool_checkout',
                           return_value=entry):
            self.service.dispatch_input(events)
        return self._shot_params(conn)

    def test_a_scroll_can_skip_the_frame(self):
        conn = FakeCdpConnection()
        entry = {'conn': conn, 'page': {}, 'lock': threading.Lock()}
        state = {'app_url': 'http://127.0.0.1:5174', 'viewport': [1000, 800],
                 'device_scale_factor': 2, 'cdp_port': 9999}
        wheel = {'kind': 'wheel', 'x': 5, 'y': 5, 'deltaX': 0, 'deltaY': 120}
        with mock.patch.object(self.service, '_require_state', return_value=state), \
                mock.patch('apps.Imagi.Build.services.browser_preview_service._pool_checkout',
                           return_value=entry):
            payload = self.service.dispatch_input([wheel], frame=False)
        self.assertTrue(payload['frame_skipped'])
        self.assertIsNone(payload['frame'])
        self.assertEqual(payload['scroll']['y'], 640)
        self.assertFalse([m for m, _ in conn.calls if m == 'Page.captureScreenshot'])
        self.assertIn('Input.dispatchMouseEvent', [m for m, _ in conn.calls])

    def test_hovering_gets_full_frames_and_dragging_gets_motion_frames(self):
        hover = {'kind': 'mouse', 'type': 'mouseMoved', 'x': 5, 'y': 5, 'buttons': 0}
        self.assertEqual(self._dispatch([hover])['format'], 'png')
        drag = dict(hover, buttons=1)
        shot = self._dispatch([drag])
        self.assertEqual(shot['format'], 'jpeg')
        self.assertEqual(shot['clip']['scale'], 0.5)



class FakeScrollingPage(FakeCdpConnection):
    """A 4000px page in an 800px viewport that really scrolls."""

    def __init__(self, fixed_elements=1):
        super().__init__()
        self.y = 640.0
        self.fixed_elements = fixed_elements
        self.warmed = False
        # How many times the page's DOM has changed (the doc stamp's count).
        self.mutations = 0

    def call(self, method, params=None):
        expr = (params or {}).get('expression', '')
        if method == 'Runtime.evaluate':
            if 'scrollingElement' in expr:
                self.scroll_metrics = dict(self.scroll_metrics, y=self.y)
            elif 'window.scrollTo' in expr and 'imagi' not in expr:
                self.calls.append((method, params or {}))
                top = float(re.search(r'top: ([\d.]+)', expr).group(1))
                self.y = max(0.0, min(top, 4000.0 - 800.0))
                return {'result': {'type': 'object', 'value': [0, self.y]}}
            elif '__imagiDocStamp' in expr:
                self.calls.append((method, params or {}))
                return {'result': {'type': 'string', 'value': f'http://127.0.0.1:5174/#doc:{self.mutations}'}}
            elif '__imagiBackdropWarm' in expr:
                self.calls.append((method, params or {}))
                first, self.warmed = not self.warmed, True
                return {'result': {'type': 'boolean', 'value': first}}
            elif "querySelectorAll('body *')" in expr:
                self.calls.append((method, params or {}))
                return {'result': {'type': 'number', 'value': self.fixed_elements}}
            elif '__imagi_backdrop' in expr or 'requestAnimationFrame(f)' in expr:
                self.calls.append((method, params or {}))
                return {'result': {'type': 'boolean', 'value': True}}
        return super().call(method, params)


class PreviewBackdropTests(TestCase):
    """The page captured ahead of time, for the client to scroll through."""

    def setUp(self):
        self.user = User.objects.create_user(username='backdrop', password='pw123456')
        projects_root = tempfile.mkdtemp(prefix='preview_root_')
        self.addCleanup(lambda: shutil.rmtree(projects_root, ignore_errors=True))
        overrides = override_settings(PROJECTS_ROOT=projects_root)
        overrides.enable()
        self.addCleanup(overrides.disable)
        project_path = tempfile.mkdtemp(prefix='preview_proj_')
        self.addCleanup(lambda: shutil.rmtree(project_path, ignore_errors=True))
        self.project = PMProject.objects.create(
            user=self.user, name='Backdrop Project', project_path=project_path
        )
        self.service = BrowserPreviewService(self.project)
        os.makedirs(self.service.pid_dir, exist_ok=True)
        self.state = {
            'app_url': 'http://127.0.0.1:5174', 'viewport': [1000, 800],
            'device_scale_factor': 2, 'cdp_port': 9999,
        }

    def _clear_cache(self):
        try:
            os.remove(self.service._backdrop_cache_file)
        except OSError:
            pass

    def _run(self, conn):
        entry = {'conn': conn, 'page': {}, 'lock': threading.Lock()}
        with mock.patch.object(self.service, '_require_state', return_value=self.state), \
                mock.patch('apps.Imagi.Build.services.browser_preview_service._pool_checkout',
                           return_value=entry), \
                mock.patch('apps.Imagi.Build.services.browser_preview_service.time.sleep'):
            return self.service.backdrop()

    def test_slices_cover_the_page_and_the_scroll_is_put_back(self):
        conn = FakeScrollingPage()
        result = self._run(conn)
        # 4000px at 800px a slice; the last one clamps at the bottom (3200).
        self.assertEqual([s['y'] for s in result['slices']], [0.0, 800.0, 1600.0, 2400.0, 3200.0])
        self.assertTrue(all(s['frame'] for s in result['slices']))
        self.assertEqual(result['scroll']['y'], 640.0)
        self.assertEqual(conn.y, 640.0)  # restored
        # Slices are at the session's full 2x, lossless while under budget,
        # clipped where each one landed (the overlay comes first, at 640).
        clips = [p['clip'] for m, p in conn.calls if m == 'Page.captureScreenshot'][1:]
        self.assertEqual([c['y'] for c in clips], [0.0, 800.0, 1600.0, 2400.0, 3200.0])
        self.assertTrue(all(c['scale'] == 1 for c in clips))
        self.assertEqual({s['type'] for s in result['slices']}, {'png'})
        # The restyle is always removed again.
        styles = [p['expression'] for m, p in conn.calls if "getElementById('__imagi_backdrop')" in p.get('expression', '')]
        self.assertTrue(styles[-1].rstrip().endswith('(null)'))

    def test_fixed_elements_come_back_as_a_transparent_overlay(self):
        conn = FakeScrollingPage(fixed_elements=2)
        result = self._run(conn)
        self.assertEqual(result['overlay'], 'ZnJhbWU=')
        overrides = [p for m, p in conn.calls if m == 'Emulation.setDefaultBackgroundColorOverride']
        self.assertEqual(overrides, [{'color': {'r': 0, 'g': 0, 'b': 0, 'a': 0}}, {}])
        png = [p for m, p in conn.calls if m == 'Page.captureScreenshot' and p.get('format') == 'png']
        self.assertEqual(png[0]['clip']['y'], 640.0)

    def test_no_fixed_elements_means_no_overlay(self):
        self.assertIsNone(self._run(FakeScrollingPage(fixed_elements=0))['overlay'])

    def test_first_backdrop_of_a_page_scrolls_through_it_first(self):
        conn = FakeScrollingPage()
        self._run(conn)
        first_shot = next(i for i, (m, _) in enumerate(conn.calls) if m == 'Page.captureScreenshot')
        frames_waited = [p for m, p in conn.calls[:first_shot] if 'requestAnimationFrame(f)' in p.get('expression', '')]
        self.assertEqual(len(frames_waited), 5)
        conn.calls.clear()
        self._run(conn)  # same page again: no warm-up pass
        self.assertFalse([p for m, p in conn.calls if 'requestAnimationFrame(f)' in p.get('expression', '')])

    def test_input_cuts_a_capture_short_and_keeps_the_nearest_slices(self):
        conn = FakeScrollingPage()
        conn.warmed = True
        conn.y = 1700.0
        checks = iter([False, False, False, True])
        with mock.patch.object(self.service, '_input_waiting', side_effect=lambda since: next(checks)):
            result = self._run(conn)
        # Here (1600), below (2400), above (800): one contiguous run.
        self.assertEqual([s['y'] for s in result['slices']], [800.0, 1600.0, 2400.0])
        self.assertEqual(conn.y, 1700.0)  # restored

    def test_input_before_the_capture_defers_it(self):
        conn = FakeScrollingPage()
        conn.warmed = True
        with mock.patch.object(self.service, '_input_waiting', return_value=True):
            result = self._run(conn)
        self.assertEqual(result['slices'], [])
        self.assertFalse([m for m, _ in conn.calls if m == 'Page.captureScreenshot'])

    def test_input_waiting_on_the_page_lock_is_flagged(self):
        import fcntl
        started = time.time() - 1
        self.assertFalse(self.service._input_waiting(started))
        with open(os.path.join(self.service.pid_dir, f"{sidecar_stem(self.project)}_page.lock"), 'a') as held:
            fcntl.flock(held, fcntl.LOCK_EX)
            with mock.patch('apps.Imagi.Build.services.browser_preview_service.PAGE_LOCK_TIMEOUT_S', 0.05):
                with self.service._page_lock(False):
                    pass
                self.assertFalse(self.service._input_waiting(started))  # a poll just waits
                with self.service._page_lock(False, preempt=True):
                    pass
            fcntl.flock(held, fcntl.LOCK_UN)
        self.assertTrue(self.service._input_waiting(started))

    def test_slices_over_the_png_budget_fall_back_to_jpeg(self):
        class HeavyPage(FakeScrollingPage):
            heavy_until = 4000.0

            def call(self, method, params=None):
                reply = super().call(method, params)
                if (method == 'Page.captureScreenshot' and params.get('format') == 'png'
                        and params['clip']['y'] < self.heavy_until):
                    return {'data': 'A' * (BACKDROP_PNG_BUDGET_B64 + 1)}
                return reply

        # A heavy hero (0) amid light sections: only its slice is JPEG.
        conn = HeavyPage(fixed_elements=0)
        conn.heavy_until = 1.0
        conn.y = 0.0
        result = self._run(conn)
        self.assertEqual([s['type'] for s in result['slices']], ['jpeg', 'png', 'png', 'png', 'png'])

        # Heavy all the way down: two wasted PNG encodes, then straight to JPEG.
        self._clear_cache()
        conn = HeavyPage(fixed_elements=0)
        result = self._run(conn)
        self.assertEqual({s['type'] for s in result['slices']}, {'jpeg'})
        formats = [p['format'] for m, p in conn.calls if m == 'Page.captureScreenshot']
        self.assertEqual(formats, ['png', 'jpeg', 'png', 'jpeg', 'jpeg', 'jpeg', 'jpeg'])
        jpeg = [p for m, p in conn.calls if m == 'Page.captureScreenshot' and p['format'] == 'jpeg']
        self.assertTrue(all(p['quality'] == 90 and p['clip']['scale'] == 1 for p in jpeg))

    def test_an_unchanged_page_gets_the_stored_backdrop_without_capturing(self):
        conn = FakeScrollingPage()
        first = self._run(conn)
        conn.calls.clear()
        again = self._run(conn)
        self.assertTrue(again['cached'])
        self.assertEqual(again['slices'], first['slices'])
        self.assertFalse([m for m, _ in conn.calls if m == 'Page.captureScreenshot'])
        # Nor a scroll of the page under the user.
        self.assertFalse([p for m, p in conn.calls if 'window.scrollTo' in p.get('expression', '')])

    def test_a_changed_page_is_captured_again(self):
        conn = FakeScrollingPage()
        self._run(conn)
        conn.mutations += 1
        conn.calls.clear()
        again = self._run(conn)
        self.assertNotIn('cached', again)
        self.assertTrue([m for m, _ in conn.calls if m == 'Page.captureScreenshot'])

    def test_a_cut_short_capture_is_not_stored(self):
        conn = FakeScrollingPage()
        conn.warmed = True
        checks = iter([False, False, True] + [False] * 20)
        with mock.patch.object(self.service, '_input_waiting', side_effect=lambda since: next(checks)):
            self._run(conn)
        self.assertFalse(os.path.exists(self.service._backdrop_cache_file))

    def test_cached_only_never_captures(self):
        conn = FakeScrollingPage()
        entry = {'conn': conn, 'page': {}, 'lock': threading.Lock()}
        with mock.patch.object(self.service, '_require_state', return_value=self.state), \
                mock.patch('apps.Imagi.Build.services.browser_preview_service._pool_checkout',
                           return_value=entry):
            result = self.service.backdrop(cached_only=True)
        self.assertEqual(result['slices'], [])
        self.assertFalse([m for m, _ in conn.calls if m == 'Page.captureScreenshot'])

    def test_a_view_outside_the_stored_slices_is_captured_again(self):
        conn = FakeScrollingPage()
        self._run(conn)
        with open(self.service._backdrop_cache_file) as fh:
            stored = json.load(fh)
        stored['backdrop']['slices'] = stored['backdrop']['slices'][:1]  # covers 0-800 only
        with open(self.service._backdrop_cache_file, 'w') as fh:
            json.dump(stored, fh)
        conn.calls.clear()
        self.assertNotIn('cached', self._run(conn))

    def test_slices_are_taken_outward_from_the_view(self):
        order = BrowserPreviewService._nearest_first([0, 800, 1600, 2400, 3200], {'y': 1700})
        self.assertEqual(order, [1600, 2400, 800, 3200, 0])

    def test_offsets_stay_near_the_scroll_on_a_very_long_page(self):
        offsets = BrowserPreviewService._backdrop_offsets(
            {'y': 30000, 'height': 60000, 'viewport_height': 1000}
        )
        self.assertLessEqual(offsets[0], 30000)
        self.assertGreaterEqual(offsets[-1] + 1000, 31000)
        self.assertLessEqual(len(offsets), 10)


class PreviewScrollMetricsTests(TestCase):
    """Frames report the scroll offset they show, read after wheel input lands."""

    def setUp(self):
        self.user = User.objects.create_user(username='scrollmetrics', password='pw123456')
        projects_root = tempfile.mkdtemp(prefix='preview_root_')
        self.addCleanup(lambda: shutil.rmtree(projects_root, ignore_errors=True))
        overrides = override_settings(PROJECTS_ROOT=projects_root)
        overrides.enable()
        self.addCleanup(overrides.disable)
        project_path = tempfile.mkdtemp(prefix='preview_proj_')
        self.addCleanup(lambda: shutil.rmtree(project_path, ignore_errors=True))
        self.project = PMProject.objects.create(
            user=self.user, name='Scroll Project', project_path=project_path
        )
        self.service = BrowserPreviewService(self.project)
        self.state = {
            'app_url': 'http://127.0.0.1:5174', 'viewport': [1000, 800],
            'device_scale_factor': 2, 'cdp_port': 9999,
        }

    def _scroll_evaluations(self, conn):
        return [p for m, p in conn.calls
                if m == 'Runtime.evaluate' and 'scrollingElement' in p.get('expression', '')]

    def test_status_payload_carries_validated_scroll_metrics(self):
        conn = FakeCdpConnection()
        payload = self.service._status_payload(conn, self.state)
        self.assertEqual(payload['scroll'], {
            'x': 0.0, 'y': 640.0, 'width': 1000.0, 'height': 4000.0,
            'viewport_width': 1000.0, 'viewport_height': 800.0,
            'background': 'rgb(255, 255, 255)',
        })
        # A plain poll reads the offset straight away.
        self.assertNotIn('awaitPromise', self._scroll_evaluations(conn)[0])

    def test_page_supplied_garbage_is_dropped(self):
        conn = FakeCdpConnection()
        conn.scroll_metrics = {'x': 0, 'y': 'lots', 'height': 10}
        self.assertIsNone(self.service._status_payload(conn, self.state)['scroll'])
        conn = FakeCdpConnection()
        conn.scroll_metrics['background'] = 'red; background-image: url(x)'
        self.assertEqual(self.service._status_payload(conn, self.state)['scroll']['background'], '')

    def test_wheel_input_waits_for_the_scroll_to_land_and_clips_there(self):
        conn = FakeCdpConnection()
        entry = {'conn': conn, 'page': {}, 'lock': threading.Lock()}
        with mock.patch.object(self.service, '_require_state', return_value=self.state), \
                mock.patch('apps.Imagi.Build.services.browser_preview_service._pool_checkout',
                           return_value=entry):
            payload = self.service.dispatch_input(
                [{'kind': 'wheel', 'x': 10, 'y': 10, 'deltaY': 300}]
            )
        probe = self._scroll_evaluations(conn)[0]
        self.assertTrue(probe.get('awaitPromise'))
        self.assertIn('requestAnimationFrame', probe['expression'])
        self.assertEqual(payload['scroll']['y'], 640.0)
        # The 1x motion clip uses that settled offset, not a second probe.
        shot = [p for m, p in conn.calls if m == 'Page.captureScreenshot'][-1]
        self.assertEqual(shot['clip']['y'], 640.0)
        self.assertNotIn('Page.getLayoutMetrics', [m for m, _ in conn.calls])

    def test_scroll_event_scrolls_the_document_to_an_offset(self):
        method, params = self.service._translate_event({'kind': 'scroll', 'y': 1234.5}, 1000, 800)
        self.assertEqual(method, 'Runtime.evaluate')
        self.assertEqual(params['expression'], "window.scrollTo({top: 1234.50, behavior: 'instant'})")
        with self.assertRaises(BrowserPreviewError):
            self.service._translate_event({'kind': 'scroll', 'y': 'down'}, 1000, 800)

    def test_viewport_hides_native_scrollbars_before_the_metrics_override(self):
        conn = FakeCdpConnection()
        self.service._apply_viewport(conn, self.state)
        methods = [m for m, _ in conn.calls]
        self.assertEqual(methods, ['Emulation.setScrollbarsHidden', 'Emulation.setDeviceMetricsOverride'])


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

    def test_session_status_reports_not_running_when_idle(self):
        resp = self.client.get(reverse('api-preview', args=[self.project.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {'running': False})

    @patch.object(BrowserPreviewService, 'start')
    def test_session_start_passes_the_viewport_through(self, mock_start):
        mock_start.return_value = {'url': '/'}
        resp = self.client.post(
            reverse('api-preview', args=[self.project.id]),
            {'viewport': {'width': 390, 'height': 844}, 'device_scale_factor': 2},
            format='json',
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {'url': '/', 'running': True})
        mock_start.assert_called_once_with(viewport=(390, 844), device_scale_factor=2)

    @patch.object(BrowserPreviewService, 'start', side_effect=RuntimeError('npm install failed'))
    def test_session_start_failure_is_a_503_with_the_reason(self, _start):
        # The reason concerns the user's own project, so it is shown to them.
        resp = self.client.post(reverse('api-preview', args=[self.project.id]), {}, format='json')
        self.assertEqual(resp.status_code, 503)
        self.assertFalse(resp.json()['running'])
        self.assertIn('npm install failed', resp.json()['error'])

    def test_session_and_pages_of_another_users_project_are_404(self):
        other = User.objects.create_user(username='previewother', password='pw123456')
        theirs = PMProject.objects.create(
            user=other, name='Their Preview', project_path=self.project.project_path
        )
        for method, name in (('get', 'api-preview'), ('post', 'api-preview'),
                             ('delete', 'api-preview'), ('get', 'api-project-pages'),
                             ('get', 'api-preview-frame')):
            with self.subTest(method=method, name=name):
                resp = getattr(self.client, method)(reverse(name, args=[theirs.id]))
                self.assertEqual(resp.status_code, 404)

    def test_other_endpoints_report_browser_not_running_as_409(self):
        for name, body in (
            ('api-preview-backdrop', None),
            ('api-preview-input', '{"events": []}'),
            ('api-preview-navigate', '{"action": "reload"}'),
            ('api-preview-resize', '{"width": 800, "height": 600}'),
        ):
            url = reverse(name, args=[self.project.id])
            if body is None:
                resp = self.client.get(url)
            else:
                resp = self.client.post(url, data=body, content_type='application/json')
            self.assertEqual(resp.status_code, 409, name)
            self.assertFalse(resp.json()['running'])

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


class PreviewChildEnvTests(TestCase):
    """A generated project's processes must not inherit Imagi's secrets.

    The code under a preview is written by the user (or by the agent on their
    behalf) and runs in this same container, so the environment it is handed is
    an allowlist rather than a copy of Imagi's own.
    """

    def test_platform_secrets_are_not_passed_through(self):
        secrets = {
            'DJANGO_SECRET_KEY': 'super-secret',
            'DATABASE_URL': 'postgres://user:pw@host/db',
            'STRIPE_SECRET_KEY': 'sk_live_xxx',
            'STRIPE_WEBHOOK_SECRET': 'whsec_xxx',
            'OPENAI_KEY': 'sk-openai',
        }
        with patch.dict(os.environ, secrets):
            env = child_env()
        for name in secrets:
            self.assertNotIn(name, env)

    def test_essentials_survive_and_overrides_apply(self):
        with patch.dict(os.environ, {'PATH': '/usr/bin', 'HOME': '/home/app'}):
            env = child_env(PORT='5174', VITE_BACKEND_URL='http://localhost:8081')
        self.assertEqual(env['PATH'], '/usr/bin')
        self.assertEqual(env['HOME'], '/home/app')
        self.assertEqual(env['PORT'], '5174')
        self.assertEqual(env['VITE_BACKEND_URL'], 'http://localhost:8081')

    def test_path_is_never_empty(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertTrue(child_env()['PATH'])
