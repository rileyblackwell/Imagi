"""Bringing a project's preview up: readiness waits, the start lock, warm-up.

The wait between a finished first build and the founder seeing their app is
this code's to lose, so the invariants are about time: no fixed sleeps, a
warm-up that starts alongside the build, and a lock that keeps two starters
from launching two sessions.
"""

import os
import tempfile
import threading
import time
from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from apps.Imagi.Build.services import browser_preview_service, preview_service
from apps.Imagi.Build.services.browser_preview_service import start_preview_warmup
from apps.Imagi.Build.services.preview_service import (
    PreviewService,
    preview_start_lock,
    wait_for_listener,
)


class _Process:
    """Just enough of a Popen: poll() reports the exit code, or None while alive."""

    def __init__(self, exit_code=None):
        self.exit_code = exit_code

    def poll(self):
        return self.exit_code


class WaitForListenerTests(SimpleTestCase):
    def test_returns_the_moment_the_port_accepts(self):
        with patch.object(preview_service, 'port_accepting', return_value=True), \
                patch.object(preview_service.time, 'sleep') as sleep:
            self.assertIsNone(wait_for_listener(_Process(), 8080, timeout=5))
        sleep.assert_not_called()

    def test_keeps_polling_until_the_listener_appears(self):
        answers = iter([False, False, True])
        with patch.object(
            preview_service, 'port_accepting', side_effect=lambda *a, **k: next(answers)
        ), patch.object(preview_service.time, 'sleep') as sleep:
            self.assertIsNone(wait_for_listener(_Process(), 8080, timeout=5))
        self.assertEqual(sleep.call_count, 2)

    def test_reports_a_process_that_died_first(self):
        # A server that exits never listens; waiting out the timeout for it
        # would hide the exit code the caller needs to report.
        with patch.object(preview_service, 'port_accepting', return_value=False), \
                patch.object(preview_service.time, 'sleep'):
            self.assertEqual(wait_for_listener(_Process(exit_code=1), 8080, timeout=5), 1)

    def test_gives_up_at_the_timeout(self):
        with patch.object(preview_service, 'port_accepting', return_value=False), \
                patch.object(preview_service.time, 'sleep'):
            with self.assertRaises(TimeoutError):
                wait_for_listener(_Process(), 8080, timeout=0)


class DualStackStartTests(SimpleTestCase):
    """The start path waits on readiness, never on the clock."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(lambda: __import__('shutil').rmtree(self.tmp, ignore_errors=True))

    def _service(self):
        project = SimpleNamespace(
            id=1, pk=1, name='P', project_path=self.tmp, user=SimpleNamespace(id=1)
        )
        with override_settings(PROJECTS_ROOT=self.tmp):
            return PreviewService(project)

    def test_no_fixed_sleeps_between_server_starts(self):
        # Each server start returns once its port answers, so anything the
        # orchestration sleeps on top is pure waiting: eleven seconds of it,
        # before this test existed.
        service = self._service()
        with patch.object(service, '_start_django_backend', return_value=None), \
                patch.object(service, '_start_vuejs_frontend', return_value=None), \
                patch.object(service, '_save_port_state'), \
                patch.object(preview_service.time, 'sleep') as sleep:
            result = service._start_dual_stack_preview('/fe', '/be')
        self.assertTrue(result['success'])
        sleep.assert_not_called()

    def test_a_frontend_that_fails_takes_the_backend_down_with_it(self):
        service = self._service()
        with patch.object(service, '_start_django_backend', return_value=None), \
                patch.object(service, '_start_vuejs_frontend', return_value='vite exploded'), \
                patch.object(service, '_stop_django_backend') as stop_backend:
            with self.assertRaisesRegex(Exception, 'vite exploded'):
                service._start_dual_stack_preview('/fe', '/be')
        stop_backend.assert_called_once()


class PreviewStartLockTests(SimpleTestCase):
    def test_second_starter_waits_for_the_first(self):
        with tempfile.TemporaryDirectory() as pid_dir:
            order = []

            def starter(name, hold):
                with preview_start_lock(pid_dir, 'p1'):
                    order.append(f'{name}:in')
                    time.sleep(hold)
                    order.append(f'{name}:out')

            first = threading.Thread(target=starter, args=('a', 0.3))
            first.start()
            time.sleep(0.05)
            second = threading.Thread(target=starter, args=('b', 0))
            second.start()
            first.join()
            second.join()

            self.assertEqual(order, ['a:in', 'a:out', 'b:in', 'b:out'])
            # Released: nothing left behind to block the next start.
            self.assertFalse(os.path.exists(os.path.join(pid_dir, 'p1_preview_start.lock')))

    def test_projects_lock_independently(self):
        with tempfile.TemporaryDirectory() as pid_dir:
            with preview_start_lock(pid_dir, 'p1'):
                entered = []
                with preview_start_lock(pid_dir, 'p2', timeout=1):
                    entered.append(True)
            self.assertEqual(entered, [True])


class PreviewWarmupTests(SimpleTestCase):
    def _project(self):
        return SimpleNamespace(pk=5, id=5, name='P')

    def test_starts_the_session_on_a_background_thread(self):
        with patch.object(
            browser_preview_service.BrowserPreviewService, '__init__', return_value=None
        ) as init, patch.object(
            browser_preview_service.BrowserPreviewService, 'start',
            return_value={'running': True},
        ) as start:
            thread = start_preview_warmup(self._project())
            self.assertIsNotNone(thread)
            thread.join(5)
        init.assert_called_once()
        start.assert_called_once()

    def test_a_failed_warmup_is_logged_not_raised(self):
        # The workspace's own start() is the call that reports failures to
        # the founder; a warm-up that could not run must not leave anything
        # behind but a log line.
        with patch.object(
            browser_preview_service.BrowserPreviewService, '__init__', return_value=None
        ), patch.object(
            browser_preview_service.BrowserPreviewService, 'start',
            side_effect=RuntimeError('no chromium'),
        ), self.assertLogs(browser_preview_service.logger, level='WARNING') as logs:
            thread = start_preview_warmup(self._project())
            thread.join(5)
        self.assertIn('warm-up', logs.output[0])

    @override_settings(BROWSER_PREVIEW_PREWARM_ON_CREATE=False)
    def test_can_be_switched_off(self):
        with patch.object(browser_preview_service.BrowserPreviewService, 'start') as start:
            self.assertIsNone(start_preview_warmup(self._project()))
        start.assert_not_called()


class StartTakesTheLockTests(SimpleTestCase):
    def test_start_runs_under_the_projects_lock(self):
        # Reattaching is what makes the warm-up safe: the second starter must
        # see the first's session, which only holds if it waits for it.
        project = SimpleNamespace(id=9, pk=9, name='P', project_path='/x', user=SimpleNamespace(id=1))
        with tempfile.TemporaryDirectory() as root, override_settings(PROJECTS_ROOT=root):
            service = browser_preview_service.BrowserPreviewService(project)
            with patch.object(browser_preview_service, 'preview_start_lock') as lock, \
                    patch.object(service, '_start_locked', return_value={'running': True}) as locked:
                service.start(viewport=(800, 600))
            lock.assert_called_once_with(service.pid_dir, '9')
            locked.assert_called_once_with((800, 600), None)
