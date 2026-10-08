"""Reading the AI providers' API keys from the environment."""

import os

from django.conf import settings


def read_api_key(name):
    """The key in env var (or setting) `name`, stripped of whitespace; None if unset.

    A key pasted into a dashboard often carries a trailing newline, which httpx
    rejects as an illegal header value on every request — and its error message
    then writes the whole key into the logs.
    """
    value = os.getenv(name) or getattr(settings, name, None) or ''
    return value.strip() or None
