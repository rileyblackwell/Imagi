import os
import shutil
import subprocess
import re
import logging
from datetime import datetime
from django.conf import settings
from rest_framework.exceptions import ValidationError
from ..models import Project
from django.utils import timezone

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
            project_path = self._create_project_files(project)
            
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

    def _create_project_files(self, project):
        """Create a new Django project using django-admin startproject"""
        # First, deactivate any existing active projects with the same name
        existing_projects = Project.objects.filter(
            user=self.user,
            name=project.name,
            is_active=True
        )
        if existing_projects.exists():
            existing_projects.update(is_active=False)

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        sanitized_name = self._sanitize_project_name(project.name)
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
            
            # Create views.py in the project directory alongside settings.py
            project_dir = os.path.join(project_path, unique_name)
            views_path = os.path.join(project_dir, 'views.py')
            with open(views_path, 'w') as f:
                f.write(self._generate_basic_project_views_content())
            
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
                f.write(self._generate_readme_content(project.name))
            
            # Create template and static files
            self._create_default_files(project_path, project.name, project.description)
            
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

    def _create_default_files(self, project_path, project_name, project_description):
        """Create default files for a new project."""
        # Generate personalized content
        safe_project_name = project_name.replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
        safe_description = (project_description or '').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
        
        # Create description content for templates
        description_content = ''
        if project_description and project_description.strip():
            description_content = f'    <p class="project-description">{safe_description}</p>'
        
        default_files = {
            'templates/base.html': f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{% block title %}}{safe_project_name}{{% endblock %}}</title>
    <link rel="stylesheet" href="/static/css/styles.css">
    {{% block extra_css %}}{{% endblock %}}
</head>
<body>
    {{% block content %}}{{% endblock %}}
    
    {{% block extra_js %}}{{% endblock %}}
</body>
</html>
''',
            'templates/index.html': f'''
{{% extends 'base.html' %}}
{{% load static %}}

{{% block title %}}Welcome | {safe_project_name}{{% endblock %}}

{{% block content %}}
<div class="welcome-container">
    <h1>Welcome to {safe_project_name}</h1>
{description_content}
    <p>This is your starting point for building amazing Django applications.</p>
    <div class="cta-button">
        <a href="/admin/">Go to Admin</a>
    </div>
</div>
{{% endblock %}}
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

.project-description {
    font-size: 1.125rem;
    color: #6b7280;
    margin: 1.5rem 0;
    font-style: italic;
    line-height: 1.6;
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
            if not project.project_path:
                logger.error("Project path is not set")
                raise ValueError("Project path is not set")
                
            # Ensure the parent directory exists
            parent_dir = os.path.dirname(project.project_path)
            if not os.path.exists(parent_dir):
                try:
                    os.makedirs(parent_dir, exist_ok=True)
                    logger.info(f"Created parent directory for project: {parent_dir}")
                except Exception as dir_err:
                    logger.error(f"Failed to create parent directory: {str(dir_err)}")
                    raise ValueError(f"Failed to create parent directory: {str(dir_err)}")
                
            # Now check/create the project directory
            if not os.path.exists(project.project_path):
                logger.error(f"Project directory does not exist: {project.project_path}")
                # Try to create it if it doesn't exist
                try:
                    os.makedirs(project.project_path, exist_ok=True)
                    logger.info(f"Created missing project directory: {project.project_path}")
                except Exception as dir_err:
                    logger.error(f"Failed to create project directory: {str(dir_err)}")
                    raise ValueError(f"Failed to create project directory: {str(dir_err)}")
            
            project_path = project.project_path
            project_name = os.path.basename(project_path)
            
            logger.info(f"Initializing project '{project.name}' (ID: {project.id}) at path: {project_path}")
            
            # First ensure the basic project structure exists
            if not self._ensure_project_structure(project_path, project_name):
                logger.error(f"Failed to ensure basic project structure for {project_name}")
                raise ValueError(f"Failed to create basic project structure for {project_name}")
            
            # Now try to find the manage.py to determine the correct inner project directory
            inner_project_dir = project_path
            manage_py_found = False
            
            # Look for manage.py in the project directory
            for root, dirs, files in os.walk(project_path):
                if 'manage.py' in files:
                    inner_project_dir = root
                    manage_py_found = True
                    logger.info(f"Found manage.py in {inner_project_dir}")
                    break
            
            if not manage_py_found:
                logger.warning(f"manage.py not found in project structure, using project root: {inner_project_dir}")
            
            # Mark the project as initialized
            project.is_initialized = True
            project.updated_at = timezone.now()
            project.generation_status = 'completed'
            project.save()
            
            logger.info(f"Project {project.name} (ID: {project.id}) successfully initialized")
            
            # Return either the project object or a dictionary with appropriate status
            return {
                'success': True,
                'message': 'Project initialized successfully',
                'is_initialized': True,
                'project_id': project.id,
                'name': project.name
            }
        
        except Exception as e:
            logger.error(f"Error initializing project: {str(e)}")
            # Add stack trace for better debugging
            import traceback
            logger.error(f"Stack trace: {traceback.format_exc()}")
            
            # Try to update the project status if possible
            try:
                if project and hasattr(project, 'id'):
                    project.generation_status = 'failed'
                    project.save()
            except:
                pass  # Silently ignore errors in the error handler
                
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
    
    def _generate_basic_project_urls(self):
        """Generate content for a basic project urls.py file"""
        return """from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
]
"""

    def _generate_basic_project_views_content(self):
        """Generate content for a basic project views.py file"""
        return """from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView

def home(request):
    \"\"\"Home page view.\"\"\"
    return render(request, 'index.html')

class HomeView(TemplateView):
    \"\"\"Class-based home page view.\"\"\"
    template_name = 'index.html'
"""

    def _generate_basic_manage_py(self, project_name):
        """Generate a minimal Django manage.py file"""
        return f"""#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{project_name}.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
"""

    def _generate_basic_settings_py(self, project_name):
        """Generate a minimal Django settings.py file"""
        secret_key = ''.join(['x' for _ in range(50)])  # Placeholder secret key
        return f"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '{secret_key}'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

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
    'core',
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
DATABASES = {{
    'default': {{
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }}
}}

# Password validation
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Default primary key field type
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
"""

    def _ensure_project_structure(self, project_path, project_name):
        """
        Ensure the basic project structure exists
        This is a fallback if the initialization commands failed
        """
        try:
            logger.info(f"Ensuring basic project structure for {project_name} at {project_path}")
            
            # Make sure the project path exists
            if not os.path.exists(project_path):
                logger.warning(f"Creating project directory: {project_path}")
                os.makedirs(project_path, exist_ok=True)
            
            # Ensure the project package directory exists
            project_package_dir = os.path.join(project_path, project_name)
            if not os.path.exists(project_package_dir):
                logger.info(f"Creating project package directory: {project_package_dir}")
                os.makedirs(project_package_dir, exist_ok=True)
            
            # Create __init__.py if it doesn't exist
            init_path = os.path.join(project_package_dir, '__init__.py')
            if not os.path.exists(init_path):
                with open(init_path, 'w') as f:
                    f.write("# Generated by Imagi Oasis\n")
                logger.info(f"Created __init__.py at {init_path}")
                
            # Create a minimal manage.py if it doesn't exist anywhere
            manage_path = os.path.join(project_path, 'manage.py')
            manage_py_found = os.path.exists(manage_path)
            
            if not manage_py_found:
                for root, dirs, files in os.walk(project_path):
                    if 'manage.py' in files:
                        manage_py_found = True
                        break
            
            if not manage_py_found:
                logger.warning(f"manage.py not found, creating minimal version at {manage_path}")
                with open(manage_path, 'w') as f:
                    f.write(self._generate_basic_manage_py(project_name))
                # Make it executable
                try:
                    os.chmod(manage_path, 0o755)
                except:
                    logger.warning(f"Could not make manage.py executable: {manage_path}")
                    
            # Create minimal required dirs
            dirs_to_create = [
                os.path.join(project_path, 'static'),
                os.path.join(project_path, 'static', 'css'),
                os.path.join(project_path, 'templates'),
                os.path.join(project_path, 'media'),
            ]
            
            for dir_path in dirs_to_create:
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path, exist_ok=True)
                    logger.info(f"Created directory: {dir_path}")
            
            # Create a minimal settings.py if it doesn't exist
            settings_path = os.path.join(project_package_dir, 'settings.py')
            if not os.path.exists(settings_path):
                with open(settings_path, 'w') as f:
                    f.write(self._generate_basic_settings_py(project_name))
                logger.info(f"Created settings.py at {settings_path}")
                
            # Create a minimal urls.py if it doesn't exist
            urls_path = os.path.join(project_package_dir, 'urls.py')
            if not os.path.exists(urls_path):
                with open(urls_path, 'w') as f:
                    f.write(self._generate_basic_project_urls())
                logger.info(f"Created urls.py at {urls_path}")
                
            # Create a minimal views.py if it doesn't exist
            views_path = os.path.join(project_package_dir, 'views.py')
            if not os.path.exists(views_path):
                with open(views_path, 'w') as f:
                    f.write(self._generate_basic_project_views_content())
                logger.info(f"Created views.py at {views_path}")
                
            logger.info(f"Basic project structure ensured for {project_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error ensuring project structure: {str(e)}")
            import traceback
            logger.error(f"Stack trace: {traceback.format_exc()}")
            # Don't raise the exception, just return False
            return False 