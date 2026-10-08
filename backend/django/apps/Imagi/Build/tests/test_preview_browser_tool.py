"""
The preview browser tools the coordinator and threads use (Claude's browser
toolset, carried out on the project's headless preview).
"""

from types import SimpleNamespace

from django.test import SimpleTestCase

from apps.Imagi.Build.services.browser_preview_service import BrowserPreviewService
from apps.Imagi.Build.services.coding_agent import create_coding_agent
from apps.Imagi.Build.services.preview_browser_tool import (
    BrowserActionError,
    PreviewBrowserToolset,
    _parse_chord,
    _PreviewSession,
)


def _session(viewport=(1280, 800), app_url='http://127.0.0.1:5199'):
    return _PreviewSession(None, {'viewport': viewport, 'app_url': app_url})


class ToolsetParamTests(SimpleTestCase):
    def test_tabs_scripts_and_uploads_are_off_console_is_on(self):
        param = PreviewBrowserToolset().to_param()
        self.assertEqual(param['type'], 'browser_toolset_20260801')
        self.assertNotIn('name', param)
        configs = param['configs']
        for member in ('new_tab', 'switch_tab', 'close_tab', 'javascript_exec', 'file_upload'):
            self.assertFalse(configs[member]['enabled'], member)
        self.assertTrue(configs['read_console']['enabled'])

    def test_disabled_member_is_refused_without_touching_the_preview(self):
        content, is_error = PreviewBrowserToolset().run_member(None, 'javascript_exec', {})
        self.assertTrue(is_error)
        self.assertIn('not enabled', content)

    def test_no_project_is_an_error_for_the_model(self):
        content, is_error = PreviewBrowserToolset().run_member(
            SimpleNamespace(context=SimpleNamespace(project_id=None)), 'screenshot', {}
        )
        self.assertTrue(is_error)
        self.assertIn('no project', content)

    def test_coordinator_and_threads_get_the_browser_but_not_the_first_build(self):
        for kind, expected in (('lead', True), ('task', True), ('chat', True), ('initial_build', False)):
            with self.subTest(kind=kind):
                agent = create_coding_agent(kind=kind)
                has = any(isinstance(t, PreviewBrowserToolset) for t in agent.tools)
                self.assertEqual(has, expected)


class NavigationScopeTests(SimpleTestCase):
    def _path(self, url):
        return _session()._app_path(url, BrowserPreviewService)

    def test_paths_and_the_apps_own_urls_are_allowed(self):
        self.assertEqual(self._path('/about'), '/about')
        self.assertEqual(self._path('http://127.0.0.1:5199/shop?x=1#top'), '/shop?x=1#top')
        self.assertEqual(self._path('localhost:5199/'), '/')

    def test_anything_off_the_app_is_refused(self):
        for url in (
            'https://example.com', '//evil.com/x', 'http://127.0.0.1:8000/admin',
            'file:///etc/passwd', 'javascript:alert(1)',
        ):
            with self.subTest(url=url):
                with self.assertRaises(BrowserActionError):
                    self._path(url)


class CoordinateTests(SimpleTestCase):
    def test_screenshot_pixels_map_back_to_css_pixels(self):
        session = _session(viewport=(1600, 900))
        # 1600 wide is shot at 1280, so screenshot x=640 is CSS x=800.
        self.assertEqual(session.to_css(640, 360), (800.0, 450.0))

    def test_points_outside_the_viewport_are_refused(self):
        with self.assertRaises(BrowserActionError):
            _session().to_css(5000, 10)
        with self.assertRaises(BrowserActionError):
            _session().to_css('left', 10)


class ChordTests(SimpleTestCase):
    def test_plain_letter_types_its_text(self):
        self.assertEqual(_parse_chord('a'), (0, 'a', 'KeyA', 65, 'a'))

    def test_shortcut_carries_modifiers_and_no_text(self):
        mask, key, code, _, text = _parse_chord('ctrl+shift+a')
        self.assertEqual(mask, 2 | 8)
        self.assertEqual((key, code, text), ('a', 'KeyA', ''))

    def test_named_keys(self):
        _, key, _, key_code, _ = _parse_chord('Enter')
        self.assertEqual((key, key_code), ('Enter', 13))

    def test_unknown_keys_and_modifiers_are_errors(self):
        for chord in ('hyper+a', 'NotAKey', ''):
            with self.subTest(chord=chord):
                with self.assertRaises(BrowserActionError):
                    _parse_chord(chord)
