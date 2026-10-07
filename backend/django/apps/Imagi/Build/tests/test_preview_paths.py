"""Tests that a project's name can never steer a preview sidecar path.

The preview services keep per-project PID, log, port-state and browser-session
files beside the project directory. Those filenames used to interpolate
``project.name`` — a free-form, renamable field — which let a crafted name
write, read-and-kill, and rmtree outside the owner's own directory, and let one
tenant's browser-preview state resolve to another's live CDP session.

Also covers the browser preview's validation of client-supplied navigation
paths and viewport sizes.
"""

import os
import shutil
import tempfile
from types import SimpleNamespace

from django.test import SimpleTestCase, override_settings

from apps.Imagi.Build.services import preview_service
from apps.Imagi.Build.services.browser_preview_service import (
    DEFAULT_VIEWPORT,
    MAX_VIEWPORT,
    MIN_VIEWPORT,
    BrowserPreviewError,
    BrowserPreviewService,
)
from apps.Imagi.Build.services.preview_service import sidecar_path, sidecar_stem


def _project(pk, name, user_id=1):
    return SimpleNamespace(id=pk, name=name, user=SimpleNamespace(id=user_id))


class SidecarStemTests(SimpleTestCase):
    def test_stem_is_the_project_id_not_the_name(self):
        self.assertEqual(sidecar_stem(_project(7, 'My Shop')), '7')

    def test_traversing_name_does_not_reach_the_stem(self):
        self.assertEqual(sidecar_stem(_project(7, '../9/Their Shop')), '7')

    def test_absolute_name_does_not_reach_the_stem(self):
        self.assertEqual(sidecar_stem(_project(7, '/etc/cron.d/x')), '7')


class SidecarPathTests(SimpleTestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        self.pid_dir = os.path.join(self.root, '1')
        os.makedirs(self.pid_dir)

    def test_ordinary_stem_resolves_inside_the_directory(self):
        path = sidecar_path(self.pid_dir, '7', '_frontend.pid')
        self.assertEqual(path, os.path.join(os.path.realpath(self.pid_dir), '7_frontend.pid'))

    def test_relative_escape_is_refused(self):
        # The legacy name sweep still passes user-controlled strings here.
        self.assertIsNone(sidecar_path(self.pid_dir, '../9/Their Shop', '_frontend.pid'))

    def test_absolute_escape_is_refused(self):
        self.assertIsNone(sidecar_path(self.pid_dir, '/etc/cron.d/x', '_frontend.log'))


class PreviewServicePathTests(SimpleTestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)

    def test_sidecar_files_stay_in_the_users_directory(self):
        project = _project(7, '../9/Their Shop', user_id=1)
        with override_settings(PROJECTS_ROOT=self.root):
            service = preview_service.PreviewService(project)

        owned = os.path.realpath(os.path.join(self.root, '1'))
        for path in (
            service.frontend_pid_file,
            service.backend_pid_file,
            service.ports_file,
            service.frontend_log_file,
            service.backend_log_file,
        ):
            self.assertEqual(os.path.dirname(os.path.realpath(path)), owned)
            self.assertTrue(os.path.basename(path).startswith('7'))

    def test_two_projects_named_alike_do_not_collide(self):
        # Keying on the id also removes the same-name collision the old
        # scheme had between a user's own projects.
        with override_settings(PROJECTS_ROOT=self.root):
            first = preview_service.PreviewService(_project(7, 'Shop'))
            second = preview_service.PreviewService(_project(8, 'Shop'))
        self.assertNotEqual(first.frontend_pid_file, second.frontend_pid_file)


class GrepPatternGuardTests(SimpleTestCase):
    """grep_files compiles a caller-supplied regex with no engine-level timeout.

    stdlib `re` offers no match deadline and the tool runs in a worker thread
    where a signal alarm cannot fire, so the hazardous pattern shapes are
    refused at compile time instead of interrupted mid-match.
    """

    def _compile(self, pattern):
        from apps.Imagi.Build.services.tools import _compile_search_pattern
        return _compile_search_pattern(pattern)

    def test_nested_quantifier_is_refused(self):
        for pattern in (r'^(a+)+$', r'(a*)*', r'(x|y)+*', r'((ab)+)+'):
            with self.assertRaises(ValueError, msg=pattern):
                self._compile(pattern)

    def test_overlong_pattern_is_refused(self):
        with self.assertRaises(ValueError):
            self._compile('a' * 500)

    def test_invalid_pattern_reports_cleanly(self):
        with self.assertRaises(ValueError):
            self._compile('(unclosed')

    def test_ordinary_patterns_still_compile(self):
        for pattern in (
            r'TODO',
            r'def \w+\(',
            r'^import (os|sys)$',
            r'class [A-Z]\w+\(.*\):',
            r'\d{3}-\d{4}',
        ):
            self.assertIsNotNone(self._compile(pattern), pattern)


class PreviewInputValidationTests(SimpleTestCase):
    """The preview browser's guards on client-supplied paths and sizes.

    The navigate path is typed by the user into the preview's address bar and
    loaded by a headless browser on the server, so anything that could leave
    the project's own dev server has to be refused before it reaches CDP.
    """

    def test_paths_inside_the_app_are_normalized(self):
        normalize = BrowserPreviewService._normalize_path
        self.assertEqual(normalize(None), '/')
        self.assertEqual(normalize(''), '/')
        self.assertEqual(normalize('about'), '/about')
        self.assertEqual(normalize('  /shop?page=2  '), '/shop?page=2')

    def test_paths_that_could_leave_the_app_are_refused(self):
        for path in ('//evil.example', 'http://evil.example', '/a\\b',
                     '/redirect?to=https://evil.example', 5, ['/']):
            with self.subTest(path=path):
                with self.assertRaises(BrowserPreviewError):
                    BrowserPreviewService._normalize_path(path)

    def test_viewport_is_clamped_to_sane_bounds(self):
        clamp = BrowserPreviewService._clamp_viewport
        self.assertEqual(clamp(1024, 768), (1024, 768))
        self.assertEqual(clamp(10, 10), (MIN_VIEWPORT, MIN_VIEWPORT))
        self.assertEqual(clamp(99999, 99999), (MAX_VIEWPORT, MAX_VIEWPORT))
        self.assertEqual(clamp('wide', None), DEFAULT_VIEWPORT)

    def test_device_scale_factor_is_clamped(self):
        clamp = BrowserPreviewService._clamp_dsf
        self.assertEqual(clamp(2), 2.0)
        self.assertEqual(clamp(0.1), 1.0)
        self.assertEqual(clamp(10), 3.0)
        self.assertEqual(clamp(None), 1.0)
        self.assertEqual(clamp('retina'), 1.0)
