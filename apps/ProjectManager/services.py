import os
import subprocess
import shutil
from datetime import datetime
from django.conf import settings
from django.template.loader import render_to_string
from .models import UserProject

class ProjectGenerationService:
    def __init__(self, user):
        self.user = user
        self.base_directory = os.path.join(settings.PROJECTS_ROOT, str(user.id))
        os.makedirs(self.base_directory, exist_ok=True)

    def _sanitize_project_name(self, name):
        """Convert project name to a valid Python identifier"""
        # Replace spaces and special chars with underscores
        sanitized = ''.join(c if c.isalnum() else '_' for c in name)
        # Ensure it starts with a letter
        if not sanitized[0].isalpha():
            sanitized = 'project_' + sanitized
        return sanitized

    def create_project(self, project_name):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        sanitized_name = self._sanitize_project_name(project_name)
        unique_name = f"{sanitized_name}_{timestamp}"
        project_path = os.path.join(self.base_directory, unique_name)
        
        try:
            # Create the project directory first
            os.makedirs(project_path, exist_ok=True)
            
            # Create Django project
            subprocess.run(
                ["django-admin", "startproject", unique_name, "."],  # Note the "." at the end
                check=True,
                capture_output=True,
                text=True,
                cwd=project_path  # Set the working directory to project_path
            )
            
            # Create additional directories
            self._create_project_structure(project_path)
            
            # Initialize basic templates and static files
            self._initialize_project_files(project_path, project_name)
            
            # Create project record
            project = UserProject.objects.create(
                user=self.user,
                name=project_name,
                project_path=project_path
            )
            
            return project
            
        except subprocess.CalledProcessError as e:
            # Clean up if project creation fails
            if os.path.exists(project_path):
                shutil.rmtree(project_path)
            raise Exception(f"Failed to create project: {e.stderr}")
        except Exception as e:
            # Clean up if project creation fails
            if os.path.exists(project_path):
                shutil.rmtree(project_path)
            raise Exception(f"Failed to create project: {str(e)}")

    def _create_project_structure(self, project_path):
        """Create additional directories needed for the project"""
        dirs = [
            os.path.join(project_path, 'templates'),
            os.path.join(project_path, 'static'),
            os.path.join(project_path, 'static', 'css'),
            os.path.join(project_path, 'static', 'js'),
            os.path.join(project_path, 'static', 'images'),
        ]
        
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)

    def _initialize_project_files(self, project_path, project_name):
        """Initialize basic template and static files"""
        # Create base template with a simple string instead of using render_to_string
        base_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name}</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <header>
        <h1>{project_name}</h1>
    </header>
    
    <main>
        {{% block content %}}
        {{% endblock %}}
    </main>
    
    <footer>
        <p>Created with Imagi Oasis</p>
    </footer>
</body>
</html>"""
        
        with open(os.path.join(project_path, 'templates', 'base.html'), 'w') as f:
            f.write(base_template)
            
        # Create basic CSS file
        with open(os.path.join(project_path, 'static', 'css', 'style.css'), 'w') as f:
            f.write('/* Custom styles for your web app */')