"""
Tests for the ProjectManager app.

These focus on the logic that is safe and fast to exercise: the Project model
(slug/path generation, validation, soft vs hard delete), the create serializer,
the management service, and the REST API. The heavy filesystem/subprocess work
performed by ProjectCreationService is mocked out so the suite stays fast and
does not pollute the repository or depend on npm/Django scaffolding.
"""

import importlib
import os
import shutil
import tempfile
import threading
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase, TransactionTestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from apps.Imagi.ProjectManager.models import Project
from apps.Imagi.ProjectManager.services.project_management_service import (
    ProjectManagementService,
)

User = get_user_model()

# A business description long enough to pass the create serializer's
# MIN_DESCRIPTION_LENGTH validation (the description seeds the initial AI build).
VALID_DESCRIPTION = (
    'A subscription coffee roastery for remote workers. Customers are '
    'home-office professionals; we sell direct online with monthly plans.'
)

# A throwaway PROJECTS_ROOT so the services' os.makedirs() calls never touch
# the real repository. Created once for the module, removed at teardown.
_TMP_PROJECTS_ROOT = tempfile.mkdtemp(prefix='imagi_pm_tests_')


def tearDownModule():
    shutil.rmtree(_TMP_PROJECTS_ROOT, ignore_errors=True)


@override_settings(PROJECTS_ROOT=_TMP_PROJECTS_ROOT)
class ProjectModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='owner', password='pw123456')
        self.other = User.objects.create_user(username='other', password='pw123456')

    def test_slug_is_generated_from_name(self):
        project = Project.objects.create(user=self.user, name='My Cool App')
        self.assertEqual(project.slug, 'my-cool-app')

    def test_slug_is_made_unique(self):
        # The same name is only unique per-user, but slugs are unique globally,
        # so two different users picking the same name still get distinct slugs.
        first = Project.objects.create(user=self.user, name='Duplicate Name')
        second = Project.objects.create(user=self.other, name='Duplicate Name')
        self.assertEqual(first.slug, 'duplicate-name')
        self.assertEqual(second.slug, 'duplicate-name-1')

    def test_project_path_is_generated(self):
        project = Project.objects.create(user=self.user, name='Path App')
        self.assertTrue(project.project_path)
        self.assertIn(self.user.username, project.project_path)
        self.assertIn(project.slug, project.project_path)

    def test_generated_directory_is_stored_relative(self):
        # The whole point of project_dir: nothing machine-specific on the row.
        project = Project.objects.create(user=self.user, name='Relative App')
        self.assertEqual(
            project.project_dir, os.path.join(self.user.username, project.slug)
        )
        self.assertFalse(os.path.isabs(project.project_dir))

    def test_project_path_follows_the_configured_root(self):
        # A row written under one root resolves under whichever root is
        # configured when it is read — the portability this replaced absolute
        # paths to get.
        project = Project.objects.create(user=self.user, name='Portable App')
        stored = project.project_dir

        with override_settings(PROJECTS_ROOT='/somewhere/else'):
            project.refresh_from_db()
            self.assertEqual(
                project.project_path, os.path.join('/somewhere/else', stored)
            )

    def test_assigning_a_path_under_the_root_stores_it_relative(self):
        with override_settings(PROJECTS_ROOT='/roots/projects'):
            project = Project(user=self.user, name='Assigned App')
            project.project_path = '/roots/projects/owner/assigned-app'
            self.assertEqual(project.project_dir, 'owner/assigned-app')
            self.assertEqual(
                project.project_path, '/roots/projects/owner/assigned-app'
            )

    def test_a_path_outside_the_root_is_kept_absolute(self):
        # Tests and PROJECTS_ROOT overrides point projects at temp directories;
        # those cannot be expressed relative to the root and must survive
        # round-tripping unchanged.
        with tempfile.TemporaryDirectory() as tmp:
            project = Project.objects.create(
                user=self.user, name='Outside App', project_path=tmp
            )
            project.refresh_from_db()
            self.assertEqual(project.project_dir, tmp)
            self.assertEqual(project.project_path, tmp)

    def test_blank_path_round_trips_as_empty(self):
        project = Project(user=self.user, name='Empty App')
        project.project_path = ''
        self.assertEqual(project.project_dir, '')
        self.assertEqual(project.project_path, '')


    def test_clean_rejects_short_names(self):
        project = Project(user=self.user, name='ab')
        with self.assertRaises(ValidationError):
            project.clean()

    def test_soft_delete_marks_inactive(self):
        project = Project.objects.create(user=self.user, name='Soft Delete')
        project.delete()
        project.refresh_from_db()
        self.assertFalse(project.is_active)
        self.assertTrue(Project.objects.filter(id=project.id).exists())

    def test_hard_delete_removes_row(self):
        project = Project.objects.create(user=self.user, name='Hard Delete')
        pid = project.id
        project.delete(hard_delete=True)
        self.assertFalse(Project.objects.filter(id=pid).exists())


class ProjectDirMigrationTests(TestCase):
    """The 0005 data step that converted stored absolute paths to relative.

    Exercised directly rather than through the migration executor: the point
    worth pinning is the path arithmetic, which had to work for rows written by
    a *different* checkout than the one running the migration.
    """

    def _convert(self, stored):
        # importlib because the module name starts with a digit.
        mod = importlib.import_module(
            'apps.Imagi.ProjectManager.migrations.'
            '0005_project_dir_relative_to_projects_root'
        )
        marker = stored.find(mod._ROOT_MARKER)
        if marker == -1:
            return stored
        return stored[marker + len(mod._ROOT_MARKER):]

    def test_path_from_another_checkout_becomes_relative(self):
        # The case that motivated the change: the row was written by a git
        # worktree that is not the one running the migration, so relpath()
        # against the local root would have produced '../..' escapes.
        stored = (
            '/Users/dev/proj/.claude/worktrees/some-branch/backend/django/'
            'apps/Imagi/Build/imagi_projects/9/My_App_20260731145400'
        )
        self.assertEqual(self._convert(stored), '9/My_App_20260731145400')

    def test_path_under_the_production_root_becomes_relative(self):
        stored = '/home/imagi/.imagi/projects/imagi_projects/4/Shop_20260101000000'
        self.assertEqual(self._convert(stored), '4/Shop_20260101000000')

    def test_path_without_the_marker_is_left_absolute(self):
        # Temp directories from old test runs have no imagi_projects segment;
        # they stay absolute and the model returns them unchanged.
        stored = '/var/folders/sc/T/exploit_a1k9cxnt/project'
        self.assertEqual(self._convert(stored), stored)


@override_settings(PROJECTS_ROOT=_TMP_PROJECTS_ROOT)
class ProjectCreateSerializerTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='owner', password='pw123456')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_duplicate_active_name_rejected(self):
        Project.objects.create(user=self.user, name='Existing Project')
        from apps.Imagi.ProjectManager.api.serializers import (
            ProjectCreateSerializer,
        )

        request = type('R', (), {'user': self.user})()
        serializer = ProjectCreateSerializer(
            data={'name': 'Existing Project', 'description': VALID_DESCRIPTION},
            context={'request': request},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)

    def test_missing_description_rejected(self):
        from apps.Imagi.ProjectManager.api.serializers import (
            ProjectCreateSerializer,
        )

        request = type('R', (), {'user': self.user})()
        serializer = ProjectCreateSerializer(
            data={'name': 'No Description'}, context={'request': request}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('description', serializer.errors)

    def test_short_description_rejected(self):
        from apps.Imagi.ProjectManager.api.serializers import (
            ProjectCreateSerializer,
        )

        request = type('R', (), {'user': self.user})()
        serializer = ProjectCreateSerializer(
            data={'name': 'Short Description', 'description': 'too short'},
            context={'request': request},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('description', serializer.errors)


@override_settings(PROJECTS_ROOT=_TMP_PROJECTS_ROOT)
class ProjectManagementServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='owner', password='pw123456')
        self.other = User.objects.create_user(username='other', password='pw123456')
        self.service = ProjectManagementService(self.user)

    def test_get_active_projects_scoped_to_user(self):
        mine = Project.objects.create(user=self.user, name='Mine')
        Project.objects.create(user=self.other, name='Theirs')
        inactive = Project.objects.create(user=self.user, name='Archived')
        inactive.delete()  # soft delete
        active = list(self.service.get_active_projects())
        self.assertEqual(active, [mine])

    def test_get_project_returns_none_for_other_users_project(self):
        theirs = Project.objects.create(user=self.other, name='Theirs')
        self.assertIsNone(self.service.get_project(theirs.id))

    @patch.object(ProjectManagementService, '_stop_project_server_and_cleanup_files')
    @patch.object(ProjectManagementService, '_delete_project_directory')
    def test_delete_project_hard_deletes_row(self, mock_dir, mock_pid):
        project = Project.objects.create(user=self.user, name='To Delete')
        pid = project.id
        result = self.service.delete_project(project)
        self.assertTrue(result['success'])
        self.assertFalse(Project.objects.filter(id=pid).exists())

    @patch.object(ProjectManagementService, '_delete_project_directory')
    def test_delete_project_removes_preview_sidecar_files(self, mock_dir):
        # PreviewService writes these next to the project directory, so they
        # survive the rmtree and have to be removed explicitly.
        project = Project.objects.create(user=self.user, name='Saturn')
        # A PID no live process holds: cleanup should skip the kill but still
        # remove the file.
        contents = {
            '_backend.log': 'Starting development server...',
            '_frontend.log': 'VITE ready in 300 ms',
            '_preview_ports.json': '{"frontend_port": 5174, "backend_port": 8080}',
            '_backend.pid': '999999',
            '_frontend.pid': '999999',
        }
        sidecars = []
        for suffix, body in contents.items():
            path = os.path.join(self.service.base_directory, f'Saturn{suffix}')
            with open(path, 'w') as f:
                f.write(body)
            sidecars.append(path)

        self.service.delete_project(project)

        for path in sidecars:
            self.assertFalse(os.path.exists(path), f'{path} was left behind')

    @patch.object(ProjectManagementService, '_delete_project_directory')
    def test_delete_project_removes_legacy_named_sidecar_files(self, mock_dir):
        # Older releases wrote these under a sanitized spelling of the name.
        project = Project.objects.create(user=self.user, name='My App')
        legacy = [
            os.path.join(self.service.base_directory, name)
            for name in ('My_App_server.pid', 'My_App_backend.log')
        ]
        for path in legacy:
            with open(path, 'w') as f:
                f.write('999999')

        self.service.delete_project(project)

        for path in legacy:
            self.assertFalse(os.path.exists(path), f'{path} was left behind')


@override_settings(PROJECTS_ROOT=_TMP_PROJECTS_ROOT)
class ProjectManagerAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='owner', password='pw123456')
        self.other = User.objects.create_user(username='other', password='pw123456')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_list_requires_authentication(self):
        self.client.credentials()
        resp = self.client.get(reverse('project_manager:project-list'))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_returns_only_own_active_projects(self):
        Project.objects.create(user=self.user, name='Mine One')
        Project.objects.create(user=self.other, name='Not Mine')
        archived = Project.objects.create(user=self.user, name='Archived')
        archived.delete()
        resp = self.client.get(reverse('project_manager:project-list'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # The list endpoint is paginated, so projects live under "results".
        names = [p['name'] for p in resp.data['results']]
        self.assertEqual(names, ['Mine One'])

    @patch('apps.Imagi.ProjectManager.api.views.start_initial_build')
    @patch(
        'apps.Imagi.ProjectManager.api.views.ProjectCreationService.create_project'
    )
    def test_create_project(self, mock_create, mock_build):
        mock_create.side_effect = lambda project: project
        resp = self.client.post(
            reverse('project_manager:project-create'),
            {'name': 'Brand New App', 'description': VALID_DESCRIPTION},
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['name'], 'Brand New App')
        project = Project.objects.get(user=self.user, name='Brand New App')
        self.assertEqual(project.description, VALID_DESCRIPTION)
        mock_create.assert_called_once()
        # Creation must hand the new project off to the initial AI build.
        mock_build.assert_called_once()
        self.assertEqual(mock_build.call_args.args[0].pk, project.pk)
        self.assertEqual(mock_build.call_args.args[1], self.user)

    @patch(
        'apps.Imagi.ProjectManager.api.views.start_initial_build',
        side_effect=RuntimeError('agent unavailable'),
    )
    @patch(
        'apps.Imagi.ProjectManager.api.views.ProjectCreationService.create_project'
    )
    def test_create_succeeds_when_initial_build_kickoff_fails(self, mock_create, mock_build):
        mock_create.side_effect = lambda project: project
        resp = self.client.post(
            reverse('project_manager:project-create'),
            {'name': 'Resilient App', 'description': VALID_DESCRIPTION},
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_create_duplicate_name_returns_400(self):
        Project.objects.create(user=self.user, name='Taken Name')
        resp = self.client.post(
            reverse('project_manager:project-create'),
            {'name': 'Taken Name', 'description': VALID_DESCRIPTION},
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_without_description_returns_400(self):
        resp = self.client.post(
            reverse('project_manager:project-create'), {'name': 'No Description'}
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('description', resp.data)

    @patch(
        'apps.Imagi.ProjectManager.api.views.ProjectCreationService.create_project'
    )
    def test_create_failure_rolls_back_and_returns_safe_500(self, mock_create):
        # A failure during file generation must roll back the half-created
        # project and return a generic 500 (no leaked internal error string).
        mock_create.side_effect = Exception('secret path /srv/imagi/secret')
        resp = self.client.post(
            reverse('project_manager:project-create'),
            {'name': 'Rollback Me', 'description': VALID_DESCRIPTION},
        )
        self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertNotIn('secret path', str(resp.data))
        self.assertFalse(
            Project.objects.filter(
                user=self.user, name='Rollback Me', is_active=True
            ).exists()
        )

    def test_initialize_missing_project_returns_404(self):
        # get_project() raises NotFound; it must surface as a 404, not be
        # swallowed into a 500 by the view's outer exception handler.
        resp = self.client.post(
            reverse('project_manager:project-initialize', args=[99999])
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_detail_retrieve_own_project(self):
        project = Project.objects.create(user=self.user, name='Detail App')
        resp = self.client.get(
            reverse('project_manager:project-detail', args=[project.id])
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['name'], 'Detail App')

    def test_detail_of_other_users_project_returns_404(self):
        project = Project.objects.create(user=self.other, name='Their App')
        resp = self.client.get(
            reverse('project_manager:project-detail', args=[project.id])
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    @patch.object(ProjectManagementService, '_stop_project_server_and_cleanup_files')
    @patch.object(ProjectManagementService, '_delete_project_directory')
    def test_delete_project_endpoint(self, mock_dir, mock_pid):
        project = Project.objects.create(user=self.user, name='Delete Me')
        resp = self.client.delete(
            reverse('project_manager:project-delete', args=[project.id])
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Project.objects.filter(id=project.id).exists())

    def test_delete_missing_project_returns_404(self):
        resp = self.client.delete(
            reverse('project_manager:project-delete', args=[99999])
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_status_endpoint(self):
        project = Project.objects.create(user=self.user, name='Status App')
        resp = self.client.get(
            reverse('project_manager:project-status', args=[project.id])
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['name'], 'Status App')
        self.assertFalse(resp.data['is_initialized'])

    @patch(
        'apps.Imagi.ProjectManager.api.views.ProjectCreationService.initialize_project'
    )
    def test_initialize_endpoint(self, mock_init):
        project = Project.objects.create(user=self.user, name='Init App')

        def _mark_initialized(proj):
            proj.is_initialized = True
            proj.save()
            return {'success': True}

        mock_init.side_effect = _mark_initialized
        resp = self.client.post(
            reverse('project_manager:project-initialize', args=[project.id])
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data['success'])
        project.refresh_from_db()
        self.assertTrue(project.is_initialized)


@override_settings(PROJECTS_ROOT=_TMP_PROJECTS_ROOT)
class InitialBuildServiceTests(TransactionTestCase):
    """Tests for the initial AI build kicked off at project creation.

    A TransactionTestCase rather than a TestCase because the build fans its
    pages out across worker threads: those threads open their own database
    connections, which cannot see data still sitting in an uncommitted test
    transaction.

    Most of these cover per-page behaviour (repairs, deadlines, what does and
    does not get merged), so they pin the build to the home page alone and stay
    deterministic. The fan-out itself is covered by ParallelInitialBuildTests.
    """

    def setUp(self):
        self.user = User.objects.create_user(username='owner', password='pw123456')
        self.project = Project.objects.create(
            user=self.user, name='Beanline', description=VALID_DESCRIPTION
        )

    def test_skips_without_api_key(self):
        from apps.Imagi.ProjectManager.services import initial_build_service

        with patch(
            'apps.Imagi.Build.services.base_agent.OPENAI_API_KEY', None
        ):
            started = initial_build_service.start_initial_build(self.project, self.user)
        self.assertFalse(started)
        self.project.refresh_from_db()
        self.assertEqual(self.project.generation_status, 'pending')

    def test_marks_generating_and_spawns_thread(self):
        from apps.Imagi.ProjectManager.services import initial_build_service

        with patch(
            'apps.Imagi.Build.services.base_agent.OPENAI_API_KEY', 'test-key'
        ), patch.object(initial_build_service.threading, 'Thread') as mock_thread:
            started = initial_build_service.start_initial_build(self.project, self.user)
        self.assertTrue(started)
        self.project.refresh_from_db()
        self.assertEqual(self.project.generation_status, 'generating')
        mock_thread.assert_called_once()
        mock_thread.return_value.start.assert_called_once()

    def _run_build(self, outcomes, unresolved=(), pages=('home',)):
        """Drive a full initial build with the agent run itself stubbed out.

        Everything around the model call is real — the lead and task
        conversations, their messages, and the applied/not-applied decision
        read back off the task — so these tests exercise the actual wiring.

        Args:
            outcomes: one entry per expected run. 'accept' stands in for a run
                whose worktree merged cleanly (the real finalization sets
                review_status='accepted'), 'leave' for one that finished
                without being applied, and 'fail' for a failed run.
            unresolved: dangling imports the integrity check should report on
                an unapplied worktree, which is what triggers a repair run.
            pages: which pages the build covers. Defaults to home alone, so a
                test about repair or deadline behaviour drives one subagent and
                the run order stays deterministic.

        Returns the kwargs of every process() call made.
        """
        from apps.Imagi.ProjectManager.services import initial_build_service
        from apps.Imagi.Build.models import AgentConversation
        from apps.Imagi.Build.services.base_agent import ImagiAgentService

        calls = []
        pending = list(outcomes)

        def fake_process(_self, **kwargs):
            calls.append(kwargs)
            outcome = pending.pop(0) if pending else 'leave'
            if outcome == 'fail':
                return {'success': False, 'error': 'model error'}
            if outcome == 'accept':
                AgentConversation.objects.filter(
                    id=kwargs['conversation_id']
                ).update(review_status='accepted')
            else:
                AgentConversation.objects.filter(
                    id=kwargs['conversation_id']
                ).update(review_status='ready')
            return {'success': True, 'files_changed': []}

        builder = {**settings.IMAGI_BUILDER, 'INITIAL_BUILD_PAGES': list(pages)}
        with override_settings(IMAGI_BUILDER=builder), patch.object(
            ImagiAgentService, 'process', fake_process
        ), patch(
            'apps.Imagi.Build.services.frontend_integrity.find_unresolved_imports',
            return_value=list(unresolved),
        ):
            initial_build_service._run_initial_build(self.project.pk, self.user.pk)
        return calls

    def test_applied_build_marks_completed_and_prompts_with_business_details(self):
        calls = self._run_build(['accept'])

        self.project.refresh_from_db()
        self.assertEqual(self.project.generation_status, 'completed')
        self.assertIsNotNone(self.project.last_generated_at)

        # The prompt must carry the business name and description into the agent.
        self.assertEqual(len(calls), 1)
        prompt = calls[0]['user_input']
        self.assertIn('Beanline', prompt)
        self.assertIn('coffee roastery', prompt)

        # The run must be bounded by the initial-build turn and cost caps.
        self.assertEqual(calls[0]['cost_budget_usd'],
                         settings.IMAGI_BUILDER['INITIAL_BUILD_COST_BUDGET_USD'])
        self.assertEqual(calls[0]['max_turns'],
                         settings.IMAGI_BUILDER['INITIAL_BUILD_MAX_TURNS'])

    def test_build_runs_as_a_subagent_dispatched_from_the_main_thread(self):
        from apps.Imagi.Build.models import AgentConversation
        from apps.Imagi.Build.services.coding_agent import INITIAL_BUILD_INSTRUCTIONS

        calls = self._run_build(['accept'])

        lead = AgentConversation.objects.get(
            user=self.user, project_id=self.project.pk, kind='lead'
        )
        task = AgentConversation.objects.get(
            user=self.user, project_id=self.project.pk, kind='task'
        )
        # The build is an ordinary background task of the project's main
        # thread, so it inherits the worktree isolation and review lifecycle
        # every dispatched task has.
        self.assertEqual(task.parent_id, lead.id)
        self.assertEqual(task.title, 'Initial build — home page')
        self.assertEqual(task.system_prompt.content, INITIAL_BUILD_INSTRUCTIONS)
        self.assertEqual(calls[0]['conversation_id'], task.id)

        # The main thread opens with the founder's brief and a one-line
        # acknowledgement linking to the subagent's thread.
        messages = list(lead.messages.order_by('created_at'))
        self.assertEqual([m.role for m in messages], ['user', 'assistant'])
        self.assertIn('Beanline', messages[0].content)
        self.assertEqual(
            messages[1].metadata['dispatched_tasks'],
            [{'conversation_id': task.id, 'title': 'Initial build — home page'}],
        )

    def test_build_runs_on_the_configured_initial_build_model(self):
        from apps.Imagi.Build.models import AgentConversation

        self._run_build(['accept'])

        task = AgentConversation.objects.get(
            user=self.user, project_id=self.project.pk, kind='task'
        )
        self.assertEqual(
            task.model_name, settings.IMAGI_BUILDER['INITIAL_BUILD_MODEL']
        )

    def test_reuses_an_existing_main_thread(self):
        from apps.Imagi.Build.models import AgentConversation
        from apps.Imagi.Build.services.base_agent import ImagiAgentService

        existing = ImagiAgentService().create_conversation(
            self.user, 'gpt-5.6-terra', project_id=self.project.pk, kind='lead'
        )
        self._run_build(['accept'])

        # A second live lead would violate the single-lead invariant.
        self.assertEqual(
            AgentConversation.objects.filter(
                user=self.user, project_id=self.project.pk, kind='lead'
            ).count(),
            1,
        )
        task = AgentConversation.objects.get(
            user=self.user, project_id=self.project.pk, kind='task'
        )
        self.assertEqual(task.parent_id, existing.id)

    def test_run_failure_marks_failed(self):
        self._run_build(['fail'])
        self.project.refresh_from_db()
        self.assertEqual(self.project.generation_status, 'failed')

    def test_design_preferences_flow_into_prompt(self):
        self.project.design_preferences = 'Warm, earthy palette; minimal, lots of whitespace'
        self.project.save(update_fields=['design_preferences'])

        calls = self._run_build(['accept'])

        self.assertIn('Warm, earthy palette', calls[0]['user_input'])

    def test_dangling_imports_trigger_a_repair_run_before_applying(self):
        # A build cut short by its cost cap can leave a page importing a
        # component it never wrote. That must not reach the project: the
        # subagent gets a repair run naming the broken references first.
        calls = self._run_build(
            ['leave', 'accept'],
            unresolved=[{
                'file': 'frontend/vuejs/src/apps/home/views/HomeView.vue',
                'import': '@/shared/components/SiteHeader.vue',
            }],
        )

        self.assertEqual(len(calls), 2)
        repair_prompt = calls[1]['user_input']
        self.assertIn('@/shared/components/SiteHeader.vue', repair_prompt)
        self.assertIn('HomeView.vue', repair_prompt)
        # Repairs run on their own tighter budget.
        self.assertEqual(calls[1]['cost_budget_usd'],
                         settings.IMAGI_BUILDER['INITIAL_BUILD_REPAIR_COST_BUDGET_USD'])
        self.assertEqual(calls[1]['max_turns'],
                         settings.IMAGI_BUILDER['INITIAL_BUILD_REPAIR_MAX_TURNS'])

        self.project.refresh_from_db()
        self.assertEqual(self.project.generation_status, 'completed')

    def test_unrepairable_build_is_not_applied(self):
        # After the repair budget is spent the build is abandoned rather than
        # merged, so the project keeps the scaffold its preview can serve.
        attempts = settings.IMAGI_BUILDER['INITIAL_BUILD_REPAIR_ATTEMPTS']
        calls = self._run_build(
            ['leave'] * (attempts + 1),
            unresolved=[{
                'file': 'frontend/vuejs/src/apps/home/views/HomeView.vue',
                'import': '@/shared/components/SiteHeader.vue',
            }],
        )

        self.assertEqual(len(calls), attempts + 1)
        self.project.refresh_from_db()
        self.assertEqual(self.project.generation_status, 'failed')

    def test_unapplied_build_without_dangling_imports_is_not_retried(self):
        # A merge conflict or git failure is not something another run fixes.
        calls = self._run_build(['leave'], unresolved=[])
        self.assertEqual(len(calls), 1)
        self.project.refresh_from_db()
        self.assertEqual(self.project.generation_status, 'failed')

    def test_a_rewritten_app_router_triggers_a_repair_run(self):
        # The worst failure mode seen live: the build replaced the home app's
        # route module with its own createRouter, which compiles and builds
        # cleanly but leaves every page — including home — 404ing. It must be
        # repaired before the build can be applied.
        from apps.Imagi.ProjectManager.services import initial_build_service

        router_problem = [{
            'file': 'frontend/vuejs/src/apps/home/router/index.ts',
            'detail': "calls createRouter(), but an app router must only export a 'routes' array",
        }]
        with patch(
            'apps.Imagi.Build.services.frontend_integrity.find_router_contract_problems',
            return_value=router_problem,
        ):
            calls = self._run_build(['leave', 'accept'], unresolved=[])

        self.assertEqual(len(calls), 2, 'a broken app router was not repaired')
        repair_prompt = calls[1]['user_input']
        self.assertIn('router/index.ts', repair_prompt)
        self.assertIn('createRouter', repair_prompt)
        self.assertIn('export { routes }', repair_prompt)
        self.project.refresh_from_db()
        self.assertEqual(self.project.generation_status, 'completed')

    def test_a_home_page_that_dropped_its_auth_links_is_repaired(self):
        # The build compiles and looks finished, but nothing on it reaches the
        # sign-in or register pages the project already ships.
        with patch(
            'apps.Imagi.Build.services.frontend_integrity.find_auth_link_problems',
            return_value=[{'path': '/auth/register'}],
        ):
            calls = self._run_build(['leave', 'accept'], unresolved=[])

        self.assertEqual(len(calls), 2, 'a home page with no way into auth was shipped as-is')
        repair_prompt = calls[1]['user_input']
        self.assertIn('/auth/register', repair_prompt)
        self.assertIn('/auth/signin', repair_prompt)
        self.project.refresh_from_db()
        self.assertEqual(self.project.generation_status, 'completed')

    def test_an_unrepaired_auth_link_still_ships_the_page(self):
        # Unlike a dangling import, this build loads — it is just harder to
        # sign into. A tailored page beats handing the founder the scaffold,
        # so once the repairs are spent it is merged anyway.
        from apps.Imagi.Build import api as build_api

        attempts = settings.IMAGI_BUILDER['INITIAL_BUILD_REPAIR_ATTEMPTS']
        with patch(
            'apps.Imagi.Build.services.frontend_integrity.find_auth_link_problems',
            return_value=[{'path': '/auth/register'}],
        ), patch.object(
            build_api.views, '_apply_task_worktree', return_value={'ok': True}
        ) as apply_worktree:
            calls = self._run_build(['leave'] * (attempts + 1), unresolved=[])

        self.assertEqual(len(calls), attempts + 1)
        apply_worktree.assert_called_once()
        self.project.refresh_from_db()
        self.assertEqual(self.project.generation_status, 'completed')

    def test_a_dangling_import_alongside_it_is_still_discarded(self):
        # The soft treatment is only for the auth links. A build that does not
        # load is abandoned however it got there.
        from apps.Imagi.Build import api as build_api

        attempts = settings.IMAGI_BUILDER['INITIAL_BUILD_REPAIR_ATTEMPTS']
        with patch(
            'apps.Imagi.Build.services.frontend_integrity.find_auth_link_problems',
            return_value=[{'path': '/auth/register'}],
        ), patch.object(
            build_api.views, '_apply_task_worktree', return_value={'ok': True}
        ) as apply_worktree:
            self._run_build(
                ['leave'] * (attempts + 1),
                unresolved=[{
                    'file': 'frontend/vuejs/src/apps/home/views/HomeView.vue',
                    'import': '@/shared/components/SiteHeader.vue',
                }],
            )

        apply_worktree.assert_not_called()
        self.project.refresh_from_db()
        self.assertEqual(self.project.generation_status, 'failed')

    def test_repair_prompt_covers_imports_and_routers_together(self):
        from apps.Imagi.ProjectManager.services.initial_build_service import (
            build_repair_prompt,
        )

        prompt = build_repair_prompt(
            [{'file': 'HomeView.vue', 'import': '/images/hero.jpg'}],
            [{'file': 'router/index.ts', 'detail': 'calls createRouter()'}],
        )
        self.assertIn('/images/hero.jpg', prompt)
        self.assertIn('router/index.ts', prompt)
        # An invented image must be removed, not "created properly" — the
        # project has no image assets and the agent cannot make binaries.
        self.assertIn('inline <svg>', prompt)

    def test_every_run_shares_one_wall_clock_deadline(self):
        # The founder's wait is what is being bounded, so a repair must eat
        # into the same budget as the build — not restart it. A per-run budget
        # would let one slow build plus two repairs run three times as long as
        # the configured limit.
        calls = self._run_build(
            ['leave', 'accept'],
            unresolved=[{
                'file': 'frontend/vuejs/src/apps/home/views/HomeView.vue',
                'import': '@/shared/components/SiteHeader.vue',
            }],
        )

        self.assertEqual(len(calls), 2)
        deadlines = {call['deadline_at'] for call in calls}
        self.assertEqual(len(deadlines), 1, 'each run got its own deadline')
        self.assertIsNotNone(calls[0]['deadline_at'])

    def test_deadline_is_the_configured_time_budget_away(self):
        from apps.Imagi.ProjectManager.services import initial_build_service

        with patch.object(initial_build_service.time, 'monotonic', return_value=1000.0):
            calls = self._run_build(['accept'])

        self.assertEqual(
            calls[0]['deadline_at'],
            1000.0 + settings.IMAGI_BUILDER['INITIAL_BUILD_TIME_BUDGET_S'],
        )

    def test_repair_is_skipped_when_too_little_time_remains(self):
        # Starting a repair that will be killed mid-edit tends to leave more
        # dangling references than it fixes, so a page with no time left keeps
        # its scaffold instead.
        #
        # Driven through _build_and_apply with an all-but-expired deadline
        # rather than by faking the clock: time.monotonic is module-global, so
        # patching it also feeds Django's own connection bookkeeping and the
        # scripted readings stop lining up with this code's.
        import time as real_time

        from apps.Imagi.Build.models import AgentConversation
        from apps.Imagi.ProjectManager.services import initial_build_service

        min_repair = settings.IMAGI_BUILDER['INITIAL_BUILD_MIN_REPAIR_SECONDS']
        task = AgentConversation.objects.create(
            user=self.user,
            model_name='gpt-5.6-terra',
            project_id=self.project.pk,
            mode='agent',
            title='Initial build — home page',
            kind='task',
            review_status='active',
        )

        calls = []

        class FakeService:
            def process(self, **kwargs):
                calls.append(kwargs)
                AgentConversation.objects.filter(id=task.id).update(
                    review_status='ready'
                )
                return {'success': True, 'files_changed': []}

        with patch(
            'apps.Imagi.Build.services.frontend_integrity.find_unresolved_imports',
            return_value=[{
                'file': 'frontend/vuejs/src/apps/home/views/HomeView.vue',
                'import': '@/shared/components/SiteHeader.vue',
            }],
        ):
            applied = initial_build_service._build_and_apply(
                FakeService(),
                task,
                self.user,
                self.project.pk,
                'brief',
                settings.IMAGI_BUILDER,
                deadline_at=real_time.monotonic() + (min_repair / 2),
            )

        self.assertEqual(len(calls), 1, 'a repair ran with no time budget left')
        self.assertFalse(applied)


class ParallelInitialBuildTests(TransactionTestCase):
    """The first build fans out across pages instead of writing just one.

    A sequential build can only produce one page inside the founder's
    half-minute wait. Dispatching a subagent per page spends that same half
    minute on all of them at once — which only works if the pages stay
    genuinely independent: one file each, one deadline for the lot, and no page
    able to take another down with it.
    """

    def setUp(self):
        self.user = User.objects.create_user(username='owner', password='pw123456')
        self.project = Project.objects.create(
            user=self.user, name='Beanline', description=VALID_DESCRIPTION
        )

    def _run(self, outcome_by_slug=None):
        """Run a full three-page build, stubbing out only the model call.

        outcome_by_slug maps a page slug to 'accept' (its worktree merged),
        'leave' (finished but unmerged) or 'fail' (the run errored); anything
        unnamed accepts. Returns the process() kwargs keyed by page slug.
        """
        from apps.Imagi.ProjectManager.services import initial_build_service
        from apps.Imagi.Build.models import AgentConversation
        from apps.Imagi.Build.services.base_agent import ImagiAgentService

        outcome_by_slug = outcome_by_slug or {}
        calls = {}

        def slug_of(conversation_id):
            title = AgentConversation.objects.get(id=conversation_id).title
            return title.rsplit('—', 1)[-1].strip().split(' ')[0]

        def fake_process(_self, **kwargs):
            slug = slug_of(kwargs['conversation_id'])
            calls.setdefault(slug, []).append(kwargs)
            outcome = outcome_by_slug.get(slug, 'accept')
            if outcome == 'fail':
                return {'success': False, 'error': 'model error'}
            AgentConversation.objects.filter(id=kwargs['conversation_id']).update(
                review_status='accepted' if outcome == 'accept' else 'ready'
            )
            return {'success': True, 'files_changed': []}

        with patch.object(ImagiAgentService, 'process', fake_process), patch(
            'apps.Imagi.Build.services.frontend_integrity.find_unresolved_imports',
            return_value=[],
        ):
            initial_build_service._run_initial_build(self.project.pk, self.user.pk)
        return calls

    def test_every_page_gets_its_own_subagent_and_its_own_file(self):
        from apps.Imagi.ProjectManager.services.initial_build_service import PAGE_BRIEFS

        calls = self._run()

        self.assertEqual(set(calls), {'home', 'about', 'contact'})
        # Each subagent is told to rewrite its own view and no other.
        for page in PAGE_BRIEFS:
            prompt = calls[page.slug][0]['user_input']
            self.assertIn(page.view_path, prompt)
            for other in PAGE_BRIEFS:
                if other.slug != page.slug:
                    self.assertNotIn(other.view_path, prompt)

    def test_no_two_pages_are_given_the_same_file(self):
        # The merge-safety invariant: the three worktrees are merged one after
        # another, so two agents writing the same path would conflict and lose
        # somebody's page.
        from apps.Imagi.ProjectManager.services.initial_build_service import PAGE_BRIEFS

        paths = [p.view_path for p in PAGE_BRIEFS]
        self.assertEqual(len(paths), len(set(paths)))

    def test_pages_run_against_one_shared_deadline(self):
        # The founder waits for the slowest page, not the sum of all three, so
        # the clock has to start once for the whole build rather than per page.
        calls = self._run()

        deadlines = {
            call['deadline_at'] for runs in calls.values() for call in runs
        }
        self.assertEqual(len(deadlines), 1, 'each page got its own deadline')
        self.assertIsNotNone(next(iter(deadlines)))

    def test_all_three_subagents_are_dispatched_from_the_one_main_thread(self):
        from apps.Imagi.Build.models import AgentConversation

        self._run()

        leads = AgentConversation.objects.filter(
            user=self.user, project_id=self.project.pk, kind='lead'
        )
        self.assertEqual(leads.count(), 1)
        lead = leads.get()
        tasks = AgentConversation.objects.filter(
            user=self.user, project_id=self.project.pk, kind='task'
        )
        self.assertEqual(tasks.count(), 3)
        self.assertTrue(all(t.parent_id == lead.id for t in tasks))

        # The thread opens with the founder's brief and one acknowledgement
        # carrying a link to every subagent thread it started.
        messages = list(lead.messages.order_by('created_at'))
        self.assertEqual([m.role for m in messages], ['user', 'assistant'])
        self.assertIn('Beanline', messages[0].content)
        dispatched = messages[1].metadata['dispatched_tasks']
        self.assertEqual(
            {d['conversation_id'] for d in dispatched},
            set(tasks.values_list('id', flat=True)),
        )

    def test_a_page_that_fails_does_not_stop_its_siblings(self):
        # Pages stand alone: one agent erroring out must not cost the founder
        # the other two, and the build still counts as completed.
        calls = self._run({'about': 'fail'})

        self.assertEqual(set(calls), {'home', 'about', 'contact'})
        self.project.refresh_from_db()
        self.assertEqual(self.project.generation_status, 'completed')

    def test_a_page_left_unmerged_does_not_stop_its_siblings(self):
        calls = self._run({'contact': 'leave'})

        self.assertEqual(set(calls), {'home', 'about', 'contact'})
        self.project.refresh_from_db()
        self.assertEqual(self.project.generation_status, 'completed')

    def test_the_build_fails_only_when_no_page_lands(self):
        self._run({'home': 'fail', 'about': 'fail', 'contact': 'fail'})

        self.project.refresh_from_db()
        self.assertEqual(self.project.generation_status, 'failed')

    def test_the_page_set_is_configurable(self):
        from apps.Imagi.ProjectManager.services import initial_build_service

        builder = {**settings.IMAGI_BUILDER, 'INITIAL_BUILD_PAGES': ['home', 'contact']}
        with override_settings(IMAGI_BUILDER=builder):
            calls = self._run()
        self.assertEqual(set(calls), {'home', 'contact'})

    def test_an_unknown_page_never_leaves_the_build_with_nothing_to_do(self):
        from apps.Imagi.ProjectManager.services.initial_build_service import (
            _pages_to_build,
        )

        pages = _pages_to_build({'INITIAL_BUILD_PAGES': ['nonsense']})
        self.assertEqual([p.slug for p in pages], ['home'])


class ConcurrentWorktreeSetupTests(TransactionTestCase):
    """Several subagents claiming worktrees on a brand-new project at once.

    Seen live: all three of a first build's pages reached `git init` on the
    same fresh directory together and two died with "Failed to initialize git
    repository". The repo lock could not cover it because it keyed on '.git',
    which does not exist yet at exactly that moment.
    """

    def setUp(self):
        self.project_dir = tempfile.mkdtemp(prefix='imagi_concurrent_git_')
        with open(os.path.join(self.project_dir, 'seed.txt'), 'w') as f:
            f.write('scaffold\n')

    def tearDown(self):
        shutil.rmtree(self.project_dir, ignore_errors=True)

    def test_the_repo_lock_covers_creating_the_repo(self):
        from apps.Imagi.Build.services.version_control_service import (
            canonical_repo_lock,
        )

        # A directory with no repo in it must still be lockable, or the one
        # moment that needs serializing most is the one moment left unguarded.
        holder_entered = threading.Event()
        second_acquired = threading.Event()

        def hold():
            with canonical_repo_lock(self.project_dir):
                holder_entered.set()
                second_acquired.wait(timeout=0.5)

        def contend():
            with canonical_repo_lock(self.project_dir):
                second_acquired.set()

        holder = threading.Thread(target=hold)
        holder.start()
        self.assertTrue(holder_entered.wait(timeout=5))
        contender = threading.Thread(target=contend)
        contender.start()
        # The contender must NOT get in while the holder has it.
        self.assertFalse(
            second_acquired.wait(timeout=0.2),
            'the lock let a second holder in on a repo-less project directory',
        )
        holder.join(timeout=5)
        contender.join(timeout=5)
        self.assertTrue(second_acquired.is_set())

    def test_parallel_worktree_creation_on_a_fresh_project_all_succeed(self):
        from apps.Imagi.Build.services.version_control_service import (
            VersionControlService,
        )

        results = {}

        def make(conversation_id):
            results[conversation_id] = VersionControlService().create_task_worktree(
                self.project_dir, conversation_id
            )

        threads = [
            threading.Thread(target=make, args=(cid,)) for cid in (901, 902, 903)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=60)

        self.assertEqual(len(results), 3)
        for cid, result in results.items():
            self.assertTrue(
                result.get('success'),
                f'worktree {cid} failed: {result.get("message")}',
            )
            self.assertTrue(os.path.isdir(result['worktree_path']))


@override_settings(PROJECTS_ROOT=_TMP_PROJECTS_ROOT)
class ScaffoldWiringTests(TestCase):
    """Full-scaffold integration test: run the real ProjectCreationService
    (npm install mocked out) and verify the generated project is wired so the
    prebuilt home and auth apps actually work.

    This is the regression net for the initial-build starting point: the
    frontend's auth pages call /api/v1/auth/..., which requires the auth app
    to be registered (with its non-conflicting 'user_auth' label), authtoken
    to be installed, and the API urls to be mounted.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from apps.Imagi.ProjectManager.services.project_creation_service import (
            ProjectCreationService,
        )

        cls.user = User.objects.create_user(username='scaffolder', password='pw123456')
        cls.project = Project.objects.create(
            user=cls.user, name='Wiring Check', description=VALID_DESCRIPTION
        )
        with patch.object(ProjectCreationService, '_install_vuejs_dependencies'):
            cls.project = ProjectCreationService(cls.user).create_project(cls.project)
        cls.backend_root = os.path.join(cls.project.project_path, 'backend', 'django')

    @classmethod
    def _read(cls, *parts):
        with open(os.path.join(*parts), 'r', encoding='utf-8') as f:
            return f.read()

    def _settings_src(self):
        for entry in os.listdir(self.backend_root):
            candidate = os.path.join(self.backend_root, entry, 'settings.py')
            if os.path.isfile(candidate):
                return self._read(candidate), os.path.join(self.backend_root, entry)
        self.fail('No Django settings.py found in scaffolded backend')

    def test_auth_app_is_installed_with_authtoken(self):
        settings_src, _ = self._settings_src()
        self.assertIn("'apps.auth'", settings_src)
        self.assertIn("'apps.home'", settings_src)
        self.assertIn("'rest_framework.authtoken'", settings_src)

    def test_auth_api_is_mounted_under_api_v1(self):
        api_v1 = self._read(self.backend_root, 'api', 'v1', 'url.py')
        self.assertIn("path('auth/', include('apps.auth.api.urls'))", api_v1)

    def test_home_urls_are_mounted_exactly_once(self):
        _, project_dir = self._settings_src()
        urls_src = self._read(project_dir, 'urls.py')
        self.assertEqual(
            urls_src.count("include('apps.home.urls')"), 1,
            'home urls must be registered exactly once (idempotent registration)',
        )

    def test_auth_app_ships_label_and_migrations(self):
        apps_py = self._read(self.backend_root, 'apps', 'auth', 'apps.py')
        self.assertIn("label = 'user_auth'", apps_py)
        self.assertTrue(os.path.isfile(
            os.path.join(self.backend_root, 'apps', 'auth', 'migrations', '__init__.py')
        ))

    def test_home_page_links_to_auth(self):
        home_view = self._read(
            self.project.project_path,
            'frontend', 'vuejs', 'src', 'apps', 'home', 'views', 'HomeView.vue',
        )
        self.assertIn('/auth/signin', home_view)
        self.assertIn('/auth/register', home_view)

    def test_a_freshly_scaffolded_project_passes_the_auth_link_check(self):
        # The check gates the first build's merge, so a false positive on a
        # clean project would block every build there is.
        from apps.Imagi.Build.services.frontend_integrity import (
            find_auth_link_problems,
        )

        self.assertEqual(find_auth_link_problems(self.project.project_path), [])

    def test_every_first_build_page_is_scaffolded_and_routed(self):
        # Each page subagent rewrites one already-routed view. If the scaffold
        # were missing, the agent would have to create its own route file too —
        # two files, and a run cut off between them leaves a dangling import
        # that discards the page.
        from apps.Imagi.ProjectManager.services.initial_build_service import (
            PAGE_BRIEFS,
        )

        for page in PAGE_BRIEFS:
            view = os.path.join(self.project.project_path, page.view_path)
            self.assertTrue(
                os.path.isfile(view), f'{page.slug} view missing: {page.view_path}'
            )
            app_dir = os.path.dirname(os.path.dirname(view))
            router = self._read(app_dir, 'router', 'index.ts')
            self.assertIn(f"path: '{page.route}'", router)
            self.assertIn('export { routes }', router)

    def test_page_apps_are_frontend_only(self):
        # about/contact are static marketing pages: giving them a Django app
        # would add INSTALLED_APPS entries and migrations for nothing.
        for app in ('about', 'contact'):
            self.assertTrue(os.path.isdir(os.path.join(
                self.project.project_path, 'frontend', 'vuejs', 'src', 'apps', app
            )))
            self.assertFalse(os.path.isdir(os.path.join(
                self.backend_root, 'apps', app
            )))

    def test_scaffolded_files_are_mirrored_to_database(self):
        # Disk is the source of truth; the DB mirror should hold the same
        # files for debugging and rehydration.
        paths = set(self.project.files.values_list('path', flat=True))
        self.assertIn('backend/django/apps/auth/api/urls.py', paths)
        self.assertIn('frontend/vuejs/src/apps/home/views/HomeView.vue', paths)


class ProjectNameValidationTests(APITestCase):
    """A project name must never be usable as a filesystem path fragment.

    The preview services key their sidecar files on the project id now, so a
    crafted name no longer escapes anything; this keeps one out of the database
    in the first place, and out of the log lines and directory basenames the
    name still reaches.
    """

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='namer', email='namer@example.com', password='correct-horse-9'
        )
        self.client.force_authenticate(user=self.user)

    def _create(self, name):
        return self.client.post(
            reverse('project_manager:project-create'),
            {'name': name, 'description': 'A shop that sells useful things online.'},
            format='json',
        )

    def test_traversal_name_is_rejected_on_create(self):
        resp = self._create('../9/Their Shop')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', resp.data)

    def test_absolute_name_is_rejected_on_create(self):
        resp = self._create('/etc/cron.d/x')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_backslash_name_is_rejected_on_create(self):
        resp = self._create(r'..\9\Their Shop')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_control_character_name_is_rejected_on_create(self):
        resp = self._create('Shop\x00evil')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_ordinary_name_is_accepted(self):
        with patch('apps.Imagi.ProjectManager.api.views.ProjectCreationService'), \
                patch('apps.Imagi.ProjectManager.api.views.start_initial_build'):
            resp = self._create('My Corner Shop')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_rename_to_a_traversal_name_is_rejected(self):
        # The update path is the one an attacker actually uses: create a
        # normal project, then PATCH the name.
        with patch('apps.Imagi.ProjectManager.api.views.ProjectCreationService'), \
                patch('apps.Imagi.ProjectManager.api.views.start_initial_build'):
            created = self._create('My Corner Shop')
        project_id = created.data['id']

        resp = self.client.patch(
            reverse('project_manager:project-detail', kwargs={'pk': project_id}),
            {'name': '../9/Their Shop'},
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
