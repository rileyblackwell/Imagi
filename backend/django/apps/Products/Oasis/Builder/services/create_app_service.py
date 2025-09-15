"""
Service for creating Vue.js applications with proper structure.
Also supports generating prebuilt default apps (home, auth, payments)
for both frontend and backend via codegen templates.
"""

import logging
from typing import Dict, List, Any
import os
from rest_framework.exceptions import ValidationError, NotFound
from apps.Products.Oasis.ProjectManager.models import Project
from .file_service import FileService
from .codegen.prebuilt_apps import generate_prebuilt_app_files

logger = logging.getLogger(__name__)

class CreateAppService:
    def __init__(self, user=None, project=None):
        """
        Initialize the app creation service.
        """
        self.user = user
        self.project = project
        self.file_service = FileService(user=user, project=project)
        
    def get_project(self, project_id):
        """Get a project by ID when initialized with user."""
        if not self.user:
            raise ValidationError("CreateAppService initialized without user")
            
        try:
            return Project.objects.get(id=project_id, user=self.user, is_active=True)
        except Project.DoesNotExist:
            raise NotFound('Project not found')
    
    def create_app_from_gallery(self, app_name: str, app_description: str = "", project_id: str = None) -> Dict[str, Any]:
        """
        Create a new Vue.js app with complete structure (equivalent to handleCreateAppFromGallery).
        
        Args:
            app_name: Name of the app (must be lowercase, alphanumeric, start with letter)
            app_description: Optional description for the app
            project_id: Project ID if not initialized with project
            
        Returns:
            Dict containing success status and created files info
        """
        try:
            # Validate app name
            if not app_name or not app_name.strip():
                raise ValidationError("App name is required")
                
            app_name = app_name.strip().lower()
            if not app_name.replace('_', '').replace('-', '').isalnum() or not app_name[0].isalpha():
                raise ValidationError("App name must contain only letters, numbers, hyphens, and underscores, and start with a letter")
            
            # Get project if needed
            if project_id and not self.project:
                project = self.get_project(project_id)
                self.file_service = FileService(project=project)
            elif not self.project and not project_id:
                raise ValidationError("No project specified")
            
            # Generate app structure
            cap = app_name.replace('_', '').replace('-', '').capitalize()
            app_welcome = app_description.strip() if app_description and app_description.strip() else f'Welcome to the {app_name} app.'

            # If this is a default app, use prebuilt codegen (includes backend + frontend)
            default_apps = {"home", "auth", "payments"}
            if app_name in default_apps:
                files_to_create = generate_prebuilt_app_files(app_name, app_description)
                # Fallback to generic if codegen returns nothing for some reason
                if not files_to_create:
                    files_to_create = self._generate_app_files(app_name, cap, app_welcome)
            else:
                files_to_create = self._generate_app_files(app_name, cap, app_welcome)
            
            created_files = []
            for file_data in files_to_create:
                try:
                    result = self.file_service.create_file(file_data, project_id)
                    created_files.append(result)
                except Exception as e:
                    logger.warning(f"Failed to create file {file_data['name']}: {str(e)}")
                    # Continue creating other files even if one fails
            
            # After files are created, register backend app (for non-conflicting cases)
            try:
                project_path = self.file_service.get_project_path(project_id)
                if project_path:
                    self._register_backend_app(project_path, app_name)
            except Exception as reg_err:
                logger.warning(f"App created but registration step failed: {str(reg_err)}")

            return {
                'success': True,
                'app_name': app_name,
                'files_created': len(created_files),
                'created_files': created_files,
                'message': f'Successfully created {app_name} app with {len(created_files)} files'
            }
            
        except Exception as e:
            logger.error(f"Error creating app from gallery: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to create app: {str(e)}'
            }
    
    def ensure_default_apps(self, project_id: str = None) -> Dict[str, Any]:
        """
        Ensure default apps (home, auth, payments) exist in the project.
        
        Args:
            project_id: Project ID if not initialized with project
            
        Returns:
            Dict containing success status and created apps info
        """
        try:
            # Get project if needed
            if project_id and not self.project:
                project = self.get_project(project_id)
                self.file_service = FileService(project=project)
            elif not self.project and not project_id:
                raise ValidationError("No project specified")
            
            # Get existing files to check for existing apps
            existing_files = self.file_service.list_files(project_id)
            existing_apps = set()
            
            for file_info in existing_files:
                path = str(file_info.get('path', '')).lower().replace('\\', '/')
                # Match pattern: /src/apps/{app_name}/
                if '/src/apps/' in path:
                    parts = path.split('/src/apps/')
                    if len(parts) > 1:
                        app_part = parts[1].split('/')[0]
                        if app_part:
                            existing_apps.add(app_part)
            
            required_apps = ['home', 'auth', 'payments']
            missing_apps = [app for app in required_apps if app not in existing_apps]
            
            if not missing_apps:
                return {
                    'success': True,
                    'message': 'All default apps already exist',
                    'existing_apps': list(existing_apps),
                    'created_apps': []
                }
            
            created_apps = []
            total_files_created = 0
            
            for app_name in missing_apps:
                try:
                    result = self.create_app_from_gallery(
                        app_name=app_name,
                        app_description=f"Default {app_name} application",
                        project_id=project_id
                    )
                    if result.get('success'):
                        created_apps.append(app_name)
                        total_files_created += result.get('files_created', 0)
                        # Ensure registration as well (idempotent)
                        try:
                            project_path = self.file_service.get_project_path(project_id)
                            if project_path:
                                self._register_backend_app(project_path, app_name)
                        except Exception as reg_err:
                            logger.warning(f"Registration failed for default app {app_name}: {str(reg_err)}")
                except Exception as e:
                    logger.warning(f"Failed to create default app {app_name}: {str(e)}")
            
            return {
                'success': True,
                'message': f'Successfully ensured default apps. Created {len(created_apps)} apps with {total_files_created} files.',
                'existing_apps': list(existing_apps),
                'created_apps': created_apps,
                'total_files_created': total_files_created
            }
            
        except Exception as e:
            logger.error(f"Error ensuring default apps: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to ensure default apps: {str(e)}'
            }
    
    def _generate_app_files(self, app_name: str, cap_name: str, app_welcome: str) -> List[Dict[str, str]]:
        """
        Generate the file structure for a new app.
        Creates both frontend (Vue) and minimal backend (Django) scaffolding so that
        every app consistently exists in `frontend/vuejs/src/apps/<app>/` and
        `backend/django/apps/<app>/`.
        
        Args:
            app_name: Lowercase app name
            cap_name: Capitalized app name
            app_welcome: Welcome message for the app
            
        Returns:
            List of file data dictionaries
        """
        files: List[Dict[str, str]] = [
            {
                'name': f'frontend/vuejs/src/apps/{app_name}/index.ts',
                'type': 'typescript',
                'content': f'// {cap_name} app entry point\nexport * from \'./router\'\nexport * from \'./stores\'\nexport * from \'./components\'\nexport * from \'./views\'\n'
            },
            {
                'name': f'frontend/vuejs/src/apps/{app_name}/router/index.ts',
                'type': 'typescript',
                'content': f'''import type {{ RouteRecordRaw }} from 'vue-router'

import {cap_name}View from '../views/{cap_name}View.vue'

const routes: RouteRecordRaw[] = [
  {{
    path: '/{app_name}',
    name: '{app_name}-view',
    component: {cap_name}View,
    meta: {{ requiresAuth: false, title: '{cap_name}' }}
  }}
]

export {{ routes }}
'''
            },
            {
                'name': f'frontend/vuejs/src/apps/{app_name}/stores/index.ts',
                'type': 'typescript',
                'content': f'export * from \'./{app_name}\'\n'
            },
            {
                'name': f'frontend/vuejs/src/apps/{app_name}/stores/{app_name}.ts',
                'type': 'typescript',
                'content': f'''import {{ defineStore }} from 'pinia'
import {{ ref }} from 'vue'

export const use{cap_name}Store = defineStore('{app_name}', () => {{
  const loading = ref(false)
  const setLoading = (v: boolean) => (loading.value = v)
  return {{ loading, setLoading }}
}})
'''
            },
            {
                'name': f'frontend/vuejs/src/apps/{app_name}/components/index.ts',
                'type': 'typescript',
                'content': 'export * from \'./atoms\'\nexport * from \'./molecules\'\nexport * from \'./organisms\'\n'
            },
            {
                'name': f'frontend/vuejs/src/apps/{app_name}/components/atoms/index.ts',
                'type': 'typescript',
                'content': '// atoms\n'
            },
            {
                'name': f'frontend/vuejs/src/apps/{app_name}/components/molecules/index.ts',
                'type': 'typescript',
                'content': '// molecules\n'
            },
            {
                'name': f'frontend/vuejs/src/apps/{app_name}/components/organisms/index.ts',
                'type': 'typescript',
                'content': '// organisms\n'
            },
            {
                'name': f'frontend/vuejs/src/apps/{app_name}/views/{cap_name}View.vue',
                'type': 'vue',
                'content': f'''<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 py-12">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center mb-16">
        <h1 class="text-5xl font-bold text-gray-900 mb-6">{cap_name} App</h1>
        <p class="text-xl text-gray-600 max-w-3xl mx-auto">{app_welcome}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
</script>
'''
            },
        ]

        # Minimal backend scaffold for any app (not only defaults)
        app_module = f"apps.{app_name}"
        files += [
            {
                'name': f'backend/django/apps/{app_name}/__init__.py',
                'type': 'python',
                'content': '',
            },
            {
                'name': f'backend/django/apps/{app_name}/apps.py',
                'type': 'python',
                'content': (
                    "from django.apps import AppConfig\n\n"
                    f"class {cap_name.capitalize()}Config(AppConfig):\n"
                    "    default_auto_field = 'django.db.models.BigAutoField'\n"
                    f"    name = '{app_module}'\n"
                ),
            },
            {
                'name': f'backend/django/apps/{app_name}/models.py',
                'type': 'python',
                'content': "from django.db import models\n\n# Add your models here.\n",
            },
            {
                'name': f'backend/django/apps/{app_name}/serializers.py',
                'type': 'python',
                'content': "from rest_framework import serializers\n\n# Add your serializers here.\n",
            },
            {
                'name': f'backend/django/apps/{app_name}/views.py',
                'type': 'python',
                'content': (
                    "from rest_framework.decorators import api_view\n"
                    "from rest_framework.response import Response\n"
                    "from rest_framework import status\n\n"
                    "@api_view(['GET'])\n"
                    "def health(_request):\n"
                    f"    return Response({{'app': '{app_name}', 'status': 'ok'}}, status=status.HTTP_200_OK)\n"
                ),
            },
            {
                'name': f'backend/django/apps/{app_name}/urls.py',
                'type': 'python',
                'content': (
                    "from django.urls import path\n"
                    "from . import views\n\n"
                    "urlpatterns = [\n"
                    "    path('health/', views.health, name='health'),\n"
                    "]\n"
                ),
            },
            {
                'name': f'backend/django/apps/{app_name}/admin.py',
                'type': 'python',
                'content': "from django.contrib import admin\n\n# Register your models here.\n",
            },
            {
                'name': f'backend/django/apps/{app_name}/tests.py',
                'type': 'python',
                'content': (
                    "from django.test import TestCase\n\n"
                    "class BasicTest(TestCase):\n"
                    "    def test_health(self):\n"
                    "        self.assertTrue(True)\n"
                ),
            },
        ]

        return files

    # ... (rest of the code remains the same)
    def _register_backend_app(self, project_path: str, app_name: str) -> None:
        """Ensure the backend Django app is added to INSTALLED_APPS and URLs.
        Skips if a capitalized variant already exists (e.g., 'apps.Home').
        """
        try:
            settings_path = os.path.join(project_path, 'backend', 'django', 'Imagi', 'settings.py')
            urls_path = os.path.join(project_path, 'backend', 'django', 'Imagi', 'urls.py')

            # Read settings.py
            with open(settings_path, 'r', encoding='utf-8') as f:
                settings_src = f.read()

            lower_module = f"apps.{app_name}"
            cap_module = f"apps.{app_name.capitalize()}"

            # Only add if neither lower nor capitalized variant is present
            if (lower_module not in settings_src) and (cap_module not in settings_src):
                settings_src = self._inject_into_installed_apps(settings_src, lower_module)
                with open(settings_path, 'w', encoding='utf-8') as f:
                    f.write(settings_src)

            # Update urls.py
            with open(urls_path, 'r', encoding='utf-8') as f:
                urls_src = f.read()

            include_line = f"        path('{app_name}/', include('apps.{app_name}.urls')),"
            if include_line not in urls_src:
                urls_src = self._inject_into_urls(urls_src, app_name)
                with open(urls_path, 'w', encoding='utf-8') as f:
                    f.write(urls_src)
        except Exception as e:
            # Don't raise - app creation succeeded; registration can be manual if needed
            logger.warning(f"Failed to register backend app '{app_name}': {str(e)}")

    def _inject_into_installed_apps(self, settings_src: str, module_name: str) -> str:
        """Insert the module into INSTALLED_APPS list in settings.py.
        Tries to place it after existing custom apps.
        """
        lines = settings_src.splitlines()
        out = []
        in_list = False
        inserted = False
        for line in lines:
            out.append(line)
            if not in_list and line.strip().startswith('INSTALLED_APPS = ['):
                in_list = True
                continue
            if in_list:
                # Detect end of list
                if line.strip().startswith(']'):
                    if not inserted:
                        out.insert(len(out) - 1, f"    '{module_name}',")
                        inserted = True
                    in_list = False
        return "\n".join(out)

    def _inject_into_urls(self, urls_src: str, app_name: str) -> str:
        """Insert include('apps.<app>.urls') into Imagi/urls.py urlpatterns under app URLs section."""
        lines = urls_src.splitlines()
        out = []
        inserted = False
        for i, line in enumerate(lines):
            out.append(line)
            # Heuristic: append after the existing app URL includes block
            if line.strip().startswith("# App URLs") and not inserted:
                include_line = f"    path('{app_name}/', include('apps.{app_name}.urls')),"
                if include_line not in urls_src:
                    out.append(include_line)
                    inserted = True
        if not inserted:
            # Fallback: append near the end, before closing bracket of urlpatterns list
            for idx in range(len(out) - 1, -1, -1):
                if out[idx].strip().startswith(']') and 'urlpatterns' in ''.join(out[max(0, idx-20):idx]):
                    out.insert(idx, f"    path('{app_name}/', include('apps.{app_name}.urls')),")
                    inserted = True
                    break
        return "\n".join(out)