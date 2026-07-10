"""
Tests for the ProjectManager app.

These focus on the logic that is safe and fast to exercise: the Project model
(slug/path generation, validation, soft vs hard delete), the create serializer,
the management service, and the REST API. The heavy filesystem/subprocess work
performed by ProjectCreationService is mocked out so the suite stays fast and
does not pollute the repository or depend on npm/Django scaffolding.
"""

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

from apps.Products.Imagi.ProjectManager.models import Project
from apps.Products.Imagi.ProjectManager.services.project_management_service import (
    ProjectManagementService,
)

User = get_user_model()

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
        from apps.Products.Imagi.ProjectManager.api.serializers import (
            ProjectCreateSerializer,
        )

        request = type('R', (), {'user': self.user})()
        serializer = ProjectCreateSerializer(
            data={'name': 'Existing Project'}, context={'request': request}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)


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

    @patch.object(ProjectManagementService, '_stop_project_server_and_cleanup_pid')
    @patch.object(ProjectManagementService, '_delete_project_directory')
    def test_delete_project_hard_deletes_row(self, mock_dir, mock_pid):
        project = Project.objects.create(user=self.user, name='To Delete')
        pid = project.id
        result = self.service.delete_project(project)
        self.assertTrue(result['success'])
        self.assertFalse(Project.objects.filter(id=pid).exists())


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

    @patch(
        'apps.Products.Imagi.ProjectManager.api.views.ProjectCreationService.create_project'
    )
    def test_create_project(self, mock_create):
        mock_create.side_effect = lambda project: project
        resp = self.client.post(
            reverse('project_manager:project-create'),
            {'name': 'Brand New App', 'description': 'hello'},
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['name'], 'Brand New App')
        self.assertTrue(
            Project.objects.filter(user=self.user, name='Brand New App').exists()
        )
        mock_create.assert_called_once()

    def test_create_duplicate_name_returns_400(self):
        Project.objects.create(user=self.user, name='Taken Name')
        resp = self.client.post(
            reverse('project_manager:project-create'), {'name': 'Taken Name'}
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

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

    @patch.object(ProjectManagementService, '_stop_project_server_and_cleanup_pid')
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
        'apps.Products.Imagi.ProjectManager.api.views.ProjectCreationService.initialize_project'
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
