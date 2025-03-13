from django.test import TestCase
from django.contrib.auth import get_user_model
from django.conf import settings
import os
import shutil
from .models import UserProject
from .services.project_creation_service import ProjectCreationService
from .services.project_management_service import ProjectManagementService

class ProjectManagerTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.creation_service = ProjectCreationService(self.user)
        self.management_service = ProjectManagementService(self.user)

    def tearDown(self):
        # Clean up created project directories
        user_projects_dir = os.path.join(settings.PROJECTS_ROOT, str(self.user.id))
        if os.path.exists(user_projects_dir):
            shutil.rmtree(user_projects_dir)

    def test_create_project(self):
        # First create the project object
        project = UserProject.objects.create(
            user=self.user,
            name='TestProject'
        )
        
        # Now use the service to create project files
        self.creation_service.create_project(project)
        
        self.assertEqual(project.user, self.user)
        self.assertEqual(project.name, 'TestProject')
        self.assertTrue(project.project_path)
        
        # Verify project is created in oasis_projects directory
        expected_base_path = os.path.join(settings.PROJECTS_ROOT, str(self.user.id))
        self.assertTrue(project.project_path.startswith(expected_base_path))
        
        # Verify directory structure
        self.assertTrue(os.path.exists(project.project_path))
        self.assertTrue(os.path.exists(os.path.join(project.project_path, 'templates')))
        self.assertTrue(os.path.exists(os.path.join(project.project_path, 'static')))
        
        # Verify template files
        self.assertTrue(os.path.exists(os.path.join(project.project_path, 'templates', 'base.html')))
        self.assertTrue(os.path.exists(os.path.join(project.project_path, 'static', 'css', 'style.css')))
