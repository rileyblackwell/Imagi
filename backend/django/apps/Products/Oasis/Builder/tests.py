from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Conversation, Page, Message
from apps.Products.Oasis.ProjectManager.models import Project as PMProject
from apps.Products.Oasis.Builder.services.create_file_service import CreateFileService
import os
import shutil
import tempfile

class BuilderModelTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        # Create a project
        self.project_root = tempfile.mkdtemp(prefix='builder_model_')
        self.project = PMProject.objects.create(
            user=self.user,
            name="Test Project",
            project_path=self.project_root
        )
        self.addCleanup(lambda: shutil.rmtree(self.project_root, ignore_errors=True))

        # Create a conversation
        self.conversation = Conversation.objects.create(
            user=self.user,
            project_id=self.project.id
        )
        
        # Create a page
        self.page = Page.objects.create(
            conversation=self.conversation,
            filename="index.html"
        )

    def test_project_creation(self):
        """Test project model creation and string representation"""
        self.assertEqual(str(self.project), "Test Project (testuser)")
        self.assertEqual(self.project.slug, "test-project")

    def test_conversation_creation(self):
        """Test conversation model creation and string representation"""
        expected_str = f"Conversation {self.conversation.id} for testuser - Project ID: {self.project.id}"
        self.assertEqual(str(self.conversation), expected_str)

    def test_page_creation(self):
        """Test page model creation and string representation"""
        expected_str = f"Page index.html in Conversation {self.conversation.id}"
        self.assertEqual(str(self.page), expected_str)

    def test_message_creation(self):
        """Test message model creation and string representation"""
        message = Message.objects.create(
            conversation=self.conversation,
            page=self.page,
            role='user',
            content='Test message'
        )
        expected_str = "User message for index.html"
        self.assertEqual(str(message), expected_str)

class BuilderViewTests(TestCase):
    def setUp(self):
        # Create test user and log them in
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')

        self.project_root = tempfile.mkdtemp(prefix='builder_view_')
        self.project = PMProject.objects.create(
            user=self.user,
            name="Test Project",
            project_path=self.project_root
        )

    def tearDown(self):
        shutil.rmtree(self.project_root, ignore_errors=True)

    def test_landing_page_view(self):
        """Test the landing page view"""
        response = self.client.get(reverse('builder:landing_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'builder/builder_landing_page.html')
        self.assertIn('projects', response.context)

    def test_create_project_view(self):
        """Test project creation"""
        response = self.client.post(
            reverse('builder:create_project'),
            {'project_name': 'New Test Project'}
        )
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        self.assertTrue(PMProject.objects.filter(name='New Test Project').exists())

    def test_delete_project_view(self):
        """Test project deletion"""
        response = self.client.post(
            reverse('builder:delete_project', args=[self.project.id])
        )
        self.assertEqual(response.status_code, 302)  # Redirect after deletion
        self.assertFalse(PMProject.objects.filter(id=self.project.id).exists())

    def test_project_workspace_view(self):
        """Test the project workspace view"""
        response = self.client.get(
            reverse('builder:project_workspace', 
                   args=[self.project.slug])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'builder/oasis_builder.html')

class BuilderServiceTests(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        self.project_root = tempfile.mkdtemp(prefix='builder_service_')
        self.project = PMProject.objects.create(
            user=self.user,
            name="Test Project",
            project_path=self.project_root
        )

        # Create conversation and page
        self.conversation = Conversation.objects.create(
            user=self.user,
            project_id=self.project.id
        )
        
        self.page = Page.objects.create(
            conversation=self.conversation,
            filename="index.html"
        )

    def tearDown(self):
        shutil.rmtree(self.project_root, ignore_errors=True)

    def test_process_builder_mode_input(self):
        """Test the builder mode input processing"""
        from apps.Products.Oasis.Agents.services import process_builder_mode_input
        
        # Create necessary directories
        os.makedirs(os.path.join(self.project_root, "templates"), exist_ok=True)
        os.makedirs(os.path.join(self.project_root, "static/css"), exist_ok=True)
        
        response = process_builder_mode_input(
            user_input="Create a simple landing page",
            model="claude-sonnet-4-20250514",
            file_name="index.html",
            user=self.user
        )
        
        self.assertIn('success', response)
        if response['success']:
            self.assertIn('response', response)

    def test_undo_last_action(self):
        """Test the undo last action functionality"""
        from apps.Products.Oasis.Agents.services import undo_last_action_service
        
        # Create test messages
        Message.objects.create(
            conversation=self.conversation,
            page=self.page,
            role='assistant',
            content='First version'
        )
        
        Message.objects.create(
            conversation=self.conversation,
            page=self.page,
            role='assistant',
            content='Second version'
        )
        
        content, message, status_code = undo_last_action_service(
            self.user,
            "index.html"
        )
        
        self.assertEqual(status_code, 200)
        self.assertEqual(Message.objects.filter(
            conversation=self.conversation,
            page=self.page
        ).count(), 1)

class BuilderIntegrationTests(TestCase):
    def setUp(self):
        # Set up test user and client
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')

    def test_project_lifecycle(self):
        """Test the complete lifecycle of a project"""
        # 1. Create project
        response = self.client.post(
            reverse('builder:create_project'),
            {'project_name': 'Lifecycle Test Project'}
        )
        self.assertEqual(response.status_code, 302)
        
        project = PMProject.objects.get(name='Lifecycle Test Project')
        
        # 2. Access project workspace
        response = self.client.get(
            reverse('builder:project_workspace', 
                   args=[project.slug])
        )
        self.assertEqual(response.status_code, 200)
        
        # 3. Generate content
        response = self.client.post(
            reverse('builder:process_input'),
            {
                'user_input': 'Create a simple landing page',
                'model': 'claude-sonnet-4-20250514',
                'file': 'index.html',
                'mode': 'build'
            }
        )
        self.assertEqual(response.status_code, 200)
        
        # 4. Delete project
        response = self.client.post(
            reverse('builder:delete_project', args=[project.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(PMProject.objects.filter(id=project.id).exists())


class CreateFileServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='fileserviceuser',
            password='testpass123'
        )
        self.project_root = tempfile.mkdtemp(prefix='imagi_file_service_')
        self.project = PMProject.objects.create(
            user=self.user,
            name='File Service Project',
            project_path=self.project_root
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
