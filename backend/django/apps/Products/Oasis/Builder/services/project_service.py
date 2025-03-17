"""
Service for managing project metadata and file structure.
"""

import os
import logging
from datetime import datetime
from rest_framework.exceptions import ValidationError, NotFound
from apps.Products.Oasis.ProjectManager.models import Project

logger = logging.getLogger(__name__)

class ProjectService:
    """
    Service for managing project metadata and file structure.
    This service handles project metadata and provides methods to access
    templates and static files separately.
    """
    
    def __init__(self, user=None, project=None):
        """
        Initialize the project service with either a user or a project.
        If a project is provided, it will be used directly.
        If a user is provided, project_id must be passed to methods.
        """
        self.user = user
        self.project = project
        
        if project:
            self.project_path = project.project_path
    
    def get_project(self, project_id):
        """Get a project by ID when initialized with user."""
        if not self.user:
            raise ValidationError("ProjectService initialized without user")
            
        try:
            return Project.objects.get(id=project_id, user=self.user, is_active=True)
        except Project.DoesNotExist:
            raise NotFound('Project not found')
    
    def get_project_path(self, project_id=None):
        """Get the project path for the current project or specified project ID."""
        try:
            if self.project:
                if not self.project.project_path:
                    logger.error(f"Project {self.project.id} has no project_path")
                    return None
                return self.project.project_path
                
            if project_id:
                project = self.get_project(project_id)
                if not project.project_path:
                    logger.error(f"Project {project.id} has no project_path")
                    return None
                return project.project_path
                
            raise ValidationError("No project specified")
        except Exception as e:
            logger.error(f"Error getting project path: {str(e)}")
            return None
    
    def get_project_details(self, project_id=None):
        """Get detailed information about the project."""
        try:
            if self.project:
                project = self.project
            elif project_id:
                project = self.get_project(project_id)
            else:
                raise ValidationError("No project specified")
                
            return {
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'created_at': project.created_at,
                'updated_at': project.updated_at,
                'template_count': len(self.list_template_files(project_id)),
                'static_count': len(self.list_static_files(project_id))
            }
        except Exception as e:
            logger.error(f"Error getting project details: {str(e)}")
            raise
    
    def list_template_files(self, project_id=None):
        """List all template files in the project."""
        try:
            project_path = self.get_project_path(project_id)
            
            # Check if project path exists
            if not project_path or not os.path.exists(project_path):
                logger.error(f"Project path does not exist: {project_path}")
                return []
            
            templates_dir = os.path.join(project_path, 'templates')
            if not os.path.exists(templates_dir):
                # Create templates directory if it doesn't exist
                try:
                    os.makedirs(templates_dir, exist_ok=True)
                    logger.info(f"Created templates directory for project: {project_path}")
                except Exception as e:
                    logger.error(f"Error creating templates directory: {str(e)}")
                return []
            
            template_files = []
            
            for root, dirs, filenames in os.walk(templates_dir):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for filename in filenames:
                    # Skip hidden files
                    if filename.startswith('.'):
                        continue
                    
                    full_path = os.path.join(root, filename)
                    # Make the path relative to the project path, not just templates dir
                    rel_path = os.path.relpath(full_path, project_path)
                    
                    # Get file extension
                    _, file_extension = os.path.splitext(filename)
                    
                    # Get file stats
                    stats = os.stat(full_path)
                    
                    template_files.append({
                        'id': f"template-{rel_path}",
                        'name': filename,
                        'path': rel_path,
                        'type': 'html',
                        'size': os.path.getsize(full_path),
                        'lastModified': datetime.fromtimestamp(stats.st_mtime).isoformat()
                    })
            
            return sorted(template_files, key=lambda x: x['path'])
        except Exception as e:
            logger.error(f"Error listing template files: {str(e)}")
            return []
    
    def list_static_files(self, project_id=None):
        """List all static files in the project."""
        try:
            project_path = self.get_project_path(project_id)
            
            # Check if project path exists
            if not project_path or not os.path.exists(project_path):
                logger.error(f"Project path does not exist: {project_path}")
                return []
            
            static_dir = os.path.join(project_path, 'static')
            if not os.path.exists(static_dir):
                # Create static directory if it doesn't exist
                try:
                    os.makedirs(static_dir, exist_ok=True)
                    # Also create common subdirectories
                    os.makedirs(os.path.join(static_dir, 'css'), exist_ok=True)
                    os.makedirs(os.path.join(static_dir, 'js'), exist_ok=True)
                    os.makedirs(os.path.join(static_dir, 'img'), exist_ok=True)
                    logger.info(f"Created static directories for project: {project_path}")
                except Exception as e:
                    logger.error(f"Error creating static directories: {str(e)}")
                return []
            
            static_files = []
            
            for root, dirs, filenames in os.walk(static_dir):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for filename in filenames:
                    # Skip hidden files
                    if filename.startswith('.'):
                        continue
                    
                    full_path = os.path.join(root, filename)
                    # Make the path relative to the project path, not just static dir
                    rel_path = os.path.relpath(full_path, project_path)
                    
                    # Get file extension
                    _, file_extension = os.path.splitext(filename)
                    file_extension = file_extension.lower()
                    
                    # Determine file type based on extension
                    file_type = 'text'
                    if file_extension in ['.css']:
                        file_type = 'css'
                    elif file_extension in ['.js']:
                        file_type = 'javascript'
                    elif file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.svg']:
                        file_type = 'image'
                    
                    # Get file stats
                    stats = os.stat(full_path)
                    
                    static_files.append({
                        'id': f"static-{rel_path}",
                        'name': filename,
                        'path': rel_path,
                        'type': file_type,
                        'size': os.path.getsize(full_path),
                        'lastModified': datetime.fromtimestamp(stats.st_mtime).isoformat()
                    })
            
            return sorted(static_files, key=lambda x: x['path'])
        except Exception as e:
            logger.error(f"Error listing static files: {str(e)}")
            return []
    
    def initialize_project_files(self, project_id=None):
        """Initialize a project with basic template and static files."""
        try:
            # Get templates and static files
            template_files = self.list_template_files(project_id)
            static_files = self.list_static_files(project_id)
            
            # If there are no template files, create basic ones
            if not template_files:
                self._create_default_templates(project_id)
            
            # If there are no static files, create basic ones
            if not static_files:
                self._create_default_static_files(project_id)
                
            return True
        except Exception as e:
            logger.error(f"Error initializing project files: {str(e)}")
            return False
    
    def _create_default_templates(self, project_id=None):
        """Create default template files for the project."""
        from .file_service import FileService
        
        file_service = FileService(user=self.user, project=self.project)
        
        # Create base.html
        base_html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}Django Project{% endblock %}</title>
  {% load static %}
  <link rel="stylesheet" href="{% static 'css/styles.css' %}">
  {% block extra_css %}{% endblock %}
</head>
<body>
  <header>
    <nav>
      <div class="container">
        <h1>My Django Project</h1>
      </div>
    </nav>
  </header>

  <main class="container">
    {% block content %}{% endblock %}
  </main>

  <footer>
    <div class="container">
      <p>&copy; {% now "Y" %} My Django Project</p>
    </div>
  </footer>
  
  {% block extra_js %}{% endblock %}
</body>
</html>"""
        
        # Create index.html
        index_html = """{% extends "base.html" %}
{% load static %}

{% block title %}Home | Django Project{% endblock %}

{% block content %}
<div class="welcome-section">
  <h2>Welcome to your new Django project</h2>
  <p>This is the homepage of your Django application.</p>
  <p>Edit this template to start building your web application.</p>
</div>
{% endblock %}"""
        
        try:
            file_service.create_file('templates/base.html', base_html, project_id)
            file_service.create_file('templates/index.html', index_html, project_id)
            logger.info("Created default template files")
        except Exception as e:
            logger.error(f"Error creating template files: {str(e)}")
            raise
    
    def _create_default_static_files(self, project_id=None):
        """Create default static files for the project."""
        from .file_service import FileService
        
        file_service = FileService(user=self.user, project=self.project)
        
        # Create styles.css
        styles_css = """/* Main stylesheet */

:root {
  --primary-color: #4b6bfb;
  --secondary-color: #2e3856;
  --text-color: #333;
  --light-bg: #f9f9f9;
  --dark-bg: #2d3748;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen,
    Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
  line-height: 1.6;
  margin: 0;
  padding: 0;
  color: var(--text-color);
  background-color: var(--light-bg);
}

.container {
  width: 85%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
}

header {
  background-color: var(--primary-color);
  color: white;
  padding: 1rem 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

header h1 {
  margin: 0;
  font-size: 1.75rem;
}

main {
  padding: 2rem 0;
}

.welcome-section {
  background-color: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  margin-bottom: 2rem;
}

footer {
  background-color: var(--secondary-color);
  color: white;
  padding: 1rem 0;
  text-align: center;
  margin-top: 2rem;
}"""
        
        # Create script.js
        script_js = """// Main JavaScript file
document.addEventListener('DOMContentLoaded', function() {
  console.log('Application initialized');
});"""
        
        try:
            file_service.create_file('static/css/styles.css', styles_css, project_id)
            file_service.create_file('static/js/script.js', script_js, project_id)
            logger.info("Created default static files")
        except Exception as e:
            logger.error(f"Error creating static files: {str(e)}")
            raise 