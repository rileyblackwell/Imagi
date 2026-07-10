"""
Tests for the Builder app.

Covers the Builder models, the CreateFileService, and the current Builder DRF
API (file creation/content, the models endpoint, auth gating and project
ownership).

Note: the previous server-rendered view/service tests (`builder:landing_page`,
`process_builder_mode_input`, ...) were removed. Those exercised a legacy
template UI and pre-SDK agent helpers that no longer exist — the workspace is
now a Vue SPA talking to the DRF API exercised below.
"""

import os
import shutil
import tempfile

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from apps.Products.Imagi.ProjectManager.models import Project as PMProject
from apps.Products.Imagi.Builder.models import Conversation, Page, Message
from apps.Products.Imagi.Builder.services.create_file_service import CreateFileService


class BuilderModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')

        self.project_root = tempfile.mkdtemp(prefix='builder_model_')
        self.project = PMProject.objects.create(
            user=self.user, name="Test Project", project_path=self.project_root
        )
        self.addCleanup(lambda: shutil.rmtree(self.project_root, ignore_errors=True))

        self.conversation = Conversation.objects.create(
            user=self.user, project_id=self.project.id
        )
        self.page = Page.objects.create(
            conversation=self.conversation, filename="index.html"
        )

    def test_project_creation(self):
        self.assertEqual(str(self.project), "Test Project (testuser)")
        self.assertEqual(self.project.slug, "test-project")

    def test_conversation_creation(self):
        expected_str = (
            f"Conversation {self.conversation.id} for testuser "
            f"- Project ID: {self.project.id}"
        )
        self.assertEqual(str(self.conversation), expected_str)

    def test_page_creation(self):
        expected_str = f"Page index.html in Conversation {self.conversation.id}"
        self.assertEqual(str(self.page), expected_str)

    def test_message_creation(self):
        message = Message.objects.create(
            conversation=self.conversation, page=self.page,
            role='user', content='Test message',
        )
        self.assertEqual(str(message), "User message for index.html")


class BuilderAPITests(APITestCase):
    """The current Builder REST API (replaces the legacy view tests)."""

    def setUp(self):
        self.user = User.objects.create_user(username='builder', password='testpass123')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        self.project_root = tempfile.mkdtemp(prefix='builder_api_')
        self.project = PMProject.objects.create(
            user=self.user, name="API Project", project_path=self.project_root
        )
        self.addCleanup(lambda: shutil.rmtree(self.project_root, ignore_errors=True))

    def test_models_endpoint_requires_auth(self):
        self.client.credentials()  # drop auth
        resp = self.client.get(reverse('api-ai-models'))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_models_endpoint_returns_models(self):
        resp = self.client.get(reverse('api-ai-models'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('models', resp.data)
        self.assertGreater(len(resp.data['models']), 0)

    def test_create_file_writes_to_disk(self):
        relative_path = 'frontend/vuejs/src/apps/blog/views/About.vue'
        resp = self.client.post(
            reverse('api-create-file', args=[self.project.id]),
            {'path': relative_path, 'content': 'hello world'},
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['path'], relative_path)
        self.assertTrue(os.path.exists(os.path.join(self.project_root, relative_path)))

    def test_create_file_requires_path_or_name(self):
        resp = self.client.post(
            reverse('api-create-file', args=[self.project.id]),
            {'content': 'x'}, format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_file_on_other_users_project_is_rejected(self):
        other = User.objects.create_user(username='intruder', password='testpass123')
        other_root = tempfile.mkdtemp(prefix='builder_other_')
        self.addCleanup(lambda: shutil.rmtree(other_root, ignore_errors=True))
        other_project = PMProject.objects.create(
            user=other, name="Their Project", project_path=other_root
        )
        relative_path = 'frontend/vuejs/src/x.vue'
        resp = self.client.post(
            reverse('api-create-file', args=[other_project.id]),
            {'path': relative_path, 'content': 'x'}, format='json',
        )
        # The project is owned by another user, so the request must not succeed
        # and no file may be written into their project directory.
        self.assertGreaterEqual(resp.status_code, 400)
        self.assertFalse(os.path.exists(os.path.join(other_root, relative_path)))

    def test_file_content_round_trip(self):
        relative_path = 'frontend/vuejs/src/apps/blog/views/Home.vue'
        self.client.post(
            reverse('api-create-file', args=[self.project.id]),
            {'path': relative_path, 'content': 'the content'},
            format='json',
        )
        resp = self.client.get(
            reverse('api-file-content', args=[self.project.id, relative_path])
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['content'], 'the content')


class CreateFileServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='fileserviceuser', password='testpass123'
        )
        self.project_root = tempfile.mkdtemp(prefix='imagi_file_service_')
        self.project = PMProject.objects.create(
            user=self.user, name='File Service Project', project_path=self.project_root
        )
        self.service = CreateFileService(project=self.project)

    def tearDown(self):
        shutil.rmtree(self.project_root, ignore_errors=True)

    def test_creates_default_view_when_content_blank(self):
        relative_path = 'frontend/vuejs/src/apps/blog/views/NewAbout.vue'
        result = self.service.create_file({
            'name': relative_path,
            'type': 'vue',
            'content': '   '  # simulate blank content coming from UI
        })

        expected_path = os.path.join(self.project_root, relative_path)
        self.assertTrue(os.path.exists(expected_path))
        self.assertEqual(result['path'], relative_path)
        self.assertEqual(result['type'], 'vue')

        with open(expected_path, 'r', encoding='utf-8') as created_file:
            created_content = created_file.read()

        self.assertIn('<template>', created_content)
        self.assertIn('Welcome to NewAbout', created_content)
        self.assertIn("defineOptions({ name: 'NewAbout' })", created_content)

    def test_creates_default_component_when_content_empty(self):
        relative_path = 'frontend/vuejs/src/components/atoms/PrimaryButton.vue'
        result = self.service.create_file({
            'name': relative_path,
            'type': 'vue',
            'content': '\n'
        })

        expected_path = os.path.join(self.project_root, relative_path)
        self.assertTrue(os.path.exists(expected_path))
        self.assertEqual(result['path'], relative_path)

        with open(expected_path, 'r', encoding='utf-8') as created_file:
            created_content = created_file.read()

        self.assertIn('<!-- Atom: PrimaryButton -->', created_content)
        self.assertIn('.primarybutton-component', created_content)
        self.assertIn("defineOptions({ name: 'PrimaryButton' })", created_content)
