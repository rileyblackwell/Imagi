"""Prewarming previews at sign-in, and the bounds that keep it cheap.

The bet is that the projects someone opened last are the ones they open next,
so their previews are started before the workspace asks. Every prewarmed
session costs memory until it is reaped, so the tests pin the bounds: how
many projects, a host-wide session cap, and a shorter idle limit for a
session nobody opened.
"""

import json
import os
import shutil
import tempfile
import threading
import time
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from apps.Imagi.Build.services import browser_preview_service
from apps.Imagi.Build.services.browser_preview_service import (
    BrowserPreviewService,
    _evict_sessions,
    make_room_for_session,
    prewarm_recent_previews,
    reap_idle_sessions,
)
from apps.Imagi.ProjectManager.models import Project

User = get_user_model()


class _Root:
    """A private PROJECTS_ROOT, so no real session on this machine counts."""

    def make_root(self):
        root = tempfile.mkdtemp(prefix='prewarm_root_')
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        overrides = override_settings(PROJECTS_ROOT=root)
        overrides.enable()
        self.addCleanup(overrides.disable)
        return root


class _RecentProjects(_Root):
    def setUp(self):
        self.make_root()
        self.user = User.objects.create_user(username='prewarm', password='pw123456')
        now = timezone.now()
        self.projects = {}
        # Opened 1, 2, 3 and 4 hours ago, plus one never opened.
        for hours, name in ((3, 'c'), (1, 'a'), (4, 'd'), (2, 'b'), (None, 'never')):
            project = Project.objects.create(user=self.user, name=name, project_path=f'/tmp/prewarm-{name}')
            if hours is not None:
                Project.objects.filter(pk=project.pk).update(last_opened_at=now - timedelta(hours=hours))
            self.projects[name] = project

    def _prewarm(self, running=(), live=0):
        started = []
        kept = self.kept = []

        def start(service, **kwargs):
            started.append((service.project.name, kwargs))
            return {'running': True}

        with patch.object(BrowserPreviewService, 'start', autospec=True, side_effect=start), \
                patch.object(BrowserPreviewService, 'keep_alive', autospec=True,
                             side_effect=lambda service: kept.append(service.project.name)
                             or service.project.name in running), \
                patch.object(browser_preview_service, 'live_session_count', return_value=live), \
                patch('apps.Imagi.Build.services.project_files_service.ensure_working_copy'):
            thread = prewarm_recent_previews(self.user)
            if thread is not None:
                thread.join(5)
        return started


class PrewarmRecentPreviewsTests(_RecentProjects, TestCase):
    def test_starts_the_three_most_recently_opened_newest_first(self):
        started = self._prewarm()
        self.assertEqual([name for name, _ in started], ['a', 'b', 'c'])
        self.assertTrue(all(
            kwargs == {'viewport': None, 'device_scale_factor': None, 'prewarm': True}
            for _, kwargs in started
        ))

    def test_keeps_running_ones_warm_instead_of_restarting_them(self):
        started = self._prewarm(running={'a'})
        self.assertEqual([name for name, _ in started], ['b', 'c'])
        # Every heartbeat touches each of the three, so none idles out while
        # the owner is signed in.
        self.assertEqual(self.kept, ['a', 'b', 'c'])

    def test_a_heartbeat_during_a_prewarm_adds_nothing(self):
        release = threading.Event()

        def slow_start(service, **_kwargs):
            release.wait(5)

        with patch.object(BrowserPreviewService, 'start', autospec=True, side_effect=slow_start), \
                patch.object(BrowserPreviewService, 'keep_alive', return_value=False), \
                patch.object(browser_preview_service, 'live_session_count', return_value=0), \
                patch('apps.Imagi.Build.services.project_files_service.ensure_working_copy'):
            first = prewarm_recent_previews(self.user)
            self.assertIsNone(prewarm_recent_previews(self.user))
            release.set()
            first.join(5)

    @override_settings(BROWSER_PREVIEW_MAX_SESSIONS=5)
    def test_starts_nothing_once_the_host_is_at_its_session_cap(self):
        self.assertEqual(self._prewarm(live=5), [])

    @override_settings(BROWSER_PREVIEW_PREWARM_RECENT=0)
    def test_can_be_switched_off(self):
        self.assertIsNone(prewarm_recent_previews(self.user))

    def test_never_touches_another_users_projects(self):
        other = User.objects.create_user(username='someone-else', password='pw123456')
        Project.objects.create(user=other, name='theirs', project_path='/tmp/prewarm-theirs',
                               last_opened_at=timezone.now())
        self.assertNotIn('theirs', [name for name, _ in self._prewarm()])

    def test_a_failed_prewarm_moves_on_to_the_next_project(self):
        calls = []

        def start(service, **_kwargs):
            calls.append(service.project.name)
            if service.project.name == 'a':
                raise RuntimeError('vite exploded')

        with patch.object(BrowserPreviewService, 'start', autospec=True, side_effect=start), \
                patch.object(BrowserPreviewService, 'keep_alive', return_value=False), \
                patch.object(browser_preview_service, 'live_session_count', return_value=0), \
                patch('apps.Imagi.Build.services.project_files_service.ensure_working_copy'), \
                self.assertLogs(browser_preview_service.logger, level='WARNING'):
            prewarm_recent_previews(self.user).join(5)
        self.assertEqual(calls, ['a', 'b', 'c'])


class LeastRecentlyUsedEvictionTests(_RecentProjects, TestCase):
    """The owner's previews beyond the three most recently used are stopped."""

    def _evicted_by_prewarm(self):
        with patch.object(browser_preview_service, '_evict_sessions') as evict:
            self._prewarm()
        return [p.name for p in evict.call_args.args[0]]

    def test_the_least_recently_opened_make_way(self):
        self.assertEqual(self._evicted_by_prewarm(), ['d', 'never'])

    def test_using_a_preview_counts_as_recent_use(self):
        # 'd' was opened longest ago but its preview was in use a minute ago,
        # so 'c' (opened 3 hours ago, untouched since) is the one to go.
        service = BrowserPreviewService(self.projects['d'])
        with open(service.state_file, 'w') as f:
            json.dump({'pid': 1, 'last_used': time.time() - 60}, f)
        started = self._prewarm()
        self.assertEqual([name for name, _ in started], ['d', 'a', 'b'])
        self.assertEqual(self._evicted_by_prewarm(), ['c', 'never'])

    def _evict(self, last_used):
        project = self.projects['d']
        service = BrowserPreviewService(project)
        with open(service.state_file, 'w') as f:
            json.dump({'pid': 1, 'last_used': last_used}, f)
        with patch.object(BrowserPreviewService, 'is_running', return_value=True), \
                patch.object(BrowserPreviewService, 'stop', autospec=True) as stop:
            _evict_sessions([project])
        return stop.called

    def test_eviction_stops_an_idle_preview(self):
        self.assertTrue(self._evict(time.time() - 600))

    def test_eviction_spares_a_preview_on_screen(self):
        self.assertFalse(self._evict(time.time() - 5))

    def test_opening_a_project_evicts_at_once(self):
        token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        with patch.object(BrowserPreviewService, 'start', return_value={'path': '/'}), \
                patch('apps.Imagi.Build.api.views.evict_least_recent_previews') as evict:
            self.client.post(reverse('api-preview', args=[self.projects['d'].id]), {}, format='json')
        evict.assert_called_once_with(self.user)


@override_settings(BROWSER_PREVIEW_MAX_SESSIONS=3)
class HostSessionCapTests(_Root, SimpleTestCase):
    """At the host's cap, a workspace opening pushes out the least recently used session."""

    def setUp(self):
        self.user_dir = os.path.join(self.make_root(), '1')
        os.makedirs(self.user_dir)
        self.now = time.time()

    def _session(self, stem, last_used=None):
        path = os.path.join(self.user_dir, f'{stem}_browser.json')
        state = {'pid': os.getpid(), 'last_active': self.now}
        if last_used is not None:
            state['last_used'] = self.now - last_used
        with open(path, 'w') as f:
            json.dump(state, f)
        return path

    def _make_room(self, exclude=None):
        with patch.object(browser_preview_service, '_shut_down_session') as shut:
            make_room_for_session(exclude=exclude)
        return [os.path.basename(c.args[0]) for c in shut.call_args_list]

    def test_below_the_cap_nothing_goes(self):
        self._session('1', last_used=600)
        self._session('2', last_used=600)
        self.assertEqual(self._make_room(), [])

    def test_an_unopened_prewarm_goes_before_any_used_session(self):
        self._session('1', last_used=900)
        self._session('2')  # prewarmed, never used
        self._session('3', last_used=300)
        self.assertEqual(self._make_room(), ['2_browser.json'])

    def test_the_least_recently_used_goes(self):
        self._session('1', last_used=300)
        self._session('2', last_used=900)
        self._session('3', last_used=600)
        self.assertEqual(self._make_room(), ['2_browser.json'])

    def test_a_session_on_screen_is_never_pushed_out(self):
        self._session('1', last_used=5)
        self._session('2', last_used=10)
        self._session('3', last_used=20)
        self.assertEqual(self._make_room(), [])

    def test_the_session_being_started_does_not_count(self):
        self._session('1', last_used=300)
        self._session('2', last_used=900)
        mine = self._session('3', last_used=1200)
        self.assertEqual(self._make_room(exclude=mine), [])


class KeepAliveTests(_Root, SimpleTestCase):
    def test_touches_a_running_session_and_leaves_it_prewarmed(self):
        root = self.make_root()
        project = SimpleNamespace(id=4, pk=4, name='P', project_path=root, user=SimpleNamespace(id=1))
        service = BrowserPreviewService(project)
        with open(service.state_file, 'w') as f:
            json.dump({'pid': 1, 'cdp_port': 9301, 'last_active': time.time() - 500, 'prewarmed': True}, f)
        with patch.object(service, '_browser_alive', return_value=True):
            self.assertTrue(service.keep_alive())
        with open(service.state_file) as f:
            state = json.load(f)
        self.assertGreater(state['last_active'], time.time() - 5)
        self.assertTrue(state['prewarmed'])
        # Kept warm isn't used: it doesn't move up the eviction order.
        self.assertNotIn('last_used', state)

    def test_reports_a_session_that_is_not_running(self):
        root = self.make_root()
        project = SimpleNamespace(id=5, pk=5, name='P', project_path=root, user=SimpleNamespace(id=1))
        self.assertFalse(BrowserPreviewService(project).keep_alive())


@override_settings(BROWSER_PREVIEW_IDLE_TIMEOUT=1800, BROWSER_PREVIEW_PREWARM_IDLE_TIMEOUT=600)
class PrewarmedSessionReapingTests(_Root, SimpleTestCase):
    def setUp(self):
        self.user_dir = os.path.join(self.make_root(), '1')
        os.makedirs(self.user_dir)

    def _session(self, stem, idle_seconds, prewarmed):
        path = os.path.join(self.user_dir, f'{stem}_browser.json')
        with open(path, 'w') as f:
            json.dump({'pid': 0, 'last_active': time.time() - idle_seconds, 'prewarmed': prewarmed}, f)
        return path

    def test_an_unopened_prewarmed_session_goes_after_the_shorter_limit(self):
        prewarmed = self._session('1', idle_seconds=700, prewarmed=True)
        opened = self._session('2', idle_seconds=700, prewarmed=False)
        reap_idle_sessions()
        self.assertFalse(os.path.exists(prewarmed))
        self.assertTrue(os.path.exists(opened))

    def test_an_opened_session_keeps_the_full_limit(self):
        opened = self._session('2', idle_seconds=1900, prewarmed=False)
        reap_idle_sessions()
        self.assertFalse(os.path.exists(opened))


class PrewarmEndpointTests(_Root, APITestCase):
    def setUp(self):
        self.make_root()
        cache.clear()
        self.addCleanup(cache.clear)
        self.user = User.objects.create_user(username='prewarm-api', password='pw123456')
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_requires_auth(self):
        self.client.credentials()
        self.assertEqual(self.client.post(reverse('api-preview-prewarm')).status_code, 401)

    def test_answers_at_once_and_throttles_repeats(self):
        with patch('apps.Imagi.Build.api.views.prewarm_recent_previews', return_value=object()) as prewarm:
            first = self.client.post(reverse('api-preview-prewarm'))
            second = self.client.post(reverse('api-preview-prewarm'))
        self.assertEqual(first.status_code, 202)
        self.assertTrue(first.json()['started'])
        self.assertFalse(second.json()['started'])
        prewarm.assert_called_once_with(self.user, viewport=None, device_scale_factor=None)

    def test_passes_on_the_panes_last_size(self):
        with patch('apps.Imagi.Build.api.views.prewarm_recent_previews', return_value=object()) as prewarm:
            self.client.post(
                reverse('api-preview-prewarm'),
                {'viewport': {'width': 900, 'height': 700}, 'device_scale_factor': 2},
                format='json',
            )
        prewarm.assert_called_once_with(self.user, viewport=(900, 700), device_scale_factor=2.0)

    def test_ignores_a_malformed_size(self):
        with patch('apps.Imagi.Build.api.views.prewarm_recent_previews', return_value=object()) as prewarm:
            self.client.post(
                reverse('api-preview-prewarm'),
                {'viewport': {'width': 'wide'}, 'device_scale_factor': 'retina'},
                format='json',
            )
        prewarm.assert_called_once_with(self.user, viewport=None, device_scale_factor=None)


class OpeningAProjectRanksItTests(_Root, APITestCase):
    def test_starting_the_preview_records_when_it_was_opened(self):
        self.make_root()
        user = User.objects.create_user(username='opener', password='pw123456')
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        project = Project.objects.create(user=user, name='Opened', project_path='/tmp/prewarm-opened')
        updated_at = Project.objects.get(pk=project.pk).updated_at

        with patch.object(BrowserPreviewService, 'start', return_value={'path': '/'}), \
                patch('apps.Imagi.Build.api.views.evict_least_recent_previews'):
            resp = self.client.post(reverse('api-preview', args=[project.id]), {}, format='json')
        self.assertEqual(resp.status_code, 200)
        project.refresh_from_db()
        self.assertIsNotNone(project.last_opened_at)
        # Opening isn't editing.
        self.assertEqual(project.updated_at, updated_at)
