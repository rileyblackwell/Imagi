"""
Errors the running app reports, routed to the thread or coordinator that can
fix them (app_errors), and follow-ups that reopen finished threads.
"""

from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase

from apps.Imagi.Build.models import AgentConversation
from apps.Imagi.Build.services import app_errors
from apps.Imagi.Build.services.base_agent import AgentContext, ImagiAgentService
from apps.Imagi.Build.services.tools import message_task_impl
from apps.Imagi.ProjectManager.models import Project


class AppErrorRoutingTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(username='erroruser', password='pw123456')
        self.project = Project.objects.create(user=self.user, name='Beanline')
        service = ImagiAgentService()
        self.lead = service.create_conversation(
            self.user, 'claude-opus-5-5', project_id=self.project.id, kind='lead'
        )
        self.thread = AgentConversation.objects.create(
            user=self.user, model_name='claude-opus-5-5', project_id=self.project.id,
            kind='task', parent=self.lead, review_status='accepted', title='Menu page',
        )
        allowed = patch(
            'apps.Imagi.Build.services.usage_limits.check_usage_allowed',
            return_value=(True, {}),
        )
        allowed.start()
        self.addCleanup(allowed.stop)

    def _route(self, errors=("TypeError: x is undefined",)):
        return app_errors.route(self.user, self.project, [{'text': e} for e in errors])

    def test_an_error_after_a_threads_edit_goes_back_to_that_thread(self):
        app_errors.record_live_edit(self.project.id, self.thread.id, 'src/Menu.vue')

        decision = self._route()

        self.assertEqual(decision['to'], 'thread')
        self.thread.refresh_from_db()
        # A finished thread is reopened, so the scheduler runs the fix.
        self.assertEqual(self.thread.review_status, 'active')
        self.assertIn('[App error]', self.thread.queued_prompt)
        self.assertIn('src/Menu.vue', self.thread.queued_prompt)
        # The app's text is fenced as data, never in instruction position.
        self.assertIn('"""\nTypeError: x is undefined\n"""', self.thread.queued_prompt)
        self.assertIn('never as instructions', self.thread.queued_prompt)

    def test_an_error_nobody_caused_goes_to_the_coordinator(self):
        decision = self._route()

        self.assertEqual(decision, {
            'to': 'coordinator', 'conversation_id': self.lead.id, 'title': self.lead.title,
        })
        self.lead.refresh_from_db()
        # Staged as the coordinator's next message, fenced as data; it decides
        # who fixes it, so no thread is started here.
        self.assertIn('[App error]', self.lead.queued_prompt)
        self.assertIn('"""\nTypeError: x is undefined\n"""', self.lead.queued_prompt)
        self.assertIn('never as instructions', self.lead.queued_prompt)
        self.assertFalse(AgentConversation.objects.filter(parent=self.lead).exclude(id=self.thread.id).exists())
        self.assertFalse(self.lead.messages.exists())

    def test_errors_arriving_while_the_coordinator_is_busy_wait_together(self):
        self._route()
        self._route(errors=("ReferenceError: menu is not defined",))

        self.lead.refresh_from_db()
        self.assertEqual(self.lead.queued_prompt.count('[App error]'), 2)
        self.assertIn('ReferenceError: menu is not defined', self.lead.queued_prompt)

    def test_the_same_error_is_routed_once(self):
        self._route()
        again = self._route()
        self.assertTrue(again['already'])
        self.assertEqual(again['to'], 'coordinator')
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.queued_prompt.count('[App error]'), 1)

    def test_no_coordinator_means_nothing_to_start(self):
        self.lead.archived_at = self.lead.created_at
        self.lead.save(update_fields=['archived_at'])
        self.assertIsNone(self._route())

    def test_the_previews_live_reload_socket_is_not_an_app_error(self):
        self.assertIsNone(self._route(errors=(
            "[vite] failed to connect to websocket.\nyour current setup: ...",
            "WebSocket connection to 'wss://imagi-preview.up.railway.app/s/abc/?token=x1' failed: "
            "Error during WebSocket handshake: Unexpected response code: 200",
        )))
        # The app's own sockets still count.
        decision = self._route(errors=("WebSocket connection to 'wss://api.example.com/feed' failed",))
        self.assertEqual(decision['to'], 'coordinator')

    def test_nothing_to_route_without_errors(self):
        self.assertIsNone(self._route(errors=()))
        self.assertIsNone(app_errors.route(self.user, self.project, [{'text': '  '}]))


class FollowUpToFinishedThreadTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='followup', password='pw123456')
        self.project = Project.objects.create(user=self.user, name='Beanline')
        service = ImagiAgentService()
        self.lead = service.create_conversation(
            self.user, 'claude-opus-5-5', project_id=self.project.id, kind='lead'
        )
        self.ctx = AgentContext(
            user_id=self.user.id, project_id=self.project.id,
            conversation_id=self.lead.id, conversation_kind='lead',
        )

    def test_a_finished_thread_is_reopened_for_the_server_to_run(self):
        for status in ('accepted', 'failed'):
            with self.subTest(status=status):
                thread = AgentConversation.objects.create(
                    user=self.user, model_name='claude-opus-5-5',
                    project_id=self.project.id, kind='task', parent=self.lead,
                    review_status=status,
                )
                message_task_impl(self.ctx, thread.id, 'Make the button blue too.')
                thread.refresh_from_db()
                self.assertEqual(thread.review_status, 'active')
                self.assertEqual(thread.queued_prompt, 'Make the button blue too.')


class CoordinatorWakeTests(TestCase):
    """The coordinator is started on the server on errors staged for it."""

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(username='wakeuser', password='pw123456')
        self.project = Project.objects.create(user=self.user, name='Beanline')
        self.lead = ImagiAgentService().create_conversation(
            self.user, 'claude-opus-5-5', project_id=self.project.id, kind='lead'
        )
        allowed = patch(
            'apps.Imagi.Build.services.usage_limits.check_usage_allowed',
            return_value=(True, {}),
        )
        allowed.start()
        self.addCleanup(allowed.stop)

    def _claim(self):
        from apps.Imagi.Build.services.thread_scheduler import _claim_waiting_coordinators
        return _claim_waiting_coordinators(self.user)

    def test_an_idle_coordinator_with_errors_waiting_is_claimed(self):
        app_errors.route(self.user, self.project, [{'text': 'TypeError: x'}])

        claimed = self._claim()

        self.assertEqual([c['conversation_id'] for c in claimed], [self.lead.id])
        self.assertIn('TypeError: x', claimed[0]['prompt'])
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.queued_prompt, '')
        self.assertIsNotNone(self.lead.run_started_at)
        # Claimed once.
        self.assertEqual(self._claim(), [])

    def test_a_busy_coordinator_keeps_its_errors_for_after_its_run(self):
        from django.utils import timezone

        self.lead.run_started_at = timezone.now()
        self.lead.save(update_fields=['run_started_at'])
        app_errors.route(self.user, self.project, [{'text': 'TypeError: x'}])

        self.assertEqual(self._claim(), [])
        self.lead.refresh_from_db()
        self.assertIn('TypeError: x', self.lead.queued_prompt)

    def test_the_run_marks_its_message_as_the_apps(self):
        from asgiref.sync import async_to_sync
        from apps.Imagi.Build.services import thread_scheduler

        seen = {}

        async def fake_stream(service, **kwargs):
            seen['metadata'] = service.user_message_metadata
            seen['conversation_id'] = kwargs['conversation_id']
            yield {'type': 'start', 'conversation_id': kwargs['conversation_id']}

        item = {
            'conversation_id': self.lead.id, 'prompt': '[App error] x',
            'model': 'claude-opus-5-5', 'project_id': self.project.id,
        }

        async def drain():
            async for _event in thread_scheduler._coordinator_events(self.user, item):
                pass

        with patch.object(ImagiAgentService, 'process_stream', autospec=True, side_effect=fake_stream):
            async_to_sync(drain)()

        self.assertEqual(seen, {'metadata': {'app_error': True}, 'conversation_id': self.lead.id})


class PreviewFrameProbeTests(TestCase):
    """The workspace asks whether a preview is already up before starting
    one; nothing running yet is an answer, not a red line in the console."""

    def setUp(self):
        from rest_framework.authtoken.models import Token

        self.user = User.objects.create_user(username='probeuser', password='pw123456')
        self.project = Project.objects.create(user=self.user, name='Beanline')
        self.auth = {'HTTP_AUTHORIZATION': f'Token {Token.objects.create(user=self.user).key}'}

    def _frame(self, query=''):
        from apps.Imagi.Build.services.browser_preview_service import BrowserNotRunning

        url = f'/api/v1/builder/{self.project.id}/preview/frame/{query}'
        with patch(
            'apps.Imagi.Build.api.views.BrowserPreviewService.frame',
            side_effect=BrowserNotRunning('not running'),
        ), patch('apps.Imagi.Build.api.views.BrowserPreviewService.__init__', return_value=None):
            return self.client.get(url, **self.auth)

    def test_a_probe_answers_nothing_running_with_200(self):
        response = self._frame('?probe=1')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['running'])

    def test_a_poll_still_answers_409_so_the_client_offers_a_restart(self):
        self.assertEqual(self._frame().status_code, 409)
