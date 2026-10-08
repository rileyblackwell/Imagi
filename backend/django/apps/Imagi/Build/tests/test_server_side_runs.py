"""
Threads run on the server: the scheduler starts staged work whether or not a
browser is open, every run logs its events, and any tab watches (or resumes
watching) a run from that log.
"""

import asyncio
import json
from unittest.mock import patch

from asgiref.sync import async_to_sync
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.authtoken.models import Token

from apps.Imagi.Build.models import AgentConversation, AgentRunEvent
from apps.Imagi.Build.services import detached_runs, thread_scheduler
from apps.Imagi.Build.services.detached_runs import watch_conversation
from apps.Imagi.Build.services.thread_scheduler import (
    _claim_waiting_threads,
    start_waiting_threads,
)


def _decode(frame):
    return json.loads(frame[len('data: '):]) if frame.startswith('data: ') else None


class _ThreadsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='server', password='pw123456')
        self.lead = AgentConversation.objects.create(
            user=self.user, model_name='claude-opus-5-5', project_id=1, kind='lead',
        )

    def _task(self, brief='Build the pricing page', **kwargs):
        fields = dict(
            user=self.user, model_name='claude-opus-5-5', project_id=1, kind='task',
            parent=self.lead, review_status='active', queued_prompt=brief,
        )
        fields.update(kwargs)
        return AgentConversation.objects.create(**fields)


@patch('apps.Imagi.Build.services.usage_limits.check_usage_allowed', return_value=(True, None))
class SchedulerClaimTests(_ThreadsTestCase):
    def test_claims_staged_threads_once(self, _allowed):
        first, second = self._task(), self._task('Build the about page')

        claimed = _claim_waiting_threads(self.user)['claimed']

        self.assertEqual([c['conversation_id'] for c in claimed], [first.id, second.id])
        self.assertEqual(claimed[0]['brief'], 'Build the pricing page')
        first.refresh_from_db()
        self.assertIsNotNone(first.run_started_at)
        # Claimed means running: a second call (another process) gets nothing.
        self.assertEqual(_claim_waiting_threads(self.user)['claimed'], [])

    def test_respects_the_parallel_ceiling(self, _allowed):
        for _ in range(thread_scheduler.MAX_CONCURRENT_TASK_RUNS):
            self._task(queued_prompt='', run_started_at=timezone.now())
        waiting = self._task()

        self.assertEqual(_claim_waiting_threads(self.user)['claimed'], [])
        waiting.refresh_from_db()
        self.assertIsNone(waiting.run_started_at)

    def test_leaves_running_failed_and_discarded_threads_alone(self, _allowed):
        self._task(run_started_at=timezone.now())  # already being run
        self._task(review_status='failed')  # the user's to retry
        self._task(review_status='dismissed')
        self._task(archived_at=timezone.now())

        self.assertEqual(_claim_waiting_threads(self.user)['claimed'], [])

    def test_waits_when_the_usage_allowance_is_spent(self, allowed):
        allowed.return_value = (False, {'error': 'usage_limit_exceeded'})
        task = self._task()

        outcome = _claim_waiting_threads(self.user)

        self.assertEqual(outcome, {'claimed': [], 'blocked': 'usage'})
        task.refresh_from_db()
        self.assertEqual(task.queued_prompt, 'Build the pricing page')


async def _fake_process_stream(self, user_input, user, conversation_id=None, **kwargs):
    yield {'type': 'start', 'conversation_id': conversation_id}
    yield {'type': 'delta', 'text': f'On it: {user_input}'}
    yield {'type': 'done', 'success': True, 'response': 'Done.', 'conversation_id': conversation_id}


@patch('apps.Imagi.Build.services.usage_limits.check_usage_allowed', return_value=(True, None))
class ServerStartedRunTests(_ThreadsTestCase):
    def _start_and_finish(self):
        async def scenario():
            outcome = await start_waiting_threads(self.user)
            # Let the runs it started finish, and anything they start after.
            while detached_runs._running:
                await asyncio.gather(*list(detached_runs._running))
            return outcome

        with patch(
            'apps.Imagi.Build.services.base_agent.ImagiAgentService.process_stream',
            _fake_process_stream,
        ):
            return async_to_sync(scenario)()

    def test_a_staged_thread_runs_with_nobody_watching_and_logs_its_events(self, _allowed):
        task = self._task()
        AgentRunEvent.objects.create(
            conversation=task, seq_end=1, events=[{'type': 'done', 'seq': 1}]
        )

        outcome = self._start_and_finish()

        self.assertEqual(outcome['started'], 1)
        events = [
            event for row in AgentRunEvent.objects.filter(conversation=task)
            for event in row.events
        ]
        # The previous run's events were cleared; this run's are numbered.
        self.assertEqual([e['type'] for e in events], ['start', 'delta', 'done'])
        self.assertEqual([e['seq'] for e in events], [1, 2, 3])
        self.assertEqual(events[1]['text'], 'On it: Build the pricing page')

    def test_a_thread_that_never_starts_gives_its_claim_back(self, _allowed):
        task = self._task()

        async def broken(self, **kwargs):
            yield {'type': 'error', 'error': 'no worktree'}

        async def scenario():
            await start_waiting_threads(self.user)
            while detached_runs._running:
                await asyncio.gather(*list(detached_runs._running))

        with patch(
            'apps.Imagi.Build.services.base_agent.ImagiAgentService.process_stream', broken,
        ):
            async_to_sync(scenario)()

        task.refresh_from_db()
        self.assertIsNone(task.run_started_at)
        self.assertEqual(task.review_status, 'failed')
        self.assertIn('could not start: no worktree', task.check_ins.get().body)


class WatchTests(_ThreadsTestCase):
    def setUp(self):
        super().setUp()
        self.task = self._task(queued_prompt='')
        self._patches = [
            patch.object(detached_runs, 'WATCH_POLL_INTERVAL', 0.01),
            patch.object(detached_runs, 'WATCH_ENDED_GRACE', 0.05),
        ]
        for p in self._patches:
            p.start()

    def tearDown(self):
        for p in self._patches:
            p.stop()

    def _log(self, *events):
        AgentRunEvent.objects.create(
            conversation=self.task, seq_end=events[-1]['seq'], events=list(events)
        )

    def _watch(self, after=None):
        async def collect():
            return [
                frame async for frame in watch_conversation(
                    self.task.id, self.user, lambda e: f"data: {json.dumps(e)}",
                    after=after, keepalive=60,
                )
            ]
        return [_decode(f) for f in async_to_sync(collect)()]

    def test_replays_the_run_up_to_its_end(self):
        self._log({'type': 'start', 'seq': 1}, {'type': 'delta', 'text': 'a', 'seq': 2})
        self._log({'type': 'done', 'seq': 3})

        self.assertEqual([e['seq'] for e in self._watch()], [1, 2, 3])

    def test_resumes_after_the_last_event_a_tab_saw(self):
        self._log({'type': 'start', 'seq': 1}, {'type': 'delta', 'text': 'a', 'seq': 2})
        self._log({'type': 'delta', 'text': 'b', 'seq': 3}, {'type': 'done', 'seq': 4})

        self.assertEqual([e['seq'] for e in self._watch(after=2)], [3, 4])

    def test_reports_a_run_that_ended_without_a_final_event(self):
        self._log({'type': 'start', 'seq': 1})

        events = self._watch()

        self.assertEqual(events[-1]['type'], 'error')
        self.assertEqual(events[-1]['code'], 'run_ended')

    def test_waits_for_the_next_run_when_work_is_staged(self):
        # The previous run's events are still logged; staged work means a new
        # run is coming, and the watcher must not replay the old one.
        self._watch_for_next_run(claimed=False)

    def test_waits_for_a_run_claimed_but_not_yet_logging(self):
        # A message was just sent: the scheduler claimed the thread, but its
        # run has not cleared the previous run's log yet.
        self._watch_for_next_run(claimed=True)

    def test_follows_the_run_in_progress_when_more_work_waits_behind_it(self):
        self._log({'type': 'start', 'seq': 1}, {'type': 'delta', 'text': 'a', 'seq': 2})
        AgentConversation.objects.filter(id=self.task.id).update(
            queued_prompt='Follow-up', run_started_at=timezone.now(),
        )

        async def run_finishes():
            await asyncio.sleep(0.05)
            from asgiref.sync import sync_to_async
            await sync_to_async(AgentRunEvent.objects.create)(
                conversation=self.task, seq_end=3, events=[{'type': 'done', 'seq': 3}]
            )

        async def collect():
            finishing = asyncio.create_task(run_finishes())
            frames = [
                frame async for frame in watch_conversation(
                    self.task.id, self.user, lambda e: f"data: {json.dumps(e)}",
                    keepalive=60,
                )
            ]
            await finishing
            return frames

        events = [_decode(f) for f in async_to_sync(collect)()]

        self.assertEqual([e['seq'] for e in events], [1, 2, 3])

    def _watch_for_next_run(self, claimed):
        self._log({'type': 'start', 'seq': 1}, {'type': 'done', 'seq': 2})
        AgentConversation.objects.filter(id=self.task.id).update(
            queued_prompt='Next job', run_started_at=timezone.now() if claimed else None,
        )

        async def new_run_arrives():
            await asyncio.sleep(0.05)
            from asgiref.sync import sync_to_async

            def write():
                AgentRunEvent.objects.filter(conversation=self.task).delete()
                AgentConversation.objects.filter(id=self.task.id).update(queued_prompt='')
                AgentRunEvent.objects.create(conversation=self.task, seq_end=2, events=[
                    {'type': 'start', 'seq': 1, 'new': True}, {'type': 'done', 'seq': 2},
                ])
            await sync_to_async(write)()

        async def collect():
            arrival = asyncio.create_task(new_run_arrives())
            frames = [
                frame async for frame in watch_conversation(
                    self.task.id, self.user, lambda e: f"data: {json.dumps(e)}",
                    keepalive=60,
                )
            ]
            await arrival
            return frames

        with patch(
            'apps.Imagi.Build.services.thread_scheduler.start_waiting_threads',
            return_value={'started': 0, 'blocked': None},
        ):
            events = [_decode(f) for f in async_to_sync(collect)()]

        self.assertTrue(events[0].get('new'))
        self.assertEqual([e['type'] for e in events], ['start', 'done'])


class SendEndpointTests(_ThreadsTestCase):
    def setUp(self):
        super().setUp()
        self.token = Token.objects.create(user=self.user)

    def _send(self, conversation, message):
        return self.client.post(
            reverse('conversation_send', args=[conversation.id]),
            data=json.dumps({'message': message}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.token.key}',
        )

    @patch('apps.Imagi.Build.api.views.start_waiting_threads')
    def test_stages_the_message_and_starts_the_thread(self, start):
        start.return_value = {'started': 1, 'blocked': None}
        task = self._task(queued_prompt='', review_status='failed')

        resp = self._send(task, 'Make the button blue')

        self.assertEqual(resp.status_code, 202)
        task.refresh_from_db()
        self.assertEqual(task.queued_prompt, 'Make the button blue')
        self.assertEqual(task.review_status, 'active')
        start.assert_called_once()

    @patch('apps.Imagi.Build.api.views.start_waiting_threads')
    def test_a_message_for_a_busy_thread_joins_what_is_waiting(self, start):
        start.return_value = {'started': 0, 'blocked': None}
        task = self._task(queued_prompt='First', run_started_at=timezone.now())

        self._send(task, 'Second')

        task.refresh_from_db()
        self.assertEqual(task.queued_prompt, 'First\n\nSecond')

    @patch('apps.Imagi.Build.api.views.start_waiting_threads')
    def test_refuses_the_coordinator_and_discarded_threads(self, start):
        self.assertEqual(self._send(self.lead, 'hi').status_code, 400)
        self.assertEqual(
            self._send(self._task(review_status='dismissed'), 'hi').status_code, 400
        )
        start.assert_not_called()

    @patch('apps.Imagi.Build.api.views.start_waiting_threads')
    def test_a_resent_message_is_not_staged_twice(self, start):
        start.return_value = {'started': 0, 'blocked': None}
        task = self._task(queued_prompt='First\n\nSecond', run_started_at=timezone.now())

        self._send(task, 'Second')

        task.refresh_from_db()
        self.assertEqual(task.queued_prompt, 'First\n\nSecond')
