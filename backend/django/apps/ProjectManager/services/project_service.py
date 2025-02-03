import os
import shutil
from datetime import datetime
from django.conf import settings
from ..models import Project
import subprocess
from pathlib import Path

class ProjectGenerationService:
    def __init__(self, user):
        self.user = user
        self.base_directory = os.path.join(settings.PROJECTS_ROOT, str(user.id))
        os.makedirs(self.base_directory, exist_ok=True)

    def _sanitize_project_name(self, name):
        """Convert project name to a valid Python identifier"""
        sanitized = ''.join(c if c.isalnum() else '_' for c in name)
        if not sanitized[0].isalpha():
            sanitized = 'project_' + sanitized
        return sanitized

    def create_project(self, project_name):
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
            print(f"Creating project at: {project_path}")
            
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
                file_path = os.path.join(package_dir, filename)
                with open(file_path, 'w') as f:
                    f.write(content)
            
            # Create manage.py with correct project name
            manage_content = self._generate_manage_content(unique_name)
            with open(os.path.join(project_path, 'manage.py'), 'w') as f:
                f.write(manage_content)
                os.chmod(f.name, 0o755)
            
            # Create additional directories
            self._create_project_structure(project_path)
            
            # Create Pipfile
            self._create_pipfile(project_path)
            
            # Initialize pipenv environment
            self._initialize_pipenv(project_path)
            
            # Create project record
            project = Project.objects.create(
                user=self.user,
                name=project_name,
                project_path=project_path
            )
            
            print(f"Project created successfully: {project.id}")
            return project
            
        except Exception as e:
            print(f"Error creating project: {str(e)}")
            if os.path.exists(project_path):
                shutil.rmtree(project_path)
            raise Exception(f"Failed to create project: {str(e)}")

    def _create_project_structure(self, project_path):
        """Create additional directories needed for the project"""
        dirs = [
            os.path.join(project_path, 'media'),
            os.path.join(project_path, 'staticfiles'),
            os.path.join(project_path, 'api'),
        ]
        
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)

    def _generate_manage_content(self, project_name):
        """Generate the manage.py content with the correct project name"""
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
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
'''

    def _generate_asgi_content(self, project_name):
        return f'''"""
ASGI config for {project_name} project.
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{project_name}.settings')
application = get_asgi_application()
'''

    def _generate_wsgi_content(self, project_name):
        return f'''"""
WSGI config for {project_name} project.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{project_name}.settings')
application = get_wsgi_application()
'''

    def _generate_views_content(self):
        return '''from rest_framework import viewsets, permissions
from .models import Project
from .serializers import ProjectSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
'''

    def _generate_urls_content(self):
        return '''from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'projects', views.ProjectViewSet, basename='project')

urlpatterns = [
    path('api/', include(router.urls)),
]
'''

    def _generate_models_content(self):
        return '''from django.db import models
from django.conf import settings

class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.user.username}"
'''

    def _generate_serializers_content(self):
        return '''from rest_framework import serializers
from .models import Project

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
'''

    def _generate_settings_content(self, project_name):
        """Generate Django settings.py content with the correct project name"""
        return f'''"""
Django settings for {project_name} project.
"""
from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-development-key-change-this-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

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
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework settings
REST_FRAMEWORK = {{
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}}

# CORS settings
CORS_ALLOWED_ORIGINS = [
    'http://localhost:8080',
    'http://127.0.0.1:8080',
]

CORS_ALLOW_CREDENTIALS = True
'''

    def _create_pipfile(self, project_path):
        """Create a Pipfile with Django dependencies"""
        pipfile_content = """[[source]]
url = "https://pypi.org/simple"
verify_ssl = true
name = "pypi"

[packages]
django = "*"
djangorestframework = "*"
djangorestframework-simplejwt = "*"
django-cors-headers = "*"

[dev-packages]

[requires]
python_version = "3.13"
"""
        pipfile_path = os.path.join(project_path, 'Pipfile')
        with open(pipfile_path, 'w') as f:
            f.write(pipfile_content)

    def _initialize_pipenv(self, project_path):
        """Initialize pipenv environment and install dependencies"""
        try:
            # Change to project directory
            original_dir = os.getcwd()
            os.chdir(project_path)

            # Create setup.py for the project
            setup_content = f"""from setuptools import setup, find_packages

setup(
    name="{os.path.basename(project_path)}",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'django',
        'djangorestframework',
        'djangorestframework-simplejwt',
        'django-cors-headers',
    ],
)
"""
            with open('setup.py', 'w') as f:
                f.write(setup_content)

            # Run pipenv install
            print(f"Initializing pipenv in {project_path}")
            result = subprocess.run(
                ['pipenv', 'install'],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"Pipenv output: {result.stdout}")

            # Install the project package in development mode
            result = subprocess.run(
                ['pipenv', 'run', 'pip', 'install', '-e', '.'],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"Package install output: {result.stdout}")

            # Change back to original directory
            os.chdir(original_dir)

        except subprocess.CalledProcessError as e:
            print(f"Error running pipenv: {e.stdout} {e.stderr}")
            raise Exception(f"Failed to initialize pipenv: {str(e)}")
        except Exception as e:
            print(f"Error in _initialize_pipenv: {str(e)}")
            raise

    def delete_project(self, project_name):
        """Delete a project's files from the filesystem"""
        try:
            # Find all active projects with this name for this user
            projects = Project.objects.filter(
                user=self.user,
                name=project_name,
                is_active=True
            ).order_by('-updated_at')  # Get most recently updated first

            if not projects.exists():
                print(f"Project not found: {project_name}")
                return False

            # Get the most recently updated project
            project = projects.first()
            project_path = project.project_path

            # Delete project directory if it exists
            if os.path.exists(project_path):
                shutil.rmtree(project_path)
                print(f"Project files deleted successfully at: {project_path}")

            # Mark all duplicate projects as inactive
            projects.update(is_active=False)

            return True
        except Exception as e:
            print(f"Error deleting project: {str(e)}")
            raise