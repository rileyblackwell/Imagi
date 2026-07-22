"""
Tests for the lead/task conversation model and per-task git worktrees.

Covers the worktree lifecycle at the service level (create/merge/remove,
conflict handling) against real throwaway git repos, the kind-scoped busy
guards (tasks run in parallel with the lead; canonical-tree runs stay
serialized), the single-lead invariant, review-status transitions, and the
accept/dismiss review endpoints.
"""

import os
import shutil
import subprocess
import tempfile
from types import SimpleNamespace

from asgiref.sync import async_to_sync
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.authtoken.models import Token
from unittest.mock import patch

from apps.Imagi.Build.api.views import _project_has_running_conversation
from apps.Imagi.Build.models import AgentConversation, AgentMessage, ProjectFile
from apps.Imagi.Build.services.base_agent import AgentContext, ImagiAgentService
from apps.Imagi.Build.services.tools import _get_project, edit_file_impl
from apps.Imagi.Build.services.version_control_service import (
    MergeConflict,
    StaleForkPoint,
    VersionControlService,
    task_branch,
    task_worktree_path,
)
from apps.Imagi.ProjectManager.models import Project


def _git(cwd, *args, check=True):
    return subprocess.run(
        ['git', *args], cwd=cwd, capture_output=True, text=True, check=check
    )


class GitRepoTestMixin:
    """A throwaway canonical git repo with one committed file."""

    def _make_repo(self):
        # The worktree is created as a sibling of the repo directory, so the
        # repo needs its own parent directory to keep cleanup a single rmtree.
        parent = tempfile.mkdtemp(prefix='task_wt_')
        self.addCleanup(lambda: shutil.rmtree(parent, ignore_errors=True))
        repo = os.path.join(parent, 'proj')
        os.makedirs(repo)
        _git(repo, 'init')
        _git(repo, 'config', 'user.email', 't@t.co')
        _git(repo, 'config', 'user.name', 'T')
        self._write_commit(repo, 'app.txt', 'hello', 'initial')
        return repo

    def _write_commit(self, repo, name, content, message):
        with open(os.path.join(repo, name), 'w') as f:
            f.write(content)
        _git(repo, 'add', '.')
        _git(repo, 'commit', '-m', message)
        return _git(repo, 'rev-parse', 'HEAD').stdout.strip()


class WorktreeServiceTests(GitRepoTestMixin, SimpleTestCase):
    """create/merge/remove worktree lifecycle at the service level."""

    def setUp(self):
        self.repo = self._make_repo()
        self.service = VersionControlService()

    def test_create_checks_out_sibling_branch(self):
        result = self.service.create_task_worktree(self.repo, 7)

        self.assertTrue(result['success'])
        expected_path = task_worktree_path(self.repo, 7)
        self.assertEqual(result['worktree_path'], expected_path)
        # A sibling of the project dir, never inside it.
        self.assertEqual(os.path.dirname(expected_path), os.path.dirname(self.repo))
        self.assertTrue(os.path.isdir(expected_path))
        # Canonical content is checked out on the task branch.
        with open(os.path.join(expected_path, 'app.txt')) as f:
            self.assertEqual(f.read(), 'hello')
        branch = _git(expected_path, 'rev-parse', '--abbrev-ref', 'HEAD').stdout.strip()
        self.assertEqual(branch, task_branch(7))

    def test_create_is_idempotent(self):
        first = self.service.create_task_worktree(self.repo, 7)
        second = self.service.create_task_worktree(self.repo, 7)
        self.assertTrue(second['success'])
        self.assertEqual(second['worktree_path'], first['worktree_path'])

    def test_create_snapshots_pending_canonical_changes(self):
        # Uncommitted canonical edits are checkpointed first, so the task
        # branches from what is on disk right now.
        with open(os.path.join(self.repo, 'app.txt'), 'w') as f:
            f.write('edited but uncommitted')

        result = self.service.create_task_worktree(self.repo, 3)

        self.assertTrue(result['success'])
        with open(os.path.join(result['worktree_path'], 'app.txt')) as f:
            self.assertEqual(f.read(), 'edited but uncommitted')

    def test_create_without_snapshot_forks_from_committed_head(self):
        # snapshot_pending=False (a canonical run is live): pending edits are
        # neither committed nor forked — the task starts from the last
        # committed HEAD and the canonical tree stays dirty.
        with open(os.path.join(self.repo, 'app.txt'), 'w') as f:
            f.write('half-written lead edit')

        result = self.service.create_task_worktree(self.repo, 3, snapshot_pending=False)

        self.assertTrue(result['success'])
        with open(os.path.join(result['worktree_path'], 'app.txt')) as f:
            self.assertEqual(f.read(), 'hello')
        # The dirty canonical edit was not committed away.
        with open(os.path.join(self.repo, 'app.txt')) as f:
            self.assertEqual(f.read(), 'half-written lead edit')
        status = _git(self.repo, 'status', '--porcelain').stdout
        self.assertIn('app.txt', status)
        log = _git(self.repo, 'log', '--oneline').stdout
        self.assertNotIn('Checkpoint before task', log)

    def test_merge_brings_task_changes_into_canonical(self):
        worktree = self.service.create_task_worktree(self.repo, 7)['worktree_path']
        # Uncommitted worktree edit: merge must commit it first.
        with open(os.path.join(worktree, 'feature.txt'), 'w') as f:
            f.write('task output')

        result = self.service.merge_task_worktree(self.repo, 7)

        self.assertTrue(result['success'])
        self.assertTrue(result['commit_hash'])
        with open(os.path.join(self.repo, 'feature.txt')) as f:
            self.assertEqual(f.read(), 'task output')

    def test_merge_conflict_aborts_and_raises(self):
        worktree = self.service.create_task_worktree(self.repo, 7)['worktree_path']
        self._write_commit(self.repo, 'app.txt', 'canonical edit', 'canonical change')
        with open(os.path.join(worktree, 'app.txt'), 'w') as f:
            f.write('conflicting task edit')

        with self.assertRaises(MergeConflict):
            self.service.merge_task_worktree(self.repo, 7)

        # The merge was aborted: no merge in progress, canonical untouched.
        self.assertFalse(os.path.exists(os.path.join(self.repo, '.git', 'MERGE_HEAD')))
        with open(os.path.join(self.repo, 'app.txt')) as f:
            self.assertEqual(f.read(), 'canonical edit')

    def test_merge_without_worktree_fails_cleanly(self):
        result = self.service.merge_task_worktree(self.repo, 99)
        self.assertFalse(result['success'])

    def test_merge_after_canonical_restore_raises_stale_fork_point(self):
        # Canonical A-B; task forks at B; the user then restores canonical to
        # A. Merging the branch would fast-forward B straight back in, so the
        # merge must refuse and leave canonical untouched.
        commit_a = _git(self.repo, 'rev-parse', 'HEAD').stdout.strip()
        self._write_commit(self.repo, 'app.txt', 'version B', 'commit B')
        worktree = self.service.create_task_worktree(self.repo, 7)['worktree_path']
        with open(os.path.join(worktree, 'feature.txt'), 'w') as f:
            f.write('task output')
        _git(self.repo, 'reset', '--hard', commit_a)

        with self.assertRaises(StaleForkPoint):
            self.service.merge_task_worktree(self.repo, 7)

        # Canonical stayed on the restored commit with none of B's content.
        self.assertEqual(_git(self.repo, 'rev-parse', 'HEAD').stdout.strip(), commit_a)
        with open(os.path.join(self.repo, 'app.txt')) as f:
            self.assertEqual(f.read(), 'hello')
        self.assertFalse(os.path.exists(os.path.join(self.repo, 'feature.txt')))

    def test_merge_allowed_when_restored_to_the_fork_point_itself(self):
        # Restoring to exactly the fork commit keeps it in history, so the
        # merge carries only the task's own work.
        self._write_commit(self.repo, 'app.txt', 'version B', 'commit B')
        fork = _git(self.repo, 'rev-parse', 'HEAD').stdout.strip()
        worktree = self.service.create_task_worktree(self.repo, 7)['worktree_path']
        with open(os.path.join(worktree, 'feature.txt'), 'w') as f:
            f.write('task output')
        _git(self.repo, 'reset', '--hard', fork)

        result = self.service.merge_task_worktree(self.repo, 7)

        self.assertTrue(result['success'])
        with open(os.path.join(self.repo, 'feature.txt')) as f:
            self.assertEqual(f.read(), 'task output')

    def test_remove_deletes_worktree_and_branch(self):
        worktree = self.service.create_task_worktree(self.repo, 7)['worktree_path']

        result = self.service.remove_task_worktree(self.repo, 7)

        self.assertTrue(result['success'])
        self.assertFalse(os.path.exists(worktree))
        branch_check = _git(
            self.repo, 'rev-parse', '--verify', f'refs/heads/{task_branch(7)}',
            check=False,
        )
        self.assertNotEqual(branch_check.returncode, 0)

    def test_remove_tolerates_already_gone(self):
        # Never created at all.
        self.assertTrue(self.service.remove_task_worktree(self.repo, 42)['success'])
        # Created, directory deleted manually, then removed twice.
        worktree = self.service.create_task_worktree(self.repo, 7)['worktree_path']
        shutil.rmtree(worktree)
        self.assertTrue(self.service.remove_task_worktree(self.repo, 7)['success'])
        self.assertTrue(self.service.remove_task_worktree(self.repo, 7)['success'])

    def test_recreate_after_manual_delete(self):
        # A pruned-then-recreated worktree must come back working even though
        # the stale branch still exists.
        worktree = self.service.create_task_worktree(self.repo, 7)['worktree_path']
        shutil.rmtree(worktree)
        result = self.service.create_task_worktree(self.repo, 7)
        self.assertTrue(result['success'])
        self.assertTrue(os.path.isdir(result['worktree_path']))

    def test_initialize_repo_leaves_worktree_git_file_alone(self):
        # A linked worktree's .git is a FILE; initialize_repo must treat it
        # as an existing repo, not git-init inside it.
        worktree = self.service.create_task_worktree(self.repo, 7)['worktree_path']
        git_pointer = os.path.join(worktree, '.git')
        self.assertTrue(os.path.isfile(git_pointer))

        self.assertTrue(self.service.initialize_repo(worktree))
        self.assertTrue(os.path.isfile(git_pointer))


class BusyGuardMatrixTests(TestCase):
    """Kind-scoped busy guards: tasks run in parallel, canonical runs don't."""

    def setUp(self):
        self.user = User.objects.create_user(username='matrix', password='pw123456')
        self.token = Token.objects.create(user=self.user)

    def _conversation(self, kind='chat', **kwargs):
        return AgentConversation.objects.create(
            user=self.user, model_name='gpt-5.6-terra', project_id=1,
            kind=kind, **kwargs
        )

    def _stream(self, payload):
        return self.client.post(
            reverse('agent_stream'), data=payload,
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.token.key}',
        )

    def test_running_task_does_not_trip_the_canonical_guard(self):
        self._conversation(kind='task', run_started_at=timezone.now())
        self.assertFalse(_project_has_running_conversation(self.user, 1))

    def test_running_lead_trips_the_canonical_guard(self):
        self._conversation(kind='lead', run_started_at=timezone.now())
        self.assertTrue(_project_has_running_conversation(self.user, 1))

    def test_second_canonical_run_is_rejected(self):
        self._conversation(kind='lead', run_started_at=timezone.now())
        resp = self._stream('{"message": "hi", "project_id": 1}')
        self.assertEqual(resp.status_code, 409)
        self.assertEqual(resp.json()['detail'], 'agent_busy')

    def test_task_rerun_while_same_task_running_is_rejected(self):
        task = self._conversation(kind='task', run_started_at=timezone.now())
        resp = self._stream(
            f'{{"message": "hi", "project_id": 1, "conversation_id": {task.id}}}'
        )
        self.assertEqual(resp.status_code, 409)
        self.assertEqual(resp.json()['detail'], 'agent_busy')

    def test_task_run_allowed_while_lead_runs(self):
        self._conversation(kind='lead', run_started_at=timezone.now())
        task = self._conversation(kind='task')

        class _FakeAgentService:
            def __init__(self, *args, **kwargs):
                pass

            async def process_stream(self, **kwargs):
                yield {'type': 'done', 'success': True}

        with patch('apps.Imagi.Build.api.views.ImagiAgentService', _FakeAgentService):
            resp = self._stream(
                f'{{"message": "hi", "project_id": 1, "conversation_id": {task.id}}}'
            )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'text/event-stream')

        async def _drain(stream):
            return b''.join([chunk async for chunk in stream])

        self.assertIn(b'"done"', async_to_sync(_drain)(resp.streaming_content))

    def test_second_task_allowed_while_another_task_runs(self):
        self._conversation(kind='task', run_started_at=timezone.now())
        other_task = self._conversation(kind='task')

        class _FakeAgentService:
            def __init__(self, *args, **kwargs):
                pass

            async def process_stream(self, **kwargs):
                yield {'type': 'done', 'success': True}

        with patch('apps.Imagi.Build.api.views.ImagiAgentService', _FakeAgentService):
            resp = self._stream(
                f'{{"message": "hi", "project_id": 1, "conversation_id": {other_task.id}}}'
            )
        self.assertEqual(resp.status_code, 200)


class RestoreWhileTasksRunTests(GitRepoTestMixin, TestCase):
    """Canonical restores only wait for canonical-tree runs."""

    def setUp(self):
        self.user = User.objects.create_user(username='restorer', password='pw123456')
        self.client.force_login(self.user)
        self.repo = self._make_repo()
        self.project = Project.objects.create(
            user=self.user, name='P', project_path=self.repo, is_active=True
        )

    def test_restore_allowed_while_only_tasks_run(self):
        checkpoint = self._write_commit(self.repo, 'page.txt', 'original', 'v1')
        self._write_commit(self.repo, 'page.txt', 'agent edit', 'v2')
        conversation = AgentConversation.objects.create(
            user=self.user, model_name='gpt-5.6-terra', project_id=self.project.id
        )
        message = AgentMessage.objects.create(
            conversation=conversation, role='user', content='x',
            metadata={'checkpoint': checkpoint},
        )
        # A task mid-run edits only its worktree: it must not block the
        # canonical restore (its worktree branched from an earlier HEAD).
        AgentConversation.objects.create(
            user=self.user, model_name='gpt-5.6-terra', project_id=self.project.id,
            kind='task', run_started_at=timezone.now(),
        )

        resp = self.client.post(
            reverse('conversation_restore_checkpoint', args=[conversation.id]),
            data={'message_id': message.id}, content_type='application/json',
        )

        self.assertEqual(resp.status_code, 200)
        with open(os.path.join(self.repo, 'page.txt')) as f:
            self.assertEqual(f.read(), 'original')

    def test_task_restore_rewinds_its_worktree_not_canonical(self):
        task = AgentConversation.objects.create(
            user=self.user, model_name='gpt-5.6-terra', project_id=self.project.id,
            kind='task',
        )
        worktree = VersionControlService().create_task_worktree(
            self.repo, task.id
        )['worktree_path']
        task.worktree_path = worktree
        task.save(update_fields=['worktree_path'])

        service = VersionControlService()
        checkpoint = service.ensure_checkpoint(worktree, 'before')['commit_hash']
        with open(os.path.join(worktree, 'app.txt'), 'w') as f:
            f.write('task edit')
        service.ensure_checkpoint(worktree, 'after')

        message = AgentMessage.objects.create(
            conversation=task, role='user', content='x',
            metadata={'checkpoint': checkpoint},
        )

        resp = self.client.post(
            reverse('conversation_restore_checkpoint', args=[task.id]),
            data={'message_id': message.id}, content_type='application/json',
        )

        self.assertEqual(resp.status_code, 200)
        with open(os.path.join(worktree, 'app.txt')) as f:
            self.assertEqual(f.read(), 'hello')
        # Canonical stayed on its own HEAD.
        with open(os.path.join(self.repo, 'app.txt')) as f:
            self.assertEqual(f.read(), 'hello')


class SingleLeadTests(TestCase):
    """Conversation creation: kinds, parents, and the single-lead invariant."""

    def setUp(self):
        self.user = User.objects.create_user(username='leaduser', password='pw123456')
        self.client.force_login(self.user)
        self.url = reverse('conversations_list_create')

    def _create(self, **payload):
        payload.setdefault('project_id', 1)
        return self.client.post(self.url, data=payload, content_type='application/json')

    def test_lead_created_once_then_reused(self):
        first = self._create(kind='lead')
        self.assertEqual(first.status_code, 201)
        self.assertEqual(first.json()['kind'], 'lead')
        self.assertEqual(first.json()['review_status'], '')

        second = self._create(kind='lead')
        self.assertEqual(second.status_code, 200)
        self.assertEqual(second.json()['id'], first.json()['id'])
        self.assertEqual(
            AgentConversation.objects.filter(kind='lead', project_id=1).count(), 1
        )

    def test_archived_lead_does_not_block_a_new_one(self):
        first = self._create(kind='lead')
        AgentConversation.objects.filter(id=first.json()['id']).update(
            archived_at=timezone.now()
        )
        second = self._create(kind='lead')
        self.assertEqual(second.status_code, 201)
        self.assertNotEqual(second.json()['id'], first.json()['id'])

    def test_db_constraint_blocks_a_second_live_lead(self):
        # The API's check-then-create is not atomic; the partial unique
        # constraint is what actually holds the invariant under concurrency.
        self._create(kind='lead')
        with self.assertRaises(IntegrityError), transaction.atomic():
            AgentConversation.objects.create(
                user=self.user, model_name='gpt-5.6-terra', project_id=1,
                kind='lead',
            )

    def test_unarchiving_a_lead_is_refused_while_a_live_lead_exists(self):
        # Unarchive would resurrect a second live lead — the invariant is
        # enforced on this path too, not just at create time.
        first = self._create(kind='lead')
        AgentConversation.objects.filter(id=first.json()['id']).update(
            archived_at=timezone.now()
        )
        self._create(kind='lead')  # the replacement live lead

        resp = self.client.patch(
            reverse('conversation_detail', args=[first.json()['id']]),
            data={'archived': False}, content_type='application/json',
        )

        self.assertEqual(resp.status_code, 409)
        self.assertEqual(resp.json()['error'], 'lead_exists')
        self.assertIsNotNone(
            AgentConversation.objects.get(id=first.json()['id']).archived_at
        )

    def test_unarchiving_a_lead_is_allowed_when_no_live_lead_exists(self):
        first = self._create(kind='lead')
        AgentConversation.objects.filter(id=first.json()['id']).update(
            archived_at=timezone.now()
        )

        resp = self.client.patch(
            reverse('conversation_detail', args=[first.json()['id']]),
            data={'archived': False}, content_type='application/json',
        )

        self.assertEqual(resp.status_code, 200)
        self.assertIsNone(resp.json()['archived_at'])

    def test_leads_are_scoped_per_project(self):
        first = self._create(kind='lead', project_id=1)
        second = self._create(kind='lead', project_id=2)
        self.assertEqual(second.status_code, 201)
        self.assertNotEqual(second.json()['id'], first.json()['id'])

    def test_task_gets_active_review_status_and_parent(self):
        lead = self._create(kind='lead').json()
        resp = self._create(kind='task', parent=lead['id'], variant_group='v1')

        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertEqual(data['kind'], 'task')
        self.assertEqual(data['review_status'], 'active')
        self.assertEqual(data['parent'], lead['id'])
        self.assertEqual(data['variant_group'], 'v1')
        self.assertFalse(data['has_worktree'])

    def test_unknown_kind_falls_back_to_chat(self):
        resp = self._create(kind='supervisor')
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json()['kind'], 'chat')
        self.assertEqual(resp.json()['review_status'], '')

    def test_legacy_rows_default_to_chat(self):
        conversation = AgentConversation.objects.create(
            user=self.user, model_name='gpt-5.6-terra', project_id=1
        )
        self.assertEqual(conversation.kind, 'chat')
        self.assertEqual(conversation.review_status, '')
        self.assertEqual(conversation.worktree_path, '')
        self.assertIsNone(conversation.parent)


class TaskRunLifecycleTests(GitRepoTestMixin, TestCase):
    """_prepare_run wires task runs into their worktrees."""

    def setUp(self):
        self.user = User.objects.create_user(username='taskrun', password='pw123456')
        self.repo = self._make_repo()
        self.project = Project.objects.create(
            user=self.user, name='P', project_path=self.repo, is_active=True
        )
        self.service = ImagiAgentService()

    def _prepare(self, conversation):
        return self.service._prepare_run(
            user_input='do the thing',
            user=self.user,
            project_id=self.project.id,
            conversation_id=conversation.id,
        )

    def test_task_run_gets_worktree_as_effective_root(self):
        task = self.service.create_conversation(
            self.user, 'gpt-5.6-terra', project_id=self.project.id, kind='task'
        )
        conversation, context, _ = self._prepare(task)

        task.refresh_from_db()
        expected = task_worktree_path(self.repo, task.id)
        self.assertEqual(task.worktree_path, expected)
        self.assertTrue(os.path.isdir(expected))
        self.assertEqual(context.effective_project_path, expected)
        self.assertEqual(context.project_path, self.repo)
        self.assertIsNotNone(conversation.run_started_at)

    def test_task_dispatched_during_live_lead_run_skips_canonical_snapshot(self):
        # A live lead run may have half-written edits on the canonical tree;
        # dispatching a task must not commit that broken intermediate state
        # (as the fork point AND a permanent canonical commit). The task
        # forks from the last committed HEAD instead.
        self.service.create_conversation(
            self.user, 'gpt-5.6-terra', project_id=self.project.id, kind='lead'
        )
        AgentConversation.objects.filter(
            user=self.user, project_id=self.project.id, kind='lead'
        ).update(run_started_at=timezone.now())
        with open(os.path.join(self.repo, 'app.txt'), 'w') as f:
            f.write('half-written lead edit')

        task = self.service.create_conversation(
            self.user, 'gpt-5.6-terra', project_id=self.project.id, kind='task'
        )
        self._prepare(task)

        task.refresh_from_db()
        with open(os.path.join(task.worktree_path, 'app.txt')) as f:
            self.assertEqual(f.read(), 'hello')
        # The lead's in-flight edit stays uncommitted on the canonical tree.
        with open(os.path.join(self.repo, 'app.txt')) as f:
            self.assertEqual(f.read(), 'half-written lead edit')
        log = _git(self.repo, 'log', '--oneline').stdout
        self.assertNotIn('Checkpoint before task', log)

    def test_prompt_reopens_a_ready_task(self):
        task = self.service.create_conversation(
            self.user, 'gpt-5.6-terra', project_id=self.project.id, kind='task'
        )
        task.review_status = 'ready'
        task.save(update_fields=['review_status'])

        self._prepare(task)

        task.refresh_from_db()
        self.assertEqual(task.review_status, 'active')

    def test_chat_run_uses_canonical_root(self):
        chat = self.service.create_conversation(
            self.user, 'gpt-5.6-terra', project_id=self.project.id
        )
        _, context, _ = self._prepare(chat)

        self.assertEqual(context.effective_project_path, self.repo)
        chat.refresh_from_db()
        self.assertEqual(chat.worktree_path, '')

    def test_mark_task_ready_only_touches_tasks(self):
        task = self.service.create_conversation(
            self.user, 'gpt-5.6-terra', project_id=self.project.id, kind='task'
        )
        chat = self.service.create_conversation(
            self.user, 'gpt-5.6-terra', project_id=self.project.id
        )

        self.service._mark_task_ready(task)
        self.service._mark_task_ready(chat)

        task.refresh_from_db()
        chat.refresh_from_db()
        self.assertEqual(task.review_status, 'ready')
        self.assertEqual(chat.review_status, '')


class WorktreeMirrorSuppressionTests(GitRepoTestMixin, TestCase):
    """Worktree runs write disk only — never the ProjectFile mirror."""

    def setUp(self):
        self.user = User.objects.create_user(username='mirror', password='pw123456')
        self.repo = self._make_repo()
        self.project = Project.objects.create(
            user=self.user, name='P', project_path=self.repo, is_active=True
        )

    def _context(self, effective_root):
        return AgentContext(
            user_id=self.user.id,
            project_id=self.project.id,
            project_path=self.repo,
            effective_project_path=effective_root,
        )

    def test_get_project_repoints_at_worktree_and_suppresses_mirror(self):
        worktree = VersionControlService().create_task_worktree(
            self.repo, 5
        )['worktree_path']

        project = _get_project(self._context(worktree))

        self.assertEqual(project.project_path, worktree)
        self.assertTrue(getattr(project, '_suppress_db_mirror', False))
        # The DB row itself is untouched.
        self.project.refresh_from_db()
        self.assertEqual(self.project.project_path, self.repo)

    def test_get_project_keeps_canonical_runs_mirrored(self):
        project = _get_project(self._context(self.repo))
        self.assertEqual(project.project_path, self.repo)
        self.assertFalse(getattr(project, '_suppress_db_mirror', False))

    def test_worktree_edit_skips_the_db_mirror(self):
        worktree = VersionControlService().create_task_worktree(
            self.repo, 5
        )['worktree_path']
        project = _get_project(self._context(worktree))

        result = edit_file_impl(project, 'app.txt', 'hello', 'task variant')

        self.assertTrue(result['success'])
        with open(os.path.join(worktree, 'app.txt')) as f:
            self.assertEqual(f.read(), 'task variant')
        # Canonical disk and the mirror both untouched.
        with open(os.path.join(self.repo, 'app.txt')) as f:
            self.assertEqual(f.read(), 'hello')
        self.assertFalse(ProjectFile.objects.filter(project=self.project).exists())


class ReviewEndpointTests(GitRepoTestMixin, TestCase):
    """Accept merges + resyncs + cleans up; dismiss discards."""

    def setUp(self):
        self.user = User.objects.create_user(username='reviewer', password='pw123456')
        self.client.force_login(self.user)
        self.repo = self._make_repo()
        self.project = Project.objects.create(
            user=self.user, name='P', project_path=self.repo, is_active=True
        )

    def _task_with_worktree(self, review_status='ready'):
        task = AgentConversation.objects.create(
            user=self.user, model_name='gpt-5.6-terra', project_id=self.project.id,
            kind='task', review_status=review_status,
        )
        worktree = VersionControlService().create_task_worktree(
            self.repo, task.id
        )['worktree_path']
        task.worktree_path = worktree
        task.save(update_fields=['worktree_path'])
        return task, worktree

    def _accept(self, conversation):
        return self.client.post(reverse('conversation_accept', args=[conversation.id]))

    def _dismiss(self, conversation):
        return self.client.post(reverse('conversation_dismiss', args=[conversation.id]))

    def test_accept_merges_resyncs_and_removes_worktree(self):
        task, worktree = self._task_with_worktree()
        with open(os.path.join(worktree, 'feature.md'), 'w') as f:
            f.write('# built by the task')

        resp = self._accept(task)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {'status': 'accepted'})
        # Merged into canonical disk...
        with open(os.path.join(self.repo, 'feature.md')) as f:
            self.assertEqual(f.read(), '# built by the task')
        # ...and into the DB mirror (worktree runs skipped mirror writes).
        self.assertTrue(
            ProjectFile.objects.filter(project=self.project, path='feature.md').exists()
        )
        task.refresh_from_db()
        self.assertEqual(task.review_status, 'accepted')
        self.assertEqual(task.worktree_path, '')
        self.assertFalse(os.path.exists(worktree))

    def test_accept_conflict_returns_409_and_keeps_worktree(self):
        task, worktree = self._task_with_worktree()
        self._write_commit(self.repo, 'app.txt', 'canonical edit', 'canonical change')
        with open(os.path.join(worktree, 'app.txt'), 'w') as f:
            f.write('conflicting task edit')

        resp = self._accept(task)

        self.assertEqual(resp.status_code, 409)
        body = resp.json()
        self.assertEqual(body['error'], 'merge_conflict')
        self.assertIn('detail', body)
        task.refresh_from_db()
        self.assertEqual(task.review_status, 'ready')  # unchanged
        self.assertTrue(os.path.isdir(worktree))
        # Canonical tree left untouched (merge aborted).
        with open(os.path.join(self.repo, 'app.txt')) as f:
            self.assertEqual(f.read(), 'canonical edit')

    def test_accept_rejects_non_task(self):
        chat = AgentConversation.objects.create(
            user=self.user, model_name='gpt-5.6-terra', project_id=self.project.id
        )
        self.assertEqual(self._accept(chat).status_code, 400)

    def test_accept_rejects_task_without_worktree(self):
        task = AgentConversation.objects.create(
            user=self.user, model_name='gpt-5.6-terra', project_id=self.project.id,
            kind='task',
        )
        self.assertEqual(self._accept(task).status_code, 400)

    def test_accept_rejects_while_task_runs(self):
        task, _ = self._task_with_worktree()
        task.run_started_at = timezone.now()
        task.save(update_fields=['run_started_at'])
        resp = self._accept(task)
        self.assertEqual(resp.status_code, 409)
        self.assertEqual(resp.json()['detail'], 'agent_busy')

    def test_accept_rejects_while_canonical_run_live(self):
        task, _ = self._task_with_worktree()
        AgentConversation.objects.create(
            user=self.user, model_name='gpt-5.6-terra', project_id=self.project.id,
            kind='lead', run_started_at=timezone.now(),
        )
        resp = self._accept(task)
        self.assertEqual(resp.status_code, 409)

    def test_accept_after_canonical_restore_returns_409_stale_base(self):
        # The user restored the project to before this task's fork point;
        # accepting would silently resurrect the restored-away commits.
        commit_a = _git(self.repo, 'rev-parse', 'HEAD').stdout.strip()
        self._write_commit(self.repo, 'app.txt', 'version B', 'commit B')
        task, worktree = self._task_with_worktree()
        with open(os.path.join(worktree, 'feature.md'), 'w') as f:
            f.write('# built by the task')
        _git(self.repo, 'reset', '--hard', commit_a)

        resp = self._accept(task)

        self.assertEqual(resp.status_code, 409)
        body = resp.json()
        self.assertEqual(body['error'], 'stale_base')
        self.assertIn('detail', body)
        task.refresh_from_db()
        self.assertEqual(task.review_status, 'ready')  # unchanged
        self.assertTrue(os.path.isdir(worktree))
        # Canonical stayed restored, with none of B's content back.
        self.assertEqual(_git(self.repo, 'rev-parse', 'HEAD').stdout.strip(), commit_a)
        with open(os.path.join(self.repo, 'app.txt')) as f:
            self.assertEqual(f.read(), 'hello')

    def test_dismiss_discards_worktree(self):
        task, worktree = self._task_with_worktree()
        with open(os.path.join(worktree, 'feature.md'), 'w') as f:
            f.write('discarded work')

        resp = self._dismiss(task)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {'status': 'dismissed'})
        task.refresh_from_db()
        self.assertEqual(task.review_status, 'dismissed')
        self.assertEqual(task.worktree_path, '')
        self.assertFalse(os.path.exists(worktree))
        # Nothing leaked into the canonical tree.
        self.assertFalse(os.path.exists(os.path.join(self.repo, 'feature.md')))

    def test_dismiss_rejects_non_task(self):
        chat = AgentConversation.objects.create(
            user=self.user, model_name='gpt-5.6-terra', project_id=self.project.id
        )
        self.assertEqual(self._dismiss(chat).status_code, 400)

    def test_dismiss_rejects_while_task_runs(self):
        task, _ = self._task_with_worktree()
        task.run_started_at = timezone.now()
        task.save(update_fields=['run_started_at'])
        self.assertEqual(self._dismiss(task).status_code, 409)

    def test_dismiss_rejects_already_accepted_task(self):
        # 'accepted' is terminal: the worktree is already merged, so a stale
        # tab's dismiss must not relabel merged changes as discarded.
        task, _ = self._task_with_worktree()
        self.assertEqual(self._accept(task).status_code, 200)

        resp = self._dismiss(task)

        self.assertEqual(resp.status_code, 409)
        self.assertEqual(resp.json()['error'], 'already_accepted')
        task.refresh_from_db()
        self.assertEqual(task.review_status, 'accepted')

    def test_delete_conversation_removes_worktree(self):
        task, worktree = self._task_with_worktree()

        resp = self.client.delete(reverse('conversation_detail', args=[task.id]))

        self.assertEqual(resp.status_code, 204)
        self.assertFalse(os.path.exists(worktree))
        self.assertFalse(AgentConversation.objects.filter(id=task.id).exists())

    def test_delete_rejects_while_task_runs(self):
        # Deleting a running task would rip its worktree out from under the
        # live run; same agent_busy contract as accept/dismiss.
        task, worktree = self._task_with_worktree()
        task.run_started_at = timezone.now()
        task.save(update_fields=['run_started_at'])

        resp = self.client.delete(reverse('conversation_detail', args=[task.id]))

        self.assertEqual(resp.status_code, 409)
        self.assertEqual(resp.json()['detail'], 'agent_busy')
        self.assertTrue(os.path.isdir(worktree))
        self.assertTrue(AgentConversation.objects.filter(id=task.id).exists())
