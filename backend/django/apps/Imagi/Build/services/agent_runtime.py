"""
The agent loop for the Imagi workspace, on the Anthropic Messages API.

Every run is a plain tool loop against Claude: send the conversation, stream
the reply, run the tools it asked for, send their results back, repeat until
it answers without a tool call. The pieces the rest of the harness relies on
are defined here, so nothing above this module depends on a provider SDK:

  function_tool   turns a Python function into a tool (schema from its
                  signature, description from its docstring)
  Agent           instructions + model + tools + settings for one role
  Runner          run_streamed() for the workspace, run_sync() for the
                  blocking callers (the initial build)
  RunHooks        on_llm_start / on_llm_end, where the cost, time and turn
                  bounds are checked
  RunResult       final_output, new_items (tool calls and their outputs, in
                  order) and context_wrapper.usage

Claude's own server tools (web search) and client toolsets (the preview
browser, see preview_browser_tool) ride alongside the function tools.

Provider-specific behavior lives in two places only: request building
(_build_request) and token accounting (_add_usage). A second provider would
mean a second implementation of those, with the same items and events.
"""

import asyncio
import inspect
import json
import logging
import re
import textwrap
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence

from pydantic import ConfigDict, Field, ValidationError, create_model

from apps.Imagi.Build.services.api_keys import read_api_key

logger = logging.getLogger(__name__)

ANTHROPIC_API_KEY = read_api_key('ANTHROPIC_KEY')

# Output ceiling per model response. Every request streams, so a generous cap
# costs nothing unless it is used; a whole page written in one tool call needs
# the room.
DEFAULT_MAX_TOKENS = 64000

# Efforts Claude accepts on output_config.effort.
CLAUDE_EFFORTS = ('low', 'medium', 'high', 'xhigh', 'max')

# Server-side refusal fallback: when a model's safety classifiers decline a
# request, the API re-runs it on the fallback Anthropic recommends for that
# refusal category instead of returning the refusal.
REFUSAL_FALLBACK_BETA = 'server-side-fallback-2026-07-01'

# Claude's server-side web search. Runs on Anthropic's side inside a single
# response, so the loop never executes it. The current version filters
# results by running code (programmatic tool calling), which the API refuses
# alongside disable_parallel_tool_use — so a run that must call its tools one
# at a time (the coordinator) gets the basic version instead.
WEB_SEARCH_TOOL = {'type': 'web_search_20260209', 'name': 'web_search'}
BASIC_WEB_SEARCH_TOOL = {'type': 'web_search_20250305', 'name': 'web_search'}

# A long server-tool loop can hand the turn back mid-way (stop_reason
# 'pause_turn'); the request is re-sent with the partial turn appended.
# Bounded so a stuck loop cannot spin.
MAX_PAUSE_CONTINUATIONS = 5

# With eager input streaming the server stops validating tool input, so a
# turn whose tool JSON cannot be parsed at all is re-issued, a few times.
MAX_UNPARSEABLE_RETRIES = 2

REFUSAL_TEXT = (
    "I can't help with that request. Try rephrasing it, or pick a different "
    "model from the model menu."
)

TRUNCATED_CALL_TEXT = (
    "This call was cut off by the output limit before its input was complete, "
    "so it was not run. Send it again with less content in one call — for a "
    "large file, write it in parts or use edit_file."
)


class MaxTurnsExceeded(Exception):
    """The run reached its turn cap with the model still calling tools."""


class ModelBehaviorError(Exception):
    """The model produced something the loop cannot act on."""


# ---------------------------------------------------------------------------
# Run context and usage
# ---------------------------------------------------------------------------

@dataclass
class InputTokensDetails:
    cached_tokens: int = 0


@dataclass
class Usage:
    """Tokens a run has used, summed across its requests.

    input_tokens counts every token the model read, cache reads and writes
    included (Anthropic reports those separately); cached_tokens is the part
    served from the prompt cache. long_context_* hold the share that came from
    requests over a model's long-context pricing threshold (see
    models_service), so cost can bill those at the higher rate.
    """

    requests: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    input_tokens_details: InputTokensDetails = field(default_factory=InputTokensDetails)
    long_context_input_tokens: int = 0
    long_context_cached_tokens: int = 0
    long_context_output_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


@dataclass
class RunContextWrapper:
    """What a tool, an instructions callable and a hook receive: the run's own
    context object (AgentContext) plus the run's usage so far."""

    context: Any = None
    usage: Usage = field(default_factory=Usage)


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

def _parse_docstring(doc: str):
    """Split a Google-style docstring into (description, {arg: description})."""
    doc = textwrap.dedent(doc or '').strip()
    if not doc:
        return '', {}
    lines = doc.splitlines()
    # The summary line is not indented like the body, so dedent the body on
    # its own.
    body = textwrap.dedent('\n'.join(lines[1:]))
    text = (lines[0] + '\n' + body).strip()
    match = re.search(r'^Args:\s*$', text, flags=re.MULTILINE)
    if not match:
        return text, {}
    description = text[:match.start()].strip()
    args: Dict[str, str] = {}
    current = None
    for line in text[match.end():].splitlines():
        if not line.strip():
            continue
        if re.match(r'^\S', line):  # a new section (Returns:, ...) ends Args
            break
        entry = re.match(r'^\s{2,4}(\w+)(?:\s*\([^)]*\))?:\s*(.*)$', line)
        if entry:
            current = entry.group(1)
            args[current] = entry.group(2).strip()
        elif current:
            args[current] = (args[current] + ' ' + line.strip()).strip()
    return description, args


def _inline_refs(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Resolve pydantic's $defs/$ref into one self-contained schema."""
    defs = schema.pop('$defs', {})

    def resolve(node):
        if isinstance(node, dict):
            ref = node.get('$ref')
            if isinstance(ref, str) and ref.startswith('#/$defs/'):
                target = dict(defs.get(ref.split('/')[-1], {}))
                extra = {k: v for k, v in node.items() if k != '$ref'}
                return resolve({**target, **extra})
            return {k: resolve(v) for k, v in node.items()}
        if isinstance(node, list):
            return [resolve(v) for v in node]
        return node

    return resolve(schema)


def _strip_titles(node):
    """Drop pydantic's auto-generated titles: noise in every prompt."""
    if isinstance(node, dict):
        return {
            k: _strip_titles(v) for k, v in node.items()
            if not (k == 'title' and isinstance(v, str))
        }
    if isinstance(node, list):
        return [_strip_titles(v) for v in node]
    return node


class FunctionTool:
    """A Python function the model can call.

    The function's first parameter receives the RunContextWrapper; the rest
    are the tool's arguments, validated against its signature before the
    function runs. Synchronous functions run in a worker thread, so their ORM
    access stays off the event loop.
    """

    def __init__(self, func: Callable):
        self.func = func
        self.name = func.__name__
        description, arg_docs = _parse_docstring(func.__doc__ or '')
        self.description = description

        params = list(inspect.signature(func).parameters.values())[1:]
        fields = {}
        for param in params:
            annotation = param.annotation if param.annotation is not inspect.Parameter.empty else Any
            default = ... if param.default is inspect.Parameter.empty else param.default
            fields[param.name] = (annotation, Field(default, description=arg_docs.get(param.name)))
        self._args_model = create_model(
            f'{self.name}_args', __config__=ConfigDict(extra='ignore'), **fields
        )
        schema = _strip_titles(_inline_refs(self._args_model.model_json_schema()))
        schema.setdefault('properties', {})
        schema['type'] = 'object'
        self.params_json_schema = schema

    def to_param(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'description': self.description,
            'input_schema': self.params_json_schema,
            # Large inputs (a whole file) stream as they are generated
            # instead of arriving in one burst; validation is ours then,
            # which on_invoke_tool does.
            'eager_input_streaming': True,
        }

    def parse_arguments(self, arguments: Any) -> Dict[str, Any]:
        """Validated keyword arguments; raises ValueError on bad input."""
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments or '{}')
            except ValueError as e:
                raise ValueError(f"arguments are not valid JSON: {e}")
        if not isinstance(arguments, dict):
            raise ValueError("arguments must be a JSON object")
        try:
            validated = self._args_model.model_validate(arguments)
        except ValidationError as e:
            raise ValueError(str(e))
        return {name: getattr(validated, name) for name in self._args_model.model_fields}

    async def on_invoke_tool(self, ctx: RunContextWrapper, arguments: Any) -> str:
        """Run the tool; bad input comes back to the model as an error."""
        try:
            kwargs = self.parse_arguments(arguments)
        except ValueError as e:
            return json.dumps({
                'success': False,
                'error': f"Invalid arguments for {self.name}: {e}",
            })
        if inspect.iscoroutinefunction(self.func):
            result = await self.func(ctx, **kwargs)
        else:
            result = await asyncio.to_thread(self.func, ctx, **kwargs)
        if isinstance(result, str):
            return result
        return json.dumps(result, default=str)

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


def function_tool(func: Callable) -> FunctionTool:
    """Decorator: expose a function to the agent as a tool."""
    return FunctionTool(func)


class WebSearchTool:
    """Claude's server-side web search (runs on Anthropic's side)."""

    name = 'web_search'

    def to_param(self, sequential: bool = False) -> Dict[str, Any]:
        return dict(BASIC_WEB_SEARCH_TOOL if sequential else WEB_SEARCH_TOOL)


class ClientToolset:
    """An Anthropic-defined client toolset the harness executes (for example
    browser_toolset_20260801). Subclasses provide the tools[] entry and run
    one member call at a time.

    run_member returns (content blocks, is_error). Member calls in a turn run
    in order and stop at the first failure, as the toolset contract requires.
    """

    toolset_name = ''
    halt_text = 'Not executed: an earlier action in this turn failed.'

    def to_param(self) -> Dict[str, Any]:  # pragma: no cover - abstract
        raise NotImplementedError

    def run_member(self, ctx: RunContextWrapper, name: str, tool_input: Dict[str, Any]):  # pragma: no cover
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Agent definition
# ---------------------------------------------------------------------------

@dataclass
class ModelSettings:
    """Per-agent request settings."""

    effort: Optional[str] = None
    # False: the model calls one tool per turn and sees each result before
    # the next (the coordinator, whose dispatches have side effects).
    parallel_tool_calls: Optional[bool] = None
    max_tokens: Optional[int] = None
    # Opt into the server-side refusal fallback (models that support it).
    refusal_fallback: bool = False


@dataclass
class StopAtTools:
    """End the run when one of these tools is called; its output becomes the
    run's final output (ask_user: the user's answer is the next turn)."""

    stop_at_tool_names: Sequence[str] = ()


@dataclass
class Agent:
    name: str
    instructions: Any  # str, or callable(RunContextWrapper, Agent) -> str
    model: str  # the provider model id
    tools: List[Any] = field(default_factory=list)
    model_settings: ModelSettings = field(default_factory=ModelSettings)
    tool_use_behavior: Optional[StopAtTools] = None

    def system_prompt(self, wrapper: RunContextWrapper) -> str:
        if callable(self.instructions):
            return self.instructions(wrapper, self)
        return self.instructions or ''


class RunHooks:
    """Lifecycle hooks. on_llm_start runs before every model request,
    on_llm_end after each finished turn with the run's usage already updated.
    Raising from either stops the run with that exception."""

    async def on_llm_start(self, context, agent, system_prompt, input_items):  # noqa: ANN001
        return None

    async def on_llm_end(self, context, agent, response):  # noqa: ANN001
        return None


@dataclass
class RunConfig:
    """Kept for call-site symmetry; carries tracing labels only."""

    workflow_name: str = ''
    trace_metadata: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Items and stream events
# ---------------------------------------------------------------------------

@dataclass
class ToolCall:
    """One tool call as the model made it. type ends in '_call'."""

    name: str
    arguments: str  # JSON text
    call_id: str
    type: str = 'function_call'  # | 'web_search_call' | 'browser_call'


@dataclass
class ToolCallItem:
    raw_item: ToolCall
    type: str = 'tool_call_item'


@dataclass
class ToolCallOutputItem:
    raw_item: ToolCall
    output: str
    type: str = 'tool_call_output_item'


@dataclass
class MessageOutputItem:
    text: str
    type: str = 'message_output_item'


@dataclass
class TextDeltaEvent:
    delta: str
    type: str = 'text_delta'


@dataclass
class RunItemStreamEvent:
    item: Any
    type: str = 'run_item_stream_event'


@dataclass
class ModelTurn:
    """What on_llm_end receives: the turn's tool calls (output) and usage."""

    output: List[ToolCall]
    stop_reason: Optional[str]


# ---------------------------------------------------------------------------
# Request building and accounting (provider-specific)
# ---------------------------------------------------------------------------

def to_api_messages(input_items: Any) -> List[Dict[str, Any]]:
    """Plain {role, content} history into Messages API turns.

    Consecutive same-role messages are merged and empty ones dropped, since
    the API requires alternating, non-empty turns.
    """
    if isinstance(input_items, str):
        return [{'role': 'user', 'content': input_items}]
    turns: List[Dict[str, Any]] = []
    for item in input_items or []:
        role = item.get('role')
        content = item.get('content')
        if role not in ('user', 'assistant'):
            continue
        if isinstance(content, str):
            if not content.strip():
                continue
            blocks = [{'type': 'text', 'text': content}]
        else:
            blocks = list(content or [])
            if not blocks:
                continue
        if turns and turns[-1]['role'] == role:
            turns[-1]['content'].extend(blocks)
        else:
            turns.append({'role': role, 'content': blocks})
    # The conversation must open with the user.
    while turns and turns[0]['role'] != 'user':
        turns.pop(0)
    return turns


def _tool_params(agent: Agent) -> List[Dict[str, Any]]:
    sequential = agent.model_settings.parallel_tool_calls is False
    params = []
    for tool in agent.tools:
        if isinstance(tool, WebSearchTool):
            params.append(tool.to_param(sequential=sequential))
        else:
            params.append(tool.to_param())
    return params


def _build_request(agent: Agent, system: str, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Keyword arguments for client.beta.messages.stream()."""
    settings_ = agent.model_settings
    request: Dict[str, Any] = {
        'model': agent.model,
        'max_tokens': settings_.max_tokens or DEFAULT_MAX_TOKENS,
        'messages': messages,
        'thinking': {'type': 'adaptive'},
        # An agent loop resends a growing prefix every turn; caching it is the
        # difference between paying for it once and paying every turn. This
        # automatic breakpoint caches up to the end of the request, which the
        # loop's next turn extends.
        'cache_control': {'type': 'ephemeral'},
    }
    if system:
        # A second breakpoint after the tools and system prompt — the part
        # every request in the conversation shares. The automatic one alone
        # only pays off inside a run: the next user message changes the end
        # of the prompt, so without this the whole prefix would be rebilled
        # at the full input rate on every new message.
        request['system'] = [
            {'type': 'text', 'text': system, 'cache_control': {'type': 'ephemeral'}}
        ]
    if settings_.effort in CLAUDE_EFFORTS:
        request['output_config'] = {'effort': settings_.effort}

    tools = _tool_params(agent)
    if tools:
        request['tools'] = tools
        # The current models take no forced tool choice; auto it is.
        tool_choice: Dict[str, Any] = {'type': 'auto'}
        if settings_.parallel_tool_calls is False:
            tool_choice['disable_parallel_tool_use'] = True
        request['tool_choice'] = tool_choice

    if settings_.refusal_fallback:
        request['fallbacks'] = 'default'
        request['betas'] = [REFUSAL_FALLBACK_BETA]
    return request


def _add_usage(usage: Usage, api_usage: Any, model_id: Optional[str] = None) -> None:
    """Fold one response's usage into the run's."""
    cache_read = getattr(api_usage, 'cache_read_input_tokens', 0) or 0
    cache_write = getattr(api_usage, 'cache_creation_input_tokens', 0) or 0
    fresh = getattr(api_usage, 'input_tokens', 0) or 0
    output = getattr(api_usage, 'output_tokens', 0) or 0
    # The platform meters every token the model read, cached or not.
    prompt = fresh + cache_read + cache_write
    usage.requests += 1
    usage.input_tokens += prompt
    usage.input_tokens_details.cached_tokens += cache_read
    usage.output_tokens += output

    from .models_service import long_context_threshold
    threshold = long_context_threshold(model_id) if model_id else None
    if threshold and prompt > threshold:
        usage.long_context_input_tokens += prompt
        usage.long_context_cached_tokens += cache_read
        usage.long_context_output_tokens += output


def _block_dict(block: Any) -> Dict[str, Any]:
    if isinstance(block, dict):
        return block
    return block.model_dump(mode='json', exclude_none=True)


# ---------------------------------------------------------------------------
# The loop
# ---------------------------------------------------------------------------

class RunResult:
    """A run's outcome, readable while it is still going (new_items and usage
    fill in as it progresses, so a run cut short still reports its work)."""

    def __init__(self, context_wrapper: RunContextWrapper):
        self.context_wrapper = context_wrapper
        self.new_items: List[Any] = []
        self.final_output: Optional[str] = None


class RunResultStreaming(RunResult):
    def __init__(self, runner: '_Run'):
        super().__init__(runner.wrapper)
        self._runner = runner
        runner.result = self

    def stream_events(self):
        return self._runner.events()


def _client():
    import anthropic
    return anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)


class _Run:
    """One agent run: the loop, surfaced as an async stream of events."""

    def __init__(self, agent: Agent, input_items: Any, context: Any,
                 max_turns: int, hooks: Optional[RunHooks]):
        self.agent = agent
        self.messages = to_api_messages(input_items)
        self.wrapper = RunContextWrapper(context=context)
        self.max_turns = max_turns
        self.hooks = hooks
        self.result: Optional[RunResult] = None
        self._tools = {t.name: t for t in agent.tools if isinstance(t, FunctionTool)}
        self._toolsets = {
            t.toolset_name: t for t in agent.tools if isinstance(t, ClientToolset)
        }
        stop = agent.tool_use_behavior
        self._stop_at = set(stop.stop_at_tool_names) if stop else set()

    async def events(self):
        client = _client()
        try:
            async for event in self._loop(client):
                yield event
        finally:
            try:
                await client.close()
            except Exception:  # pragma: no cover - best effort
                pass

    def _record(self, item):
        self.result.new_items.append(item)
        return RunItemStreamEvent(item=item)

    async def _loop(self, client):
        system = self.agent.system_prompt(self.wrapper)
        turns = 0
        while True:
            turns += 1
            if turns > self.max_turns:
                raise MaxTurnsExceeded(f"Max turns ({self.max_turns}) exceeded")
            if self.hooks is not None:
                await self.hooks.on_llm_start(self.wrapper, self.agent, system, self.messages)

            content: List[Dict[str, Any]] = []
            stop_reason = None
            async for event in self._model_turn(client, system, content):
                yield event
            stop_reason = self._last_stop_reason

            self.messages.append({'role': 'assistant', 'content': content})
            text = ''.join(b.get('text') or '' for b in content if b.get('type') == 'text')

            # Server tool calls (web search) already ran inside the response;
            # surface them so the activity feed shows them.
            for block in content:
                if block.get('type') == 'server_tool_use':
                    call = ToolCall(
                        name=block.get('name') or 'web_search',
                        arguments=json.dumps(block.get('input') or {}),
                        call_id=block.get('id') or '',
                        type=f"{block.get('name') or 'server'}_call",
                    )
                    yield self._record(ToolCallItem(raw_item=call))

            tool_uses = [b for b in content if b.get('type') == 'tool_use']
            # A toolset member is named after its toolset too
            # ('browser_screenshot'), so it can't be mistaken for a function
            # tool of the same name in the activity feed.
            calls = [
                ToolCall(
                    name=(
                        f"{b['toolset_name']}_{b.get('name') or ''}"
                        if b.get('toolset_name') else b.get('name') or ''
                    ),
                    arguments=json.dumps(b.get('input') or {}),
                    call_id=b.get('id') or '',
                    type=f"{b['toolset_name']}_call" if b.get('toolset_name') else 'function_call',
                )
                for b in tool_uses
            ]
            if self.hooks is not None:
                await self.hooks.on_llm_end(
                    self.wrapper, self.agent, ModelTurn(output=calls, stop_reason=stop_reason)
                )

            if stop_reason == 'refusal':
                logger.warning("Claude (%s) declined a request", self.agent.model)
                self.result.final_output = text.strip() or REFUSAL_TEXT
                self.result.new_items.append(MessageOutputItem(text=self.result.final_output))
                return

            if not tool_uses:
                if text.strip():
                    self.result.new_items.append(MessageOutputItem(text=text))
                self.result.final_output = text
                return

            for call in calls:
                yield self._record(ToolCallItem(raw_item=call))

            results, stop_output = await self._run_tools(tool_uses, calls, stop_reason)
            for call, result in zip(calls, results):
                output = result.get('content')
                if not isinstance(output, str):
                    output = json.dumps(
                        [b for b in output if b.get('type') == 'text'], default=str
                    )
                yield self._record(ToolCallOutputItem(raw_item=call, output=output))

            if stop_output is not None:
                # A stop-at tool (ask_user) ends the run; its output is the
                # final answer and nothing is sent back to the model.
                self.result.final_output = stop_output
                return
            self.messages.append({'role': 'user', 'content': results})

    async def _model_turn(self, client, system, content):
        """Stream one assistant turn into content, yielding text deltas.

        Handles pause_turn (a long server-tool loop handed back mid-way) and
        re-issues a turn whose tool input could not be parsed at all.
        """
        messages = list(self.messages)
        self._last_stop_reason = None
        unparseable = 0
        pauses = 0
        while True:
            request = _build_request(self.agent, system, messages)
            turn_blocks: List[Dict[str, Any]] = []
            try:
                async with client.beta.messages.stream(**request) as stream:
                    async for event in stream:
                        if event.type == 'content_block_delta':
                            delta = event.delta
                            if getattr(delta, 'type', None) == 'text_delta' and delta.text:
                                yield TextDeltaEvent(delta=delta.text)
                    final = await stream.get_final_message()
            except ValueError:
                # Tool input JSON the SDK could not parse at all: there is no
                # complete tool_use to answer, so re-issue the turn. API
                # errors are not ValueError and propagate.
                unparseable += 1
                if unparseable > MAX_UNPARSEABLE_RETRIES:
                    raise ModelBehaviorError("The model's tool input could not be parsed.")
                logger.warning("Unparseable tool input from %s; re-issuing the turn", self.agent.model)
                continue

            _add_usage(self.wrapper.usage, final.usage, self.agent.model)
            turn_blocks = [_block_dict(b) for b in final.content]
            content.extend(turn_blocks)
            self._last_stop_reason = final.stop_reason
            if final.stop_reason != 'pause_turn' or pauses >= MAX_PAUSE_CONTINUATIONS:
                return
            pauses += 1
            # A paused server-tool loop resumes from the partial turn as-is.
            messages = messages + [{'role': 'assistant', 'content': turn_blocks}]

    async def _run_tools(self, tool_uses, calls, stop_reason):
        """Run a turn's tool calls; returns (tool_result blocks, stop output).

        Function tools run concurrently; toolset members run in order and
        stop at the first failure. Results come back in the calls' order.
        """
        results: List[Optional[Dict[str, Any]]] = [None] * len(tool_uses)
        stop_output = None

        async def run_function(index, block):
            tool = self._tools.get(block.get('name'))
            if tool is None:
                output = json.dumps({'success': False, 'error': f"Unknown tool: {block.get('name')}"})
            else:
                output = await tool.on_invoke_tool(self.wrapper, block.get('input') or {})
            results[index] = {
                'type': 'tool_result',
                'tool_use_id': block['id'],
                'content': output or '(no output)',
            }

        function_jobs = []
        toolset_jobs: Dict[str, List[int]] = {}
        last = len(tool_uses) - 1
        for index, block in enumerate(tool_uses):
            if stop_reason == 'max_tokens' and index == last:
                # Cut off mid-input by the output cap: running it would act
                # on half an instruction.
                result = {
                    'type': 'tool_result',
                    'tool_use_id': block['id'],
                    'is_error': True,
                    'content': TRUNCATED_CALL_TEXT,
                }
                if block.get('toolset_name'):
                    result['toolset_name'] = block['toolset_name']
                results[index] = result
                continue
            if block.get('toolset_name'):
                toolset_jobs.setdefault(block['toolset_name'], []).append(index)
            else:
                function_jobs.append(run_function(index, block))

        async def run_toolset(name, indexes):
            toolset = self._toolsets.get(name)
            failed = False
            for index in indexes:
                block = tool_uses[index]
                result = {'type': 'tool_result', 'tool_use_id': block['id'], 'toolset_name': name}
                if toolset is None:
                    result.update(is_error=True, content=f"Error: the {name} tools are not available here.")
                    failed = True
                elif failed:
                    result.update(is_error=True, content=toolset.halt_text)
                else:
                    try:
                        blocks, is_error = await asyncio.to_thread(
                            toolset.run_member, self.wrapper, block.get('name') or '',
                            block.get('input') or {},
                        )
                    except Exception as e:  # a failed action is the model's to see
                        logger.info("%s.%s failed: %s", name, block.get('name'), e)
                        blocks, is_error = f"Error: {e}", True
                    result['content'] = blocks
                    if is_error:
                        result['is_error'] = True
                        failed = True
                results[index] = result

        await asyncio.gather(
            *function_jobs,
            *(run_toolset(name, indexes) for name, indexes in toolset_jobs.items()),
        )

        for call, result in zip(calls, results):
            if call.name in self._stop_at and not result.get('is_error'):
                stop_output = result.get('content') if isinstance(result.get('content'), str) else ''
                break
        return results, stop_output


class Runner:
    """Entry points for running an agent."""

    @staticmethod
    def run_streamed(agent: Agent, input: Any, context: Any = None, max_turns: int = 10,
                     run_config: Optional[RunConfig] = None, hooks: Optional[RunHooks] = None):
        """Start a run that advances as its stream_events() is consumed."""
        return RunResultStreaming(_Run(agent, input, context, max_turns, hooks))

    @staticmethod
    def run_sync(agent: Agent, input: Any, context: Any = None, max_turns: int = 10,
                 run_config: Optional[RunConfig] = None, hooks: Optional[RunHooks] = None):
        """Run to completion on a fresh event loop (for synchronous callers)."""
        result = Runner.run_streamed(agent, input, context, max_turns, run_config, hooks)

        async def drain():
            async for _ in result.stream_events():
                pass

        asyncio.run(drain())
        return result
