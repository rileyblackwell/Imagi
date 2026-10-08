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

        self.assertEqual(decision['to'], 'coordinator')
        self.assertEqual(decision['conversation_id'], self.lead.id)
        self.assertIn('[App error]', decision['prompt'])
        self.assertIn('TypeError: x is undefined', decision['prompt'])

    def test_the_same_error_is_routed_once(self):
        self._route()
        again = self._route()
        self.assertTrue(again['already'])
        self.assertEqual(again['to'], 'coordinator')
        self.assertNotIn('prompt', again)

    def test_a_busy_coordinator_is_not_interrupted(self):
        with patch(
            'apps.Imagi.Build.api.views._project_has_running_conversation',
            return_value=True,
        ):
            self.assertIsNone(self._route())
        # Not marked as routed, so a later poll still sends it.
        self.assertEqual(self._route()['to'], 'coordinator')

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
