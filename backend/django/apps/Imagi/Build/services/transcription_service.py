"""
Speech-to-text for the workspace composer.

The composer's mic button (and ⌘D) records a short clip in the browser and
posts it here; OpenAI turns it into the text of a prompt, which lands in the
textbox for the user to read over and send. Nothing here reaches the agent:
dictation only writes what the user would otherwise have typed.
"""

import logging
import os

from django.conf import settings

logger = logging.getLogger(__name__)

_BUILDER_SETTINGS = getattr(settings, 'IMAGI_BUILDER', {})

# OpenAI's speech-to-text model (see IMAGI_BUILDER in imagi/settings.py).
TRANSCRIPTION_MODEL = _BUILDER_SETTINGS.get('TRANSCRIPTION_MODEL', 'gpt-4o-transcribe')

# Bound on one clip. OpenAI's own ceiling is 25 MB and a minute of browser
# Opus is well under one, so anything near this is not a dictated prompt.
MAX_AUDIO_BYTES = 20 * 1024 * 1024

# Containers a browser's MediaRecorder produces (Chrome: webm, Safari: mp4),
# mapped to the extension OpenAI reads the format from. It goes by the
# upload's file name rather than its content type, so the name must carry it.
AUDIO_EXTENSIONS = {
    'audio/webm': 'webm',
    'video/webm': 'webm',
    'audio/ogg': 'ogg',
    'audio/mp4': 'mp4',
    'audio/x-m4a': 'm4a',
    'audio/mpeg': 'mp3',
    'audio/wav': 'wav',
    'audio/x-wav': 'wav',
    'audio/flac': 'flac',
}

# Vocabulary the speaker is likely to use, so the model hears "Stripe" and
# "Vue" as the names they are rather than the nearest English words. A bare
# word list rather than a sentence on purpose: given a near-silent clip, a
# transcription model tends to continue whatever prose it was primed with.
TRANSCRIPTION_PROMPT = (
    'Imagi, Vue, Django, Stripe, Railway, API, OAuth, webhook, checkout, '
    'navbar, footer, hero, CTA, homepage, subagent, deploy.'
)

# List price per token for gpt-4o-transcribe (audio in, text in, text out),
# used only to debit the plan allowance. A minute of speech is about $0.006.
_PRICE_PER_TOKEN = {
    'audio': 6.0 / 1_000_000,
    'text': 2.5 / 1_000_000,
    'output': 10.0 / 1_000_000,
}


class TranscriptionUnavailable(Exception):
    """Speech-to-text is not configured on this server (no OpenAI key)."""


class InvalidAudio(ValueError):
    """The upload is not a clip we will send for transcription."""


class TranscriptionFailed(Exception):
    """OpenAI did not return a transcript for the clip."""


def audio_extension(content_type):
    """The file extension for a clip's media type, or None if unsupported.

    Parameters ("audio/webm;codecs=opus") are dropped: MediaRecorder reports
    the codec, and the container is all the extension names.
    """
    base = (content_type or '').split(';', 1)[0].strip().lower()
    return AUDIO_EXTENSIONS.get(base)


def _api_key():
    # Read per call rather than at import (unlike base_agent) so a key added
    # to the environment after start-up — or patched in by a test — is seen.
    return os.getenv('OPENAI_KEY') or getattr(settings, 'OPENAI_KEY', None)


def _usage_from(result):
    """Token counts and a cost for metering, or Nones when OpenAI sent none."""
    usage = getattr(result, 'usage', None)
    input_tokens = getattr(usage, 'input_tokens', None)
    output_tokens = getattr(usage, 'output_tokens', None)
    if input_tokens is None and output_tokens is None:
        return {'input_tokens': None, 'output_tokens': None, 'cost_usd': None}
    details = getattr(usage, 'input_token_details', None)
    audio_tokens = getattr(details, 'audio_tokens', None)
    text_tokens = getattr(details, 'text_tokens', None)
    if audio_tokens is None:
        # No breakdown: price the whole input at the dearer audio rate rather
        # than guess low.
        audio_tokens, text_tokens = input_tokens or 0, 0
    cost = (
        (audio_tokens or 0) * _PRICE_PER_TOKEN['audio']
        + (text_tokens or 0) * _PRICE_PER_TOKEN['text']
        + (output_tokens or 0) * _PRICE_PER_TOKEN['output']
    )
    return {
        'input_tokens': input_tokens or 0,
        'output_tokens': output_tokens or 0,
        'cost_usd': round(cost, 6),
    }


def transcribe_audio(data, content_type):
    """Transcribe one clip.

    Returns (text, usage): the transcript with surrounding whitespace
    stripped — empty when nothing was said — and the dict from _usage_from
    for the caller to meter.

    Raises InvalidAudio for a clip we will not send (empty, oversize, or in
    a container OpenAI cannot read), TranscriptionUnavailable when no key is
    configured, and TranscriptionFailed when the API call itself fails.
    """
    if not data:
        raise InvalidAudio('The recording was empty')
    if len(data) > MAX_AUDIO_BYTES:
        raise InvalidAudio('The recording is too long to transcribe')
    extension = audio_extension(content_type)
    if not extension:
        raise InvalidAudio(f'Unsupported audio format: {content_type or "unknown"}')
    api_key = _api_key()
    if not api_key:
        raise TranscriptionUnavailable('OPENAI_KEY is not configured')

    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    try:
        result = client.audio.transcriptions.create(
            model=TRANSCRIPTION_MODEL,
            file=(f'dictation.{extension}', data),
            prompt=TRANSCRIPTION_PROMPT,
            response_format='json',
        )
    except Exception as exc:
        raise TranscriptionFailed(str(exc)) from exc
    text = (getattr(result, 'text', None) or '').strip()
    return text, _usage_from(result)
