"""
A first-build page's opening model call, sent before its run exists.

The home page is what the founder waits on, and its first model call (the
whole page, written in one go) is nearly all of that wait. Everything a run
sets up first (the project's files, its conversation rows, the thread's git
worktree) only matters once that call returns. So the call goes out the moment
Create is clicked (begin), and the run picks its answer up when it gets there
(claim): the set-up happens while the page is being written, not before.

The call is the run's own first request: the same agent, instructions, tools
and prompt the run would send. The run swaps its model for HeadStartModel,
which answers the first request with this response and sends every later one
(a repair, say) to the real model as usual. If the run's prompt differs from
the one sent ahead, the early answer is thrown away and the run asks again.
"""

import asyncio
import logging
import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Dict, Optional

from agents.models.interface import Model, ModelTracing

from .api_keys import read_api_key
from .models_service import get_backend_model_id, get_model_provider

logger = logging.getLogger(__name__)

# An answer nobody claims (the project failed to create, say) is dropped
# after this long.
_UNCLAIMED_TTL_S = 600

_pool = ThreadPoolExecutor(max_workers=4, thread_name_prefix='head-start')
_lock = threading.Lock()
_pending: Dict[object, 'HeadStart'] = {}


class HeadStart:
    def __init__(self, prompt: str, future: Optional[Future]):
        self.prompt = prompt
        self.future = future
        self.sent_at = time.monotonic()
        # When the answer came back (set by the worker), for the timing line.
        self.answered_at: Optional[float] = None


def begin(key, model: str, service_tier: Optional[str], prompt: str) -> bool:
    """Send a first-build page's opening request now, for a run to claim.

    Only GPT models: their requests are plain Responses calls the SDK model
    can make on its own. Returns whether a request went out.
    """
    if get_model_provider(model) != 'openai':
        return False
    from .coding_agent import INITIAL_BUILD_INSTRUCTIONS, create_coding_agent

    agent = create_coding_agent(model, kind='initial_build', service_tier=service_tier)
    entry = None

    def call():
        from agents.models.openai_provider import OpenAIProvider

        provider = OpenAIProvider(api_key=read_api_key('OPENAI_KEY'))
        sdk_model = provider.get_model(get_backend_model_id(model))

        async def ask():
            return await sdk_model.get_response(
                INITIAL_BUILD_INSTRUCTIONS,
                [{'role': 'user', 'content': prompt}],
                agent.model_settings,
                list(agent.tools),
                None,
                [],
                ModelTracing.DISABLED,
                previous_response_id=None,
                conversation_id=None,
                prompt=None,
            )

        try:
            return asyncio.run(ask())
        finally:
            entry.answered_at = time.monotonic()

    with _lock:
        _drop_stale()
        entry = HeadStart(prompt, None)
        entry.future = _pool.submit(call)
        _pending[key] = entry
    return True


def prompt_for(key) -> Optional[str]:
    """The prompt sent ahead for this key, which its run must send as-is."""
    with _lock:
        entry = _pending.get(key)
    return entry.prompt if entry else None


def claim(key, prompt: str) -> Optional[HeadStart]:
    """Take the early request sent for this key, if it was for this prompt."""
    with _lock:
        entry = _pending.get(key)
        if entry is None or entry.prompt != prompt:
            return None
        del _pending[key]
    return entry


def _drop_stale():
    now = time.monotonic()
    for key in [k for k, e in _pending.items() if now - e.sent_at > _UNCLAIMED_TTL_S]:
        del _pending[key]


class HeadStartModel(Model):
    """The run's model, with its first answer already on the way."""

    def __init__(self, inner: Model, head_start: HeadStart):
        self.inner = inner
        self.head_start = head_start

    async def get_response(self, *args, **kwargs):
        head_start, self.head_start = self.head_start, None
        if head_start is not None:
            try:
                return await asyncio.wrap_future(head_start.future)
            except Exception as e:
                logger.warning("The early first request failed (%s); asking again", e)
        return await self.inner.get_response(*args, **kwargs)

    def stream_response(self, *args, **kwargs):
        return self.inner.stream_response(*args, **kwargs)

    async def close(self):
        await self.inner.close()
