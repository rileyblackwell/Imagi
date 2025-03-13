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
                'views.py': self._generate_views_content(),
            }
            
            # Create project package directory using unique name
            package_dir = os.path.join(project_path, unique_name)
            os.makedirs(package_dir, exist_ok=True)
            
            # Create project files
            for filename, content in project_files.items():
                with open(os.path.join(package_dir, filename), 'w') as f:
                    f.write(content)
            
            # Create manage.py
            with open(os.path.join(project_path, 'manage.py'), 'w') as f:
                f.write(self._generate_manage_content(unique_name))
            
            # Create Pipfile instead of requirements.txt
            with open(os.path.join(project_path, 'Pipfile'), 'w') as f:
                f.write(self._generate_pipfile_content())
            
            # Create .gitignore
            with open(os.path.join(project_path, '.gitignore'), 'w') as f:
                f.write(self._generate_gitignore_content())
            
            # Create README.md
            with open(os.path.join(project_path, 'README.md'), 'w') as f:
                f.write(self._generate_readme_content(project_name))
            
            # Create necessary directories
            os.makedirs(os.path.join(project_path, 'static', 'css'), exist_ok=True)
            os.makedirs(os.path.join(project_path, 'templates'), exist_ok=True)
            
            # Create default files
            self._create_default_files(project_path)
                
            return project_path
        except Exception as e:
            logger.error(f"Error creating project: {str(e)}")
            # Clean up failed project directory
            if os.path.exists(project_path):
                shutil.rmtree(project_path, ignore_errors=True)
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
        'DIRS': [BASE_DIR / 'templates'],
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
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

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
from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
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

    def _generate_views_content(self):
        return '''"""
Project views
"""
# You can define your views here if needed.
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