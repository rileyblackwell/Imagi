import os
import shutil
import subprocess
import re
import logging
import threading
from datetime import datetime
from django.conf import settings
from rest_framework.exceptions import ValidationError
from ..models import Project
from django.utils import timezone
from .codegen import templates as tpl

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
        """Create a new full-stack project with VueJS frontend and Django backend"""
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
            logger.info(f"Creating full-stack project at: {project_path}")
            
            # Create the main project directory
            os.makedirs(project_path, exist_ok=True)
            
            # Create frontend and backend directories
            frontend_path = os.path.join(project_path, 'frontend', 'vuejs')
            backend_path = os.path.join(project_path, 'backend', 'django')
            os.makedirs(frontend_path, exist_ok=True)
            os.makedirs(backend_path, exist_ok=True)
            
            # Create apps directory inside backend/django
            # Frontend apps directory will be created under src/ by the templates scaffolder
            os.makedirs(os.path.join(backend_path, 'apps'), exist_ok=True)
            
            # Create VueJS frontend
            self._create_vuejs_frontend(frontend_path, project.name, project.description)
            
            # Create Django backend
            self._create_django_backend(backend_path, unique_name, project.name, project.description)
            
            # Clean up immediately after Django backend creation
            self._cleanup_root_django_dirs(project_path)
            
            # Create root project files
            self._create_root_project_files(project_path, project.name, project.description)
            
            # Final cleanup - remove any Django directories that may have been created in root
            self._cleanup_root_django_dirs(project_path)
                
            return project_path
        except Exception as e:
            logger.error(f"Error creating project: {str(e)}")
            # Clean up failed project directory
            if os.path.exists(project_path):
                shutil.rmtree(project_path, ignore_errors=True)
            raise

    # Legacy methods removed - now using _create_django_backend for proper dual-stack structure

    def _create_vuejs_frontend(self, frontend_path, project_name, project_description):
        """Create VueJS frontend by delegating to templates module and install deps."""
        logger.info(f"Creating VueJS frontend at: {frontend_path}")
        tpl.create_vuejs_frontend_files(frontend_path, project_name, project_description)
        # Install npm dependencies in background
        npm_thread = self._install_vuejs_dependencies(frontend_path)
    
    
    
    def _install_vuejs_dependencies(self, frontend_path):
        """Install npm dependencies for VueJS frontend in background"""
        # Start npm install in background thread to not block project creation
        def install_dependencies_background():
            try:
                logger.info(f"Background: Installing npm dependencies in: {frontend_path}")
                
                # Run npm install in the frontend directory
                result = subprocess.run([
                    'npm', 'install'
                ], cwd=frontend_path, check=True, capture_output=True, text=True)
                
                logger.info(f"Background: npm install completed successfully in {frontend_path}")
                logger.debug(f"Background: npm install output: {result.stdout}")
                
            except subprocess.CalledProcessError as e:
                logger.error(f"Background: Failed to install npm dependencies in {frontend_path}")
                logger.error(f"Background: Error output: {e.stderr}")
            except FileNotFoundError:
                logger.warning(f"Background: npm command not found - dependencies not installed")
                logger.warning(f"Background: Please run 'npm install' manually in {frontend_path}")
            except Exception as e:
                logger.error(f"Background: Unexpected error during npm install: {str(e)}")
        
        # Start background thread for dependency installation
        logger.info(f"Starting background npm install for: {frontend_path}")
        install_thread = threading.Thread(
            target=install_dependencies_background,
            name=f"npm-install-{os.path.basename(frontend_path)}",
            daemon=True  # Thread will not prevent program exit
        )
        install_thread.start()
        logger.info(f"npm install started in background - project creation can continue")
        
        # Optional: Store thread reference for status checking (not currently used)
        # You could potentially use this to check if dependencies are still installing
        return install_thread

    def _create_django_backend(self, backend_path, unique_name, project_name, project_description):
        """Create Django backend with DRF"""
        logger.info(f"Creating Django backend at: {backend_path}")
        
        # Use Django's startproject command to create the basic project structure
        # This creates the Django project inside the backend_path directory
        subprocess.run([
            'django-admin', 'startproject', 
            unique_name,  # Project name
            backend_path  # Destination directory - Django project files will be created here
        ], check=True)
        
        # Create Django-specific directories ONLY within the backend directory
        django_dirs = [
            os.path.join(backend_path, 'static'),
            os.path.join(backend_path, 'static', 'css'),
            os.path.join(backend_path, 'static', 'js'),
            os.path.join(backend_path, 'static', 'images'),
            os.path.join(backend_path, 'templates'),
            os.path.join(backend_path, 'media')
        ]
        
        for dir_path in django_dirs:
            os.makedirs(dir_path, exist_ok=True)
            
        # Create a .gitkeep file in empty directories to ensure they're tracked by git
        for empty_dir in [os.path.join(backend_path, 'static', 'js'), 
                         os.path.join(backend_path, 'static', 'images'),
                         os.path.join(backend_path, 'media')]:
            with open(os.path.join(empty_dir, '.gitkeep'), 'w') as f:
                f.write('')
        
        # Create views.py in the project directory alongside settings.py
        project_dir = os.path.join(backend_path, unique_name)
        views_path = os.path.join(project_dir, 'views.py')
        with open(views_path, 'w') as f:
            f.write(tpl.django_project_views())
        
        # Create API app
        api_app_path = os.path.join(backend_path, 'api')
        os.makedirs(api_app_path, exist_ok=True)
        
        # Create API app files
        self._create_django_api_app(api_app_path)
        
        # Create Pipfile for Django dependencies
        with open(os.path.join(backend_path, 'Pipfile'), 'w') as f:
            f.write(tpl.django_pipfile())
        
        # Create basic Django templates within the backend
        self._create_django_templates(backend_path, project_name, project_description)
        
        # Create basic Django static files within the backend
        self._create_django_static_files(backend_path)
        
        # Update Django settings.py
        self._update_django_settings(backend_path, unique_name)
        
        # Update Django urls.py
        self._update_django_urls(backend_path, unique_name)
    
    def _create_django_api_app(self, api_app_path):
        """Create minimal Django API routing structure.

        Only create:
        - backend/django/api/urls.py
        - backend/django/api/v1/url.py
        """
        # Ensure api directory exists
        os.makedirs(api_app_path, exist_ok=True)

        # Ensure v1 subdirectory exists
        v1_path = os.path.join(api_app_path, 'v1')
        os.makedirs(v1_path, exist_ok=True)

        # Make both api/ and api/v1/ Python packages
        with open(os.path.join(api_app_path, '__init__.py'), 'w') as f:
            f.write('')
        with open(os.path.join(v1_path, '__init__.py'), 'w') as f:
            f.write('')

        # Create api root urls.py
        with open(os.path.join(api_app_path, 'urls.py'), 'w') as f:
            f.write(tpl.api_urls_py())

        # Create api/v1/url.py
        with open(os.path.join(v1_path, 'url.py'), 'w') as f:
            f.write(tpl.api_v1_url_py())
    
    def _create_django_templates(self, backend_path, project_name, project_description):
        """Create Django templates within the backend directory"""
        templates_path = os.path.join(backend_path, 'templates')
        
        # Create base template
        with open(os.path.join(templates_path, 'base.html'), 'w') as f:
            f.write(tpl.django_base_template(project_name))
        
        # Create index template
        with open(os.path.join(templates_path, 'index.html'), 'w') as f:
            f.write(tpl.django_index_template(project_name, project_description))
    
    def _create_django_static_files(self, backend_path):
        """Create Django static files within the backend directory"""
        static_css_path = os.path.join(backend_path, 'static', 'css')
        
        # Create basic CSS file
        with open(os.path.join(static_css_path, 'styles.css'), 'w') as f:
            f.write(tpl.django_static_css())
    
    def _create_root_project_files(self, project_path, project_name, project_description):
        """Create root-level project files"""
        # Create .gitignore
        with open(os.path.join(project_path, '.gitignore'), 'w') as f:
            f.write(tpl.fullstack_gitignore())
        
        # Create README.md
        with open(os.path.join(project_path, 'README.md'), 'w') as f:
            f.write(tpl.fullstack_readme(project_name, project_description))
        
        # Create development scripts
        self._create_development_scripts(project_path)
    
    def _cleanup_root_django_dirs(self, project_path):
        """Remove any Django directories that may have been accidentally created in the root"""
        directories_to_remove = ['static', 'templates', 'media', 'staticfiles']
        
        for dir_name in directories_to_remove:
            root_dir_path = os.path.join(project_path, dir_name)
            if os.path.exists(root_dir_path):
                try:
                    # Ensure we're not removing directories from backend
                    backend_path = os.path.join(project_path, 'backend', 'django', dir_name)
                    if root_dir_path != backend_path:
                        shutil.rmtree(root_dir_path)
                        logger.info(f"Cleaned up accidentally created directory: {root_dir_path}")
                    else:
                        logger.info(f"Skipping removal of backend directory: {root_dir_path}")
                except Exception as e:
                    logger.warning(f"Failed to remove directory {root_dir_path}: {e}")
        
        # Also clean up any files that might have been created in root
        files_to_remove = ['db.sqlite3', 'manage.py']
        for file_name in files_to_remove:
            root_file_path = os.path.join(project_path, file_name)
            if os.path.exists(root_file_path):
                try:
                    # Make sure it's not in the backend directory
                    backend_file_path = os.path.join(project_path, 'backend', 'django', file_name)
                    if root_file_path != backend_file_path:
                        os.remove(root_file_path)
                        logger.info(f"Cleaned up accidentally created file: {root_file_path}")
                except Exception as e:
                    logger.warning(f"Failed to remove file {root_file_path}: {e}")

    def _create_development_scripts(self, project_path):
        """Create development helper scripts"""
        # Create simple shell scripts for development (no package.json at root)
        
        # Create start-dev.sh script for Unix-like systems
        with open(os.path.join(project_path, 'start-dev.sh'), 'w') as f:
            f.write(tpl.start_dev_sh())
        
        # Make script executable
        try:
            import stat
            os.chmod(os.path.join(project_path, 'start-dev.sh'), stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)
        except:
            pass


    

    def _update_django_settings(self, backend_path, project_name):
        """Update Django settings.py for API and CORS"""
        settings_path = os.path.join(backend_path, project_name, 'settings.py')
        
        with open(settings_path, 'r') as f:
            settings_content = f.read()
        
        # Add DRF and CORS to INSTALLED_APPS
        installed_apps_pattern = r"INSTALLED_APPS = \[\n(.*?)\]"
        installed_apps_match = re.search(installed_apps_pattern, settings_content, re.DOTALL)
        if installed_apps_match:
            current_apps = installed_apps_match.group(1)
            updated_apps = current_apps + "    'rest_framework',\n    'corsheaders',\n"
            settings_content = settings_content.replace(current_apps, updated_apps)
        
        # Add CORS middleware
        middleware_pattern = r"MIDDLEWARE = \[\n(.*?)\]"
        middleware_match = re.search(middleware_pattern, settings_content, re.DOTALL)
        if middleware_match:
            current_middleware = middleware_match.group(1)
            updated_middleware = current_middleware.replace(
                "    'django.middleware.common.CommonMiddleware',", 
                "    'corsheaders.middleware.CorsMiddleware',\n    'django.middleware.common.CommonMiddleware',"
            )
            settings_content = settings_content.replace(current_middleware, updated_middleware)
        
        # Update TEMPLATES to point to backend templates directory
        templates_pattern = r"'DIRS': \[\],"
        templates_replacement = "'DIRS': [BASE_DIR / 'templates'],"
        settings_content = re.sub(templates_pattern, templates_replacement, settings_content)
        
        # Update STATIC_URL and add STATICFILES_DIRS to point to backend static directory
        static_url_pattern = r"STATIC_URL = 'static/'"
        static_replacement = "STATIC_URL = 'static/'\nSTATICFILES_DIRS = [\n    BASE_DIR / 'static',\n]"
        settings_content = re.sub(static_url_pattern, static_replacement, settings_content)
        
        # Add CORS and REST Framework settings
        if "# Default primary key field type" in settings_content:
            additional_settings = tpl.django_additional_settings()
            settings_content = settings_content.replace(
                "# Default primary key field type",
                additional_settings + "\n# Default primary key field type"
            )
        
        with open(settings_path, 'w') as f:
            f.write(settings_content)

    def _update_django_urls(self, backend_path, project_name):
        """Update Django urls.py to include API endpoints and home page"""
        urls_path = os.path.join(backend_path, project_name, 'urls.py')
        
        with open(urls_path, 'r') as f:
            urls_content = f.read()
        
        # Add include import and TemplateView
        if 'include' not in urls_content:
            urls_content = urls_content.replace(
                'from django.urls import path',
                'from django.urls import path, include'
            )
        
        if 'TemplateView' not in urls_content:
            urls_content = urls_content.replace(
                'from django.urls import path, include',
                'from django.urls import path, include\nfrom django.views.generic import TemplateView'
            )
        
        # Add home page and API URLs
        if 'api/' not in urls_content:
            urls_content = urls_content.replace(
                'urlpatterns = [',
                'urlpatterns = [\n    path(\'\', TemplateView.as_view(template_name=\'index.html\'), name=\'home\'),\n    path(\'api/\', include(\'api.urls\')),'
            )
        
        with open(urls_path, 'w') as f:
            f.write(urls_content)

    

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
    
    def _ensure_project_structure(self, project_path, project_name):
        """
        Ensure the basic dual-stack project structure exists
        For the new dual-stack architecture, we only verify structure, not create legacy Django dirs
        """
        try:
            logger.info(f"Ensuring dual-stack project structure for {project_name} at {project_path}")
            
            # Make sure the project path exists
            if not os.path.exists(project_path):
                logger.warning(f"Creating project directory: {project_path}")
                os.makedirs(project_path, exist_ok=True)
            
            # Check for dual-stack structure (frontend/vuejs and backend/django)
            frontend_vuejs_path = os.path.join(project_path, 'frontend', 'vuejs')
            backend_django_path = os.path.join(project_path, 'backend', 'django')
            
            # Check if this is a dual-stack project
            is_dual_stack = os.path.exists(frontend_vuejs_path) and os.path.exists(backend_django_path)
            
            if is_dual_stack:
                logger.info(f"Dual-stack project structure detected for {project_name}")
                
                # For dual-stack projects, only verify that Django backend has proper structure
                django_project_dir = None
                for item in os.listdir(backend_django_path):
                    item_path = os.path.join(backend_django_path, item)
                    if os.path.isdir(item_path) and not item.startswith('.') and item != '__pycache__':
                        # Check if this looks like a Django project directory (has settings.py)
                        settings_path = os.path.join(item_path, 'settings.py')
                        if os.path.exists(settings_path):
                            django_project_dir = item_path
                            logger.info(f"Found Django project directory: {django_project_dir}")
                            break
                
                if not django_project_dir:
                    logger.warning(f"No Django project directory found in backend structure")
                    return False
                
                # Verify essential Django backend directories exist ONLY in backend path
                required_backend_dirs = [
                    os.path.join(backend_django_path, 'static'),
                    os.path.join(backend_django_path, 'templates')
                ]
                
                for dir_path in required_backend_dirs:
                    if not os.path.exists(dir_path):
                        logger.info(f"Creating missing Django backend directory: {dir_path}")
                        os.makedirs(dir_path, exist_ok=True)
                
                # Clean up any Django directories that may exist in root
                self._cleanup_root_django_dirs(project_path)
                
            else:
                # Legacy single Django project - this is for backward compatibility only
                logger.info(f"Legacy Django project structure detected for {project_name}")
                
                # Only create minimal structure for legacy projects as fallback
                project_package_dir = os.path.join(project_path, project_name)
                if not os.path.exists(project_package_dir):
                    logger.info(f"Creating legacy project package directory: {project_package_dir}")
                    os.makedirs(project_package_dir, exist_ok=True)
                
                # Create __init__.py if it doesn't exist
                init_path = os.path.join(project_package_dir, '__init__.py')
                if not os.path.exists(init_path):
                    with open(init_path, 'w') as f:
                        f.write("# Generated by Imagi Oasis\n")
                    logger.info(f"Created __init__.py at {init_path}")
                
                # Create minimal Django files only if they don't exist
                manage_path = os.path.join(project_path, 'manage.py')
                if not os.path.exists(manage_path):
                    logger.warning(f"Creating minimal manage.py for legacy project: {manage_path}")
                    with open(manage_path, 'w') as f:
                        f.write(tpl.basic_manage_py(project_name))
                    try:
                        os.chmod(manage_path, 0o755)
                    except:
                        pass
                
                # For legacy projects, create basic Django structure if missing
                settings_path = os.path.join(project_package_dir, 'settings.py')
                if not os.path.exists(settings_path):
                    with open(settings_path, 'w') as f:
                        f.write(tpl.basic_settings_py(project_name))
                    logger.info(f"Created settings.py at {settings_path}")
                
                urls_path = os.path.join(project_package_dir, 'urls.py')
                if not os.path.exists(urls_path):
                    with open(urls_path, 'w') as f:
                        f.write(tpl.basic_project_urls_py())
                    logger.info(f"Created urls.py at {urls_path}")
                
                views_path = os.path.join(project_package_dir, 'views.py')
                if not os.path.exists(views_path):
                    with open(views_path, 'w') as f:
                        f.write(tpl.basic_project_views_py())
                    logger.info(f"Created views.py at {views_path}")
            
            logger.info(f"Project structure verification completed for {project_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error ensuring project structure: {str(e)}")
            import traceback
            logger.error(f"Stack trace: {traceback.format_exc()}")
            # Don't raise the exception, just return False
            return False 