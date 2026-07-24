"""
Tests for the ProjectManager app.

These focus on the logic that is safe and fast to exercise: the Project model
(slug/path generation, validation, soft vs hard delete), the create serializer,
the management service, and the REST API. The heavy filesystem/subprocess work
performed by ProjectCreationService is mocked out so the suite stays fast and
does not pollute the repository or depend on npm/Django scaffolding.
"""

import os
import shutil
import tempfile
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
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
class InitialBuildServiceTests(TestCase):
    """Tests for the initial AI build kicked off at project creation."""

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

    def _run_build(self, outcomes, unresolved=()):
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

        with patch.object(ImagiAgentService, 'process', fake_process), patch(
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
        self.assertEqual(task.title, 'Initial build')
        self.assertEqual(task.system_prompt.content, INITIAL_BUILD_INSTRUCTIONS)
        self.assertEqual(calls[0]['conversation_id'], task.id)

        # The main thread opens with the founder's brief and a one-line
        # acknowledgement linking to the subagent's thread.
        messages = list(lead.messages.order_by('created_at'))
        self.assertEqual([m.role for m in messages], ['user', 'assistant'])
        self.assertIn('Beanline', messages[0].content)
        self.assertEqual(
            messages[1].metadata['dispatched_tasks'],
            [{'conversation_id': task.id, 'title': 'Initial build'}],
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
        # dangling references than it fixes, so a build with no time left keeps
        # its scaffold instead.
        from apps.Imagi.ProjectManager.services import initial_build_service

        budget = settings.IMAGI_BUILDER['INITIAL_BUILD_TIME_BUDGET_S']
        min_repair = settings.IMAGI_BUILDER['INITIAL_BUILD_MIN_REPAIR_SECONDS']
        # First reading sets the deadline; the second is checked before repair,
        # by which point less than the repair minimum is left.
        clock = iter([0.0, budget - (min_repair / 2)])

        with patch.object(
            initial_build_service.time, 'monotonic', side_effect=lambda: next(clock)
        ):
            calls = self._run_build(
                ['leave', 'accept'],
                unresolved=[{
                    'file': 'frontend/vuejs/src/apps/home/views/HomeView.vue',
                    'import': '@/shared/components/SiteHeader.vue',
                }],
            )

        self.assertEqual(len(calls), 1, 'a repair ran with no time budget left')
        self.project.refresh_from_db()
        self.assertEqual(self.project.generation_status, 'failed')


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

    def test_scaffolded_files_are_mirrored_to_database(self):
        # Disk is the source of truth; the DB mirror should hold the same
        # files for debugging and rehydration.
        paths = set(self.project.files.values_list('path', flat=True))
        self.assertIn('backend/django/apps/auth/api/urls.py', paths)
        self.assertIn('frontend/vuejs/src/apps/home/views/HomeView.vue', paths)
