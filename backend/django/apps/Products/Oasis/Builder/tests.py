from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Project, Conversation, Page, Message
from apps.Products.Oasis.ProjectManager.models import UserProject
import os
import shutil

class BuilderModelTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create a test project
        self.user_project = UserProject.objects.create(
            user=self.user,
            name="Test Project",
            project_path="/tmp/test_project"
        )
        
        # Create a project
        self.project = Project.objects.create(
            user=self.user,
            name="Test Project",
            user_project=self.user_project
        )
        
        # Create a conversation
        self.conversation = Conversation.objects.create(
            user=self.user,
            project=self.project
        )
        
        # Create a page
        self.page = Page.objects.create(
            conversation=self.conversation,
            filename="index.html"
        )

    def test_project_creation(self):
        """Test project model creation and string representation"""
        self.assertEqual(str(self.project), "Test Project - testuser")
        self.assertEqual(self.project.get_url_safe_name(), "test-project")

    def test_conversation_creation(self):
        """Test conversation model creation and string representation"""
        expected_str = f"Conversation {self.conversation.id} for testuser - Project: Test Project"
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
        
        # Create test project
        self.user_project = UserProject.objects.create(
            user=self.user,
            name="Test Project",
            project_path="/tmp/test_project"
        )
        
        self.project = Project.objects.create(
            user=self.user,
            name="Test Project",
            user_project=self.user_project
        )

    def tearDown(self):
        # Clean up any test project directories
        if os.path.exists("/tmp/test_project"):
            shutil.rmtree("/tmp/test_project")

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
        self.assertTrue(Project.objects.filter(name='New Test Project').exists())

    def test_delete_project_view(self):
        """Test project deletion"""
        response = self.client.post(
            reverse('builder:delete_project', args=[self.project.id])
        )
        self.assertEqual(response.status_code, 302)  # Redirect after deletion
        self.assertFalse(Project.objects.filter(id=self.project.id).exists())

    def test_project_workspace_view(self):
        """Test the project workspace view"""
        response = self.client.get(
            reverse('builder:project_workspace', 
                   args=[self.project.get_url_safe_name()])
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
        
        # Create test project
        self.user_project = UserProject.objects.create(
            user=self.user,
            name="Test Project",
            project_path="/tmp/test_project"
        )
        
        self.project = Project.objects.create(
            user=self.user,
            name="Test Project",
            user_project=self.user_project
        )
        
        # Create conversation and page
        self.conversation = Conversation.objects.create(
            user=self.user,
            project=self.project
        )
        
        self.page = Page.objects.create(
            conversation=self.conversation,
            filename="index.html"
        )

    def tearDown(self):
        # Clean up test project directories
        if os.path.exists("/tmp/test_project"):
            shutil.rmtree("/tmp/test_project")

    def test_process_builder_mode_input(self):
        """Test the builder mode input processing"""
        from apps.Products.Oasis.Agents.services import process_builder_mode_input
        
        # Create necessary directories
        os.makedirs("/tmp/test_project/templates", exist_ok=True)
        os.makedirs("/tmp/test_project/static/css", exist_ok=True)
        
        response = process_builder_mode_input(
            user_input="Create a simple landing page",
            model="claude-3-5-sonnet-20241022",
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
        
        project = Project.objects.get(name='Lifecycle Test Project')
        
        # 2. Access project workspace
        response = self.client.get(
            reverse('builder:project_workspace', 
                   args=[project.get_url_safe_name()])
        )
        self.assertEqual(response.status_code, 200)
        
        # 3. Generate content
        response = self.client.post(
            reverse('builder:process_input'),
            {
                'user_input': 'Create a simple landing page',
                'model': 'claude-3-5-sonnet-20241022',
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
        self.assertFalse(Project.objects.filter(id=project.id).exists())
