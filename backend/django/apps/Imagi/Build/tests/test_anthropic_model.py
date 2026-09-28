"""
Tests for Claude support in the Imagi agent (services/anthropic_model.py).

The adapter is driven through the real Agents SDK Runner against a scripted
fake of the Anthropic client, so the translation both ways — Responses items
into Anthropic messages and Claude's content back out — is checked end to end
without network calls.
"""

import json
from types import SimpleNamespace

from agents import Agent, Runner, WebSearchTool, function_tool
from anthropic.types.beta import BetaMessage
from asgiref.sync import async_to_sync
from django.test import SimpleTestCase

from apps.Imagi.Build.services.anthropic_model import (
    DEFAULT_MAX_TOKENS,
    REFUSAL_FALLBACK_BETA,
    REFUSAL_TEXT,
    AnthropicModel,
    to_anthropic_messages,
    to_output_items,
)
from apps.Imagi.Build.services.base_agent import build_model_settings
from apps.Imagi.Build.services.coding_agent import build_agent_model, create_coding_agent
from apps.Imagi.Build.services.models_service import (
    compute_cost_usd,
    get_model_choices,
    get_model_provider,
    get_model_reasoning_efforts,
    resolve_reasoning_effort,
)

CLAUDE_MODELS = ('claude-opus-5-5',)


def _message(content, stop_reason='end_turn', usage=None):
    return BetaMessage.model_validate({
        'id': 'msg_test',
        'type': 'message',
        'role': 'assistant',
        'model': 'claude-sonnet-5',
        'content': content,
        'stop_reason': stop_reason,
        'stop_sequence': None,
        'usage': usage or {'input_tokens': 10, 'output_tokens': 5},
    })


class _FakeStream:
    def __init__(self, message):
        self._message = message

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    def __aiter__(self):
        return self._events()

    async def _events(self):
        for block in self._message.content:
            if block.type == 'text':
                yield SimpleNamespace(
                    type='content_block_delta',
                    delta=SimpleNamespace(type='text_delta', text=block.text),
                )

    async def get_final_message(self):
        return self._message


class _FakeClient:
    """Plays back scripted messages and records every request it was sent."""

    def __init__(self, *messages):
        self._messages = list(messages)
        self.requests = []
        self.beta = SimpleNamespace(messages=SimpleNamespace(stream=self._stream))

    def _stream(self, **request):
        self.requests.append(json.loads(json.dumps(request)))
        return _FakeStream(self._messages.pop(0))


@function_tool
def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b


class ClaudeRegistryTests(SimpleTestCase):
    def test_claude_models_are_offered_with_the_shared_effort_ladder(self):
        ids = [model_id for model_id, _ in get_model_choices()]
        for model_id in CLAUDE_MODELS:
            self.assertIn(model_id, ids)
            self.assertEqual(get_model_provider(model_id), 'anthropic')
            self.assertEqual(get_model_reasoning_efforts(model_id), ['low', 'medium', 'high', 'xhigh'])
            self.assertEqual(resolve_reasoning_effort(model_id, 'max'), 'xhigh')
        self.assertEqual(get_model_provider('gpt-6-luna'), 'openai')
        self.assertEqual(get_model_provider('gpt-6-astra'), 'openai')

    def test_claude_is_billed_at_list_price(self):
        # Opus 5.5 lists at $4 / $20 per million tokens, $0.20 cache reads.
        self.assertEqual(compute_cost_usd('claude-opus-5-5', 1_000_000, 0), 4.0)
        self.assertEqual(compute_cost_usd('claude-opus-5-5', 0, 1_000_000), 20.0)
        self.assertEqual(compute_cost_usd('claude-opus-5-5', 1_000_000, 0, 1_000_000), 0.2)

    def test_the_agent_is_served_by_the_provider_of_its_model(self):
        self.assertEqual(build_agent_model('gpt-6-luna'), 'gpt-6-luna')
        claude = build_agent_model('claude-opus-5-5')
        self.assertIsInstance(claude, AnthropicModel)
        self.assertEqual(claude.model, 'claude-opus-5-5')
        self.assertTrue(claude.refusal_fallback)

        agent = create_coding_agent('claude-opus-5-5', 'high', kind='chat')
        self.assertIsInstance(agent.model, AnthropicModel)
        self.assertEqual(agent.model_settings.reasoning.effort, 'high')


class ClaudeRequestTests(SimpleTestCase):
    def test_request_carries_effort_caching_thinking_and_tools(self):
        model = AnthropicModel('claude-opus-5-5', refusal_fallback=True)
        request = model.build_request(
            'You are Imagi.',
            'hello',
            build_model_settings('xhigh', parallel_tool_calls=False, service_tier='priority'),
            [add, WebSearchTool()],
            None,
        )
        self.assertEqual(request['model'], 'claude-opus-5-5')
        # The shared prefix (tools + system) gets its own cache breakpoint, so
        # it is reused across messages, not just within one run's loop.
        self.assertEqual(request['system'], [
            {'type': 'text', 'text': 'You are Imagi.', 'cache_control': {'type': 'ephemeral'}},
        ])
        self.assertEqual(request['messages'], [{'role': 'user', 'content': 'hello'}])
        self.assertEqual(request['max_tokens'], DEFAULT_MAX_TOKENS)
        self.assertEqual(request['thinking'], {'type': 'adaptive'})
        self.assertEqual(request['output_config'], {'effort': 'xhigh'})
        self.assertEqual(request['cache_control'], {'type': 'ephemeral'})
        self.assertEqual(request['tool_choice'], {'type': 'auto', 'disable_parallel_tool_use': True})
        self.assertEqual([t['name'] for t in request['tools']], ['add', 'web_search'])
        self.assertEqual(request['tools'][0]['input_schema']['required'], ['a', 'b'])
        # One-at-a-time tool calls rule out the code-filtered search variant.
        self.assertEqual(request['tools'][1]['type'], 'web_search_20250305')
        parallel = model.build_request(None, 'hi', build_model_settings('low'), [WebSearchTool()], None)
        self.assertEqual(parallel['tools'][0]['type'], 'web_search_20260209')
        self.assertEqual(parallel['tool_choice'], {'type': 'auto'})
        self.assertEqual(request['fallbacks'], 'default')
        self.assertEqual(request['betas'], [REFUSAL_FALLBACK_BETA])
        # OpenAI's service tier has no Claude meaning and is not sent.
        self.assertNotIn('service_tier', request)

    def test_models_without_fallbacks_send_neither_the_param_nor_the_beta(self):
        request = AnthropicModel('claude-sonnet-5').build_request(
            None, 'hi', build_model_settings('low'), [], None,
        )
        self.assertNotIn('fallbacks', request)
        self.assertNotIn('betas', request)
        self.assertNotIn('tools', request)
        self.assertNotIn('system', request)

    def test_history_translates_into_alternating_messages(self):
        system, messages = to_anthropic_messages([
            {'role': 'system', 'content': 'Extra rules.'},
            {'role': 'user', 'content': 'first'},
            {'role': 'assistant', 'content': 'reply'},
            {'role': 'user', 'content': [{'type': 'input_text', 'text': 'second'}]},
            {'type': 'function_call', 'call_id': 'c1', 'name': 'add', 'arguments': '{"a": 1, "b": 2}'},
            {'type': 'function_call', 'call_id': 'c2', 'name': 'add', 'arguments': '{"a": 3, "b": 4}'},
            {'type': 'function_call_output', 'call_id': 'c1', 'output': '3'},
            {'type': 'function_call_output', 'call_id': 'c2', 'output': '7'},
        ])
        self.assertEqual(system, ['Extra rules.'])
        self.assertEqual([m['role'] for m in messages], ['user', 'assistant', 'user', 'assistant', 'user'])
        self.assertEqual(messages[3]['content'], [
            {'type': 'tool_use', 'id': 'c1', 'name': 'add', 'input': {'a': 1, 'b': 2}},
            {'type': 'tool_use', 'id': 'c2', 'name': 'add', 'input': {'a': 3, 'b': 4}},
        ])
        self.assertEqual(messages[4]['content'], [
            {'type': 'tool_result', 'tool_use_id': 'c1', 'content': '3'},
            {'type': 'tool_result', 'tool_use_id': 'c2', 'content': '7'},
        ])

    def test_a_claude_turn_replays_verbatim_instead_of_its_items(self):
        content = [
            {'type': 'thinking', 'thinking': '', 'signature': 'sig'},
            {'type': 'text', 'text': 'Adding.'},
            {'type': 'tool_use', 'id': 'c1', 'name': 'add', 'input': {'a': 1, 'b': 2}},
        ]
        items = [
            item.model_dump(exclude_none=True)
            for item in to_output_items(content, 'tool_use')
        ]
        self.assertEqual([i['type'] for i in items], ['reasoning', 'message', 'function_call'])
        _, messages = to_anthropic_messages(
            [{'role': 'user', 'content': 'go'}]
            + items
            + [{'type': 'function_call_output', 'call_id': 'c1', 'output': '3'}]
        )
        self.assertEqual(messages[1], {'role': 'assistant', 'content': content})
        self.assertEqual(messages[2]['content'][0]['tool_use_id'], 'c1')


class ClaudeOutputTests(SimpleTestCase):
    def test_a_cited_answer_split_across_blocks_is_one_reply(self):
        items = to_output_items([
            {'type': 'server_tool_use', 'id': 's1', 'name': 'web_search', 'input': {}},
            {'type': 'text', 'text': 'Django 5.2 '},
            {'type': 'text', 'text': 'is the LTS.', 'citations': [{}]},
        ], 'end_turn')
        messages = [i for i in items if i.type == 'message']
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].content[0].text, 'Django 5.2 is the LTS.')

    def test_a_tool_call_truncated_by_the_output_cap_is_not_run(self):
        items = to_output_items([
            {'type': 'tool_use', 'id': 'c1', 'name': 'add', 'input': {'a': 1, 'b': 2}},
            {'type': 'tool_use', 'id': 'c2', 'name': 'add', 'input': {'a': 1}},
        ], 'max_tokens')
        self.assertEqual([i.call_id for i in items if i.type == 'function_call'], ['c1'])

    def test_a_refusal_still_answers_the_user(self):
        items = to_output_items([], 'refusal')
        self.assertEqual(items[-1].content[0].text, REFUSAL_TEXT)


class ClaudeRunnerTests(SimpleTestCase):
    def _agent(self, client):
        return Agent(
            name='t',
            instructions='Use the tool.',
            model=AnthropicModel('claude-sonnet-5', client=client),
            tools=[add],
            model_settings=build_model_settings('medium'),
        )

    def _script(self):
        return _FakeClient(
            _message(
                [
                    {'type': 'thinking', 'thinking': '', 'signature': 'sig-1'},
                    {'type': 'tool_use', 'id': 'toolu_1', 'name': 'add', 'input': {'a': 17, 'b': 25}},
                ],
                stop_reason='tool_use',
                usage={
                    'input_tokens': 100, 'output_tokens': 20,
                    'cache_read_input_tokens': 0, 'cache_creation_input_tokens': 400,
                },
            ),
            _message(
                [{'type': 'text', 'text': 'It is 42.'}],
                usage={
                    'input_tokens': 30, 'output_tokens': 8,
                    'cache_read_input_tokens': 400, 'cache_creation_input_tokens': 0,
                },
            ),
        )

    def _assert_tool_loop(self, client, usage):
        first, second = client.requests
        self.assertEqual(first['output_config'], {'effort': 'medium'})
        # The second request replays the first turn — thinking block and
        # all — and answers its tool call.
        self.assertEqual(second['messages'][1], {'role': 'assistant', 'content': [
            {'type': 'thinking', 'thinking': '', 'signature': 'sig-1'},
            {'type': 'tool_use', 'id': 'toolu_1', 'name': 'add', 'input': {'a': 17, 'b': 25}},
        ]})
        self.assertEqual(second['messages'][2], {'role': 'user', 'content': [
            {'type': 'tool_result', 'tool_use_id': 'toolu_1', 'content': '42'},
        ]})
        # Every token read is metered, cached or not.
        self.assertEqual(usage.requests, 2)
        self.assertEqual(usage.input_tokens, 100 + 400 + 30 + 400)
        self.assertEqual(usage.output_tokens, 28)
        self.assertEqual(usage.input_tokens_details.cached_tokens, 400)

    def test_a_tool_loop_runs_to_a_final_answer(self):
        client = self._script()
        result = async_to_sync(Runner.run)(self._agent(client), 'What is 17+25?')
        self.assertEqual(result.final_output, 'It is 42.')
        self._assert_tool_loop(client, result.context_wrapper.usage)

    def test_a_streamed_run_relays_text_and_each_tool_call_once(self):
        client = self._script()

        async def run():
            result = Runner.run_streamed(self._agent(client), 'What is 17+25?')
            deltas, tool_calls = [], []
            async for event in result.stream_events():
                if event.type == 'raw_response_event' and event.data.type == 'response.output_text.delta':
                    deltas.append(event.data.delta)
                elif event.type == 'run_item_stream_event' and event.item.type == 'tool_call_item':
                    tool_calls.append(event.item.raw_item.name)
            return result, deltas, tool_calls

        result, deltas, tool_calls = async_to_sync(run)()
        self.assertEqual(deltas, ['It is 42.'])
        self.assertEqual(tool_calls, ['add'])
        self.assertEqual(result.final_output, 'It is 42.')
        self._assert_tool_loop(client, result.context_wrapper.usage)

    def test_a_paused_server_tool_turn_is_resumed(self):
        client = _FakeClient(
            _message([{'type': 'server_tool_use', 'id': 's1', 'name': 'web_search', 'input': {'query': 'x'}}],
                     stop_reason='pause_turn'),
            _message([{'type': 'text', 'text': 'Found it.'}]),
        )
        result = async_to_sync(Runner.run)(self._agent(client), 'Look it up.')
        self.assertEqual(result.final_output, 'Found it.')
        self.assertEqual(client.requests[1]['messages'][-1]['role'], 'assistant')
        self.assertEqual(client.requests[1]['messages'][-1]['content'][0]['type'], 'server_tool_use')
