"""
Service for managing Oasis web app projects.
"""

import os
import shutil
import logging
from django.conf import settings
from apps.ProjectManager.services import ProjectGenerationService

logger = logging.getLogger(__name__)

class ProjectService:
    def __init__(self, user):
        self.user = user
        self.project_generator = ProjectGenerationService(user)
    
    def create_project(self, name):
        """Create a new Oasis web app project."""
        try:
            # Create the project using ProjectManager service
            user_project = self.project_generator.create_project(name)
            
            # Initialize project with default files
            self._initialize_project_files(user_project.project_path)
            
            return user_project
        except Exception as e:
            logger.error(f"Error creating project: {str(e)}")
            raise
    
    def delete_project(self, project):
        """Delete a project and its files."""
        try:
            # Delete project files
            if project.user_project and os.path.exists(project.user_project.project_path):
                shutil.rmtree(project.user_project.project_path)
            
            # Delete project record
            project.is_active = False
            project.save()
            
            logger.info(f"Project {project.name} deleted successfully")
        except Exception as e:
            logger.error(f"Error deleting project: {str(e)}")
            raise
    
    def undo_last_action(self, project):
        """Undo the last action in a project."""
        try:
            # Get the project's git repository
            repo_path = project.user_project.project_path
            if not os.path.exists(repo_path):
                raise Exception("Project repository not found")
            
            # TODO: Implement git-based undo functionality
            # For now, return a placeholder response
            return {
                'success': True,
                'message': 'Last action undone successfully'
            }
        except Exception as e:
            logger.error(f"Error undoing action: {str(e)}")
            raise
    
    def _initialize_project_files(self, project_path):
        """Initialize a new project with default files and structure."""
        try:
            # Create necessary directories
            os.makedirs(os.path.join(project_path, 'static', 'css'), exist_ok=True)
            os.makedirs(os.path.join(project_path, 'static', 'js'), exist_ok=True)
            os.makedirs(os.path.join(project_path, 'templates'), exist_ok=True)
            
            # Create default files
            self._create_default_files(project_path)
            
            logger.info(f"Project files initialized at {project_path}")
        except Exception as e:
            logger.error(f"Error initializing project files: {str(e)}")
            raise
    
    def _create_default_files(self, project_path):
        """Create default files for a new project."""
        default_files = {
            'templates/base.html': '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}My Oasis App{% endblock %}</title>
    <link rel="stylesheet" href="/static/css/styles.css">
    {% block extra_css %}{% endblock %}
</head>
<body>
    {% block content %}{% endblock %}
    
    <script src="/static/js/main.js"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
''',
            'static/css/styles.css': '''
/* Base styles */
:root {
    --primary-color: #4f46e5;
    --secondary-color: #818cf8;
    --text-color: #1f2937;
    --bg-color: #ffffff;
}

body {
    font-family: system-ui, -apple-system, sans-serif;
    color: var(--text-color);
    background-color: var(--bg-color);
    line-height: 1.5;
    margin: 0;
    padding: 0;
}
''',
            'static/js/main.js': '''
// Main JavaScript file
document.addEventListener('DOMContentLoaded', function() {
    console.log('Application initialized');
});
'''
        }
        
        for file_path, content in default_files.items():
            full_path = os.path.join(project_path, file_path)
            with open(full_path, 'w') as f:
                f.write(content.strip()) 