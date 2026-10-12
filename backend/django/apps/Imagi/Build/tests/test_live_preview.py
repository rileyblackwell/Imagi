"""The live preview (PREVIEW_V2): the app itself in an iframe on a preview host.

Covers the pieces that decide who can reach a preview and what it costs:
route files the edge reads, the wrapper configs around the project's own,
logs and console errors read back for the drawer and the agent, the memory
budget and idle shutdown, and the API's gating. The edge proxy itself is
tested in preview_edge.test.mjs, which this file runs through node.
"""

import json
import os
import shutil
import subprocess
import tempfile
import time
from types import SimpleNamespace
from unittest import skipUnless
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, override_settings
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from apps.Imagi.Build.services import live_preview_service as live
from apps.Imagi.Build.services.preview_service import PreviewService
from apps.Imagi.ProjectManager.models import Project

User = get_user_model()
HERE = os.path.dirname(os.path.abspath(__file__))


class _Root:
    def make_root(self):
        root = tempfile.mkdtemp(prefix='live_root_')
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        overrides = override_settings(PROJECTS_ROOT=root, PREVIEW_ROUTES_DIR='')
        overrides.enable()
        self.addCleanup(overrides.disable)
        return root


class RouteTests(_Root, SimpleTestCase):
    def setUp(self):
        self.root = self.make_root()

    def test_tokens_are_long_and_url_safe(self):
        token = live.mint_token()
        self.assertRegex(token, live.TOKEN_RE)
        self.assertNotEqual(token, live.mint_token())

    def test_route_files_are_written_and_revoked(self):
        token = live.mint_token()
        live.write_route(token, 5174, 8080)
        path = os.path.join(live.routes_dir(), f'{token}.json')
        with open(path) as f:
            self.assertEqual(json.load(f), {'frontend_port': 5174, 'backend_port': 8080})
        self.assertEqual(os.stat(live.routes_dir()).st_mode & 0o777, 0o700)
        live.remove_route(token)
        self.assertFalse(os.path.exists(path))

    def test_a_token_cannot_name_a_path(self):
        with self.assertRaises(ValueError):
            live.write_route('../' + 'a' * 40, 5174, 8080)
        live.remove_route('../../etc/passwd')  # ignored, never raises


class WrapperTests(SimpleTestCase):
    def setUp(self):
        self.config = live.LiveConfig(token='t' * 43, public_origin='https://imagi-preview.up.railway.app')

    @override_settings(PREVIEW_PARENT_ORIGINS=['https://imagi.up.railway.app'], PREVIEW_PARENT_ORIGIN_RE='')
    def test_bridge_only_answers_the_workspace(self):
        source = live.bridge_source(self.config)
        self.assertNotIn('__IMAGI_PARENT_RE__', source)
        self.assertIn(json.dumps('^(https://imagi\\.up\\.railway\\.app)$'), source)
        self.assertIn(json.dumps('/s/' + 't' * 43), source)

    def test_vite_wrapper_serves_under_the_token_and_frees_hmr(self):
        source = live.vite_wrapper_source('/p/frontend/vuejs/vite.config.ts', self.config)
        self.assertIn('import userConfig from "/p/frontend/vuejs/vite.config.ts"', source)
        self.assertIn(f'"base": "/s/{"t" * 43}/"', source)
        self.assertIn('"host": "imagi-preview.up.railway.app"', source)
        self.assertIn("apply: 'serve'", source)  # never in the app's own build
        for key in ('host', 'port', 'clientPort', 'protocol', 'path'):
            self.assertIn(f'delete hmr.{key}', source)

    def test_django_wrapper_trusts_the_preview_origin(self):
        source = live.django_wrapper_source('mysite.settings', self.config)
        self.assertIn('from mysite.settings import *', source)
        self.assertIn("'https://imagi-preview.up.railway.app'", source)
        self.assertIn("SESSION_COOKIE_SAMESITE = 'None'", source)
        namespace = {}
        exec(source.replace('from mysite.settings import *  # noqa: F401,F403', "ALLOWED_HOSTS = ['example.com']"), namespace)
        self.assertIn('imagi-preview.up.railway.app', namespace['ALLOWED_HOSTS'])
        self.assertIn('example.com', namespace['ALLOWED_HOSTS'])

    def test_plain_http_origin_keeps_default_cookies(self):
        local = live.LiveConfig(token='t' * 43, public_origin='http://127.0.0.1:8790')
        self.assertNotIn('SAMESITE', live.django_wrapper_source('mysite.settings', local))
        self.assertEqual(local.host, '127.0.0.1')


class SessionFilesTests(_Root, SimpleTestCase):
    """Logs and console errors, read from a session's files."""

    def setUp(self):
        self.root = self.make_root()
        project_dir = os.path.join(self.root, '7', 'Demo')
        os.makedirs(project_dir)
        self.project = SimpleNamespace(pk=7, id=7, user=SimpleNamespace(pk=1, id=1), project_path=project_dir, name='Demo')
        pid_dir = os.path.join(self.root, '7')

        def fake_init(servers, project):
            servers.project = project
            servers.pid_dir = pid_dir
            servers.backend_log_file = os.path.join(pid_dir, 'backend.log')
            servers.frontend_log_file = os.path.join(pid_dir, 'frontend.log')

        with patch.object(PreviewService, '__init__', fake_init):
            self.service = live.LivePreviewService(self.project)

    def test_logs_return_whole_lines_since_an_offset(self):
        with open(self.service.servers.backend_log_file, 'w') as f:
            f.write('\x1b[32mStarting development server\x1b[0m\nGET / 200\npartial')
        first = self.service.logs()
        self.assertEqual(first['backend']['lines'], ['Starting development server', 'GET / 200'])
        self.assertTrue(first['backend']['reset'])
        self.assertEqual(first['frontend'], {'offset': 0, 'lines': [], 'reset': True})
        with open(self.service.servers.backend_log_file, 'a') as f:
            f.write(' line\nnext\n')
        more = self.service.logs({'backend': first['backend']['offset']})
        self.assertEqual(more['backend']['lines'], ['partial line', 'next'])
        self.assertFalse(more['backend']['reset'])
        # A log that shrank (the server restarted) starts over.
        with open(self.service.servers.backend_log_file, 'w') as f:
            f.write('fresh\n')
        again = self.service.logs({'backend': more['backend']['offset']})
        self.assertTrue(again['backend']['reset'])
        self.assertEqual(again['backend']['lines'], ['fresh'])

    def test_only_console_errors_are_kept_for_the_agent(self):
        kept = self.service.record_console([
            {'level': 'log', 'text': 'hello', 'ts': 1},
            {'level': 'error', 'text': '  TypeError: x  ', 'ts': 5000},
            {'level': 'error', 'text': ''},
            'junk',
        ])
        self.assertEqual(kept, [{'level': 'error', 'text': 'TypeError: x', 'ts': 5000}])
        self.service.record_console([{'level': 'error', 'text': 'later', 'ts': 9000}])
        self.assertEqual(self.service.console_errors_since(6000), ['later'])
        for i in range(live.MAX_CONSOLE_ENTRIES + 5):
            self.service.record_console([{'level': 'error', 'text': f'e{i}', 'ts': 10000 + i}])
        with open(self.service.console_file) as f:
            self.assertEqual(len(json.load(f)), live.MAX_CONSOLE_ENTRIES)

    def test_unknown_actions_are_refused(self):
        with self.assertRaises(ValueError):
            self.service.action('rm -rf')

    def test_an_agents_browser_action_is_shown_while_recent(self):
        self.assertIsNone(self.service.agent_activity())
        self.service.record_agent_activity('/book', 'left_click', 'Coordinator')
        self.assertEqual(
            {k: v for k, v in self.service.agent_activity().items() if k != 'at'},
            {'path': '/book', 'action': 'left_click', 'label': 'Coordinator'},
        )
        with patch.object(live.time, 'time', return_value=time.time() + live.AGENT_ACTIVITY_FRESH_S + 1):
            self.assertIsNone(self.service.agent_activity())


class HostPolicyTests(_Root, SimpleTestCase):
    """Idle shutdown and the memory budget."""

    def setUp(self):
        self.root = self.make_root()
        self.stopped = []
        stop = patch.object(live, 'shut_down_live', side_effect=lambda prefix: self.stopped.append(os.path.basename(prefix)))
        stop.start()
        self.addCleanup(stop.stop)

    def _session(self, name, **state):
        folder = os.path.join(self.root, name)
        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, f'{name}{live.LIVE_STATE_SUFFIX}'), 'w') as f:
            json.dump(state, f)

    @override_settings(PREVIEW_LIVE_IDLE_TIMEOUT=600, PREVIEW_LIVE_PREWARM_IDLE_TIMEOUT=300)
    def test_idle_sessions_stop_and_prewarmed_ones_sooner(self):
        now = time.time()
        self._session('viewed', last_active=now - 30)
        self._session('idle', last_active=now - 700)
        self._session('warm_unused', last_active=now - 400, prewarmed=True)
        self._session('warm_fresh', last_active=now - 100, prewarmed=True)
        live.reap_idle_live_sessions()
        self.assertCountEqual(self.stopped, ['idle', 'warm_unused'])

    @override_settings(PREVIEW_MEMORY_BUDGET_MB=1000)
    def test_budget_evicts_least_recently_used_but_never_one_in_use(self):
        now = time.time()
        self._session('old', last_used=now - 3000)
        self._session('newer', last_used=now - 600)
        self._session('in_use', last_used=now - 10)
        self._session('warm', last_used=now - 100, prewarmed=True)
        with patch.object(live, 'session_rss_mb', return_value=300):
            live.make_room()
        # 4 x 300 + 300 for the new one: two must go, prewarmed first.
        self.assertEqual(self.stopped, ['warm', 'old'])

    @override_settings(PREVIEW_MEMORY_BUDGET_MB=500)
    def test_over_budget_beats_closing_a_preview_someone_is_viewing(self):
        self._session('in_use', last_used=time.time())
        with patch.object(live, 'session_rss_mb', return_value=400):
            live.make_room()
        self.assertEqual(self.stopped, [])

    def test_viewer_activity_keeps_dev_servers_up(self):
        self._session('a', last_active=time.time())
        prefix = os.path.join(self.root, 'a', 'a')
        self.assertTrue(live.live_session_active(prefix))
        self.assertFalse(live.live_session_active(prefix, within=-1))
        self.assertFalse(live.live_session_active(os.path.join(self.root, 'none')))

    def test_migration_files_are_recognised(self):
        self.assertTrue(live.is_migration_file('backend/django/apps/shop/migrations/0002_order.py'))
        self.assertFalse(live.is_migration_file('backend/django/apps/shop/migrations/__init__.py'))
        self.assertFalse(live.is_migration_file('backend/django/apps/shop/models.py'))


class MigrateStampTests(_Root, SimpleTestCase):
    def test_migrate_is_skipped_until_a_migration_changes(self):
        root = self.make_root()
        backend = os.path.join(root, 'backend')
        os.makedirs(os.path.join(backend, 'shop', 'migrations'))
        servers = PreviewService.__new__(PreviewService)
        servers.migrate_stamp_file = os.path.join(root, 'stamp')
        servers.backend_log_file = os.path.join(root, 'backend.log')
        done = SimpleNamespace(returncode=0, stdout='OK\n', stderr='')
        with patch('apps.Imagi.Build.services.preview_service.subprocess.run', return_value=done) as run:
            self.assertIsNone(servers.run_migrations(backend, env={}))
            self.assertIsNone(servers.run_migrations(backend, env={}))
            self.assertEqual(run.call_count, 1)
            with open(os.path.join(backend, 'shop', 'migrations', '0001_initial.py'), 'w') as f:
                f.write('# new\n')
            servers.run_migrations(backend, env={})
            self.assertEqual(run.call_count, 2)
            servers.run_migrations(backend, env={}, force=True)
            self.assertEqual(run.call_count, 3)


class LiveApiTests(_Root, APITestCase):
    def setUp(self):
        self.make_root()
        self.user = User.objects.create_user(username='owner', password='pw123456')
        self.other = User.objects.create_user(username='other', password='pw123456')
        self.project = Project.objects.create(user=self.user, name='Demo')
        self.token = Token.objects.create(user=self.user)

    def _auth(self, user=None):
        token = self.token if user is None else Token.objects.create(user=user)
        return {'HTTP_AUTHORIZATION': f'Token {token.key}'}

    def test_config_says_which_preview_to_show(self):
        self.client.force_authenticate(self.user)
        with override_settings(PREVIEW_V2=True):
            self.assertEqual(self.client.get('/api/v1/builder/preview/config/').json(), {'mode': 'live'})
        with override_settings(PREVIEW_V2=False):
            self.assertEqual(self.client.get('/api/v1/builder/preview/config/').json(), {'mode': 'stream'})

    def test_keeps_the_three_most_recently_opened_projects_running(self):
        from datetime import timedelta
        from django.utils import timezone

        now = timezone.now()
        projects = []
        for age in (4, 1, 3, 2):
            project = Project.objects.create(user=self.user, name=f'P{age}', project_dir=f'p{age}')
            Project.objects.filter(pk=project.pk).update(last_opened_at=now - timedelta(hours=age))
            projects.append(project)
        started = []

        class FakeService:
            def __init__(self, project):
                self.project = project

            def is_running(self):
                return False

            def start(self, prewarm=False):
                started.append((self.project.name, prewarm))

        with patch.object(live, 'LivePreviewService', FakeService), \
                patch('apps.Imagi.Build.services.project_files_service.ensure_working_copy'):
            live.prewarm_recent(self.user).join(5)
        self.assertEqual(started, [('P1', True), ('P2', True), ('P3', True)])

    def test_live_endpoints_are_off_without_the_flag(self):
        url = f'/api/v1/builder/{self.project.id}/preview/status/'
        with override_settings(PREVIEW_V2=False):
            res = self.client.post(url, {}, format='json', **self._auth())
        self.assertEqual(res.status_code, 404)

    @override_settings(PREVIEW_V2=True)
    def test_owner_only(self):
        url = f'/api/v1/builder/{self.project.id}/preview/status/'
        self.assertEqual(self.client.post(url, {}, format='json').status_code, 401)
        self.assertEqual(self.client.post(url, {}, format='json', **self._auth(self.other)).status_code, 404)

    @override_settings(PREVIEW_V2=True)
    def test_status_records_console_errors(self):
        url = f'/api/v1/builder/{self.project.id}/preview/status/'
        with patch.object(live.LivePreviewService, 'status', return_value={'running': True}), \
                patch.object(live.LivePreviewService, 'record_console', return_value=[]) as record:
            res = self.client.post(url, {'console_errors': [{'level': 'error', 'text': 'x', 'ts': 1}], 'visible': True},
                                   format='json', **self._auth())
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['running'], True)
        record.assert_called_once_with([{'level': 'error', 'text': 'x', 'ts': 1}])

    @override_settings(PREVIEW_V2=True)
    def test_bad_requests(self):
        base = f'/api/v1/builder/{self.project.id}/preview'
        self.assertEqual(self.client.post(f'{base}/action/', {'action': 'shell'}, format='json', **self._auth()).status_code, 400)
        self.assertEqual(self.client.get(f'{base}/logs/?backend=x', **self._auth()).status_code, 400)
        self.assertEqual(self.client.get(f'{base}/action/', **self._auth()).status_code, 405)


@skipUnless(shutil.which('node'), 'node is not installed')
class EdgeTests(SimpleTestCase):
    def test_edge_proxy(self):
        result = subprocess.run(
            ['node', '--test', os.path.join(HERE, 'preview_edge.test.mjs')],
            capture_output=True, text=True, timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stdout[-4000:] + result.stderr[-2000:])
