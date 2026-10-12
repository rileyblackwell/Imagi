"""
How GPT runs reach OpenAI: the Responses API over a WebSocket.

OpenAI recommends WebSocket mode for its fast tiers, Ultrafast above all
(Riley, 2026-10-12): an agent run is many model calls in a row, and one open
connection saves a fresh HTTPS request per call. The Agents SDK supports it
natively (OpenAIProvider(use_responses_websocket=True)), so this only decides
when to use it and makes sure each run closes what it opened.

Each run gets its own provider, so concurrent runs never queue behind one
shared socket, and the connection lives for the run's model calls only.
Claude runs are untouched: their Agent carries an AnthropicModel, and the SDK
only asks a provider to resolve model names given as strings.

OPENAI_RESPONSES_TRANSPORT=http (environment, or IMAGI_BUILDER in settings)
switches GPT runs back to plain HTTPS without a code change.
"""

import asyncio
import logging
import os
from typing import Optional

from django.conf import settings

from .models_service import get_model_provider

logger = logging.getLogger(__name__)

WEBSOCKET = 'websocket'
HTTP = 'http'


def responses_transport() -> str:
    """'websocket' (the default) or 'http', for every GPT run."""
    configured = os.environ.get('OPENAI_RESPONSES_TRANSPORT') or getattr(
        settings, 'IMAGI_BUILDER', {}
    ).get('OPENAI_RESPONSES_TRANSPORT', WEBSOCKET)
    return HTTP if str(configured).strip().lower() == HTTP else WEBSOCKET


def _websockets_installed() -> bool:
    try:
        import websockets.asyncio.client  # noqa: F401
    except ImportError:
        return False
    return True


def websocket_provider_for(model: Optional[str]):
    """A fresh WebSocket provider for one GPT run, or None to use the default.

    None for Claude models, when the transport is set to http, or when the
    websockets package is missing (the run then goes over HTTPS as before,
    rather than failing at its first model call).
    """
    if not model or get_model_provider(model) != 'openai':
        return None
    if responses_transport() != WEBSOCKET:
        return None
    if not _websockets_installed():
        logger.warning("websockets isn't installed; GPT runs use HTTPS")
        return None
    from agents.models.openai_provider import OpenAIProvider
    return OpenAIProvider(use_responses_websocket=True)


async def close_provider(provider) -> None:
    """Close a run's WebSocket (from the loop the run used)."""
    if provider is None:
        return
    try:
        await provider.aclose()
    except Exception as exc:  # a failed close must not fail the run
        logger.warning("Could not close the OpenAI WebSocket: %s", exc)


def close_provider_sync(provider) -> None:
    """Close a run's WebSocket after Runner.run_sync.

    run_sync runs on the thread's default event loop and leaves it open, so
    the connection belongs to that loop and is closed on it.
    """
    if provider is None:
        return
    try:
        loop = asyncio.get_event_loop_policy().get_event_loop()
    except RuntimeError:
        return
    if loop.is_closed() or loop.is_running():
        return
    loop.run_until_complete(close_provider(provider))
