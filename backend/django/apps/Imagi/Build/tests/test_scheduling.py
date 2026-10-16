"""
The coordinator's schedule, forked threads, shared project memory, and
threads reconciling their own merge conflicts.

One test class per scheduling scenario from the design: a job that needs
nothing runs in parallel on a new thread; one that needs a thread's result
runs after it on that same thread; one that needs only a thread's context is
a fork that runs alongside it; and one that needs several results (fan-in)
waits on the schedule until all of them have landed.
"""

import os
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.authtoken.models import Token

from apps.Imagi.Build.api.views import _park_stranded_tasks
from apps.Imagi.Build.models import (
    AgentConversation,
    AgentMessage,
    ProjectMemoryChange,
    ThreadTask,
)
from apps.Imagi.Build.services import project_memory, scheduling
from apps.Imagi.Build.services.base_agent import AgentContext, ImagiAgentService
from apps.Imagi.Build.services.thread_scheduler import _claim_waiting_threads
from apps.Imagi.Build.services.tools import (
    dispatch_task_impl,
    lead_task_roster,
    message_task_impl,
)
from apps.Imagi.Build.services.version_control_service import VersionControlService
from apps.Imagi.Build.tests.test_task_worktrees import GitRepoTestMixin, _git
from apps.Imagi.ProjectManager.models import Project


class _ScheduleTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='scheduler', password='pw123456')
        self.project = Project.objects.create(
            user=self.user, name='P', project_path='/tmp/nonexistent', is_active=True
        )
        self.service = ImagiAgentService()
        self.lead = self.service.create_conversation(
            self.user, 'claude-opus-5-5', project_id=self.project.id, kind='lead'
        )

    def _ctx(self, conversation=None):
        conversation = conversation or self.lead
        return AgentContext(
            user_id=self.user.id,
            project_id=self.project.id,
            conversation_id=conversation.id,
            conversation_kind=conversation.kind,
        )

    def _dispatch(self, brief, **kwargs):
        result = dispatch_task_impl(self._ctx(), brief, **kwargs)
        self.assertTrue(result['success'], result)
        return result, AgentConversation.objects.get(
            id=result['dispatched_tasks'][0]['conversation_id']
        )

    def _run(self, thread, outcome='done', summary='Done.'):
        """A thread's run delivering what is staged on it, then ending."""
        thread.refresh_from_db()
        scheduling.task_run_started(thread, thread.queued_prompt)
        thread.queued_prompt = ''
        thread.save(update_fields=['queued_prompt'])
        scheduling.task_run_ended(thread, outcome, summary, files=['src/App.vue'])
        if outcome == 'done':
            thread.review_status = 'accepted'
            thread.save(update_fields=['review_status'])

    def _task(self, thread):
        return ThreadTask.objects.filter(thread=thread).order_by('-id').first()


@patch('apps.Imagi.Build.services.usage_limits.check_usage_allowed', return_value=(True, None))
class NewThreadInParallelTests(_ScheduleTestCase):
    """Nothing needed from other work: a new thread, staged at once."""

    def test_unrelated_jobs_are_staged_on_new_threads_side_by_side(self, _allowed):
        _, menu = self._dispatch('Add a menu', goal='Adding a menu')
        _, footer = self._dispatch('Add a footer with opening hours', goal='Adding a footer')

        for thread in (menu, footer):
            task = self._task(thread)
            self.assertEqual((task.placement, task.status), ('new', 'queued'))
            self.assertEqual(thread.queued_prompt, task.brief)
        claimed = _claim_waiting_threads(self.user)['claimed']
        self.assertEqual({c['conversation_id'] for c in claimed}, {menu.id, footer.id})

    def test_a_run_moves_its_task_through_running_to_a_structured_result(self, _allowed):
        _, thread = self._dispatch('Add a menu')
        self._run(thread, summary='Your site has a menu now.')

        task = self._task(thread)
        self.assertEqual(task.status, 'done')
        self.assertIsNotNone(task.started_at)
        self.assertIsNotNone(task.finished_at)
        self.assertEqual(task.result, {
            'outcome': 'done', 'summary': 'Your site has a menu now.',
            'files': ['src/App.vue'],
        })


class SameThreadSerialTests(_ScheduleTestCase):
    """B needs A's result: B goes on A's thread and runs after it."""

    def test_follow_up_is_lined_up_behind_the_running_job(self):
        _, thread = self._dispatch('Add a menu')
        thread.refresh_from_db()
        # A's run starts and consumes its brief.
        scheduling.task_run_started(thread, thread.queued_prompt)
        thread.queued_prompt = ''
        thread.run_started_at = timezone.now()
        thread.save(update_fields=['queued_prompt', 'run_started_at'])

        message_task_impl(self._ctx(), thread.id, 'Now make the menu sticky')

        first, second = ThreadTask.objects.filter(thread=thread).order_by('id')
        self.assertEqual((first.status, second.status), ('running', 'queued'))
        self.assertEqual(second.placement, 'append')
        thread.refresh_from_db()
        # Staged for the thread's next run, not this one.
        self.assertEqual(thread.queued_prompt, 'Now make the menu sticky')
        # The running job ends; only it is done, B is still to run.
        scheduling.task_run_ended(thread, 'done', 'Menu added.')
        first.refresh_from_db(); second.refresh_from_db()
        self.assertEqual((first.status, second.status), ('done', 'queued'))
        scheduling.task_run_started(thread, thread.queued_prompt)
        second.refresh_from_db()
        self.assertEqual(second.status, 'running')

    def test_roster_shows_work_lined_up_on_a_thread(self):
        _, thread = self._dispatch('Add a menu', goal='Adding a menu')
        scheduling.task_run_started(thread, 'Add a menu')
        message_task_impl(self._ctx(), thread.id, 'Then make it sticky')

        roster = lead_task_roster(self.lead)
        self.assertIn(f'Thread {thread.id}: "Adding a menu"', roster)
        self.assertIn('1 more job(s) lined up after this', roster)


class ForkedThreadTests(_ScheduleTestCase):
    """B needs A's context but not its result: a fork, in parallel."""

    def setUp(self):
        super().setUp()
        _, self.source = self._dispatch('Redesign the home page', goal='Redesigning home')
        AgentMessage.objects.create(
            conversation=self.source, role='user', content='Redesign the home page'
        )
        AgentMessage.objects.create(
            conversation=self.source, role='assistant',
            content='Using navy and coral, with a big photo hero.',
        )

    def test_fork_starts_now_from_the_source_conversation(self):
        result, fork = self._dispatch(
            'Give the about page the same look', fork_from=self.source.id,
            reason='Same look as the home page thread',
        )

        self.assertEqual(fork.forked_from_id, self.source.id)
        self.assertEqual(
            fork.fork_point, self.source.messages.order_by('-id').first().id
        )
        task = self._task(fork)
        self.assertEqual((task.placement, task.status), ('fork', 'queued'))
        self.assertEqual(task.reason, 'Same look as the home page thread')
        self.assertFalse(result['dispatched_tasks'][0]['waiting'])
        self.assertEqual(result['dispatched_tasks'][0]['forked_from'], self.source.id)

    def test_fork_inherits_history_up_to_the_fork_point_only(self):
        _, fork = self._dispatch('Give the about page the same look', fork_from=self.source.id)
        # The source carries on after the fork; that does not flow across.
        AgentMessage.objects.create(
            conversation=self.source, role='assistant', content='Switched to green.'
        )
        AgentMessage.objects.create(
            conversation=fork, role='user', content='Give the about page the same look'
        )

        history = self.service.build_conversation_history(fork)
        contents = [m['content'] for m in history]

        self.assertTrue(contents[0].startswith('[Forked thread]'))
        self.assertIn('Using navy and coral, with a big photo hero.', contents)
        self.assertNotIn('Switched to green.', contents)
        self.assertEqual(contents[-1], 'Give the about page the same look')

    def test_fork_keeps_the_source_model(self):
        self.source.model_name = 'claude-sonnet-5-5'
        self.source.reasoning_effort = 'high'
        self.source.save()
        _, fork = self._dispatch('Same look for the about page', fork_from=self.source.id)
        self.assertEqual((fork.model_name, fork.reasoning_effort), ('claude-sonnet-5-5', 'high'))

    def test_cannot_fork_a_thread_from_elsewhere(self):
        stranger = AgentConversation.objects.create(
            user=self.user, model_name='claude-opus-5-5', kind='task', project_id=self.project.id,
        )
        result = None
        with self.assertRaises(ValueError):
            result = dispatch_task_impl(self._ctx(), 'Copy it', fork_from=stranger.id)
        self.assertIsNone(result)


@patch('apps.Imagi.Build.services.usage_limits.check_usage_allowed', return_value=(True, None))
class WaitsForResultsTests(_ScheduleTestCase):
    """Fan-in and chains across threads: held until every dependency lands."""

    def setUp(self):
        super().setUp()
        _, self.menu = self._dispatch('Add a menu', goal='Adding a menu')
        _, self.shop = self._dispatch('Add a shop page', goal='Adding a shop')

    def test_dependent_work_never_runs_before_what_it_depends_on(self, _allowed):
        result, summary_page = self._dispatch(
            'Link the shop from the menu', after=[self.menu.id, self.shop.id],
        )
        self.assertTrue(result['dispatched_tasks'][0]['waiting'])
        self.assertEqual(
            result['dispatched_tasks'][0]['depends_on_threads'],
            sorted([self.menu.id, self.shop.id]),
        )
        self.assertEqual(summary_page.queued_prompt, '')
        self.assertEqual(self._task(summary_page).status, 'waiting')

        # Only the independent work is started.
        claimed = {c['conversation_id'] for c in _claim_waiting_threads(self.user)['claimed']}
        self.assertEqual(claimed, {self.menu.id, self.shop.id})

        # One dependency landing is not enough for a fan-in.
        self._run(self.menu)
        scheduling.release_waiting_tasks(self.user)
        self.assertEqual(self._task(summary_page).status, 'waiting')
        summary_page.refresh_from_db()
        self.assertEqual(summary_page.queued_prompt, '')

        # Both landed: it is released onto its thread and starts.
        self._run(self.shop)
        AgentConversation.objects.filter(id__in=[self.menu.id, self.shop.id]).update(
            run_started_at=None
        )
        claimed = _claim_waiting_threads(self.user)['claimed']
        self.assertEqual([c['conversation_id'] for c in claimed], [summary_page.id])
        self.assertEqual(claimed[0]['brief'], 'Link the shop from the menu')
        self.assertEqual(self._task(summary_page).status, 'queued')

    def test_held_work_is_not_mistaken_for_a_dead_run(self, _allowed):
        _, waiting = self._dispatch('Link the shop', after=[self.menu.id])
        AgentConversation.objects.filter(id=waiting.id).update(
            updated_at=timezone.now() - timezone.timedelta(hours=1)
        )

        _park_stranded_tasks(self.user, self.project.id)

        waiting.refresh_from_db()
        self.assertEqual(waiting.review_status, 'active')

    def test_a_failed_dependency_blocks_until_it_is_retried_and_lands(self, _allowed):
        _, waiting = self._dispatch('Link the shop', after=[self.menu.id])
        self._run(self.menu, outcome='failed')
        scheduling.release_waiting_tasks(self.user)
        self.assertEqual(self._task(waiting).status, 'blocked')
        self.assertIn('stopped or was discarded', lead_task_roster(self.lead))

        # The user retries the menu thread; once it lands the work is freed.
        scheduling.task_run_started(self.menu, 'keep going')
        scheduling.release_waiting_tasks(self.user)
        self.assertEqual(self._task(waiting).status, 'waiting')
        scheduling.task_run_ended(self.menu, 'done', 'Menu added.')
        scheduling.release_waiting_tasks(self.user)
        self.assertEqual(self._task(waiting).status, 'queued')

    def test_discarding_a_dependency_blocks_and_discarding_the_waiter_cancels(self, _allowed):
        _, waiting = self._dispatch('Link the shop', after=[self.menu.id])
        scheduling.cancel_thread_tasks(self.menu)
        scheduling.release_waiting_tasks(self.user)
        self.assertEqual(self._task(waiting).status, 'blocked')

        waiting.review_status = 'dismissed'
        waiting.save(update_fields=['review_status'])
        scheduling.release_waiting_tasks(self.user)
        self.assertEqual(self._task(waiting).status, 'cancelled')

    def test_work_that_already_landed_is_nothing_to_wait_for(self, _allowed):
        self._run(self.menu)
        result, thread = self._dispatch('Link the shop', after=[self.menu.id])
        self.assertFalse(result['dispatched_tasks'][0]['waiting'])
        self.assertEqual(thread.queued_prompt, 'Link the shop')

    def test_roster_and_serializer_show_what_a_thread_waits_for(self, _allowed):
        _, waiting = self._dispatch(
            'Link the shop', goal='Linking the shop', after=[self.shop.id],
            reason='Builds on the new shop page',
        )
        self.assertIn(
            f'"Linking the shop" — waiting for thread {self.shop.id} to land',
            lead_task_roster(self.lead),
        )
        schedule = scheduling.thread_schedule(waiting)
        self.assertEqual(schedule['status'], 'waiting')
        self.assertEqual(schedule['reason'], 'Builds on the new shop page')
        self.assertEqual([w['id'] for w in schedule['waits_on']], [self.shop.id])
        self.assertEqual(schedule['waits_on'][0]['title'], 'Adding a shop')

    def test_a_follow_up_for_a_held_thread_waits_with_it(self, _allowed):
        _, waiting = self._dispatch('Link the shop', after=[self.menu.id])
        message_task_impl(self._ctx(), waiting.id, 'Use the word Store')
        waiting.refresh_from_db()
        self.assertEqual(waiting.queued_prompt, '')
        self.assertEqual(ThreadTask.objects.filter(thread=waiting).count(), 1)
        self.assertIn('Use the word Store', self._task(waiting).brief)

    def test_unknown_threads_are_refused(self, _allowed):
        with self.assertRaises(ValueError):
            dispatch_task_impl(self._ctx(), 'Link it', after=[999999])

    def test_schedule_endpoint_returns_the_task_graph(self, _allowed):
        _, waiting = self._dispatch('Link the shop', after=[self.menu.id, self.shop.id])
        token = Token.objects.create(user=self.user)
        response = self.client.get(
            reverse('project_schedule') + f'?project_id={self.project.id}',
            HTTP_AUTHORIZATION=f'Token {token.key}',
        )
        self.assertEqual(response.status_code, 200)
        tasks = {t['thread_id']: t for t in response.json()['tasks']}
        self.assertEqual(
            tasks[waiting.id]['depends_on_threads'], sorted([self.menu.id, self.shop.id])
        )
        self.assertEqual(tasks[waiting.id]['status'], 'waiting')


class _FakeCaptureModel:
    """Stands in for the Anthropic client: records the prompt it was given and
    answers with the update_memory call it was set up with."""

    def __init__(self, changes):
        self.changes = changes
        self.prompts = []
        self.messages = self

    def create(self, **kwargs):
        from types import SimpleNamespace
        self.prompts.append(kwargs['messages'][0]['content'])
        return SimpleNamespace(
            content=[SimpleNamespace(type='tool_use', input={'changes': self.changes})],
            usage=SimpleNamespace(input_tokens=900, output_tokens=60),
        )


class ProjectMemoryTests(_ScheduleTestCase):
    def _doc(self):
        return project_memory.read_document(self.user.id, self.project.id)

    def test_lines_go_under_their_section_once_and_every_prompt_reads_them(self):
        project_memory.remember(self.user.id, self.project.id, 'Brand colours are navy and coral')
        project_memory.remember(self.user.id, self.project.id, '- brand colours are navy and coral.')
        project_memory.remember(
            self.user.id, self.project.id, 'A bakery in Grand Rapids', section='About the app'
        )

        doc = self._doc()
        self.assertEqual(doc.count('navy and coral'), 1)
        self.assertLess(doc.index('## About the app'), doc.index('A bakery'))
        self.assertLess(doc.index('## Decisions'), doc.index('Brand colours'))
        self.assertEqual(ProjectMemoryChange.objects.count(), 2)

        summary = project_memory.memory_summary(self.user.id, self.project.id)
        self.assertIn('- Brand colours are navy and coral', summary)
        # Empty sections stay out of the prompt.
        self.assertNotIn("How it's built", summary)

        from agents import RunContextWrapper
        from apps.Imagi.Build.services.coding_agent import create_coding_agent
        for kind in ('lead', 'task'):
            agent = create_coding_agent(kind=kind)
            ctx = AgentContext(user_id=self.user.id, project_id=self.project.id,
                               conversation_kind=kind, project_memory=summary)
            self.assertIn('navy and coral', agent.instructions(RunContextWrapper(context=ctx), agent))

    def test_forget_removes_the_matching_line_only(self):
        project_memory.remember(self.user.id, self.project.id, 'Menu is sticky on every page')
        project_memory.remember(self.user.id, self.project.id, 'Footer shows opening hours')
        self.assertIsNotNone(project_memory.forget(self.user.id, self.project.id, 'sticky'))
        self.assertNotIn('sticky', self._doc())
        self.assertIn('Footer shows opening hours', self._doc())
        # Ambiguous or missing: nothing is removed.
        project_memory.remember(self.user.id, self.project.id, 'Footer is dark')
        self.assertIsNone(project_memory.forget(self.user.id, self.project.id, 'footer'))
        self.assertIsNone(project_memory.forget(self.user.id, self.project.id, 'pricing'))

    def test_a_threads_notes_land_with_its_work_and_not_otherwise(self):
        _, kept = self._dispatch('Add a menu')
        _, dropped = self._dispatch('Add a footer')
        project_memory.add_thread_note(kept, 'Menu is sticky at the top of every page', "How it's built")
        project_memory.add_thread_note(dropped, 'Footer is dark, with hours')
        self.assertEqual(project_memory.memory_summary(self.user.id, self.project.id), '')
        self.assertEqual(
            [p['thread']['id'] for p in project_memory.pending_notes(self.user, self.project.id)],
            [kept.id, dropped.id],
        )

        project_memory.thread_landed(kept, capture=False)
        project_memory.thread_discarded(dropped)

        doc = self._doc()
        self.assertIn('Menu is sticky', doc)
        self.assertNotIn('Footer', doc)
        change = ProjectMemoryChange.objects.get()
        self.assertEqual((change.author, change.source_id), ('thread', kept.id))
        self.assertEqual(project_memory.pending_notes(self.user, self.project.id), [])

    def test_a_running_thread_sees_a_line_saved_mid_run(self):
        ctx = AgentContext(user_id=self.user.id, project_id=self.project.id)
        self.assertIsNone(project_memory.refresh_context(ctx))
        project_memory.remember(self.user.id, self.project.id, 'Tone is friendly')
        self.assertIn('Tone is friendly', project_memory.refresh_context(ctx))
        self.assertIsNone(project_memory.refresh_context(ctx))

    def test_the_prompt_carries_at_most_the_cap(self):
        for i in range(40):
            project_memory.remember(self.user.id, self.project.id, f'Fact {i} ' + 'x' * 300)
        summary = project_memory.memory_summary(self.user.id, self.project.id)
        self.assertLess(len(summary), project_memory.MEMORY_MAX_CHARS + 200)
        self.assertTrue(summary.endswith('…'))

    def test_capture_reads_a_coordinator_turn_and_applies_its_changes(self):
        project_memory.remember(self.user.id, self.project.id, 'Colours are navy and gold')
        AgentMessage.objects.create(conversation=self.lead, role='user',
                                    content='Actually make it navy and coral, and keep it calm.')
        AgentMessage.objects.create(conversation=self.lead, role='assistant',
                                    content='On it.', metadata={})
        model = _FakeCaptureModel([
            {'action': 'remove', 'text': 'Colours are navy and gold'},
            {'action': 'add', 'section': 'Decisions', 'text': 'Colours are navy and coral'},
            {'action': 'add', 'section': 'How the user likes to work', 'text': 'Prefers a calm tone'},
        ])

        change = project_memory.capture(self.lead.id, client=model)

        self.assertIn('Colours are navy and gold', model.prompts[0])
        self.assertIn('User: Actually make it navy and coral', model.prompts[0])
        doc = self._doc()
        self.assertNotIn('gold', doc)
        self.assertIn('- Colours are navy and coral', doc)
        self.assertIn('## How the user likes to work\n- Prefers a calm tone', doc)
        self.assertEqual((change.author, change.source_id), ('auto', self.lead.id))
        # The turn was read once: a second pass has nothing new.
        self.assertIsNone(project_memory.capture(self.lead.id, client=model))
        self.assertEqual(len(model.prompts), 1)

    def test_capture_skips_turns_with_nothing_from_the_user(self):
        AgentMessage.objects.create(conversation=self.lead, role='user',
                                    content='[App error] The app reported these errors…')
        AgentMessage.objects.create(
            conversation=self.lead, role='assistant', content='The menu thread finished.',
            metadata={'task_report': {'kind': 'done'}},
        )
        model = _FakeCaptureModel([{'action': 'add', 'text': 'Should not be saved'}])
        self.assertIsNone(project_memory.capture(self.lead.id, client=model))
        self.assertEqual(model.prompts, [])

    def test_capture_of_a_landed_thread_reads_its_brief_and_files(self):
        _, thread = self._dispatch('Add a menu page with the dishes from the PDF')
        AgentMessage.objects.create(conversation=thread, role='user',
                                    content='Add a menu page with the dishes from the PDF')
        AgentMessage.objects.create(
            conversation=thread, role='assistant', content='Your menu page is live.',
            metadata={'files_changed': ['frontend/vuejs/src/apps/menu/views/MenuView.vue']},
        )
        model = _FakeCaptureModel([])
        self.assertIsNone(project_memory.capture(thread.id, client=model))
        self.assertIn('Brief from the coordinator: Add a menu page', model.prompts[0])
        self.assertIn('MenuView.vue', model.prompts[0])

    def test_undo_puts_lines_back(self):
        project_memory.remember(self.user.id, self.project.id, 'Colours are navy and gold')
        change = project_memory.apply_changes(self.user.id, self.project.id, [
            {'action': 'remove', 'text': 'Colours are navy and gold'},
            {'action': 'add', 'section': 'Decisions', 'text': 'Colours are navy and coral'},
        ], author='auto')
        project_memory.undo_change(change)
        doc = self._doc()
        self.assertIn('navy and gold', doc)
        self.assertNotIn('coral', doc)
        change.refresh_from_db()
        self.assertIsNotNone(change.undone_at)
        with self.assertRaises(ValueError):
            project_memory.undo_change(change)

    def test_the_user_views_edits_and_undoes_memory_over_the_api(self):
        token = Token.objects.create(user=self.user)
        auth = {'HTTP_AUTHORIZATION': f'Token {token.key}'}
        url = reverse('project_memory') + f'?project_id={self.project.id}'
        viewed = self.client.get(url, **auth).json()
        self.assertEqual(viewed['version'], 0)
        self.assertIn('## About the app', viewed['content'])

        content = viewed['content'].replace('## Decisions', '## Decisions\n- Audience is local families')
        saved = self.client.put(
            url, {'content': content, 'version': 0}, content_type='application/json', **auth,
        )
        self.assertEqual(saved.status_code, 200)
        self.assertEqual(saved.json()['version'], 1)
        change = saved.json()['changes'][0]
        self.assertEqual(change['author'], 'user')
        self.assertEqual(change['lines'], [
            {'op': 'add', 'section': 'Decisions', 'text': 'Audience is local families'},
        ])

        # An edit of an older copy is merged into the memory as it is now:
        # the line saved meanwhile stays, and the edit's own line is added.
        stale = self.client.put(
            url,
            {'content': viewed['content'].replace('## Decisions', '## Decisions\n- Opens at 7am'),
             'version': 0, 'base_content': viewed['content']},
            content_type='application/json', **auth,
        )
        self.assertEqual(stale.status_code, 200)
        self.assertIn('Audience is local families', stale.json()['content'])
        self.assertIn('Opens at 7am', stale.json()['content'])
        # Without the copy it started from, it is refused with the memory as it is.
        refused = self.client.put(
            url, {'content': '## Decisions\n- Something else', 'version': 0},
            content_type='application/json', **auth,
        )
        self.assertEqual(refused.status_code, 409)
        self.assertIn('Opens at 7am', refused.json()['content'])

        undone = self.client.post(
            reverse('project_memory_undo', args=[change['id']]), **auth,
        )
        self.assertEqual(undone.status_code, 200)
        self.assertNotIn('Audience', undone.json()['content'])
        self.assertIn('Opens at 7am', undone.json()['content'])
        self.assertTrue(
            next(c for c in undone.json()['changes'] if c['id'] == change['id'])['undone']
        )


class ReconcileConflictTests(GitRepoTestMixin, TestCase):
    """Parallel threads that touched the same lines: the late one reconciles
    the clash itself rather than overwriting, and nothing half-merged lands."""

    def setUp(self):
        self.user = User.objects.create_user(username='merger', password='pw123456')
        self.repo = self._make_repo()
        self.project = Project.objects.create(
            user=self.user, name='P', project_path=self.repo, is_active=True
        )
        self.service = ImagiAgentService()
        self.lead = self.service.create_conversation(
            self.user, 'claude-opus-5-5', project_id=self.project.id, kind='lead'
        )
        self.thread = self.service.create_conversation(
            self.user, 'claude-opus-5-5', project_id=self.project.id,
            kind='task', parent=self.lead,
        )
        self.thread.review_status = 'active'
        self.thread.save(update_fields=['review_status'])
        scheduling.schedule_work(lead=self.lead, thread=self.thread, brief='Retitle the app')
        scheduling.task_run_started(self.thread, 'Retitle the app')
        worktree = VersionControlService().create_task_worktree(
            self.repo, self.thread.id
        )['worktree_path']
        self.thread.worktree_path = worktree
        self.thread.save(update_fields=['worktree_path'])
        with open(os.path.join(worktree, 'app.txt'), 'w') as f:
            f.write('hello from the thread')
        # Meanwhile another thread's work landed on the same line.
        self._write_commit(self.repo, 'app.txt', 'hello from elsewhere', 'other work')

    def _context(self):
        return AgentContext(user_id=self.user.id, project_id=self.project.id,
                            conversation_kind='task')

    def test_clash_sends_the_thread_back_with_both_changes_marked(self):
        self.service._finalize_task_run(self.thread, self._context(), 'Retitled.')

        self.thread.refresh_from_db()
        self.assertEqual(self.thread.review_status, 'active')
        self.assertEqual(self.thread.merge_retries, 1)
        self.assertIn('[Reconcile]', self.thread.queued_prompt)
        self.assertIn('app.txt', self.thread.queued_prompt)
        with open(os.path.join(self.thread.worktree_path, 'app.txt')) as f:
            text = f.read()
        self.assertIn('<<<<<<<', text)
        self.assertIn('hello from elsewhere', text)
        # The app still has only the landed work; the task is still running.
        with open(os.path.join(self.repo, 'app.txt')) as f:
            self.assertEqual(f.read(), 'hello from elsewhere')
        self.assertEqual(ThreadTask.objects.get(thread=self.thread).status, 'running')

    def test_unsettled_markers_never_land_and_a_settled_merge_does(self):
        self.service._finalize_task_run(self.thread, self._context(), 'Retitled.')
        self.thread.refresh_from_db()
        # The thread's next run starts by checkpointing its copy, markers and
        # all, then ends without settling them: nothing lands.
        VersionControlService().ensure_checkpoint(self.thread.worktree_path, 'checkpoint')
        self.service._finalize_task_run(self.thread, self._context(), 'Done.')
        self.thread.refresh_from_db()
        self.assertEqual(self.thread.review_status, 'input')
        with open(os.path.join(self.repo, 'app.txt')) as f:
            self.assertNotIn('<<<<<<<', f.read())

        # Settled: both changes kept, and it lands cleanly.
        with open(os.path.join(self.thread.worktree_path, 'app.txt'), 'w') as f:
            f.write('hello from elsewhere and from the thread')
        self.thread.review_status = 'active'
        self.thread.save(update_fields=['review_status'])
        scheduling.task_run_started(self.thread, 'try again')
        self.service._finalize_task_run(self.thread, self._context(), 'Settled.')

        self.thread.refresh_from_db()
        self.assertEqual(self.thread.review_status, 'accepted')
        self.assertEqual(self.thread.merge_retries, 0)
        with open(os.path.join(self.repo, 'app.txt')) as f:
            self.assertEqual(f.read(), 'hello from elsewhere and from the thread')
        self.assertEqual(ThreadTask.objects.get(thread=self.thread).status, 'done')
        self.assertEqual(_git(self.repo, 'status', '--porcelain').stdout.strip(), '')
