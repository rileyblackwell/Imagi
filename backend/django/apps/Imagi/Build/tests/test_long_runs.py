"""
Long-running agent runs: they outlive the connection that started them,
stop on the user's Stop, stop at their cost ceiling, and stop with a clear
message when a provider account has no credit left.
"""

import asyncio
from types import SimpleNamespace
from unittest.mock import PropertyMock, patch

import anthropic
import httpx
import openai
from asgiref.sync import async_to_sync, sync_to_async
from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.authtoken.models import Token

from apps.Imagi.Build.models import AgentCheckIn, AgentConversation
from apps.Imagi.Build.services import detached_runs
from apps.Imagi.Build.services.base_agent import (
    AgentContext,
    ImagiAgentService,
    RunBudgetExceeded,
    provider_out_of_credit,
)
from apps.Imagi.Build.services.detached_runs import KEEPALIVE_FRAME, start_detached_run


def _encode(event):
    return f"data: {event['type']}\n\n"


class DetachedRunTests(SimpleTestCase):
    """The run belongs to its own task; the response only listens."""

    def test_the_run_finishes_after_its_listener_leaves(self):
        finished = []

        async def events():
            yield {'type': 'delta', 'text': 'a'}
            await asyncio.sleep(0.05)
            yield {'type': 'delta', 'text': 'b'}
            finished.append(True)

        async def scenario():
            run = start_detached_run(events)
            frames = run.frames(_encode)
            first = await frames.__anext__()
            # The client goes away after one frame.
            await frames.aclose()
            await asyncio.wait_for(run.task, 1)
            return first

        first = async_to_sync(scenario)()

        self.assertEqual(first, 'data: delta\n\n')
        self.assertEqual(finished, [True])

    def test_a_quiet_run_sends_keepalives(self):
        async def events():
            await asyncio.sleep(0.05)
            yield {'type': 'done'}

        async def scenario():
            run = start_detached_run(events)
            return [frame async for frame in run.frames(_encode, keepalive=0.01)]

        frames = async_to_sync(scenario)()

        self.assertIn(KEEPALIVE_FRAME, frames)
        self.assertEqual(frames[-1], 'data: done\n\n')


class _SlowStreamedRun:
    """A model run that keeps working until something stops it."""

    final_output = 'All done.'
    new_items = []

    async def stream_events(self):
        yield SimpleNamespace(
            type='raw_response_event',
            data=SimpleNamespace(type='response.output_text.delta', delta='Working'),
        )
        await asyncio.sleep(30)


class _RaisingStreamedRun:
    final_output = None
    new_items = []

    def __init__(self, error):
        self.error = error

    async def stream_events(self):
        yield SimpleNamespace(
            type='raw_response_event',
            data=SimpleNamespace(type='response.output_text.delta', delta='Started'),
        )
        raise self.error


class _TaskRunTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='longrun', password='pw123456')
        self.service = ImagiAgentService()
        self.lead = AgentConversation.objects.create(
            user=self.user, model_name='claude-opus-5-5', project_id=1, kind='lead',
        )
        self.task = AgentConversation.objects.create(
            user=self.user, model_name='claude-opus-5-5', project_id=1, kind='task',
            parent=self.lead, review_status='active', run_started_at=timezone.now(),
        )

    def _patched(self, fake_run):
        context = AgentContext(user_id=self.user.id, project_id=1, conversation_kind='task')
        prepare = patch.object(
            self.service, '_prepare_run',
            return_value=(self.task, context, [{'role': 'user', 'content': 'go'}]),
        )
        agent = patch.object(type(self.service), 'agent', new_callable=PropertyMock)
        runner = patch('apps.Imagi.Build.services.base_agent.Runner')
        return prepare, agent, runner, fake_run

    def _collect(self, fake_run):
        prepare, agent, runner, fake_run = self._patched(fake_run)

        async def collect():
            return [
                event async for event in self.service.process_stream(
                    user_input='go', user=self.user, project_id=1,
                    conversation_id=self.task.id,
                )
            ]

        with prepare, agent as mock_agent, runner as mock_runner:
            mock_agent.return_value = SimpleNamespace()
            mock_runner.run_streamed.return_value = fake_run
            return async_to_sync(collect)()


class StopTests(_TaskRunTestCase):
    """Stop reaches a run that no connection is holding."""

    def test_stop_cancels_a_detached_run_and_keeps_the_stopped_note(self):
        client_reason = 'This thread was stopped before it finished.'
        prepare, agent, runner, fake_run = self._patched(_SlowStreamedRun())

        async def scenario():
            run = start_detached_run(lambda: self.service.process_stream(
                user_input='go', user=self.user, project_id=1,
                conversation_id=self.task.id,
            ))
            frames = run.frames(lambda e: e)
            seen = [await frames.__anext__(), await frames.__anext__()]
            # Nobody is listening any more; the run is still going.
            await frames.aclose()
            self.assertFalse(run.task.done())
            # The user presses Stop (what the cancel endpoint writes).
            await sync_to_async(self.service._park_failed_task)(self.task, client_reason)
            await sync_to_async(
                AgentConversation.objects.filter(id=self.task.id).update
            )(run_started_at=None, cancel_requested_at=timezone.now())
            await asyncio.wait_for(run.task, 2)
            return [e['type'] for e in seen]

        with prepare, agent as mock_agent, runner as mock_runner, \
                patch.object(detached_runs, 'WATCH_INTERVAL', 0.01):
            mock_agent.return_value = SimpleNamespace()
            mock_runner.run_streamed.return_value = fake_run
            seen = async_to_sync(scenario)()

        self.assertEqual(seen, ['start', 'delta'])
        self.task.refresh_from_db()
        self.assertEqual(self.task.review_status, 'failed')
        self.assertIsNone(self.task.run_started_at)
        # The Stop's note stands; the run's cleanup did not relabel it "cut off".
        check_in = AgentCheckIn.objects.get(conversation=self.task, status='pending')
        self.assertEqual(check_in.body, client_reason)
        # What it said before the Stop is kept.
        self.assertEqual(
            [m.content for m in self.task.messages.filter(role='assistant')], ['Working'],
        )

    def test_cancel_endpoint_flags_the_run(self):
        token = Token.objects.create(user=self.user)
        resp = self.client.post(
            reverse('conversation_cancel', args=[self.task.id]),
            HTTP_AUTHORIZATION=f'Token {token.key}',
        )
        self.assertEqual(resp.status_code, 200)
        self.task.refresh_from_db()
        self.assertIsNotNone(self.task.cancel_requested_at)
        self.assertIsNone(self.task.run_started_at)


class CostCeilingTests(_TaskRunTestCase):
    def test_a_run_at_its_ceiling_stops_and_asks_to_keep_going(self):
        events = self._collect(_RaisingStreamedRun(RunBudgetExceeded(10.2, 10.0)))

        self.assertEqual(events[-1]['type'], 'error')
        self.assertEqual(events[-1]['code'], 'run_limit')
        self.assertIn('$10.00', events[-1]['error'])
        self.task.refresh_from_db()
        # Waiting on the user, not failed: "keep going" resumes it in place.
        self.assertEqual(self.task.review_status, 'input')
        self.assertEqual(
            AgentCheckIn.objects.get(conversation=self.task, status='pending').kind,
            'question',
        )

    def test_continuation_rounds_share_one_ceiling(self):
        from agents import MaxTurnsExceeded

        budgets = []
        original = self.service._stream_once

        def spy(**kwargs):
            budgets.append(kwargs['cost_budget_usd'])

            async def round_spending_four_dollars():
                async for event in original(**kwargs):
                    yield event
                kwargs['cap_state']['cost_usd'] = 4.0

            return round_spending_four_dollars()

        with patch.object(self.service, '_stream_once', side_effect=spy), \
                patch.object(self.service, '_continuation_allowed', return_value=True), \
                patch('apps.Imagi.Build.services.base_agent.RUN_COST_CEILING_USD', 10.0):
            self._collect(_RaisingStreamedRun(MaxTurnsExceeded('cap')))

        # Each round gets what the earlier ones left, never a fresh $10.
        self.assertEqual(budgets[:3], [10.0, 6.0, 2.0])


def _anthropic_error(cls, status, message, body):
    request = httpx.Request('POST', 'https://api.anthropic.com/v1/messages')
    return cls(message, response=httpx.Response(status, request=request), body=body)


def _openai_error(cls, status, message, body):
    request = httpx.Request('POST', 'https://api.openai.com/v1/responses')
    return cls(message, response=httpx.Response(status, request=request), body=body)


class OutOfCreditTests(_TaskRunTestCase):
    def test_recognizes_an_empty_anthropic_balance(self):
        error = _anthropic_error(
            anthropic.BadRequestError, 400,
            'Your credit balance is too low to access the Anthropic API.',
            {'type': 'error', 'error': {
                'type': 'invalid_request_error',
                'message': 'Your credit balance is too low to access the Anthropic API.',
            }},
        )
        self.assertEqual(provider_out_of_credit(error), 'Anthropic')

    def test_an_ordinary_rate_limit_is_not_out_of_credit(self):
        error = _openai_error(
            openai.RateLimitError, 429, 'Rate limit reached for requests.',
            {'message': 'Rate limit reached for requests.', 'type': 'requests',
             'code': 'rate_limit_exceeded'},
        )
        self.assertIsNone(provider_out_of_credit(error))
        self.assertIsNone(provider_out_of_credit(RuntimeError('credit balance is too low')))

    def test_the_thread_stops_and_says_why(self):
        error = _anthropic_error(
            anthropic.BadRequestError, 400,
            'Your credit balance is too low to access the Anthropic API.', None,
        )

        events = self._collect(_RaisingStreamedRun(error))

        self.assertEqual(events[-1]['code'], 'out_of_credit')
        self.assertEqual(events[-1]['provider'], 'Anthropic')
        self.task.refresh_from_db()
        self.assertEqual(self.task.review_status, 'failed')
        body = AgentCheckIn.objects.get(conversation=self.task, status='pending').body
        self.assertIn('run out of credit', body)
