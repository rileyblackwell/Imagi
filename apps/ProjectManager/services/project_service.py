import os
import shutil
from datetime import datetime
from django.conf import settings
from ..models import UserProject
from .template_service import ViewTemplateService
import subprocess
from pathlib import Path

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
            
            # Create the project directory
            os.makedirs(project_path, exist_ok=True)
            
            # Create Django project structure
            project_files = {
                '__init__.py': '',
                'asgi.py': self._generate_asgi_content(unique_name),
                'settings.py': self._generate_settings_content(unique_name),
                'urls.py': self._generate_urls_content(),
                'wsgi.py': self._generate_wsgi_content(unique_name),
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
            
            # Initialize basic templates and static files
            self._initialize_project_files(project_path, project_name)
            
            # Create Pipfile
            self._create_pipfile(project_path)
            
            # Initialize pipenv environment
            self._initialize_pipenv(project_path)
            
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
            os.path.join(project_path, 'staticfiles'),
        ]
        
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)

    def _initialize_project_files(self, project_path, project_name):
        """Initialize basic template and static files"""
        # Define Django template tags separately
        load_static = "{% load static %}"
        static_css = "{% static 'css/styles.css' %}"
        block_extra_css = "{% block extra_css %}{% endblock %}"
        block_content = "{% block content %}{% endblock %}"
        block_extra_js = "{% block extra_js %}{% endblock %}"
        
        base_template = f"""{load_static}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name}</title>
    <link rel="stylesheet" href="{static_css}">
    {block_extra_css}
</head>
<body>
    <header>
        <h1>{project_name}</h1>
    </header>
    
    <main>
        {block_content}
    </main>
    
    <footer>
        <p>Created with Imagi Oasis</p>
    </footer>
    {block_extra_js}
</body>
</html>"""
        
        with open(os.path.join(project_path, 'templates', 'base.html'), 'w') as f:
            f.write(base_template)
            
        # Create basic CSS file with correct name (styles.css)
        with open(os.path.join(project_path, 'static', 'css', 'styles.css'), 'w') as f:
            f.write('''/* Global Variables */
:root {
    --primary-color: #3498db;
    --secondary-color: #2ecc71;
    --text-color: #333;
    --background-color: #fff;
}

/* Base Styles */
body {
    font-family: 'Open Sans', sans-serif;
    color: var(--text-color);
    background-color: var(--background-color);
    margin: 0;
    padding: 0;
    line-height: 1.6;
}

/* Layout */
header {
    background-color: var(--primary-color);
    color: white;
    padding: 1rem;
    text-align: center;
}

main {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

footer {
    background-color: #f8f9fa;
    color: var(--text-color);
    text-align: center;
    padding: 1rem;
    margin-top: 2rem;
}
''')

    def _update_project_settings(self, settings_path, project_path, unique_name):
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
TEMPLATES = [
    {{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
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

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = '{unique_name}.urls'
WSGI_APPLICATION = '{unique_name}.wsgi.application'

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

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
"""
        
        # Write the complete settings file
        with open(settings_path, 'w') as f:
            f.write(content + additional_settings)

    def _update_project_views(self, project_path, view_name):
        """Add a new view to the project's views.py file"""
        # Get the project's main directory that contains the settings.py
        project_dir = [d for d in os.listdir(project_path) 
                      if os.path.isdir(os.path.join(project_path, d)) and 
                      os.path.exists(os.path.join(project_path, d, 'settings.py'))][0]
        
        views_path = os.path.join(project_path, project_dir, 'views.py')
        
        # Create views.py if it doesn't exist
        if not os.path.exists(views_path):
            with open(views_path, 'w') as f:
                f.write("from django.shortcuts import render\n\n")
        
        # Check if view already exists
        with open(views_path, 'r') as f:
            existing_content = f.read()
        
        view_signature = f"def {view_name}(request):"
        if view_signature not in existing_content:
            # Add the new view
            with open(views_path, 'a') as f:
                view_code = ViewTemplateService.generate_view_code(view_name)
                f.write(view_code)
                print(f"Added view for {view_name} in {views_path}")

    def _update_project_urls(self, project_path, url_patterns):
        """Update the project's urls.py file"""
        # Get the project's main directory that contains the settings.py
        project_dir = [d for d in os.listdir(project_path) 
                      if os.path.isdir(os.path.join(project_path, d)) and 
                      os.path.exists(os.path.join(project_path, d, 'settings.py'))][0]
        
        urls_path = os.path.join(project_path, project_dir, 'urls.py')
        
        # Generate the complete URLs configuration
        urls_code = ViewTemplateService.generate_urls_code(url_patterns)
        
        # Write the new URLs configuration
        with open(urls_path, 'w') as f:
            f.write(urls_code)
            print(f"Updated URLs in {urls_path}")

    def add_page_to_project(self, project, filename):
        """Add a new page to the project and update views/URLs"""
        try:
            if not filename.endswith('.html') or filename == 'base.html':
                return
            
            # Get view name (remove .html and sanitize)
            view_name = filename[:-5]  # Remove .html
            view_name = ''.join(c if c.isalnum() else '_' for c in view_name)
            
            # Get project path (this is the root project directory)
            project_path = project.project_path
            
            # Update views.py
            self._update_project_views(project_path, view_name)
            
            # Get all HTML files to update URLs
            templates_dir = os.path.join(project_path, 'templates')
            html_files = [f[:-5] for f in os.listdir(templates_dir) 
                         if f.endswith('.html') and f != 'base.html']
            
            # Update urls.py
            self._update_project_urls(project_path, html_files)
            
            print(f"Added view and URL pattern for {filename}")
            
        except Exception as e:
            print(f"Error adding page to project: {str(e)}")

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
        return '''from django.shortcuts import render

def index(request):
    """Render the index page"""
    return render(request, 'index.html')
'''

    def _generate_urls_content(self):
        return '''from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='index'),
]

# Serve static and media files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
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

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

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
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
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
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
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
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
'''

    def _create_pipfile(self, project_path):
        """Create a Pipfile with Django dependencies"""
        pipfile_content = """[[source]]
url = "https://pypi.org/simple"
verify_ssl = true
name = "pypi"

[packages]
django = "*"

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