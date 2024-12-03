import os
import subprocess
import shutil
from datetime import datetime
from django.conf import settings
from django.template.loader import render_to_string
from ..models import UserProject

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
            print(f"Creating project at: {project_path}")
            
            # Ensure the directory doesn't exist
            if os.path.exists(project_path):
                shutil.rmtree(project_path)
            
            # Create the project directory
            os.makedirs(project_path, exist_ok=True)
            
            # Create Django project directly in the target directory
            print(f"Running django-admin startproject {unique_name}")
            result = subprocess.run(
                ["django-admin", "startproject", unique_name, project_path],
                check=True,
                capture_output=True,
                text=True
            )
            print(f"django-admin output: {result.stdout}")
            if result.stderr:
                print(f"django-admin errors: {result.stderr}")
            
            # Create additional directories
            self._create_project_structure(project_path)
            
            # Initialize basic templates and static files
            self._initialize_project_files(project_path, project_name)
            
            # Update project settings
            settings_path = os.path.join(project_path, unique_name, 'settings.py')
            print(f"Updating settings at: {settings_path}")
            self._update_project_settings(settings_path, project_path)
            
            # Create project record
            project = UserProject.objects.create(
                user=self.user,
                name=project_name,
                project_path=project_path
            )
            
            print(f"UserProject created successfully: {project.id}")
            return project
            
        except Exception as e:
            print(f"Error creating project: {str(e)}")
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
            os.path.join(project_path, 'media'),
        ]
        
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)

    def _initialize_project_files(self, project_path, project_name):
        """Initialize basic template and static files"""
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

    def _update_project_settings(self, settings_path, project_path):
        """Update the Django project settings"""
        with open(settings_path, 'r') as f:
            content = f.read()
        
        # Add necessary imports
        if 'import os' not in content:
            content = 'import os\nfrom pathlib import Path\n' + content
        
        # Update BASE_DIR definition
        content = content.replace(
            "BASE_DIR = Path(__file__).resolve().parent.parent",
            "BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))"
        )

        # Add development settings
        additional_settings = f"""
# Development settings
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Templates
TEMPLATES[0]['DIRS'] = [
    os.path.join(BASE_DIR, 'templates'),
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security settings for development
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

# Database settings
DATABASES = {{
    'default': {{
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }}
}}

# Add staticfiles app
INSTALLED_APPS += [
    'django.contrib.staticfiles',
]
"""
        
        # Append the additional settings
        with open(settings_path, 'w') as f:
            f.write(content + additional_settings)