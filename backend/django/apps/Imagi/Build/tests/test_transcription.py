"""
Tests for the composer's dictation: the transcription service and the
endpoint in front of it. OpenAI is never called — the client is patched
where the service imports it.
"""

import os
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from rest_framework.authtoken.models import Token

from apps.Imagi.Build.services import transcription_service as ts
from apps.Payments.models import UsageEvent

WEBM_BYTES = b'\x1aE\xdf\xa3webm'


def fake_openai(text='Add a contact page', usage=None):
    """An `openai.OpenAI` stand-in whose transcription call returns `text`.

    Returns the class mock (to patch in) and the client it will hand out (to
    inspect the call).
    """
    client = MagicMock()
    client.audio.transcriptions.create.return_value = SimpleNamespace(text=text, usage=usage)
    return MagicMock(return_value=client), client


class TranscribeAudioTests(SimpleTestCase):
    def setUp(self):
        env = patch.dict(os.environ, {'OPENAI_KEY': 'sk-test'})
        env.start()
        self.addCleanup(env.stop)

    def test_rejects_an_empty_clip(self):
        with self.assertRaises(ts.InvalidAudio):
            ts.transcribe_audio(b'', 'audio/webm')

    def test_rejects_an_oversize_clip_before_calling_openai(self):
        fake_cls, _ = fake_openai()
        with patch('openai.OpenAI', fake_cls), self.assertRaises(ts.InvalidAudio):
            ts.transcribe_audio(b'x' * (ts.MAX_AUDIO_BYTES + 1), 'audio/webm')
        fake_cls.assert_not_called()

    def test_rejects_a_container_openai_cannot_read(self):
        with self.assertRaises(ts.InvalidAudio):
            ts.transcribe_audio(b'hello', 'text/plain')

    def test_unavailable_without_a_key(self):
        with patch.dict(os.environ, {'OPENAI_KEY': ''}), override_settings(OPENAI_KEY=None):
            with self.assertRaises(ts.TranscriptionUnavailable):
                ts.transcribe_audio(WEBM_BYTES, 'audio/webm')

    def test_names_the_upload_by_its_container_and_strips_the_text(self):
        fake_cls, client = fake_openai('  Add a contact page.  ')
        with patch('openai.OpenAI', fake_cls):
            text, usage = ts.transcribe_audio(WEBM_BYTES, 'audio/webm;codecs=opus')

        self.assertEqual(text, 'Add a contact page.')
        fake_cls.assert_called_once_with(api_key='sk-test')
        kwargs = client.audio.transcriptions.create.call_args.kwargs
        self.assertEqual(kwargs['model'], ts.TRANSCRIPTION_MODEL)
        # The codec parameter is not part of the name OpenAI sniffs.
        self.assertEqual(kwargs['file'], ('dictation.webm', WEBM_BYTES))
        self.assertEqual(kwargs['prompt'], ts.TRANSCRIPTION_PROMPT)
        # No usage on the reply: nothing to meter, and nothing invented.
        self.assertEqual(usage, {'input_tokens': None, 'output_tokens': None, 'cost_usd': None})

    def test_safari_clips_go_up_as_mp4(self):
        fake_cls, client = fake_openai()
        with patch('openai.OpenAI', fake_cls):
            ts.transcribe_audio(b'ftypisom', 'audio/mp4')
        self.assertEqual(client.audio.transcriptions.create.call_args.kwargs['file'][0], 'dictation.mp4')

    def test_silence_comes_back_as_an_empty_string(self):
        fake_cls, _ = fake_openai('   ')
        with patch('openai.OpenAI', fake_cls):
            text, _ = ts.transcribe_audio(WEBM_BYTES, 'audio/webm')
        self.assertEqual(text, '')

    def test_prices_usage_from_the_token_breakdown(self):
        usage = SimpleNamespace(
            input_tokens=1100,
            output_tokens=20,
            input_token_details=SimpleNamespace(audio_tokens=1000, text_tokens=100),
        )
        fake_cls, _ = fake_openai('hi', usage)
        with patch('openai.OpenAI', fake_cls):
            _, metered = ts.transcribe_audio(WEBM_BYTES, 'audio/webm')

        self.assertEqual(metered['input_tokens'], 1100)
        self.assertEqual(metered['output_tokens'], 20)
        expected = 1000 * 6.0 / 1e6 + 100 * 2.5 / 1e6 + 20 * 10.0 / 1e6
        self.assertAlmostEqual(metered['cost_usd'], expected, places=6)

    def test_prices_an_unbroken_down_input_as_audio(self):
        # No breakdown: the dearer rate, so the allowance is never under-debited.
        usage = SimpleNamespace(input_tokens=1000, output_tokens=0, input_token_details=None)
        fake_cls, _ = fake_openai('hi', usage)
        with patch('openai.OpenAI', fake_cls):
            _, metered = ts.transcribe_audio(WEBM_BYTES, 'audio/webm')
        self.assertAlmostEqual(metered['cost_usd'], 1000 * 6.0 / 1e6, places=6)

    def test_an_api_error_is_a_transcription_failure(self):
        fake_cls, client = fake_openai()
        client.audio.transcriptions.create.side_effect = RuntimeError('rate limited')
        with patch('openai.OpenAI', fake_cls), self.assertRaises(ts.TranscriptionFailed):
            ts.transcribe_audio(WEBM_BYTES, 'audio/webm')


class AgentTranscribeViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('dictator', 'd@example.com', 'pw')
        token = Token.objects.create(user=self.user)
        self.auth = {'HTTP_AUTHORIZATION': f'Token {token.key}'}
        self.url = reverse('agent_transcribe')

    @staticmethod
    def clip(content_type='audio/webm', data=WEBM_BYTES):
        return SimpleUploadedFile('dictation.webm', data, content_type=content_type)

    def post(self, data, **extra):
        return self.client.post(self.url, data, **{**self.auth, **extra})

    def test_requires_a_signed_in_user(self):
        resp = self.client.post(self.url, {'audio': self.clip()})
        self.assertEqual(resp.status_code, 401)

    def test_requires_a_clip(self):
        resp = self.post({})
        self.assertEqual(resp.status_code, 400)
        self.assertIn('audio', resp.json()['error'].lower())

    @patch('apps.Imagi.Build.api.views.record_usage')
    @patch('apps.Imagi.Build.api.views.transcribe_audio')
    def test_returns_the_transcript_and_meters_the_clip(self, transcribe, record):
        transcribe.return_value = (
            'Add a contact page',
            {'input_tokens': 900, 'output_tokens': 12, 'cost_usd': 0.0055},
        )
        resp = self.post({'audio': self.clip()})

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {'text': 'Add a contact page'})
        data, content_type = transcribe.call_args.args
        self.assertEqual(data, WEBM_BYTES)
        self.assertEqual(content_type, 'audio/webm')
        record.assert_called_once_with(
            self.user, ts.TRANSCRIPTION_MODEL, 900, 12, cost_usd=0.0055
        )

    @patch('apps.Imagi.Build.api.views.transcribe_audio')
    def test_the_clip_shows_up_in_the_usage_ledger(self, transcribe):
        transcribe.return_value = (
            'hi', {'input_tokens': 900, 'output_tokens': 12, 'cost_usd': 0.0055}
        )
        self.post({'audio': self.clip()})
        event = UsageEvent.objects.get(user=self.user)
        self.assertEqual(event.model_name, ts.TRANSCRIPTION_MODEL)
        self.assertEqual((event.input_tokens, event.output_tokens), (900, 12))

    @patch('apps.Imagi.Build.api.views.record_usage')
    @patch('apps.Imagi.Build.api.views.transcribe_audio')
    def test_unmetered_silence_still_returns(self, transcribe, record):
        transcribe.return_value = ('', {'input_tokens': None, 'output_tokens': None, 'cost_usd': None})
        resp = self.post({'audio': self.clip()})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {'text': ''})

    @patch('apps.Imagi.Build.api.views.record_usage', side_effect=RuntimeError('ledger down'))
    @patch('apps.Imagi.Build.api.views.transcribe_audio')
    def test_a_metering_failure_never_costs_the_transcript(self, transcribe, _record):
        transcribe.return_value = ('hi', {'input_tokens': 1, 'output_tokens': 1, 'cost_usd': 0.0})
        resp = self.post({'audio': self.clip()})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {'text': 'hi'})

    @patch('apps.Imagi.Build.api.views.transcribe_audio')
    @patch('apps.Imagi.Build.api.views.check_usage_allowed')
    def test_an_exhausted_plan_is_refused_before_openai_is_called(self, check, transcribe):
        check.return_value = (False, {
            'error': 'usage_limit_exceeded',
            'detail': 'Weekly limit reached',
            'window': 'week',
            'resets_at': None,
        })
        resp = self.post({'audio': self.clip()})
        self.assertEqual(resp.status_code, 429)
        self.assertEqual(resp.json()['error'], 'usage_limit_exceeded')
        transcribe.assert_not_called()

    @patch('apps.Imagi.Build.api.views.transcribe_audio', side_effect=ts.InvalidAudio('Unsupported audio format: text/plain'))
    def test_a_clip_openai_cannot_read_is_a_400(self, _transcribe):
        resp = self.post({'audio': self.clip(content_type='text/plain')})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['error'], 'Unsupported audio format: text/plain')

    @patch('apps.Imagi.Build.api.views.transcribe_audio', side_effect=ts.TranscriptionUnavailable('no key'))
    def test_an_unconfigured_server_says_so(self, _transcribe):
        resp = self.post({'audio': self.clip()})
        self.assertEqual(resp.status_code, 503)

    @patch('apps.Imagi.Build.api.views.transcribe_audio', side_effect=ts.TranscriptionFailed('boom'))
    def test_an_openai_failure_is_a_502(self, _transcribe):
        resp = self.post({'audio': self.clip()})
        self.assertEqual(resp.status_code, 502)
        self.assertNotIn('boom', resp.json()['error'])
