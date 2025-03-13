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
            
            # Initialize project with default files
            self._initialize_project_files(project_path)
            
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
            
            # Create Django project structure
            project_files = {
                '__init__.py': '',
                'asgi.py': self._generate_asgi_content(unique_name),
                'settings.py': self._generate_settings_content(unique_name),
                'urls.py': self._generate_urls_content(),
                'wsgi.py': self._generate_wsgi_content(unique_name),
                'models.py': self._generate_models_content(),
                'serializers.py': self._generate_serializers_content(),
                'views.py': self._generate_views_content(),
            }
            
            # Create project package directory using unique name
            package_dir = os.path.join(project_path, unique_name)
            os.makedirs(package_dir, exist_ok=True)
            
            # Create project files
            for filename, content in project_files.items():
                with open(os.path.join(package_dir, filename), 'w') as f:
                    f.write(content)
            
            # Create main app directory
            app_dir = os.path.join(project_path, 'main_app')
            os.makedirs(app_dir, exist_ok=True)
            
            # Create app files
            app_files = {
                '__init__.py': '',
                'admin.py': self._generate_admin_content(),
                'apps.py': self._generate_apps_content(),
                'models.py': self._generate_app_models_content(),
                'serializers.py': self._generate_app_serializers_content(),
                'views.py': self._generate_app_views_content(),
                'urls.py': self._generate_app_urls_content(),
            }
            
            for filename, content in app_files.items():
                with open(os.path.join(app_dir, filename), 'w') as f:
                    f.write(content)
            
            # Create manage.py
            with open(os.path.join(project_path, 'manage.py'), 'w') as f:
                f.write(self._generate_manage_content(unique_name))
            
            # Create requirements.txt
            with open(os.path.join(project_path, 'requirements.txt'), 'w') as f:
                f.write(self._generate_requirements_content())
            
            # Create .gitignore
            with open(os.path.join(project_path, '.gitignore'), 'w') as f:
                f.write(self._generate_gitignore_content())
            
            # Create README.md
            with open(os.path.join(project_path, 'README.md'), 'w') as f:
                f.write(self._generate_readme_content(project_name))
                
            return project_path
        except Exception as e:
            logger.error(f"Error creating project: {str(e)}")
            # Clean up failed project directory
            if os.path.exists(project_path):
                shutil.rmtree(project_path, ignore_errors=True)
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
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content.strip())

    def initialize_project(self, project):
        """Initialize a new Django project with standard files.
        
        This method creates a standard Django project structure with:
        1. Django project files via django-admin startproject
        2. Pipfile for dependency management
        3. templates/base.html and templates/index.html
        4. static/styles.css
        """
        # Base directory for Oasis projects
        projects_root = Path(settings.PROJECTS_ROOT)
        
        # Project-specific directory
        project_dir = projects_root / str(project.id)
        
        # Create project directory if it doesn't exist
        os.makedirs(project_dir, exist_ok=True)
        
        # Run django-admin startproject in a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize Django project
            subprocess.run([
                'django-admin', 'startproject', 
                'config',  # Using 'config' as the project name
                temp_dir
            ], check=True)
            
            # Copy Django project files to the project directory
            for item in os.listdir(temp_dir):
                item_path = os.path.join(temp_dir, item)
                if os.path.isfile(item_path):
                    with open(item_path, 'rb') as src_file:
                        with open(os.path.join(project_dir, item), 'wb') as dst_file:
                            dst_file.write(src_file.read())
                elif os.path.isdir(item_path) and item == 'config':
                    # Ensure config directory exists
                    os.makedirs(os.path.join(project_dir, 'config'), exist_ok=True)
                    
                    # Copy all files from the config directory
                    for config_file in os.listdir(item_path):
                        config_file_path = os.path.join(item_path, config_file)
                        if os.path.isfile(config_file_path):
                            with open(config_file_path, 'rb') as src_file:
                                with open(os.path.join(project_dir, 'config', config_file), 'wb') as dst_file:
                                    dst_file.write(src_file.read())
        
        # Create templates directory
        templates_dir = project_dir / 'templates'
        os.makedirs(templates_dir, exist_ok=True)
        
        # Create static directory and css subdirectory
        static_dir = project_dir / 'static'
        css_dir = static_dir / 'css'
        os.makedirs(css_dir, exist_ok=True)
        
        # Create base.html
        base_html_content = """<!DOCTYPE html>
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
        
        with open(os.path.join(templates_dir, 'base.html'), 'w') as f:
            f.write(base_html_content)
        
        # Create index.html
        index_html_content = """{% extends "base.html" %}
{% load static %}

{% block title %}Home | Django Project{% endblock %}

{% block content %}
<div class="welcome-section">
  <h2>Welcome to your new Django project</h2>
  <p>This is the homepage of your Django application.</p>
  <p>Edit this template to start building your web application.</p>
</div>
{% endblock %}"""
        
        with open(os.path.join(templates_dir, 'index.html'), 'w') as f:
            f.write(index_html_content)
        
        # Create styles.css
        styles_css_content = """/* Main stylesheet */

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
        
        with open(os.path.join(css_dir, 'styles.css'), 'w') as f:
            f.write(styles_css_content)
        
        # Create Pipfile
        pipfile_content = """[[source]]
url = "https://pypi.org/simple"
verify_ssl = true
name = "pypi"

[packages]
django = "~=4.2.0"

[dev-packages]

[requires]
python_version = "3.10"
"""
        
        with open(os.path.join(project_dir, 'Pipfile'), 'w') as f:
            f.write(pipfile_content)
        
        # Update settings.py to include templates and static directories
        settings_path = os.path.join(project_dir, 'config', 'settings.py')
        
        with open(settings_path, 'r') as f:
            settings_content = f.read()
        
        # Add templates dir to TEMPLATES setting
        templates_pattern = r"'DIRS': \[\],"
        templates_replacement = "'DIRS': [BASE_DIR / 'templates'],"
        settings_content = re.sub(templates_pattern, templates_replacement, settings_content)
        
        # Add STATICFILES_DIRS setting
        static_files_pattern = r"STATIC_URL = 'static/'"
        static_files_replacement = "STATIC_URL = 'static/'\nSTATICFILES_DIRS = [\n    BASE_DIR / 'static',\n]"
        settings_content = re.sub(static_files_pattern, static_files_replacement, settings_content)
        
        with open(settings_path, 'w') as f:
            f.write(settings_content)
        
        # Update urls.py to include a path for the home page
        urls_path = os.path.join(project_dir, 'config', 'urls.py')
        
        with open(urls_path, 'r') as f:
            urls_content = f.read()
        
        if 'TemplateView' not in urls_content:
            # Add import for TemplateView
            urls_content = urls_content.replace(
                'from django.urls import path', 
                'from django.urls import path\nfrom django.views.generic import TemplateView'
            )
            
            # Add path for home page
            urls_content = urls_content.replace(
                'urlpatterns = [', 
                'urlpatterns = [\n    path(\'\', TemplateView.as_view(template_name=\'index.html\'), name=\'home\'),'
            )
            
            with open(urls_path, 'w') as f:
                f.write(urls_content)
        
        # Mark the project as initialized in the database
        project.is_initialized = True
        project.save(update_fields=['is_initialized'])
        
        return project

    # Template generation methods
    def _generate_asgi_content(self, project_name):
        return f'''"""
ASGI config for {project_name} project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{project_name}.settings')

application = get_asgi_application()
'''

    def _generate_settings_content(self, project_name):
        return f'''"""
Django settings for {project_name} project.

Generated by Django 4.2.3
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-{os.urandom(16).hex()}'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'main_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = '{project_name}.urls'

TEMPLATES = [
    {{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {{
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        }},
    }},
]

WSGI_APPLICATION = '{project_name}.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {{
    'default': {{
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }}
}}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {{
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    }},
    {{
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    }},
    {{
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    }},
    {{
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    }},
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True

# REST Framework settings
REST_FRAMEWORK = {{
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}}
'''

    def _generate_urls_content(self):
        return '''"""
URL Configuration
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('main_app.urls')),
]
'''

    def _generate_wsgi_content(self, project_name):
        return f'''"""
WSGI config for {project_name} project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{project_name}.settings')

application = get_wsgi_application()
'''

    def _generate_models_content(self):
        return '''"""
Project models
"""
# You can define your models here if needed.
'''

    def _generate_serializers_content(self):
        return '''"""
Project serializers
"""
# You can define your serializers here if needed.
'''

    def _generate_views_content(self):
        return '''"""
Project views
"""
# You can define your views here if needed.
'''

    def _generate_admin_content(self):
        return '''from django.contrib import admin
from .models import Item

# Register your models here.
admin.site.register(Item)
'''

    def _generate_apps_content(self):
        return '''from django.apps import AppConfig


class MainAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main_app'
'''

    def _generate_app_models_content(self):
        return '''from django.db import models

class Item(models.Model):
    """Example model for the main app"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
'''

    def _generate_app_serializers_content(self):
        return '''from rest_framework import serializers
from .models import Item

class ItemSerializer(serializers.ModelSerializer):
    """Serializer for the Item model"""
    class Meta:
        model = Item
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
'''

    def _generate_app_views_content(self):
        return '''from rest_framework import viewsets
from .models import Item
from .serializers import ItemSerializer

class ItemViewSet(viewsets.ModelViewSet):
    """ViewSet for the Item model"""
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
'''

    def _generate_app_urls_content(self):
        return '''from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ItemViewSet

router = DefaultRouter()
router.register(r'items', ItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
'''

    def _generate_manage_content(self, project_name):
        return f'''#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{project_name}.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
'''

    def _generate_requirements_content(self):
        return '''Django==4.2.3
djangorestframework==3.14.0
django-cors-headers==4.1.0
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
- pip

### Installation

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
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

## API Endpoints

- Admin panel: `/admin/`
- API root: `/api/`
- Items API: `/api/items/`

## Features

- Django REST framework API
- CORS enabled
- SQLite database (for development)
''' 