"""
Service for creating Vue.js applications with proper structure.
Also supports generating prebuilt default apps (home, auth, payments)
for both frontend and backend via codegen templates.
"""

import logging
from typing import Dict, List, Any
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
        Generate the file structure for a new Vue.js app.
        
        Args:
            app_name: Lowercase app name
            cap_name: Capitalized app name
            app_welcome: Welcome message for the app
            
        Returns:
            List of file data dictionaries
        """
        return [
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
            }
        ]