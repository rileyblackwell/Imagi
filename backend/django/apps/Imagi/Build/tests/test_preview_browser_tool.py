"""
The preview browser tools the coordinator and threads use (Claude's browser
toolset, carried out on the project's headless preview).
"""

from types import SimpleNamespace
from unittest.mock import patch

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
                has = any(
                    isinstance(getattr(t, 'anthropic_toolset', None), PreviewBrowserToolset)
                    for t in agent.tools
                )
                self.assertEqual(has, expected)


class NavigationScopeTests(SimpleTestCase):
    def _path(self, url):
        return _session()._app_path(url, BrowserPreviewService)

    def test_paths_and_the_apps_own_urls_are_allowed(self):
        self.assertEqual(self._path('/about'), '/about')
        self.assertEqual(self._path('http://127.0.0.1:5199/shop?x=1#top'), '/shop?x=1#top')
        self.assertEqual(self._path('localhost:5199/'), '/')

    def test_the_live_previews_base_path_is_not_doubled(self):
        # The live preview serves the app under /s/<token>/, and app_url ends
        # in it; a URL or path the page itself reported already carries it.
        session = _session(app_url='http://127.0.0.1:5199/s/tok')
        self.assertEqual(session._app_path('http://127.0.0.1:5199/s/tok/book', BrowserPreviewService), '/book')
        self.assertEqual(session._app_path('/s/tok/book?x=1', BrowserPreviewService), '/book?x=1')
        self.assertEqual(session._app_path('http://127.0.0.1:5199/s/tok', BrowserPreviewService), '/')
        self.assertEqual(session._app_path('/s/token-other', BrowserPreviewService), '/s/token-other')

    def test_anything_off_the_app_is_refused(self):
        for url in (
            'https://example.com', '//evil.com/x', 'http://127.0.0.1:8000/admin',
            'file:///etc/passwd', 'javascript:alert(1)',
        ):
            with self.subTest(url=url):
                with self.assertRaises(BrowserActionError):
                    self._path(url)


class ActivityTests(SimpleTestCase):
    """What the user's live preview hears about an agent's browser actions."""

    def _record(self, url, context, enabled=True):
        from apps.Imagi.Build.services import preview_browser_tool as tool
        from apps.Imagi.Build.services import live_preview_service as live

        session = _session(app_url='http://127.0.0.1:5199/s/tok')
        session.service = SimpleNamespace(project=SimpleNamespace(pk=7))
        session.run = lambda body: (url, 'Title')
        recorded = []
        with patch.object(live, 'enabled', return_value=enabled), \
                patch.object(live, 'LivePreviewService') as service:
            service.return_value.record_agent_activity.side_effect = lambda *a: recorded.append(a)
            tool._note_activity(session, context, 'left_click')
        return recorded

    def test_the_agents_page_and_name_reach_the_live_preview(self):
        lead = SimpleNamespace(conversation_kind='lead', conversation_id=1)
        self.assertEqual(
            self._record('http://127.0.0.1:5199/s/tok/book?step=2', lead),
            [('/book?step=2', 'left_click', 'Coordinator')],
        )
        self.assertEqual(self._record('http://127.0.0.1:5199/s/tok', lead), [('/', 'left_click', 'Coordinator')])

    def test_nothing_is_recorded_without_the_live_preview(self):
        lead = SimpleNamespace(conversation_kind='lead', conversation_id=1)
        self.assertEqual(self._record('http://127.0.0.1:5199/s/tok/book', lead, enabled=False), [])


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
