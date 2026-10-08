"""
The workspace's agent loop (services/agent_runtime.py), run against a fake
Anthropic client: what it sends, how it runs tools, and how it stops.
"""

import json
from types import SimpleNamespace
from unittest import mock

from asgiref.sync import async_to_sync
from django.test import SimpleTestCase

from apps.Imagi.Build.services import agent_runtime
from apps.Imagi.Build.services.agent_runtime import (
    Agent,
    ClientToolset,
    MaxTurnsExceeded,
    ModelSettings,
    RunContextWrapper,
    Runner,
    RunHooks,
    StopAtTools,
    Usage,
    WebSearchTool,
    _add_usage,
    _build_request,
    function_tool,
    to_api_messages,
)


def _usage(input_tokens=100, output_tokens=10, cache_read=0, cache_write=0):
    return SimpleNamespace(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cache_read_input_tokens=cache_read,
        cache_creation_input_tokens=cache_write,
    )


def _turn(content, stop_reason='end_turn', usage=None):
    """One scripted response: content blocks as dicts."""
    return SimpleNamespace(content=content, stop_reason=stop_reason, usage=usage or _usage())


def _text(text):
    return {'type': 'text', 'text': text}


def _tool_use(name, tool_input, id_, toolset=None):
    block = {'type': 'tool_use', 'id': id_, 'name': name, 'input': tool_input}
    if toolset:
        block['toolset_name'] = toolset
    return block


class _FakeStream:
    def __init__(self, response):
        self._response = response

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    def __aiter__(self):
        async def gen():
            if isinstance(self._response, Exception):
                raise self._response
            for block in self._response.content:
                if block.get('type') == 'text':
                    yield SimpleNamespace(
                        type='content_block_delta',
                        delta=SimpleNamespace(type='text_delta', text=block['text']),
                    )
        return gen()

    async def get_final_message(self):
        return self._response


class _FakeClient:
    """Plays back scripted responses and records each request."""

    def __init__(self, responses):
        self.responses = list(responses)
        self.requests = []
        self.closed = False
        self.beta = SimpleNamespace(messages=SimpleNamespace(stream=self._stream))

    def _stream(self, **request):
        self.requests.append(json.loads(json.dumps(request, default=str)))
        return _FakeStream(self.responses.pop(0))

    async def close(self):
        self.closed = True


def _run(agent, prompt='hi', responses=(), max_turns=10, hooks=None, context=None):
    client = _FakeClient(responses)
    events = []
    with mock.patch.object(agent_runtime, '_client', return_value=client):
        result = Runner.run_streamed(
            agent, prompt, context=context, max_turns=max_turns, hooks=hooks
        )

        async def drain():
            async for event in result.stream_events():
                events.append(event)

        try:
            async_to_sync(drain)()
        except Exception as e:  # surfaced to the test with what ran so far
            return result, client, events, e
    return result, client, events, None


@function_tool
def add_numbers(ctx, a: int, b: int) -> str:
    """Add two numbers.

    Args:
        a: The first number.
        b: The second number.
    """
    return str(a + b)


@function_tool
def ask_user(ctx, question: str) -> str:
    """Ask the user something.

    Args:
        question: What to ask.
    """
    return f"asked: {question}"


class _Browser(ClientToolset):
    toolset_name = 'browser'
    name = 'browser'

    def __init__(self, fail_on=()):
        self.fail_on = set(fail_on)
        self.ran = []

    def to_param(self):
        return {'type': 'browser_toolset_20260801'}

    def run_member(self, ctx, name, tool_input):
        self.ran.append(name)
        if name in self.fail_on:
            return 'Error: no such element', True
        return [{'type': 'text', 'text': f'{name} ok'}], False


class FunctionToolTests(SimpleTestCase):
    def test_schema_comes_from_the_signature_and_docstring(self):
        param = add_numbers.to_param()
        self.assertEqual(param['name'], 'add_numbers')
        self.assertEqual(param['description'], 'Add two numbers.')
        self.assertTrue(param['eager_input_streaming'])
        schema = param['input_schema']
        self.assertEqual(schema['required'], ['a', 'b'])
        self.assertEqual(schema['properties']['a']['type'], 'integer')
        self.assertEqual(schema['properties']['b']['description'], 'The second number.')
        self.assertNotIn('ctx', schema['properties'])
        self.assertNotIn('title', schema)

    def test_invalid_input_is_an_error_result_not_a_crash(self):
        # Eager streaming leaves validation to the client: a truncated or
        # wrong-typed input must come back to the model as an error.
        out = async_to_sync(add_numbers.on_invoke_tool)(RunContextWrapper(), {'a': 'x'})
        self.assertIn('error', json.loads(out))
        out = async_to_sync(add_numbers.on_invoke_tool)(RunContextWrapper(), {'a': 1, 'b': 2})
        self.assertEqual(out, '3')


class RequestTests(SimpleTestCase):
    def _agent(self, **settings):
        return Agent(
            name='t', instructions='Be brief.', model='claude-opus-5-5',
            tools=[add_numbers, WebSearchTool()], model_settings=ModelSettings(**settings),
        )

    def test_request_shape(self):
        request = _build_request(
            self._agent(effort='max', refusal_fallback=True), 'Be brief.',
            to_api_messages('hi'),
        )
        self.assertEqual(request['model'], 'claude-opus-5-5')
        self.assertEqual(request['thinking'], {'type': 'adaptive'})
        self.assertEqual(request['output_config'], {'effort': 'max'})
        self.assertEqual(request['cache_control'], {'type': 'ephemeral'})
        self.assertEqual(request['system'][0]['cache_control'], {'type': 'ephemeral'})
        self.assertEqual(request['tool_choice'], {'type': 'auto'})
        self.assertEqual(request['fallbacks'], 'default')
        self.assertIn('server-side-fallback-2026-07-01', request['betas'])
        self.assertIn({'type': 'web_search_20260209', 'name': 'web_search'}, request['tools'])

    def test_sequential_agent_gets_one_tool_per_turn_and_basic_search(self):
        request = _build_request(
            self._agent(parallel_tool_calls=False), 'x', to_api_messages('hi')
        )
        self.assertTrue(request['tool_choice']['disable_parallel_tool_use'])
        self.assertIn({'type': 'web_search_20250305', 'name': 'web_search'}, request['tools'])
        self.assertNotIn('fallbacks', request)
        self.assertNotIn('output_config', request)

    def test_history_is_merged_into_alternating_turns(self):
        turns = to_api_messages([
            {'role': 'assistant', 'content': 'orphan'},
            {'role': 'user', 'content': 'a'},
            {'role': 'user', 'content': 'b'},
            {'role': 'assistant', 'content': '  '},
            {'role': 'assistant', 'content': 'c'},
        ])
        self.assertEqual([t['role'] for t in turns], ['user', 'assistant'])
        self.assertEqual(len(turns[0]['content']), 2)


class UsageTests(SimpleTestCase):
    def test_input_counts_cache_reads_and_writes(self):
        usage = Usage()
        _add_usage(usage, _usage(100, 20, cache_read=900, cache_write=50), 'claude-opus-5-5')
        self.assertEqual(usage.input_tokens, 1050)
        self.assertEqual(usage.input_tokens_details.cached_tokens, 900)
        self.assertEqual(usage.output_tokens, 20)
        self.assertEqual(usage.long_context_input_tokens, 0)

    def test_haiku_requests_over_the_threshold_are_tracked_as_long(self):
        usage = Usage()
        _add_usage(usage, _usage(50_000), 'claude-haiku-5-5')
        _add_usage(usage, _usage(150_000, 30), 'claude-haiku-5-5')
        self.assertEqual(usage.input_tokens, 200_000)
        self.assertEqual(usage.long_context_input_tokens, 150_000)
        self.assertEqual(usage.long_context_output_tokens, 30)


class LoopTests(SimpleTestCase):
    def _agent(self, tools=(), stop=None, instructions='sys'):
        return Agent(
            name='t', instructions=instructions, model='claude-opus-5-5',
            tools=list(tools), tool_use_behavior=stop,
        )

    def test_plain_answer_streams_text_and_ends(self):
        result, client, events, error = _run(self._agent(), responses=[_turn([_text('Hello')])])
        self.assertIsNone(error)
        self.assertEqual(result.final_output, 'Hello')
        self.assertEqual([e.delta for e in events if e.type == 'text_delta'], ['Hello'])
        self.assertEqual(result.context_wrapper.usage.requests, 1)
        self.assertTrue(client.closed)

    def test_tool_call_runs_and_its_result_goes_back(self):
        result, client, events, error = _run(
            self._agent([add_numbers]),
            responses=[
                _turn([_tool_use('add_numbers', {'a': 2, 'b': 3}, 'tu_1')], 'tool_use'),
                _turn([_text('5')]),
            ],
        )
        self.assertIsNone(error)
        self.assertEqual(result.final_output, '5')
        second = client.requests[1]['messages']
        self.assertEqual(second[-1]['content'][0]['type'], 'tool_result')
        self.assertEqual(second[-1]['content'][0]['tool_use_id'], 'tu_1')
        self.assertEqual(second[-1]['content'][0]['content'], '5')
        types = [getattr(i, 'type', '') for i in result.new_items]
        self.assertEqual(
            types, ['tool_call_item', 'tool_call_output_item', 'message_output_item']
        )

    def test_stop_at_tool_ends_the_run_with_its_output(self):
        result, client, _, error = _run(
            self._agent([ask_user], stop=StopAtTools(['ask_user'])),
            responses=[_turn([_tool_use('ask_user', {'question': 'Blue?'}, 'tu_1')], 'tool_use')],
        )
        self.assertIsNone(error)
        self.assertEqual(result.final_output, 'asked: Blue?')
        self.assertEqual(len(client.requests), 1)

    def test_turn_cap_raises_max_turns(self):
        call = _turn([_tool_use('add_numbers', {'a': 1, 'b': 1}, 'tu')], 'tool_use')
        _, client, _, error = _run(
            self._agent([add_numbers]), responses=[call, call, call], max_turns=2
        )
        self.assertIsInstance(error, MaxTurnsExceeded)
        self.assertEqual(len(client.requests), 2)

    def test_refusal_ends_with_a_plain_message(self):
        result, _, _, error = _run(
            self._agent(), responses=[_turn([], 'refusal')]
        )
        self.assertIsNone(error)
        self.assertEqual(result.final_output, agent_runtime.REFUSAL_TEXT)

    def test_a_call_cut_off_by_max_tokens_is_not_run(self):
        ran = []

        @function_tool
        def write(ctx, text: str) -> str:
            """Write.

            Args:
                text: Text.
            """
            ran.append(text)
            return 'ok'

        _, client, _, error = _run(
            self._agent([write]),
            responses=[
                _turn([_tool_use('write', {'text': 'half'}, 'tu')], 'max_tokens'),
                _turn([_text('done')]),
            ],
        )
        self.assertIsNone(error)
        self.assertEqual(ran, [])
        result_block = client.requests[1]['messages'][-1]['content'][0]
        self.assertTrue(result_block['is_error'])

    def test_pause_turn_resends_the_partial_turn(self):
        result, client, _, error = _run(
            self._agent(),
            responses=[_turn([_text('Searching ')], 'pause_turn'), _turn([_text('found it')])],
        )
        self.assertIsNone(error)
        self.assertEqual(len(client.requests), 2)
        self.assertEqual(client.requests[1]['messages'][-1]['role'], 'assistant')
        self.assertEqual(result.final_output, 'Searching found it')

    def test_unparseable_tool_input_reissues_the_turn(self):
        result, client, _, error = _run(
            self._agent(), responses=[ValueError('bad json'), _turn([_text('ok')])]
        )
        self.assertIsNone(error)
        self.assertEqual(result.final_output, 'ok')
        self.assertEqual(len(client.requests), 2)

    def test_hooks_see_each_turn_and_can_stop_the_run(self):
        class Stop(Exception):
            pass

        seen = []

        class Hooks(RunHooks):
            async def on_llm_end(self, context, agent, response):
                seen.append((context.usage.requests, [c.name for c in response.output]))
                raise Stop()

        _, _, _, error = _run(
            self._agent([add_numbers]),
            responses=[_turn([_tool_use('add_numbers', {'a': 1, 'b': 1}, 'tu')], 'tool_use')],
            hooks=Hooks(),
        )
        self.assertIsInstance(error, Stop)
        self.assertEqual(seen, [(1, ['add_numbers'])])

    def test_instructions_callable_receives_the_context(self):
        agent = self._agent(instructions=lambda wrapper, agent: f"ctx={wrapper.context}")
        _, client, _, _ = _run(agent, responses=[_turn([_text('x')])], context='abc')
        self.assertEqual(client.requests[0]['system'][0]['text'], 'ctx=abc')


class ToolsetTests(SimpleTestCase):
    def test_members_run_in_order_and_halt_after_a_failure(self):
        browser = _Browser(fail_on={'left_click'})
        agent = Agent(name='t', instructions='', model='claude-opus-5-5', tools=[browser])
        result, client, _, error = _run(
            agent,
            responses=[
                _turn([
                    _tool_use('screenshot', {}, 'a', 'browser'),
                    _tool_use('left_click', {}, 'b', 'browser'),
                    _tool_use('type', {'text': 'x'}, 'c', 'browser'),
                ], 'tool_use'),
                _turn([_text('done')]),
            ],
        )
        self.assertIsNone(error)
        self.assertEqual(browser.ran, ['screenshot', 'left_click'])
        results = client.requests[1]['messages'][-1]['content']
        self.assertEqual([r['toolset_name'] for r in results], ['browser'] * 3)
        self.assertNotIn('is_error', results[0])
        self.assertTrue(results[1]['is_error'])
        self.assertEqual(results[2]['content'], browser.halt_text)
        # The activity feed names members after their toolset.
        names = [i.raw_item.name for i in result.new_items if i.type == 'tool_call_item']
        self.assertEqual(names, ['browser_screenshot', 'browser_left_click', 'browser_type'])
