"""
Service for creating Vue.js atomic components with proper structure.
"""

import os
import logging
from typing import Dict, List, Any
from rest_framework.exceptions import ValidationError, NotFound
from apps.Products.Oasis.ProjectManager.models import Project
from .file_service import FileService

logger = logging.getLogger(__name__)

class CreateComponentService:
    def __init__(self, user=None, project=None):
        """
        Initialize the component creation service.
        """
        self.user = user
        self.project = project
        self.file_service = FileService(user=user, project=project)
        
    def get_project(self, project_id):
        """Get a project by ID when initialized with user."""
        if not self.user:
            raise ValidationError("CreateComponentService initialized without user")
            
        try:
            return Project.objects.get(id=project_id, user=self.user, is_active=True)
        except Project.DoesNotExist:
            raise NotFound('Project not found')
    
    def create_atomic_component(self, app_name: str, component_name: str, component_type: str = "atom", project_id: str = None) -> Dict[str, Any]:
        """
        Create a new Vue.js atomic component (atom, molecule, or organism).
        
        Args:
            app_name: Name of the app to create the component in
            component_name: Name of the component (will be converted to PascalCase)
            component_type: Type of component ('atom', 'molecule', 'organism')
            project_id: Project ID if not initialized with project
            
        Returns:
            Dict containing success status and created file info
        """
        try:
            # Validate inputs
            if not app_name or not app_name.strip():
                raise ValidationError("App name is required")
            if not component_name or not component_name.strip():
                raise ValidationError("Component name is required")
                
            app_name = app_name.strip().lower()
            component_name = component_name.strip()
            
            # Validate component type
            valid_types = ['atom', 'molecule', 'organism']
            if component_type not in valid_types:
                raise ValidationError(f"Invalid component type: {component_type}. Must be one of: {', '.join(valid_types)}")
            
            # Get project if needed
            if project_id and not self.project:
                project = self.get_project(project_id)
                self.file_service = FileService(project=project)
            elif not self.project and not project_id:
                raise ValidationError("No project specified")
            
            # Validate app exists
            if not self._app_exists(app_name, project_id):
                raise ValidationError(f"App '{app_name}' does not exist. Create the app first.")
            
            # Generate component name (PascalCase)
            pascal_component_name = self._to_pascal_case(component_name)
            
            # Determine file path based on component type
            file_path = f'frontend/vuejs/src/apps/{app_name}/components/{component_type}s/{pascal_component_name}.vue'
            
            # Generate component content
            component_content = self._generate_component_content(pascal_component_name, component_type, app_name)
            
            # Create the file
            file_data = {
                'name': file_path,
                'type': 'vue',
                'content': component_content
            }
            
            result = self.file_service.create_file(file_data, project_id)
            
            # Update component index file
            self._update_component_index(app_name, component_type, pascal_component_name, project_id)
            
            return {
                'success': True,
                'component_name': component_name,
                'pascal_component_name': pascal_component_name,
                'file_path': file_path,
                'component_type': component_type,
                'created_file': result,
                'message': f'Successfully created {component_type} {pascal_component_name} in {app_name} app'
            }
            
        except Exception as e:
            logger.error(f"Error creating atomic component: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to create component: {str(e)}'
            }
    
    def create_button_component(self, app_name: str, button_name: str = "Button", project_id: str = None) -> Dict[str, Any]:
        """
        Create a reusable button atom component.
        
        Args:
            app_name: Name of the app to create the button in
            button_name: Name of the button component
            project_id: Project ID if not initialized with project
            
        Returns:
            Dict containing success status and created file info
        """
        try:
            # Get project if needed
            if project_id and not self.project:
                project = self.get_project(project_id)
                self.file_service = FileService(project=project)
            elif not self.project and not project_id:
                raise ValidationError("No project specified")
            
            pascal_name = self._to_pascal_case(button_name)
            file_path = f'frontend/vuejs/src/apps/{app_name}/components/atoms/{pascal_name}.vue'
            
            # Generate specialized button content
            button_content = self._generate_button_content(pascal_name)
            
            file_data = {
                'name': file_path,
                'type': 'vue',
                'content': button_content
            }
            
            result = self.file_service.create_file(file_data, project_id)
            self._update_component_index(app_name, 'atom', pascal_name, project_id)
            
            return {
                'success': True,
                'component_name': button_name,
                'pascal_component_name': pascal_name,
                'file_path': file_path,
                'component_type': 'atom',
                'created_file': result,
                'message': f'Successfully created button atom {pascal_name} in {app_name} app'
            }
            
        except Exception as e:
            logger.error(f"Error creating button component: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to create button component: {str(e)}'
            }
    
    def create_input_component(self, app_name: str, input_name: str = "Input", project_id: str = None) -> Dict[str, Any]:
        """
        Create a reusable input atom component.
        
        Args:
            app_name: Name of the app to create the input in
            input_name: Name of the input component
            project_id: Project ID if not initialized with project
            
        Returns:
            Dict containing success status and created file info
        """
        try:
            # Get project if needed
            if project_id and not self.project:
                project = self.get_project(project_id)
                self.file_service = FileService(project=project)
            elif not self.project and not project_id:
                raise ValidationError("No project specified")
            
            pascal_name = self._to_pascal_case(input_name)
            file_path = f'frontend/vuejs/src/apps/{app_name}/components/atoms/{pascal_name}.vue'
            
            # Generate specialized input content
            input_content = self._generate_input_content(pascal_name)
            
            file_data = {
                'name': file_path,
                'type': 'vue',
                'content': input_content
            }
            
            result = self.file_service.create_file(file_data, project_id)
            self._update_component_index(app_name, 'atom', pascal_name, project_id)
            
            return {
                'success': True,
                'component_name': input_name,
                'pascal_component_name': pascal_name,
                'file_path': file_path,
                'component_type': 'atom',
                'created_file': result,
                'message': f'Successfully created input atom {pascal_name} in {app_name} app'
            }
            
        except Exception as e:
            logger.error(f"Error creating input component: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to create input component: {str(e)}'
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
    
    def _generate_component_content(self, component_name: str, component_type: str, app_name: str) -> str:
        """Generate Vue.js component content based on atomic design type."""
        if component_type == "atom":
            return f'''<template>
  <div class="{component_name.lower()}-atom">
    <span class="text-sm font-medium text-gray-900">
      {component_name}
    </span>
  </div>
</template>

<script setup lang="ts">
import {{ ref }} from 'vue'

// Props
interface Props {{
  variant?: 'primary' | 'secondary' | 'outline'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
}}

const props = withDefaults(defineProps<Props>(), {{
  variant: 'primary',
  size: 'md',
  disabled: false
}})

// Emits
const emit = defineEmits<{{
  click: [event: MouseEvent]
}}>()

// Component state
const isHovered = ref(false)

// Methods
const handleClick = (event: MouseEvent) => {{
  if (!props.disabled) {{
    emit('click', event)
  }}
}}
</script>

<style scoped>
.{component_name.lower()}-atom {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease-in-out;
}}

.{component_name.lower()}-atom:hover {{
  transform: translateY(-1px);
}}
</style>
'''
        elif component_type == "molecule":
            return f'''<template>
  <div class="{component_name.lower()}-molecule">
    <div class="flex items-center space-x-3">
      <div class="flex-shrink-0">
        <!-- Icon or image slot -->
        <slot name="icon">
          <div class="w-8 h-8 bg-gray-200 rounded-full"></div>
        </slot>
      </div>
      <div class="flex-1 min-w-0">
        <h3 class="text-lg font-medium text-gray-900 truncate">
          {component_name}
        </h3>
        <p class="text-sm text-gray-500">
          <slot name="description">
            This is a {component_name.lower()} molecule component.
          </slot>
        </p>
      </div>
      <div class="flex-shrink-0">
        <slot name="actions">
          <!-- Action buttons -->
        </slot>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {{ ref, computed }} from 'vue'

// Props
interface Props {{
  title?: string
  description?: string
  variant?: 'default' | 'compact' | 'detailed'
}}

const props = withDefaults(defineProps<Props>(), {{
  title: '{component_name}',
  description: '',
  variant: 'default'
}})

// Emits
const emit = defineEmits<{{
  select: [id: string]
  action: [type: string, payload: any]
}}>()

// Computed
const containerClasses = computed(() => {{
  const base = '{component_name.lower()}-molecule p-4 border rounded-lg'
  const variants = {{
    default: 'border-gray-200 bg-white',
    compact: 'border-gray-100 bg-gray-50 p-2',
    detailed: 'border-gray-300 bg-white shadow-sm'
  }}
  return `${{base}} ${{variants[props.variant]}}`
}})
</script>

<style scoped>
.{component_name.lower()}-molecule {{
  transition: all 0.2s ease-in-out;
}}

.{component_name.lower()}-molecule:hover {{
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}}
</style>
'''
        elif component_type == "organism":
            return f'''<template>
  <div class="{component_name.lower()}-organism">
    <div class="bg-white shadow rounded-lg">
      <!-- Header -->
      <div class="px-6 py-4 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-semibold text-gray-900">
            {component_name}
          </h2>
          <div class="flex items-center space-x-2">
            <slot name="header-actions">
              <!-- Header action buttons -->
            </slot>
          </div>
        </div>
      </div>
      
      <!-- Content -->
      <div class="px-6 py-4">
        <slot name="content">
          <div class="text-center py-8">
            <div class="text-gray-400 mb-2">
              <!-- Default content icon -->
              <svg class="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
            <h3 class="text-lg font-medium text-gray-900 mb-1">{component_name}</h3>
            <p class="text-gray-500">This is a {component_name.lower()} organism component.</p>
          </div>
        </slot>
      </div>
      
      <!-- Footer -->
      <div class="px-6 py-3 bg-gray-50 border-t border-gray-200 rounded-b-lg">
        <div class="flex items-center justify-between">
          <div class="text-sm text-gray-500">
            <slot name="footer-info">
              <!-- Footer information -->
            </slot>
          </div>
          <div class="flex items-center space-x-2">
            <slot name="footer-actions">
              <!-- Footer action buttons -->
            </slot>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {{ ref, reactive, computed, onMounted }} from 'vue'

// Props
interface Props {{
  title?: string
  loading?: boolean
  error?: string | null
  data?: any[]
}}

const props = withDefaults(defineProps<Props>(), {{
  title: '{component_name}',
  loading: false,
  error: null,
  data: () => []
}})

// Emits
const emit = defineEmits<{{
  load: []
  refresh: []
  action: [type: string, payload: any]
  error: [error: Error]
}}>()

// State
const state = reactive({{
  isLoading: false,
  hasError: false,
  items: [] as any[]
}})

// Computed
const isEmpty = computed(() => {{
  return !props.loading && !props.error && (!props.data || props.data.length === 0)
}})

// Lifecycle
onMounted(() => {{
  emit('load')
}})

// Methods
const handleRefresh = () => {{
  emit('refresh')
}}

const handleAction = (type: string, payload: any) => {{
  emit('action', type, payload)
}}
</script>

<style scoped>
.{component_name.lower()}-organism {{
  /* Organism-specific styles */
}}

.{component_name.lower()}-organism .loading-state {{
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}}

@keyframes pulse {{
  0%, 100% {{
    opacity: 1;
  }}
  50% {{
    opacity: .5;
  }}
}}
</style>
'''
        else:
            return f'''<template>
  <div class="{component_name.lower()}-component">
    <h2>{component_name}</h2>
  </div>
</template>

<script setup lang="ts">
</script>
'''
    
    def _generate_button_content(self, component_name: str) -> str:
        """Generate specialized button component content."""
        return f'''<template>
  <button
    :class="buttonClasses"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <span v-if="loading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white">
      <svg class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </span>
    <slot>{{ text || '{component_name}' }}</slot>
  </button>
</template>

<script setup lang="ts">
import {{ computed }} from 'vue'

// Props
interface Props {{
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger'
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  disabled?: boolean
  loading?: boolean
  text?: string
  fullWidth?: boolean
}}

const props = withDefaults(defineProps<Props>(), {{
  variant: 'primary',
  size: 'md',
  disabled: false,
  loading: false,
  text: '',
  fullWidth: false
}})

// Emits
const emit = defineEmits<{{
  click: [event: MouseEvent]
}}>()

// Computed
const buttonClasses = computed(() => {{
  const base = 'inline-flex items-center justify-center font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors duration-200'
  
  const variants = {{
    primary: 'bg-indigo-600 hover:bg-indigo-700 text-white focus:ring-indigo-500',
    secondary: 'bg-gray-600 hover:bg-gray-700 text-white focus:ring-gray-500',
    outline: 'border border-gray-300 bg-white hover:bg-gray-50 text-gray-700 focus:ring-indigo-500',
    ghost: 'text-gray-700 hover:bg-gray-100 focus:ring-gray-500',
    danger: 'bg-red-600 hover:bg-red-700 text-white focus:ring-red-500'
  }}
  
  const sizes = {{
    xs: 'px-2.5 py-1.5 text-xs',
    sm: 'px-3 py-2 text-sm',
    md: 'px-4 py-2 text-sm',
    lg: 'px-4 py-2 text-base',
    xl: 'px-6 py-3 text-base'
  }}
  
  const width = props.fullWidth ? 'w-full' : ''
  const disabled = props.disabled || props.loading ? 'opacity-50 cursor-not-allowed' : ''
  
  return `${{base}} ${{variants[props.variant]}} ${{sizes[props.size]}} ${{width}} ${{disabled}}`.trim()
}})

// Methods
const handleClick = (event: MouseEvent) => {{
  if (!props.disabled && !props.loading) {{
    emit('click', event)
  }}
}}
</script>
'''
    
    def _generate_input_content(self, component_name: str) -> str:
        """Generate specialized input component content."""
        return f'''<template>
  <div class="input-wrapper">
    <label v-if="label" :for="inputId" class="block text-sm font-medium text-gray-700 mb-1">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>
    
    <div class="relative">
      <input
        :id="inputId"
        v-model="inputValue"
        :type="type"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :required="required"
        :class="inputClasses"
        @blur="handleBlur"
        @focus="handleFocus"
        @input="handleInput"
      />
      
      <!-- Icon slot -->
      <div v-if="$slots.icon" class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        <slot name="icon" />
      </div>
      
      <!-- Trailing icon/button -->
      <div v-if="$slots.trailing" class="absolute inset-y-0 right-0 pr-3 flex items-center">
        <slot name="trailing" />
      </div>
    </div>
    
    <!-- Help text -->
    <p v-if="helpText && !error" class="mt-1 text-sm text-gray-500">
      {{ helpText }}
    </p>
    
    <!-- Error message -->
    <p v-if="error" class="mt-1 text-sm text-red-600">
      {{ error }}
    </p>
  </div>
</template>

<script setup lang="ts">
import {{ ref, computed, useId }} from 'vue'

// Props
interface Props {{
  modelValue?: string | number
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url' | 'search'
  label?: string
  placeholder?: string
  helpText?: string
  error?: string
  disabled?: boolean
  readonly?: boolean
  required?: boolean
  size?: 'sm' | 'md' | 'lg'
}}

const props = withDefaults(defineProps<Props>(), {{
  modelValue: '',
  type: 'text',
  label: '',
  placeholder: '',
  helpText: '',
  error: '',
  disabled: false,
  readonly: false,
  required: false,
  size: 'md'
}})

// Emits
const emit = defineEmits<{{
  'update:modelValue': [value: string | number]
  blur: [event: FocusEvent]
  focus: [event: FocusEvent]
  input: [event: Event]
}}>()

// State
const inputId = useId()
const isFocused = ref(false)

// Computed
const inputValue = computed({{
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
}})

const inputClasses = computed(() => {{
  const base = 'block w-full border rounded-md shadow-sm focus:outline-none focus:ring-1 transition-colors duration-200'
  
  const sizes = {{
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-3 py-2 text-sm',
    lg: 'px-4 py-3 text-base'
  }}
  
  const states = {{
    default: 'border-gray-300 focus:border-indigo-500 focus:ring-indigo-500',
    error: 'border-red-300 focus:border-red-500 focus:ring-red-500',
    disabled: 'bg-gray-50 text-gray-500 cursor-not-allowed'
  }}
  
  let state = 'default'
  if (props.error) state = 'error'
  if (props.disabled) state = 'disabled'
  
  const iconPadding = props.$slots?.icon ? 'pl-10' : ''
  const trailingPadding = props.$slots?.trailing ? 'pr-10' : ''
  
  return `${{base}} ${{sizes[props.size]}} ${{states[state]}} ${{iconPadding}} ${{trailingPadding}}`.trim()
}})

// Methods
const handleBlur = (event: FocusEvent) => {{
  isFocused.value = false
  emit('blur', event)
}}

const handleFocus = (event: FocusEvent) => {{
  isFocused.value = true
  emit('focus', event)
}}

const handleInput = (event: Event) => {{
  emit('input', event)
}}
</script>

<style scoped>
.input-wrapper {{
  /* Input wrapper styles */
}}
</style>
'''
    
    def _update_component_index(self, app_name: str, component_type: str, component_name: str, project_id: str = None):
        """Update the component index file to export the new component."""
        try:
            # Determine the correct index file path
            type_plural = f"{component_type}s"
            index_path = f'frontend/vuejs/src/apps/{app_name}/components/{type_plural}/index.ts'
            
            # Get current content or create new
            try:
                current_content = self.file_service.get_file_content(index_path, project_id)
            except:
                current_content = f'// {type_plural}\n'
            
            # Add export line if not already present
            export_line = f"export {{ default as {component_name} }} from './{component_name}.vue'"
            
            if export_line not in current_content:
                # Add the export
                if current_content.strip():
                    updated_content = current_content.rstrip() + '\n' + export_line + '\n'
                else:
                    updated_content = f'// {type_plural}\n{export_line}\n'
                
                # Save updated index
                self.file_service.update_file(index_path, updated_content, project_id)
                
        except Exception as e:
            logger.warning(f"Failed to update component index for {component_name}: {str(e)}")