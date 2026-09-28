"""
Claude models for the Imagi agent.

The agent harness is built on the OpenAI Agents SDK, whose Runner drives any
object implementing its `Model` interface. AnthropicModel is that interface
backed by the Anthropic Messages API, so a Claude run gets the same tools,
hooks, streaming, turn caps and usage accounting as a GPT run — nothing above
the model layer knows which provider answered.

The Runner speaks the OpenAI Responses item format, so this module translates
both ways:

  in   Responses input items  →  Anthropic `messages` (+ `system`, `tools`)
  out  Anthropic content      →  Responses output items + stream events

One Claude-specific wrinkle: within a tool loop, the assistant's thinking
blocks (and any server-tool blocks, e.g. web search) have to be sent back
exactly as they came. Each assistant turn therefore also emits a `reasoning`
item whose encrypted_content carries the turn's full Anthropic content; on the
way back in, that item is replayed verbatim and the Responses items the same
turn produced (its text and function calls) are skipped as duplicates.
"""

import asyncio
import json
import logging
import os
import time
from typing import Any, AsyncIterator, Dict, List, Optional, Tuple

from django.conf import settings

from agents.items import ModelResponse
from agents.models.fake_id import FAKE_RESPONSES_ID
from agents.models.interface import Model
from agents.tool import FunctionTool
from agents.usage import Usage
from openai.types.responses import (
    Response,
    ResponseCompletedEvent,
    ResponseCreatedEvent,
    ResponseFunctionToolCall,
    ResponseOutputItemDoneEvent,
    ResponseOutputMessage,
    ResponseOutputText,
    ResponseReasoningItem,
    ResponseTextDeltaEvent,
    ResponseUsage,
)
from openai.types.responses.response_usage import (
    InputTokensDetails,
    OutputTokensDetails,
)

try:  # Hosted web search — mapped onto Claude's own server-side web search
    from agents import WebSearchTool
except ImportError:  # pragma: no cover - defensive fallback
    WebSearchTool = None

logger = logging.getLogger(__name__)

ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_KEY') or getattr(settings, 'ANTHROPIC_KEY', None)

# Output ceiling per model response. Every request streams, so a generous cap
# costs nothing unless it is used; a whole page written in one tool call needs
# the room.
DEFAULT_MAX_TOKENS = 64000

# Efforts Claude accepts on output_config.effort. The platform ladder
# (low → xhigh) is a subset, so a platform effort passes straight through.
CLAUDE_EFFORTS = ('low', 'medium', 'high', 'xhigh', 'max')

# Server-side refusal fallback: when a model's safety classifiers decline a
# request, the API re-runs it on the fallback Anthropic recommends for that
# refusal category instead of returning the refusal.
REFUSAL_FALLBACK_BETA = 'server-side-fallback-2026-07-01'

# Claude's server-side web search. Runs on Anthropic's side inside a single
# response, so the harness never executes it. The current version filters
# results by running code (programmatic tool calling), which the API refuses
# alongside disable_parallel_tool_use — so a run that must call its tools one
# at a time (the lead) gets the basic version instead.
WEB_SEARCH_TOOL = {'type': 'web_search_20260209', 'name': 'web_search'}
BASIC_WEB_SEARCH_TOOL = {'type': 'web_search_20250305', 'name': 'web_search'}

# A long server-tool loop can hand the turn back mid-way (stop_reason
# 'pause_turn'); the request is re-sent with the partial turn appended. Bounded
# so a stuck loop cannot spin.
MAX_PAUSE_CONTINUATIONS = 5

# The marker on a reasoning item that carries a Claude turn's raw content.
REPLAY_KEY = 'anthropic_content'

REFUSAL_TEXT = (
    "I can't help with that request. Try rephrasing it, or pick a different "
    "model from the model menu."
)


def _as_dict(item: Any) -> Dict[str, Any]:
    """Input items arrive as dicts or as pydantic models; read both the same way."""
    if isinstance(item, dict):
        return item
    if hasattr(item, 'model_dump'):
        return item.model_dump(exclude_none=True)
    return {}


def _text_of(content: Any) -> str:
    """Flatten Responses message content (a string or a list of parts) to text."""
    if isinstance(content, str):
        return content
    parts = []
    for part in content or []:
        part = _as_dict(part)
        if part.get('type') in ('input_text', 'output_text', 'text'):
            parts.append(part.get('text') or '')
        elif part.get('type') == 'refusal':
            parts.append(part.get('refusal') or '')
    return ''.join(parts)


def _tool_output_text(output: Any) -> str:
    if isinstance(output, str):
        return output
    if isinstance(output, list):
        return _text_of(output)
    return json.dumps(output, default=str)


def _replay_content(item: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
    """The raw Claude content a reasoning item carries, or None if it isn't ours."""
    raw = item.get('encrypted_content')
    if not raw:
        return None
    try:
        payload = json.loads(raw)
    except (TypeError, ValueError):
        return None
    if isinstance(payload, dict) and isinstance(payload.get(REPLAY_KEY), list):
        return payload[REPLAY_KEY]
    return None


def _is_assistant_side(item: Dict[str, Any]) -> bool:
    """Items the model itself produced: its messages and its tool calls."""
    if item.get('type') == 'function_call':
        return True
    return item.get('role') == 'assistant'


def to_anthropic_messages(
    input_items: Any,
) -> Tuple[List[str], List[Dict[str, Any]]]:
    """
    Translate the Runner's Responses-format input into Anthropic messages.

    Returns (extra_system_texts, messages): system/developer items become
    extra system text, everything else becomes alternating user/assistant
    messages (consecutive same-role items are merged, as the API requires).
    """
    if isinstance(input_items, str):
        return [], [{'role': 'user', 'content': input_items}]

    system_texts: List[str] = []
    turns: List[Tuple[str, List[Dict[str, Any]]]] = []
    # After a replayed turn, the same turn's text and tool-call items are
    # already inside the replayed content — skip them until the next
    # non-assistant item (a tool result or the next user message).
    skipping_replayed_turn = False

    def add(role: str, blocks: List[Dict[str, Any]]):
        if not blocks:
            return
        if turns and turns[-1][0] == role:
            turns[-1][1].extend(blocks)
        else:
            turns.append((role, list(blocks)))

    for raw in input_items:
        item = _as_dict(raw)
        item_type = item.get('type')

        if skipping_replayed_turn:
            if _is_assistant_side(item):
                continue
            skipping_replayed_turn = False

        if item_type == 'reasoning':
            replay = _replay_content(item)
            if replay is not None:
                add('assistant', replay)
                skipping_replayed_turn = True
            # Reasoning from another provider is opaque here; drop it.
            continue

        if item_type == 'function_call':
            try:
                arguments = json.loads(item.get('arguments') or '{}')
            except ValueError:
                arguments = {}
            add('assistant', [{
                'type': 'tool_use',
                'id': item.get('call_id'),
                'name': item.get('name'),
                'input': arguments,
            }])
            continue

        if item_type == 'function_call_output':
            add('user', [{
                'type': 'tool_result',
                'tool_use_id': item.get('call_id'),
                'content': _tool_output_text(item.get('output')) or '(no output)',
            }])
            continue

        role = item.get('role')
        if role in ('system', 'developer'):
            text = _text_of(item.get('content'))
            if text:
                system_texts.append(text)
            continue
        if role in ('user', 'assistant'):
            text = _text_of(item.get('content'))
            if text.strip():
                add(role, [{'type': 'text', 'text': text}])
            continue

        logger.debug("Claude input: skipping unsupported item type %r", item_type)

    return system_texts, [{'role': role, 'content': blocks} for role, blocks in turns]


def to_anthropic_tools(tools: List[Any], sequential: bool = False) -> List[Dict[str, Any]]:
    """
    Function tools map one-to-one; hosted web search becomes Claude's own.
    sequential: the run disables parallel tool calls (see BASIC_WEB_SEARCH_TOOL).
    """
    converted = []
    for tool in tools or []:
        if isinstance(tool, FunctionTool):
            converted.append({
                'name': tool.name,
                'description': tool.description or '',
                'input_schema': tool.params_json_schema,
            })
        elif WebSearchTool is not None and isinstance(tool, WebSearchTool):
            converted.append(dict(BASIC_WEB_SEARCH_TOOL if sequential else WEB_SEARCH_TOOL))
        else:
            logger.debug("Claude tools: skipping unsupported tool %r", type(tool).__name__)
    return converted


def to_output_items(content: List[Dict[str, Any]], stop_reason: Optional[str]) -> List[Any]:
    """
    Translate a finished Claude turn into Responses output items: one replay
    carrier (see module docstring), then its text and function calls in order.
    """
    items: List[Any] = [
        ResponseReasoningItem(
            id=FAKE_RESPONSES_ID,
            summary=[],
            type='reasoning',
            encrypted_content=json.dumps({REPLAY_KEY: content}),
        )
    ]
    tool_uses = [b for b in content if b.get('type') == 'tool_use']
    # Adjacent text blocks are one message: a cited answer arrives split at
    # every citation, and the Runner takes only the last message as the
    # final reply.
    pending_text: List[str] = []

    def flush_text():
        text = ''.join(pending_text)
        pending_text.clear()
        if text.strip():
            items.append(ResponseOutputMessage(
                id=FAKE_RESPONSES_ID,
                role='assistant',
                status='completed',
                type='message',
                content=[ResponseOutputText(
                    text=text, annotations=[], type='output_text', logprobs=[],
                )],
            ))

    for block in content:
        block_type = block.get('type')
        if block_type == 'text':
            pending_text.append(block.get('text') or '')
            continue
        if block_type in ('thinking', 'redacted_thinking'):
            continue  # invisible; does not split the reply
        flush_text()
        if block_type == 'tool_use':
            # A tool call cut off by the output cap has truncated arguments;
            # running it would act on half an instruction.
            if stop_reason == 'max_tokens' and block is tool_uses[-1]:
                logger.warning("Claude hit max_tokens mid tool call %s; dropping it", block.get('name'))
                continue
            items.append(ResponseFunctionToolCall(
                id=FAKE_RESPONSES_ID,
                call_id=block['id'],
                name=block['name'],
                arguments=json.dumps(block.get('input') or {}),
                type='function_call',
                status='completed',
            ))
    flush_text()

    if stop_reason == 'refusal' and not any(isinstance(i, ResponseOutputMessage) for i in items):
        items.append(ResponseOutputMessage(
            id=FAKE_RESPONSES_ID,
            role='assistant',
            status='completed',
            type='message',
            content=[ResponseOutputText(
                text=REFUSAL_TEXT, annotations=[], type='output_text', logprobs=[],
            )],
        ))
    return items


class _TurnUsage:
    """Usage summed across a turn's requests (a paused turn is several)."""

    def __init__(self):
        self.requests = 0
        self.input_tokens = 0
        self.cached_tokens = 0
        self.output_tokens = 0

    def add(self, usage: Any):
        self.requests += 1
        cache_read = getattr(usage, 'cache_read_input_tokens', 0) or 0
        cache_write = getattr(usage, 'cache_creation_input_tokens', 0) or 0
        # Anthropic reports cached tokens separately from input_tokens; the
        # platform meters every token the model read, cached or not.
        self.input_tokens += (getattr(usage, 'input_tokens', 0) or 0) + cache_read + cache_write
        self.cached_tokens += cache_read
        self.output_tokens += getattr(usage, 'output_tokens', 0) or 0

    def as_agents_usage(self) -> Usage:
        return Usage(
            requests=self.requests,
            input_tokens=self.input_tokens,
            output_tokens=self.output_tokens,
            total_tokens=self.input_tokens + self.output_tokens,
            input_tokens_details=InputTokensDetails(cached_tokens=self.cached_tokens),
            output_tokens_details=OutputTokensDetails(reasoning_tokens=0),
        )

    def as_response_usage(self) -> ResponseUsage:
        return ResponseUsage(
            input_tokens=self.input_tokens,
            output_tokens=self.output_tokens,
            total_tokens=self.input_tokens + self.output_tokens,
            input_tokens_details=InputTokensDetails(cached_tokens=self.cached_tokens),
            output_tokens_details=OutputTokensDetails(reasoning_tokens=0),
        )


class AnthropicModel(Model):
    """An Agents SDK model served by Claude through the Anthropic Messages API."""

    def __init__(self, model: str, *, refusal_fallback: bool = False, client: Any = None):
        self.model = model
        self.refusal_fallback = refusal_fallback
        self._client = client
        self._client_loop = None

    def _get_client(self):
        """
        One AsyncAnthropic per event loop. The sync entry point (Runner.run_sync)
        runs each call on a fresh loop, and an async HTTP client cannot outlive
        the loop it was opened on.
        """
        if self._client is not None and self._client_loop is None:
            return self._client  # injected (tests)
        loop = asyncio.get_running_loop()
        if self._client is None or self._client_loop is not loop:
            import anthropic
            self._client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
            self._client_loop = loop
        return self._client

    def build_request(
        self,
        system_instructions: Optional[str],
        input: Any,
        model_settings: Any,
        tools: List[Any],
        output_schema: Any,
    ) -> Dict[str, Any]:
        """The keyword arguments for client.beta.messages.stream()."""
        extra_system, messages = to_anthropic_messages(input)
        system = '\n\n'.join(t for t in [system_instructions or '', *extra_system] if t)

        request: Dict[str, Any] = {
            'model': self.model,
            'max_tokens': getattr(model_settings, 'max_tokens', None) or DEFAULT_MAX_TOKENS,
            'messages': messages,
            'thinking': {'type': 'adaptive'},
            # An agent loop resends a growing prefix every turn; caching it is
            # the difference between paying for it once and paying every turn.
            'cache_control': {'type': 'ephemeral'},
        }
        if system:
            request['system'] = system

        output_config: Dict[str, Any] = {}
        reasoning = getattr(model_settings, 'reasoning', None)
        effort = getattr(reasoning, 'effort', None)
        if effort in CLAUDE_EFFORTS:
            output_config['effort'] = effort
        if output_schema is not None and not output_schema.is_plain_text():
            output_config['format'] = {'type': 'json_schema', 'schema': output_schema.json_schema()}
        if output_config:
            request['output_config'] = output_config

        sequential = getattr(model_settings, 'parallel_tool_calls', None) is False
        anthropic_tools = to_anthropic_tools(tools, sequential=sequential)
        if anthropic_tools:
            request['tools'] = anthropic_tools
            # Claude takes no forced tool choice with thinking on, so 'required'
            # or a named tool fall back to auto; only 'none' is honored.
            if getattr(model_settings, 'tool_choice', None) == 'none':
                request['tool_choice'] = {'type': 'none'}
            else:
                tool_choice: Dict[str, Any] = {'type': 'auto'}
                if sequential:
                    tool_choice['disable_parallel_tool_use'] = True
                request['tool_choice'] = tool_choice

        if self.refusal_fallback:
            request['fallbacks'] = 'default'
            request['betas'] = [REFUSAL_FALLBACK_BETA]
        return request

    async def _run_turn(self, request: Dict[str, Any], on_text=None):
        """
        Run one assistant turn, streaming text to on_text as it arrives.
        Returns (content blocks, stop_reason, usage). Always streams, so a large
        max_tokens never trips the SDK's long-request guard.
        """
        client = self._get_client()
        usage = _TurnUsage()
        content: List[Dict[str, Any]] = []
        stop_reason = None
        messages = list(request['messages'])

        for _ in range(MAX_PAUSE_CONTINUATIONS + 1):
            async with client.beta.messages.stream(**{**request, 'messages': messages}) as stream:
                async for event in stream:
                    if on_text is None or event.type != 'content_block_delta':
                        continue
                    delta = event.delta
                    if getattr(delta, 'type', None) == 'text_delta' and delta.text:
                        await on_text(delta.text)
                final = await stream.get_final_message()

            usage.add(final.usage)
            content.extend(block.model_dump(mode='json', exclude_none=True) for block in final.content)
            stop_reason = final.stop_reason
            if stop_reason != 'pause_turn':
                break
            # A paused server-tool loop resumes from the partial turn as-is.
            messages = messages + [{
                'role': 'assistant',
                'content': [block.model_dump(mode='json', exclude_none=True) for block in final.content],
            }]

        if stop_reason == 'refusal':
            logger.warning("Claude (%s) declined a request after fallbacks", self.model)
        return content, stop_reason, usage

    async def get_response(
        self,
        system_instructions,
        input,
        model_settings,
        tools,
        output_schema,
        handoffs,
        tracing,
        *,
        previous_response_id=None,
        conversation_id=None,
        prompt=None,
    ) -> ModelResponse:
        request = self.build_request(system_instructions, input, model_settings, tools, output_schema)
        content, stop_reason, usage = await self._run_turn(request)
        return ModelResponse(
            output=to_output_items(content, stop_reason),
            usage=usage.as_agents_usage(),
            response_id=None,
        )

    async def stream_response(
        self,
        system_instructions,
        input,
        model_settings,
        tools,
        output_schema,
        handoffs,
        tracing,
        *,
        previous_response_id=None,
        conversation_id=None,
        prompt=None,
    ) -> AsyncIterator[Any]:
        request = self.build_request(system_instructions, input, model_settings, tools, output_schema)
        sequence = 0

        def next_sequence() -> int:
            nonlocal sequence
            sequence += 1
            return sequence

        base = dict(
            id=FAKE_RESPONSES_ID,
            created_at=time.time(),
            model=self.model,
            object='response',
            tool_choice='auto',
            tools=[],
            parallel_tool_calls=getattr(model_settings, 'parallel_tool_calls', None) is not False,
        )
        yield ResponseCreatedEvent(
            response=Response(output=[], **base),
            type='response.created',
            sequence_number=0,
        )

        # Text deltas are relayed as they arrive through a queue, because the
        # stream is consumed inside _run_turn but has to be yielded from here.
        queue: asyncio.Queue = asyncio.Queue()
        done = object()

        async def on_text(text: str):
            await queue.put(text)

        async def run():
            try:
                return await self._run_turn(request, on_text=on_text)
            finally:
                await queue.put(done)

        task = asyncio.create_task(run())
        try:
            while True:
                chunk = await queue.get()
                if chunk is done:
                    break
                yield ResponseTextDeltaEvent(
                    content_index=0,
                    delta=chunk,
                    item_id=FAKE_RESPONSES_ID,
                    output_index=0,
                    logprobs=[],
                    type='response.output_text.delta',
                    sequence_number=next_sequence(),
                )
            content, stop_reason, usage = await task
        finally:
            if not task.done():
                task.cancel()

        output = to_output_items(content, stop_reason)
        for index, item in enumerate(output):
            yield ResponseOutputItemDoneEvent(
                item=item,
                output_index=index,
                type='response.output_item.done',
                sequence_number=next_sequence(),
            )
        yield ResponseCompletedEvent(
            response=Response(output=output, usage=usage.as_response_usage(), **base),
            type='response.completed',
            sequence_number=next_sequence(),
        )
