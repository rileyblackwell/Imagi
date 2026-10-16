"""
The first build's backend thread (ProjectManager.services.backend_build_service):
built beside the pages, then connected to them once they are in.
"""

from unittest.mock import patch

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TransactionTestCase

from apps.Imagi.ProjectManager.services import backend_build_service
from apps.Imagi.ProjectManager.services.initial_build_service import PAGE_BRIEFS


class BackendBuildTests(TransactionTestCase):
    def setUp(self):
        from apps.Imagi.Build.models import AgentConversation
        from apps.Imagi.ProjectManager.models import Project

        self.user = User.objects.create_user(username='baker', password='testpass123')
        self.project = Project.objects.create(
            user=self.user, name='Crumb & Co',
            description='A neighbourhood bakery taking pickup orders.',
            app_details='Customers order pastries for pickup and pay in store.',
        )
        self.lead = AgentConversation.objects.create(
            user=self.user, project_id=self.project.pk, kind='lead',
            model_name='claude-opus-5-5', title='Main thread', mode='agent',
        )

    def _queue(self):
        with patch.object(backend_build_service, '_run_now') as run_now, \
                patch('apps.Imagi.Build.services.api_keys.read_api_key', return_value='sk-test'):
            task = backend_build_service.queue_backend_build(
                self.project.pk, self.user.pk, list(PAGE_BRIEFS),
            )
        return task, run_now

    def test_the_brief_carries_the_app_and_the_pages_being_built(self):
        brief = backend_build_service.build_backend_brief(
            'Crumb & Co', 'A bakery.', 'Pickup orders.', PAGE_BRIEFS,
        )
        self.assertIn('Crumb & Co', brief)
        self.assertIn('Pickup orders.', brief)
        for page in PAGE_BRIEFS:
            self.assertIn(page.route, brief)
        self.assertIn('/api/v1/', brief)
        self.assertIn('check_backend', brief)
        self.assertIn("Don't change the pages", brief)

    def test_starts_at_once_on_the_first_builds_model_tier_and_effort(self):
        from apps.Imagi.Build.models import AgentConversation

        task, run_now = self._queue()

        thread = AgentConversation.objects.get(pk=task.thread_id)
        builder = settings.IMAGI_BUILDER
        self.assertEqual(thread.kind, 'task')
        self.assertEqual(thread.parent_id, self.lead.id)
        self.assertEqual(thread.model_name, builder['INITIAL_BUILD_MODEL'])
        self.assertEqual(thread.service_tier, builder['INITIAL_BUILD_SERVICE_TIER'])
        self.assertEqual(thread.reasoning_effort, builder['INITIAL_BUILD_REASONING_EFFORT'])
        # Claimed for its own run, so the page threads filling the user's
        # slots don't hold it back.
        self.assertIsNotNone(thread.run_started_at)
        self.assertIn('Crumb & Co', thread.queued_prompt)
        run_now.assert_called_once()
        self.assertEqual(run_now.call_args.args[1].pk, thread.pk)

        self.assertEqual(task.status, 'queued')
        self.assertEqual(task.coordinator_id, self.lead.id)
        # The main thread shows it with a card, like any other dispatch.
        message = self.lead.messages.get()
        self.assertEqual(message.metadata['dispatched_tasks'][0]['conversation_id'], thread.id)

    def test_no_main_thread_means_no_backend_thread(self):
        from apps.Imagi.Build.models import AgentConversation

        self.lead.delete()
        task, run_now = self._queue()
        self.assertIsNone(task)
        run_now.assert_not_called()
        self.assertFalse(AgentConversation.objects.filter(kind='task').exists())

    def test_connecting_the_pages_waits_for_the_backend_to_land(self):
        from apps.Imagi.Build.services.scheduling import release_waiting_tasks, task_run_ended

        backend, _ = self._queue()
        # Its run has taken its brief and is going.
        backend.status = 'running'
        backend.save(update_fields=['status'])
        backend.thread.queued_prompt = ''
        backend.thread.save(update_fields=['queued_prompt'])

        with patch('apps.Imagi.ProjectManager.services.auth_restyle_service._start_threads') as start:
            wiring = backend_build_service.queue_page_wiring(
                self.project.pk, self.user.pk, backend, list(PAGE_BRIEFS[:2]),
            )
        self.assertEqual(wiring.status, 'waiting')
        self.assertEqual(wiring.thread_id, backend.thread_id)
        self.assertEqual(list(wiring.depends_on.all()), [backend])
        start.assert_not_called()

        # The backend lands: the next scheduler pass hands the wiring to it.
        task_run_ended(backend.thread, 'done', 'Built orders.', ['backend/django/apps/orders/models.py'])
        self.assertEqual(release_waiting_tasks(self.user), 1)
        backend.thread.refresh_from_db()
        self.assertIn('The pages are in', backend.thread.queued_prompt)
        self.assertIn(PAGE_BRIEFS[1].view_path, backend.thread.queued_prompt)
        self.assertNotIn(PAGE_BRIEFS[2].view_path, backend.thread.queued_prompt)

    def test_a_backend_already_in_gets_its_pages_connected_right_away(self):
        backend, _ = self._queue()
        backend.status = 'done'
        backend.result = {'outcome': 'done', 'files': ['backend/django/apps/orders/models.py']}
        backend.save(update_fields=['status', 'result'])

        with patch('apps.Imagi.ProjectManager.services.auth_restyle_service._start_threads') as start:
            wiring = backend_build_service.queue_page_wiring(
                self.project.pk, self.user.pk, backend, list(PAGE_BRIEFS),
            )
        self.assertEqual(wiring.status, 'queued')
        start.assert_called_once()
        backend.thread.refresh_from_db()
        self.assertIn('The pages are in', backend.thread.queued_prompt)

    def test_nothing_to_connect_means_no_second_job(self):
        backend, _ = self._queue()
        with patch('apps.Imagi.ProjectManager.services.auth_restyle_service._start_threads') as start:
            # No page landed.
            self.assertIsNone(backend_build_service.queue_page_wiring(
                self.project.pk, self.user.pk, backend, [],
            ))
            # The backend thread found nothing to build.
            backend.status = 'done'
            backend.result = {'outcome': 'done', 'files': []}
            backend.save(update_fields=['status', 'result'])
            self.assertIsNone(backend_build_service.queue_page_wiring(
                self.project.pk, self.user.pk, backend, list(PAGE_BRIEFS),
            ))
            # Its work failed.
            backend.status = 'failed'
            backend.save(update_fields=['status'])
            self.assertIsNone(backend_build_service.queue_page_wiring(
                self.project.pk, self.user.pk, backend, list(PAGE_BRIEFS),
            ))
        start.assert_not_called()

    def test_never_raises_into_the_build(self):
        with patch.object(backend_build_service, '_queue_backend_build', side_effect=RuntimeError):
            self.assertIsNone(backend_build_service.queue_backend_build(
                self.project.pk, self.user.pk, list(PAGE_BRIEFS),
            ))
        with patch.object(backend_build_service, '_queue_page_wiring', side_effect=RuntimeError):
            self.assertIsNone(backend_build_service.queue_page_wiring(
                self.project.pk, self.user.pk, object(), list(PAGE_BRIEFS),
            ))
