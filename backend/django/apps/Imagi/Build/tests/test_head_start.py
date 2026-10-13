import asyncio
from concurrent.futures import Future
from unittest import mock

from django.test import SimpleTestCase

from apps.Imagi.Build.services import head_start


class _InnerModel:
    def __init__(self):
        self.calls = 0

    async def get_response(self, *args, **kwargs):
        self.calls += 1
        return 'asked again'


def _answered(value):
    future = Future()
    future.set_result(value)
    return future


class HeadStartTests(SimpleTestCase):
    def tearDown(self):
        head_start._pending.clear()

    def _sent(self, key, prompt, answer='early answer'):
        entry = head_start.HeadStart(prompt, _answered(answer))
        head_start._pending[key] = entry
        return entry

    def test_a_run_claims_the_request_sent_for_its_prompt(self):
        entry = self._sent(7, 'Build the home page')
        self.assertEqual(head_start.prompt_for(7), 'Build the home page')
        # Another page's run (a different prompt) leaves it alone.
        self.assertIsNone(head_start.claim(7, 'Build the about page'))
        self.assertIs(head_start.claim(7, 'Build the home page'), entry)
        self.assertIsNone(head_start.claim(7, 'Build the home page'))

    def test_the_first_request_gets_the_early_answer_and_later_ones_the_model(self):
        inner = _InnerModel()
        model = head_start.HeadStartModel(inner, self._sent(7, 'p'))
        self.assertEqual(asyncio.run(model.get_response()), 'early answer')
        self.assertEqual(asyncio.run(model.get_response()), 'asked again')
        self.assertEqual(inner.calls, 1)

    def test_a_failed_early_request_is_asked_again(self):
        failed = Future()
        failed.set_exception(RuntimeError('socket closed'))
        inner = _InnerModel()
        model = head_start.HeadStartModel(inner, head_start.HeadStart('p', failed))
        self.assertEqual(asyncio.run(model.get_response()), 'asked again')

    def test_only_gpt_pages_are_sent_early(self):
        with mock.patch.object(head_start, '_pool') as pool:
            self.assertFalse(head_start.begin(7, 'claude-opus-5-5', None, 'p'))
            pool.submit.assert_not_called()

    def test_the_early_brief_matches_the_scaffold_it_describes(self):
        # The early request is built from these constants before the project's
        # files exist; the run reads the same text back off disk.
        from apps.Imagi.Build.services.codegen.prebuilt_apps.home import (
            HOME_VIEW_VUE,
            SITE_PAGES_TS,
            home_app_files,
        )

        files = {f['name']: f['content'] for f in home_app_files()}
        self.assertEqual(files['frontend/vuejs/src/apps/home/views/HomeView.vue'], HOME_VIEW_VUE)
        self.assertEqual(files['frontend/vuejs/src/apps/home/site-pages.ts'], SITE_PAGES_TS)
