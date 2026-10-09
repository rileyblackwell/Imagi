"""
Haiku helpers, thread defaults and saved efforts.

The helpers (web_search, explore_project) run on Haiku whatever model the
agent is on; new threads start on the coordinator's thread defaults (Opus 5.5
on Medium unless the workspace settings say otherwise); and the effort a
conversation runs at is saved on it, so a thread the server starts runs at
the effort the user picked for it.
"""

import json
from types import SimpleNamespace

from asgiref.sync import async_to_sync
from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase
from rest_framework.authtoken.models import Token

from apps.Imagi.Build.models import AgentConversation
from apps.Imagi.Build.services import helper_tools
from apps.Imagi.Build.services.base_agent import (
    AgentContext,
    ImagiAgentService,
    RunBudgetExceeded,
    make_run_bounds_hook,
)
from apps.Imagi.Build.services.coding_agent import create_coding_agent
from apps.Imagi.Build.services.models_service import compute_cost_usd
from apps.Imagi.Build.services.tools import dispatch_task_impl, thread_defaults
from apps.Payments.models import UsageEvent


def _block(text, citations=()):
    return SimpleNamespace(type='text', text=text, citations=list(citations))


def _response(content, stop_reason='end_turn', searches=0, input_tokens=1000, output_tokens=200):
    return SimpleNamespace(
        content=content,
        stop_reason=stop_reason,
        usage=SimpleNamespace(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cache_read_input_tokens=0,
            cache_creation_input_tokens=0,
            server_tool_use=SimpleNamespace(web_search_requests=searches),
        ),
    )


class _FakeMessages:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    async def create(self, **kwargs):
        self.calls.append(kwargs)
        return self.responses.pop(0)


class WebSearchHelperTests(SimpleTestCase):
    """web_search answers on Haiku and prices every search it ran."""

    def _search(self, responses):
        messages = _FakeMessages(responses)
        client = SimpleNamespace(messages=messages)
        result, usage = async_to_sync(helper_tools.run_web_search)('Who sells bagels in Boise?', client)
        return result, usage, messages.calls

    def test_runs_on_haiku_with_claudes_web_search(self):
        _, _, calls = self._search([_response([_block('Two shops.')])])
        self.assertEqual(calls[0]['model'], 'claude-haiku-5-5')
        self.assertEqual(calls[0]['tools'][0]['type'], 'web_search_20250305')
        self.assertEqual(calls[0]['output_config'], {'effort': 'low'})

    def test_answer_carries_its_cited_sources_once_each(self):
        cite = SimpleNamespace(url='https://example.com/a', title='A')
        result, _, _ = self._search([_response([
            _block('Shop one', [cite]), _block(' and shop two.', [cite]),
        ])])
        self.assertEqual(result['answer'], 'Shop one and shop two.')
        self.assertEqual(result['sources'], [{'title': 'A', 'url': 'https://example.com/a'}])

    def test_a_paused_turn_is_continued(self):
        _, usage, calls = self._search([
            _response([_block('Half')], stop_reason='pause_turn', searches=2),
            _response([_block(' done.')], searches=1),
        ])
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[1]['messages'][-1]['role'], 'assistant')
        self.assertEqual(usage['searches'], 3)

    def test_cost_is_haiku_tokens_plus_the_per_search_fee(self):
        _, usage, _ = self._search([_response([_block('x')], searches=2)])
        tokens = compute_cost_usd('claude-haiku-5-5', 1000, 200)
        self.assertAlmostEqual(usage['cost_usd'], tokens + 2 * helper_tools.WEB_SEARCH_PRICE_PER_SEARCH_USD)


class HelperToolWiringTests(SimpleTestCase):
    """Which roles get the helpers, and what they run on."""

    def test_coordinator_and_threads_get_both_helpers(self):
        for kind in ('lead', 'task', 'chat'):
            names = {getattr(tool, 'name', '') for tool in create_coding_agent(kind=kind).tools}
            self.assertTrue({'web_search', 'explore_project'} <= names, (kind, names))

    def test_the_agent_no_longer_carries_the_hosted_search_itself(self):
        # Hosted search would put every result page into the agent's own
        # context, billed at its own rate.
        agent = create_coding_agent('claude-fable-5-1', kind='task')
        self.assertNotIn('WebSearchTool', [type(tool).__name__ for tool in agent.tools])

    def test_explorer_is_read_only_on_haiku(self):
        agent = helper_tools.explore_agent()
        self.assertEqual(agent.model.model, 'claude-haiku-5-5')
        names = {tool.name for tool in agent.tools}
        self.assertIn('grep_files', names)
        self.assertFalse({'edit_file', 'update_file', 'create_file', 'delete_file'} & names)

    def test_the_coordinator_runs_at_the_effort_it_was_given(self):
        # It used to be pinned to Low; now it honours its own composer.
        agent = create_coding_agent(reasoning_effort='high', kind='lead')
        self.assertEqual(agent.model_settings.reasoning.effort, 'high')
        agent = create_coding_agent(kind='lead')
        self.assertEqual(agent.model_settings.reasoning.effort, 'medium')

    def test_helper_cost_counts_toward_the_runs_ceiling(self):
        hook = make_run_bounds_hook('claude-opus-5-5', budget_usd=1.0)
        context = SimpleNamespace(
            usage=SimpleNamespace(input_tokens=1000, output_tokens=100),
            context=SimpleNamespace(helper_cost_usd=2.0),
        )
        with self.assertRaises(RunBudgetExceeded):
            async_to_sync(hook.on_llm_end)(context, None, SimpleNamespace(output=[]))


class HelperMeteringTests(TestCase):
    def test_a_helper_call_is_metered_at_haiku_and_added_to_the_run(self):
        user = User.objects.create_user(username='helpermeter', password='pw123456')
        context = AgentContext(user_id=user.id, conversation_id=None)
        async_to_sync(helper_tools._meter)(context, 1000, 200, 0.05)
        self.assertAlmostEqual(context.helper_cost_usd, 0.05)
        event = UsageEvent.objects.get(user=user)
        self.assertEqual(event.model_name, 'claude-haiku-5-5')


class ThreadDefaultsTests(TestCase):
    """New threads start on the coordinator's thread defaults."""

    def setUp(self):
        self.user = User.objects.create_user(username='threaddefaults', password='pw123456')
        self.lead = AgentConversation.objects.create(
            user=self.user, model_name='claude-sonnet-5-5', project_id=None, kind='lead',
        )

    def _dispatch(self):
        ctx = SimpleNamespace(user_id=self.user.id, conversation_id=self.lead.id, dispatched_tasks=[])
        result = dispatch_task_impl(ctx, 'Add a contact page.', goal='A contact page')
        return AgentConversation.objects.get(id=result['dispatched_tasks'][0]['conversation_id'])

    def test_opus_on_medium_by_default_whatever_the_coordinator_runs_on(self):
        thread = self._dispatch()
        self.assertEqual(thread.model_name, 'claude-opus-5-5')
        self.assertEqual(thread.reasoning_effort, 'medium')

    def test_the_workspace_settings_pick_the_thread_model_and_effort(self):
        self.lead.thread_model_name = 'claude-haiku-5-5'
        self.lead.thread_reasoning_effort = 'high'
        self.lead.save()
        thread = self._dispatch()
        self.assertEqual(thread.model_name, 'claude-haiku-5-5')
        self.assertEqual(thread.reasoning_effort, 'high')

    def test_a_retired_or_unknown_setting_falls_back_sensibly(self):
        self.lead.thread_model_name = 'gpt-6-luna'
        self.lead.thread_reasoning_effort = 'minimal'
        self.assertEqual(thread_defaults(self.lead), ('claude-haiku-5-5', 'low'))
        self.lead.thread_model_name = 'nope'
        self.lead.thread_reasoning_effort = 'nope'
        self.assertEqual(thread_defaults(self.lead), ('claude-opus-5-5', 'medium'))


class SavedEffortTests(TestCase):
    """A conversation's effort is saved, and a run that names none uses it."""

    def setUp(self):
        self.user = User.objects.create_user(username='savedeffort', password='pw123456')
        self.thread = AgentConversation.objects.create(
            user=self.user, model_name='claude-opus-5-5', kind='task', reasoning_effort='xhigh',
        )

    def test_a_server_started_run_uses_the_saved_effort(self):
        service = ImagiAgentService()
        service._sync_reasoning_effort(self.thread, None)
        self.assertEqual(service.reasoning_effort, 'xhigh')

    def test_a_requested_effort_is_saved(self):
        service = ImagiAgentService(reasoning_effort='low')
        service._sync_reasoning_effort(self.thread, 'low')
        self.thread.refresh_from_db()
        self.assertEqual(self.thread.reasoning_effort, 'low')

    def test_a_pinned_role_leaves_the_saved_effort_alone(self):
        service = ImagiAgentService(agent_kind='initial_build', reasoning_effort='low')
        service._sync_reasoning_effort(self.thread, 'low')
        self.thread.refresh_from_db()
        self.assertEqual(self.thread.reasoning_effort, 'xhigh')


class ConversationSettingsEndpointTests(TestCase):
    """PATCH saves efforts and thread defaults; the DTO reports them."""

    def setUp(self):
        self.user = User.objects.create_user(username='settingsapi', password='pw123456')
        token = Token.objects.create(user=self.user)
        self.client.defaults['HTTP_AUTHORIZATION'] = f'Token {token.key}'
        self.lead = AgentConversation.objects.create(
            user=self.user, model_name='claude-opus-5-5', kind='lead',
        )
        self.url = f'/api/v1/agents/conversations/{self.lead.id}/'

    def _patch(self, body):
        return self.client.patch(self.url, data=json.dumps(body), content_type='application/json')

    def test_defaults_are_reported_before_anything_is_set(self):
        data = self.client.get(self.url).json()
        self.assertEqual(data['thread_model_name'], 'claude-opus-5-5')
        self.assertEqual(data['thread_reasoning_effort'], 'medium')
        self.assertEqual(data['reasoning_effort'], 'medium')

    def test_thread_defaults_and_effort_are_saved(self):
        response = self._patch({
            'thread_model_name': 'claude-fable-5-1',
            'thread_reasoning_effort': 'high',
            'reasoning_effort': 'minimal',
        })
        self.assertEqual(response.status_code, 200, response.content)
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.thread_model_name, 'claude-fable-5-1')
        self.assertEqual(self.lead.thread_reasoning_effort, 'high')
        self.assertEqual(self.lead.reasoning_effort, 'low')

    def test_unknown_values_are_refused(self):
        self.assertEqual(self._patch({'thread_model_name': 'gpt-2'}).status_code, 400)
        self.assertEqual(self._patch({'reasoning_effort': 'turbo'}).status_code, 400)

