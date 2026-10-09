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
import time
from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from apps.Imagi.Build.services import browser_preview_service
from apps.Imagi.Build.services.browser_preview_service import (
    BrowserPreviewService,
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


class PrewarmRecentPreviewsTests(_Root, TestCase):
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

        def start(service, **kwargs):
            started.append((service.project.name, kwargs))
            return {'running': True}

        with patch.object(BrowserPreviewService, 'start', autospec=True, side_effect=start), \
                patch.object(BrowserPreviewService, 'is_running', autospec=True,
                             side_effect=lambda service: service.project.name in running), \
                patch.object(browser_preview_service, 'live_session_count', return_value=live), \
                patch('apps.Imagi.Build.services.project_files_service.ensure_working_copy'):
            thread = prewarm_recent_previews(self.user)
            if thread is not None:
                thread.join(5)
        return started

    def test_starts_the_three_most_recently_opened_newest_first(self):
        started = self._prewarm()
        self.assertEqual([name for name, _ in started], ['a', 'b', 'c'])
        self.assertTrue(all(kwargs == {'prewarm': True} for _, kwargs in started))

    def test_skips_projects_already_running(self):
        started = self._prewarm(running={'a'})
        self.assertEqual([name for name, _ in started], ['b', 'c'])

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
                patch.object(BrowserPreviewService, 'is_running', return_value=False), \
                patch.object(browser_preview_service, 'live_session_count', return_value=0), \
                patch('apps.Imagi.Build.services.project_files_service.ensure_working_copy'), \
                self.assertLogs(browser_preview_service.logger, level='WARNING'):
            prewarm_recent_previews(self.user).join(5)
        self.assertEqual(calls, ['a', 'b', 'c'])


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
        prewarm.assert_called_once_with(self.user)


class OpeningAProjectRanksItTests(_Root, APITestCase):
    def test_starting_the_preview_records_when_it_was_opened(self):
        self.make_root()
        user = User.objects.create_user(username='opener', password='pw123456')
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        project = Project.objects.create(user=user, name='Opened', project_path='/tmp/prewarm-opened')
        updated_at = Project.objects.get(pk=project.pk).updated_at

        with patch.object(BrowserPreviewService, 'start', return_value={'path': '/'}):
            resp = self.client.post(reverse('api-preview', args=[project.id]), {}, format='json')
        self.assertEqual(resp.status_code, 200)
        project.refresh_from_db()
        self.assertIsNotNone(project.last_opened_at)
        # Opening isn't editing.
        self.assertEqual(project.updated_at, updated_at)
