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

    def _run_with_agent_result(self, result):
        from unittest.mock import Mock
        from apps.Imagi.ProjectManager.services import initial_build_service
        from apps.Imagi.Build.services.base_agent import ImagiAgentService

        # spec= the real class so this test fails if the service API drifts
        # (a bare Mock once hid a rename that broke every initial build).
        fake_service = Mock(spec=ImagiAgentService)
        fake_service.model = 'gpt-5.6-sol'
        fake_service.create_conversation.return_value = Mock(id=42)
        fake_service.process.return_value = result

        with patch(
            'apps.Imagi.Build.services.base_agent.ImagiAgentService',
            return_value=fake_service,
        ):
            initial_build_service._run_initial_build(self.project.pk, self.user.pk)
        return fake_service

    def test_run_success_marks_completed_and_prompts_with_business_details(self):
        fake_service = self._run_with_agent_result(
            {'success': True, 'files_changed': ['frontend/vuejs/src/apps/home/views/Home.vue']}
        )

        self.project.refresh_from_db()
        self.assertEqual(self.project.generation_status, 'completed')
        self.assertIsNotNone(self.project.last_generated_at)

        # The prompt must carry the business name and description into the agent.
        prompt = fake_service.process.call_args.kwargs['user_input']
        self.assertIn('Beanline', prompt)
        self.assertIn('coffee roastery', prompt)
        fake_service.create_conversation.assert_called_once_with(
            self.user,
            'gpt-5.6-sol',
            project_id=self.project.pk,
            title='Initial build',
        )

    def test_run_failure_marks_failed(self):
        self._run_with_agent_result({'success': False, 'error': 'model error'})
        self.project.refresh_from_db()
        self.assertEqual(self.project.generation_status, 'failed')
