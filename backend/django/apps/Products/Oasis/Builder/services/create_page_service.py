"""
Service for creating Vue.js pages/views with proper structure.
"""

import os
import logging
from typing import Dict, List, Any
from rest_framework.exceptions import ValidationError, NotFound
from apps.Products.Oasis.ProjectManager.models import Project
from .file_service import FileService

logger = logging.getLogger(__name__)

class CreatePageService:
    def __init__(self, user=None, project=None):
        """
        Initialize the page creation service.
        """
        self.user = user
        self.project = project
        self.file_service = FileService(user=user, project=project)
        
    def get_project(self, project_id):
        """Get a project by ID when initialized with user."""
        if not self.user:
            raise ValidationError("CreatePageService initialized without user")
            
        try:
            return Project.objects.get(id=project_id, user=self.user, is_active=True)
        except Project.DoesNotExist:
            raise NotFound('Project not found')
    
    def create_page(self, app_name: str, page_name: str, page_type: str = "view", project_id: str = None) -> Dict[str, Any]:
        """
        Create a new Vue.js page/view within an existing app.
        
        Args:
            app_name: Name of the app to create the page in
            page_name: Name of the page (will be converted to PascalCase for component)
            page_type: Type of page ('view', 'component', 'layout')
            project_id: Project ID if not initialized with project
            
        Returns:
            Dict containing success status and created file info
        """
        try:
            # Validate inputs
            if not app_name or not app_name.strip():
                raise ValidationError("App name is required")
            if not page_name or not page_name.strip():
                raise ValidationError("Page name is required")
                
            app_name = app_name.strip().lower()
            page_name = page_name.strip()
            
            # Get project if needed
            if project_id and not self.project:
                project = self.get_project(project_id)
                self.file_service = FileService(project=project)
            elif not self.project and not project_id:
                raise ValidationError("No project specified")
            
            # Validate app exists
            if not self._app_exists(app_name, project_id):
                raise ValidationError(f"App '{app_name}' does not exist. Create the app first.")
            
            # Generate page component name (PascalCase)
            component_name = self._to_pascal_case(page_name)
            
            # Determine file path based on page type
            if page_type == "view":
                file_path = f'frontend/vuejs/src/apps/{app_name}/views/{component_name}.vue'
            elif page_type == "component":
                file_path = f'frontend/vuejs/src/apps/{app_name}/components/{component_name}.vue'
            elif page_type == "layout":
                file_path = f'frontend/vuejs/src/apps/{app_name}/layouts/{component_name}.vue'
            else:
                raise ValidationError(f"Invalid page type: {page_type}")
            
            # Generate page content
            page_content = self._generate_page_content(component_name, page_type, app_name)
            
            # Create the file
            file_data = {
                'name': file_path,
                'type': 'vue',
                'content': page_content
            }
            
            result = self.file_service.create_file(file_data, project_id)
            
            # Update router if it's a view
            if page_type == "view":
                self._update_router(app_name, component_name, page_name, project_id)
            
            return {
                'success': True,
                'page_name': page_name,
                'component_name': component_name,
                'file_path': file_path,
                'page_type': page_type,
                'created_file': result,
                'message': f'Successfully created {page_type} {component_name} in {app_name} app'
            }
            
        except Exception as e:
            logger.error(f"Error creating page: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to create page: {str(e)}'
            }
    
    def create_page_with_route(self, app_name: str, page_name: str, route_path: str = None, project_id: str = None) -> Dict[str, Any]:
        """
        Create a new Vue.js page with automatic route registration.
        
        Args:
            app_name: Name of the app to create the page in
            page_name: Name of the page
            route_path: Custom route path (optional, defaults to /app_name/page_name)
            project_id: Project ID if not initialized with project
            
        Returns:
            Dict containing success status and created file info
        """
        try:
            # Create the page first
            result = self.create_page(app_name, page_name, "view", project_id)
            
            if not result.get('success'):
                return result
            
            # Generate route path if not provided
            if not route_path:
                route_path = f"/{app_name}/{page_name.lower().replace(' ', '-')}"
            
            # Update router with custom route
            component_name = result['component_name']
            self._add_route_to_router(app_name, component_name, page_name, route_path, project_id)
            
            result['route_path'] = route_path
            result['message'] += f' with route {route_path}'
            
            return result
            
        except Exception as e:
            logger.error(f"Error creating page with route: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to create page with route: {str(e)}'
            }
    
    def _app_exists(self, app_name: str, project_id: str = None) -> bool:
        """Check if an app exists by looking for its index.ts file."""
        try:
            existing_files = self.file_service.list_files(project_id)
            app_index_path = f'frontend/vuejs/src/apps/{app_name}/index.ts'
            
            for file_info in existing_files:
                if file_info.get('path') == app_index_path:
                    return True
            return False
        except Exception:
            return False
    
    def _to_pascal_case(self, text: str) -> str:
        """Convert text to PascalCase."""
        # Remove special characters and split by spaces, hyphens, underscores
        words = text.replace('-', ' ').replace('_', ' ').split()
        return ''.join(word.capitalize() for word in words if word.isalnum())
    
    def _generate_page_content(self, component_name: str, page_type: str, app_name: str) -> str:
        """Generate Vue.js component content based on type."""
        if page_type == "view":
            return f'''<template>
  <div class="min-h-screen bg-white">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">{component_name}</h1>
        <p class="mt-2 text-gray-600">Welcome to the {component_name} page.</p>
      </div>
      
      <!-- Page content goes here -->
      <div class="bg-gray-50 rounded-lg p-6">
        <p class="text-gray-500">This is the {component_name} page. Add your content here.</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {{ ref, onMounted }} from 'vue'

// Component state
const loading = ref(false)

// Lifecycle hooks
onMounted(() => {{
  // Initialize page
}})

// Methods
const handleAction = () => {{
  // Handle user actions
}}
</script>

<style scoped>
/* Component-specific styles */
</style>
'''
        elif page_type == "component":
            return f'''<template>
  <div class="{component_name.lower()}-component">
    <h2 class="text-xl font-semibold text-gray-900">{component_name}</h2>
    <p class="text-gray-600">This is the {component_name} component.</p>
  </div>
</template>

<script setup lang="ts">
import {{ ref }} from 'vue'

// Props
interface Props {{
  // Define component props here
}}

const props = withDefaults(defineProps<Props>(), {{
  // Default prop values
}})

// Emits
const emit = defineEmits<{{
  // Define component events here
}}>()

// Component state
const state = ref({{}})
</script>

<style scoped>
.{component_name.lower()}-component {{
  /* Component styles */
}}
</style>
'''
        elif page_type == "layout":
            return f'''<template>
  <div class="{component_name.lower()}-layout">
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 class="text-2xl font-bold text-gray-900 py-4">{component_name} Layout</h1>
      </div>
    </header>
    
    <main class="flex-1">
      <slot />
    </main>
    
    <footer class="bg-gray-50 border-t">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <p class="text-sm text-gray-500">© 2024 {app_name.capitalize()} App</p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
// Layout logic
</script>

<style scoped>
.{component_name.lower()}-layout {{
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}}
</style>
'''
        else:
            return f'''<template>
  <div>
    <h1>{component_name}</h1>
  </div>
</template>

<script setup lang="ts">
</script>
'''
    
    def _update_router(self, app_name: str, component_name: str, page_name: str, project_id: str = None):
        """Update the app's router to include the new page."""
        try:
            router_path = f'frontend/vuejs/src/apps/{app_name}/router/index.ts'
            
            # Get current router content
            try:
                current_content = self.file_service.get_file_content(router_path, project_id)
            except:
                # If router doesn't exist, create a basic one
                current_content = self._generate_basic_router(app_name)
            
            # Add import for new component
            import_line = f"import {component_name} from '../views/{component_name}.vue'"
            
            # Add route entry
            route_path = f"/{app_name}/{page_name.lower().replace(' ', '-')}"
            route_entry = f'''  {{
    path: '{route_path}',
    name: '{app_name}-{page_name.lower().replace(' ', '-')}',
    component: {component_name},
    meta: {{ requiresAuth: false, title: '{component_name}' }}
  }}'''
            
            # Update content
            updated_content = self._add_route_to_content(current_content, import_line, route_entry)
            
            # Save updated router
            self.file_service.update_file(router_path, updated_content, project_id)
            
        except Exception as e:
            logger.warning(f"Failed to update router for {component_name}: {str(e)}")
    
    def _add_route_to_router(self, app_name: str, component_name: str, page_name: str, route_path: str, project_id: str = None):
        """Add a specific route to the router."""
        try:
            router_path = f'frontend/vuejs/src/apps/{app_name}/router/index.ts'
            
            # Get current router content
            try:
                current_content = self.file_service.get_file_content(router_path, project_id)
            except:
                current_content = self._generate_basic_router(app_name)
            
            # Add import and route
            import_line = f"import {component_name} from '../views/{component_name}.vue'"
            route_entry = f'''  {{
    path: '{route_path}',
    name: '{app_name}-{page_name.lower().replace(' ', '-')}',
    component: {component_name},
    meta: {{ requiresAuth: false, title: '{component_name}' }}
  }}'''
            
            updated_content = self._add_route_to_content(current_content, import_line, route_entry)
            self.file_service.update_file(router_path, updated_content, project_id)
            
        except Exception as e:
            logger.warning(f"Failed to add route {route_path}: {str(e)}")
    
    def _generate_basic_router(self, app_name: str) -> str:
        """Generate a basic router template."""
        cap_name = app_name.capitalize()
        return f'''import type {{ RouteRecordRaw }} from 'vue-router'

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
    
    def _add_route_to_content(self, content: str, import_line: str, route_entry: str) -> str:
        """Add import and route to existing router content."""
        lines = content.split('\n')
        
        # Find where to insert import (after existing imports)
        import_insert_idx = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('import ') and 'from' in line:
                import_insert_idx = i + 1
            elif line.strip() == '' and import_insert_idx > 0:
                break
        
        # Insert import if not already present
        if import_line not in content:
            lines.insert(import_insert_idx, import_line)
        
        # Find where to insert route (before closing bracket of routes array)
        route_insert_idx = -1
        for i in range(len(lines) - 1, -1, -1):
            if ']' in lines[i] and 'routes' in ''.join(lines[max(0, i-5):i]):
                route_insert_idx = i
                break
        
        if route_insert_idx > 0:
            # Add comma to previous route if needed
            prev_line_idx = route_insert_idx - 1
            while prev_line_idx >= 0 and lines[prev_line_idx].strip() == '':
                prev_line_idx -= 1
            
            if prev_line_idx >= 0 and lines[prev_line_idx].strip().endswith('}'):
                lines[prev_line_idx] += ','
            
            # Insert new route
            lines.insert(route_insert_idx, route_entry + ',')
        
        return '\n'.join(lines)