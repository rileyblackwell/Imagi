import os
import shutil
import subprocess
import tempfile
import re
import logging
from datetime import datetime
from pathlib import Path
from django.conf import settings
from rest_framework.exceptions import ValidationError
from typing import List, Optional
from ..models import Project

logger = logging.getLogger(__name__)

class ProjectCreationService:
    def __init__(self, user):
        self.user = user
        self.base_directory = os.path.join(settings.PROJECTS_ROOT, str(user.id))
        os.makedirs(self.base_directory, exist_ok=True)

    def create_project(self, name_or_project):
        """
        Create a new project.
        Can accept either a project name (string) or a Project instance.
        """
        try:
            # Handle both string name and Project instance
            if isinstance(name_or_project, str):
                # Create a project object
                project = Project.objects.create(
                    user=self.user,
                    name=name_or_project
                )
            else:
                project = name_or_project
                
            # Generate project files
            project_path = self._create_project_files(project.name)
            
            # Update project with path
            project.project_path = project_path
            project.save()
            
            logger.info(f"Project successfully created at: {project_path}")
            
            return project
        except Exception as e:
            logger.error(f"Error creating project: {str(e)}")
            if isinstance(name_or_project, Project):
                name_or_project.delete(hard_delete=True)
            raise ValidationError(f"Failed to generate project files: {str(e)}")

    def _sanitize_project_name(self, name):
        """Convert project name to a valid Python identifier"""
        sanitized = ''.join(c if c.isalnum() else '_' for c in name)
        if not sanitized[0].isalpha():
            sanitized = 'project_' + sanitized
        return sanitized

    def _create_project_files(self, project_name):
        """Create a new Django project using django-admin startproject"""
        # First, deactivate any existing active projects with the same name
        existing_projects = Project.objects.filter(
            user=self.user,
            name=project_name,
            is_active=True
        )
        if existing_projects.exists():
            existing_projects.update(is_active=False)

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        sanitized_name = self._sanitize_project_name(project_name)
        unique_name = f"{sanitized_name}_{timestamp}"
        project_path = os.path.join(self.base_directory, unique_name)
        
        try:
            logger.info(f"Creating project at: {project_path}")
            
            # Create the project directory
            os.makedirs(project_path, exist_ok=True)
            
            # Use Django's startproject command to create the basic project structure
            subprocess.run([
                'django-admin', 'startproject', 
                unique_name,  # Project name
                project_path  # Destination directory
            ], check=True)
            
            # Create necessary directories
            os.makedirs(os.path.join(project_path, 'static', 'css'), exist_ok=True)
            os.makedirs(os.path.join(project_path, 'templates'), exist_ok=True)
            
            # Create Pipfile instead of requirements.txt
            with open(os.path.join(project_path, 'Pipfile'), 'w') as f:
                f.write(self._generate_pipfile_content())
            
            # Create .gitignore
            with open(os.path.join(project_path, '.gitignore'), 'w') as f:
                f.write(self._generate_gitignore_content())
            
            # Create README.md
            with open(os.path.join(project_path, 'README.md'), 'w') as f:
                f.write(self._generate_readme_content(project_name))
            
            # Create template and static files
            self._create_default_files(project_path)
            
            # Update settings.py to include templates and static files directories
            self._update_settings(project_path, unique_name)
            
            # Update urls.py to serve the index template
            self._update_urls(project_path, unique_name)
                
            return project_path
        except Exception as e:
            logger.error(f"Error creating project: {str(e)}")
            # Clean up failed project directory
            if os.path.exists(project_path):
                shutil.rmtree(project_path, ignore_errors=True)
            raise

    def _update_settings(self, project_path, project_name):
        """Update the Django settings.py file to include templates and static files directories"""
        settings_path = os.path.join(project_path, project_name, 'settings.py')
        
        with open(settings_path, 'r') as f:
            settings_content = f.read()
        
        # Add rest_framework and corsheaders to INSTALLED_APPS
        installed_apps_pattern = r"INSTALLED_APPS = \[\n(.*?)\]"
        installed_apps_match = re.search(installed_apps_pattern, settings_content, re.DOTALL)
        if installed_apps_match:
            current_apps = installed_apps_match.group(1)
            updated_apps = current_apps + "    'rest_framework',\n    'corsheaders',\n"
            settings_content = settings_content.replace(current_apps, updated_apps)
        
        # Add corsheaders middleware
        middleware_pattern = r"MIDDLEWARE = \[\n(.*?)\]"
        middleware_match = re.search(middleware_pattern, settings_content, re.DOTALL)
        if middleware_match:
            current_middleware = middleware_match.group(1)
            updated_middleware = current_middleware.replace(
                "    'django.middleware.common.CommonMiddleware',", 
                "    'corsheaders.middleware.CorsMiddleware',\n    'django.middleware.common.CommonMiddleware',"
            )
            settings_content = settings_content.replace(current_middleware, updated_middleware)
        
        # Add templates dir to TEMPLATES setting
        templates_pattern = r"'DIRS': \[\],"
        templates_replacement = "'DIRS': [BASE_DIR / 'templates'],"
        settings_content = re.sub(templates_pattern, templates_replacement, settings_content)
        
        # Add STATICFILES_DIRS setting
        static_files_pattern = r"STATIC_URL = 'static/'"
        static_files_replacement = "STATIC_URL = 'static/'\nSTATICFILES_DIRS = [\n    BASE_DIR / 'static',\n]"
        settings_content = re.sub(static_files_pattern, static_files_replacement, settings_content)
        
        # Add CORS and REST Framework settings
        if "# Default primary key field type" in settings_content:
            additional_settings = """
# CORS settings
CORS_ALLOW_ALL_ORIGINS = True

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
"""
            settings_content = settings_content.replace(
                "# Default primary key field type",
                additional_settings + "\n# Default primary key field type"
            )
        
        with open(settings_path, 'w') as f:
            f.write(settings_content)

    def _update_urls(self, project_path, project_name):
        """Update the Django urls.py file to serve the index template"""
        urls_path = os.path.join(project_path, project_name, 'urls.py')
        
        with open(urls_path, 'r') as f:
            urls_content = f.read()
        
        # Add import for TemplateView
        if 'TemplateView' not in urls_content:
            urls_content = urls_content.replace(
                'from django.urls import path',
                'from django.urls import path\nfrom django.views.generic import TemplateView'
            )
        
        # Add path for home page
        if 'path(\'\', TemplateView' not in urls_content:
            urls_content = urls_content.replace(
                'urlpatterns = [',
                'urlpatterns = [\n    path(\'\', TemplateView.as_view(template_name=\'index.html\'), name=\'home\'),'
            )
        
        with open(urls_path, 'w') as f:
            f.write(urls_content)

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
    
    {% block extra_js %}{% endblock %}
</body>
</html>
''',
            'templates/index.html': '''
{% extends 'base.html' %}
{% load static %}

{% block title %}Welcome | My Oasis App{% endblock %}

{% block content %}
<div class="welcome-container">
    <h1>Welcome to your new Oasis App</h1>
    <p>This is your starting point for building amazing Django applications.</p>
    <div class="cta-button">
        <a href="/admin/">Go to Admin</a>
    </div>
</div>
{% endblock %}
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

.welcome-container {
    max-width: 800px;
    margin: 5rem auto;
    padding: 2rem;
    background-color: #f9fafb;
    border-radius: 0.5rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    text-align: center;
}

h1 {
    color: var(--primary-color);
    margin-bottom: 1rem;
}

.cta-button {
    margin-top: 2rem;
}

.cta-button a {
    display: inline-block;
    background-color: var(--primary-color);
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: 0.375rem;
    text-decoration: none;
    font-weight: 500;
    transition: background-color 0.2s;
}

.cta-button a:hover {
    background-color: var(--secondary-color);
}
'''
        }
        
        for file_path, content in default_files.items():
            full_path = os.path.join(project_path, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content.strip())

    def _generate_pipfile_content(self):
        return '''[[source]]
url = "https://pypi.org/simple"
verify_ssl = true
name = "pypi"

[packages]
django = "~=4.2.3"
djangorestframework = "~=3.14.0"
django-cors-headers = "~=4.1.0"

[dev-packages]

[requires]
python_version = "3.10"
'''

    def _generate_gitignore_content(self):
        return '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
media

# Virtual Environment
venv/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo

# macOS
.DS_Store

# Windows
Thumbs.db
'''

    def _generate_readme_content(self, project_name):
        return f'''# {project_name}

A Django REST API project.

## Getting Started

### Prerequisites

- Python 3.8+
- pipenv

### Installation

1. Clone the repository
2. Install dependencies:
   ```
   pipenv install
   ```
3. Activate the virtual environment:
   ```
   pipenv shell
   ```
4. Run migrations:
   ```
   python manage.py migrate
   ```
5. Create a superuser:
   ```
   python manage.py createsuperuser
   ```
6. Run the development server:
   ```
   python manage.py runserver
   ```

## Features

- Django REST framework API
- CORS enabled
- SQLite database (for development)
'''

    def initialize_project(self, project):
        """
        Initialize a project after it has been created.
        This method sets up additional project structure and marks it as initialized.
        """
        try:
            if not project.project_path or not os.path.exists(project.project_path):
                raise ValueError("Project directory does not exist")
            
            project_path = project.project_path
            
            # Create a default Django app within the project
            main_app_name = 'core'
            project_name = os.path.basename(project_path)
            
            # Get the inner project directory (where manage.py is)
            inner_project_dir = os.path.join(project_path, project_name)
            if not os.path.exists(inner_project_dir):
                # Try to find the manage.py to determine the correct directory
                for root, dirs, files in os.walk(project_path):
                    if 'manage.py' in files:
                        inner_project_dir = root
                        break
            
            # Create the main app
            subprocess.run([
                'python', os.path.join(inner_project_dir, 'manage.py'),
                'startapp', main_app_name
            ], cwd=inner_project_dir, check=True)
            
            # Create basic models, views, and urls for the main app
            app_path = os.path.join(inner_project_dir, main_app_name)
            
            # Update models.py with a basic model
            with open(os.path.join(app_path, 'models.py'), 'w') as f:
                f.write(self._generate_basic_model_content())
            
            # Update views.py with basic views
            with open(os.path.join(app_path, 'views.py'), 'w') as f:
                f.write(self._generate_basic_views_content())
            
            # Create urls.py for the app
            with open(os.path.join(app_path, 'urls.py'), 'w') as f:
                f.write(self._generate_basic_urls_content())
            
            # Update the project's settings.py to include the new app
            project_settings_path = os.path.join(inner_project_dir, project_name, 'settings.py')
            with open(project_settings_path, 'r') as f:
                settings_content = f.read()
            
            if main_app_name not in settings_content:
                # Add the app to INSTALLED_APPS
                installed_apps_pattern = r"INSTALLED_APPS = \[\n(.*?)\]"
                installed_apps_match = re.search(installed_apps_pattern, settings_content, re.DOTALL)
                if installed_apps_match:
                    current_apps = installed_apps_match.group(1)
                    updated_apps = current_apps + f"    '{main_app_name}',\n"
                    settings_content = settings_content.replace(current_apps, updated_apps)
                
                with open(project_settings_path, 'w') as f:
                    f.write(settings_content)
            
            # Update the project's main urls.py to include the app urls
            project_urls_path = os.path.join(inner_project_dir, project_name, 'urls.py')
            with open(project_urls_path, 'r') as f:
                urls_content = f.read()
            
            if f"include('{main_app_name}.urls')" not in urls_content:
                # Add import for include if not present
                if 'include' not in urls_content:
                    urls_content = urls_content.replace(
                        'from django.urls import path',
                        'from django.urls import path, include'
                    )
                
                # Add the app's URLs to the urlpatterns
                urls_content = urls_content.replace(
                    'urlpatterns = [',
                    f'urlpatterns = [\n    path(\'{main_app_name}/\', include(\'{main_app_name}.urls\')),'
                )
                
                with open(project_urls_path, 'w') as f:
                    f.write(urls_content)
            
            # Mark the project as initialized
            project.is_initialized = True
            project.save()
            
            return project
        
        except Exception as e:
            logger.error(f"Error initializing project: {str(e)}")
            raise ValueError(f"Failed to initialize project: {str(e)}")
    
    def _generate_basic_model_content(self):
        """Generate content for a basic Django model"""
        return """from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
"""
    
    def _generate_basic_views_content(self):
        """Generate content for basic Django views"""
        return """from django.shortcuts import render
from django.http import JsonResponse
from .models import Item

def index(request):
    \"\"\"Render the index page\"\"\"
    items = Item.objects.all()
    return render(request, 'core/index.html', {'items': items})

def item_list(request):
    \"\"\"Return a JSON list of items\"\"\"
    items = Item.objects.all().values('id', 'name', 'description')
    return JsonResponse({'items': list(items)})
"""
    
    def _generate_basic_urls_content(self):
        """Generate content for basic Django URLs"""
        return """from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/items/', views.item_list, name='item-list'),
]
""" 