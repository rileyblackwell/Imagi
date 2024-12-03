from django.test import TestCase
from django.contrib.auth import get_user_model
from django.conf import settings
import os
import shutil
from .models import UserProject
from .services import ProjectGenerationService

class ProjectManagerTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.service = ProjectGenerationService(self.user)

    def tearDown(self):
        # Clean up created project directories
        user_projects_dir = os.path.join(settings.PROJECTS_ROOT, str(self.user.id))
        if os.path.exists(user_projects_dir):
            shutil.rmtree(user_projects_dir)

    def test_create_project(self):
        project = self.service.create_project('TestProject')
        
        self.assertEqual(project.user, self.user)
        self.assertEqual(project.name, 'TestProject')
        self.assertTrue(project.project_path)
        
        # Verify directory structure
        self.assertTrue(os.path.exists(project.project_path))
        self.assertTrue(os.path.exists(os.path.join(project.project_path, 'templates')))
        self.assertTrue(os.path.exists(os.path.join(project.project_path, 'static')))
        
        # Verify template files
        self.assertTrue(os.path.exists(os.path.join(project.project_path, 'templates', 'base.html')))
        self.assertTrue(os.path.exists(os.path.join(project.project_path, 'static', 'css', 'style.css')))
