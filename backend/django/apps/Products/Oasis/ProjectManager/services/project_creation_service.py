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
        """Create VueJS frontend with Vite, Pinia, TailwindCSS, and Axios"""
        logger.info(f"Creating VueJS frontend at: {frontend_path}")
        
        # Create package.json
        package_json = {
            "name": f"{self._sanitize_project_name(project_name).lower()}-frontend",
            "private": True,
            "version": "0.0.0",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "vue-tsc && vite build",
                "preview": "vite preview"
            },
            "dependencies": {
                "vue": "^3.4.0",
                "vue-router": "^4.2.5",
                "pinia": "^2.1.7",
                "axios": "^1.6.0",
                "@headlessui/vue": "^1.7.16",
                "@heroicons/vue": "^2.0.18"
            },
            "devDependencies": {
                "@types/node": "^20.9.0",
                "@vitejs/plugin-vue": "^4.5.0",
                "autoprefixer": "^10.4.16",
                "postcss": "^8.4.32",
                "tailwindcss": "^3.3.6",
                "typescript": "^5.2.2",
                "vite": "^5.0.0",
                "vue-tsc": "^1.8.22"
            }
        }
        
        with open(os.path.join(frontend_path, 'package.json'), 'w') as f:
            import json
            f.write(json.dumps(package_json, indent=2))
        
        # Create vite.config.ts
        vite_config = '''import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 5173,
    host: true,
    cors: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      }
    }
  }
})
'''
        with open(os.path.join(frontend_path, 'vite.config.ts'), 'w') as f:
            f.write(vite_config)
        
        # Create tailwind.config.js
        tailwind_config = '''/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
'''
        with open(os.path.join(frontend_path, 'tailwind.config.js'), 'w') as f:
            f.write(tailwind_config)
        
        # Create postcss.config.js
        postcss_config = '''export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
'''
        with open(os.path.join(frontend_path, 'postcss.config.js'), 'w') as f:
            f.write(postcss_config)
        
        # Create tsconfig.json
        tsconfig = {
            "compilerOptions": {
                "target": "ES2020",
                "useDefineForClassFields": True,
                "lib": ["ES2020", "DOM", "DOM.Iterable"],
                "module": "ESNext",
                "skipLibCheck": True,
                "moduleResolution": "bundler",
                "allowImportingTsExtensions": True,
                "resolveJsonModule": True,
                "isolatedModules": True,
                "noEmit": True,
                "jsx": "preserve",
                "strict": True,
                "noUnusedLocals": True,
                "noUnusedParameters": True,
                "noFallthroughCasesInSwitch": True,
                "baseUrl": ".",
                "paths": {
                    "@/*": ["./src/*"]
                }
            },
            "include": ["src/**/*.ts", "src/**/*.tsx", "src/**/*.vue"],
            "references": [{"path": "./tsconfig.node.json"}]
        }
        
        with open(os.path.join(frontend_path, 'tsconfig.json'), 'w') as f:
            import json
            f.write(json.dumps(tsconfig, indent=2))
        
        # Create index.html
        index_html = f'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{project_name}</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
'''
        with open(os.path.join(frontend_path, 'index.html'), 'w') as f:
            f.write(index_html)
        
        # Create VueJS source files
        self._create_vuejs_src_files(frontend_path, project_name, project_description)
        
        # Install npm dependencies in background
        npm_thread = self._install_vuejs_dependencies(frontend_path)
    
    def _create_vuejs_src_files(self, frontend_path, project_name, project_description):
        """Create VueJS source files structure"""
        src_path = os.path.join(frontend_path, 'src')
        
        # Create directories
        directories = [
            'components',
            'components/atoms',
            'components/molecules', 
            'components/organisms',
            'views',
            'router',
            'stores',
            'services',
            'types',
            'assets',
            'assets/css'
        ]
        
        for directory in directories:
            os.makedirs(os.path.join(src_path, directory), exist_ok=True)
        
        # Create main.ts
        main_ts = '''import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './assets/css/main.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
'''
        with open(os.path.join(src_path, 'main.ts'), 'w') as f:
            f.write(main_ts)
        
        # Create App.vue
        app_vue = f'''<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <RouterView />
  </div>
</template>

<script setup lang="ts">
import {{ RouterView }} from 'vue-router'
</script>
'''
        with open(os.path.join(src_path, 'App.vue'), 'w') as f:
            f.write(app_vue)
        
        # Create router/index.ts
        router_index = '''import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    }
  ]
})

export default router
'''
        with open(os.path.join(src_path, 'router', 'index.ts'), 'w') as f:
            f.write(router_index)
        
        # Create stores/main.ts
        store_main = '''import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useMainStore = defineStore('main', () => {
  const message = ref('Hello from Pinia store!')
  
  function updateMessage(newMessage: string) {
    message.value = newMessage
  }
  
  return { message, updateMessage }
})
'''
        with open(os.path.join(src_path, 'stores', 'main.ts'), 'w') as f:
            f.write(store_main)
        
        # Create services/api.ts
        api_service = '''import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('authToken')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default api
'''
        with open(os.path.join(src_path, 'services', 'api.ts'), 'w') as f:
            f.write(api_service)
        
        # Create views/HomeView.vue
        safe_project_name = project_name.replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
        safe_description = (project_description or '').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
        
        home_view = f'''<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
    <div class="container mx-auto px-4 py-16">
      <div class="max-w-4xl mx-auto text-center">
        <h1 class="text-5xl font-bold text-gray-900 mb-6">
          Welcome to {safe_project_name}
        </h1>
        
        <p v-if="description" class="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          {safe_description}
        </p>
        
        <div class="bg-white rounded-2xl shadow-xl p-8 mb-8">
          <h2 class="text-2xl font-semibold text-gray-800 mb-4">
            Your VueJS + Django Application
          </h2>
          <p class="text-gray-600 mb-6">
            This project includes a modern VueJS frontend with Vite, TailwindCSS, and Pinia, 
            connected to a Django REST API backend.
          </p>
          
          <div class="grid md:grid-cols-2 gap-6">
            <div class="bg-blue-50 p-6 rounded-xl">
              <h3 class="text-lg font-medium text-blue-900 mb-2">Frontend Tech Stack</h3>
              <ul class="text-blue-700 space-y-1">
                <li>• Vue 3 with Composition API</li>
                <li>• Vite for fast development</li>
                <li>• TailwindCSS for styling</li>
                <li>• Pinia for state management</li>
                <li>• Axios for API calls</li>
              </ul>
            </div>
            
            <div class="bg-green-50 p-6 rounded-xl">
              <h3 class="text-lg font-medium text-green-900 mb-2">Backend Tech Stack</h3>
              <ul class="text-green-700 space-y-1">
                <li>• Django 4.x framework</li>
                <li>• Django REST Framework</li>
                <li>• SQLite database</li>
                <li>• CORS enabled</li>
                <li>• Token authentication</li>
              </ul>
            </div>
          </div>
        </div>
        
        <div class="flex flex-col sm:flex-row gap-4 justify-center">
          <button
            @click="testApiConnection"
            :disabled="loading"
            class="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-6 py-3 rounded-lg font-medium transition-colors"
          >
            {{ loading ? 'Testing...' : 'Test API Connection' }}
          </button>
          
          <button
            @click="updateStoreMessage"
            class="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
          >
            Test Pinia Store
          </button>
        </div>
        
        <div v-if="apiStatus" class="mt-6 p-4 rounded-lg" :class="apiStatus.success ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800">
          {{ apiStatus.message }}
        </div>
        
        <div class="mt-6 p-4 bg-gray-100 rounded-lg">
          <p class="text-gray-700">Store Message: {{ mainStore.message }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {{ ref }} from 'vue'
import {{ useMainStore }} from '@/stores/main'
import api from '@/services/api'

const mainStore = useMainStore()
const loading = ref(false)
const apiStatus = ref<{{ success: boolean; message: string }} | null>(null)
const description = '{safe_description}'

async function testApiConnection() {{
  loading.value = true
  apiStatus.value = null
  
  try {{
    const response = await api.get('/health/')
    apiStatus.value = {{
      success: true,
      message: 'API connection successful! Backend is running.'
    }}
  }} catch (error) {{
    apiStatus.value = {{
      success: false,
      message: 'API connection failed. Make sure the Django backend is running on port 8000.'
    }}
  }} finally {{
    loading.value = false
  }}
}}

function updateStoreMessage() {{
  const messages = [
    'Pinia store is working!',
    'State management is active!',
    'VueJS + Pinia = ❤️',
    'Store updated successfully!'
  ]
  const randomMessage = messages[Math.floor(Math.random() * messages.length)]
  mainStore.updateMessage(randomMessage)
}}
</script>
'''
        with open(os.path.join(src_path, 'views', 'HomeView.vue'), 'w') as f:
            f.write(home_view)
        
        # Create main.css
        main_css = '''@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  html {
    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  }
}

@layer components {
  .btn {
    @apply px-4 py-2 rounded-lg font-medium transition-colors;
  }
  
  .btn-primary {
    @apply bg-blue-600 hover:bg-blue-700 text-white;
  }
  
  .btn-secondary {
    @apply bg-gray-200 hover:bg-gray-300 text-gray-800;
  }
}
'''
        with open(os.path.join(src_path, 'assets', 'css', 'main.css'), 'w') as f:
            f.write(main_css)
    
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
            f.write(self._generate_django_project_views_content())
        
        # Create API app
        api_app_path = os.path.join(backend_path, 'api')
        os.makedirs(api_app_path, exist_ok=True)
        
        # Create API app files
        self._create_django_api_app(api_app_path)
        
        # Create Pipfile for Django dependencies
        with open(os.path.join(backend_path, 'Pipfile'), 'w') as f:
            f.write(self._generate_django_pipfile_content())
        
        # Create basic Django templates within the backend
        self._create_django_templates(backend_path, project_name, project_description)
        
        # Create basic Django static files within the backend
        self._create_django_static_files(backend_path)
        
        # Update Django settings.py
        self._update_django_settings(backend_path, unique_name)
        
        # Update Django urls.py
        self._update_django_urls(backend_path, unique_name)
    
    def _create_django_api_app(self, api_app_path):
        """Create Django API app with basic structure"""
        # Create __init__.py
        with open(os.path.join(api_app_path, '__init__.py'), 'w') as f:
            f.write('')
        
        # Create apps.py
        apps_py = '''from django.apps import AppConfig

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
'''
        with open(os.path.join(api_app_path, 'apps.py'), 'w') as f:
            f.write(apps_py)
        
        # Create models.py
        models_py = '''from django.db import models

class HealthCheck(models.Model):
    """Simple model for API health checks"""
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='healthy')
    
    def __str__(self):
        return f"Health check at {self.timestamp}"
'''
        with open(os.path.join(api_app_path, 'models.py'), 'w') as f:
            f.write(models_py)
        
        # Create serializers.py
        serializers_py = '''from rest_framework import serializers
from .models import HealthCheck

class HealthCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthCheck
        fields = ['id', 'timestamp', 'status']
'''
        with open(os.path.join(api_app_path, 'serializers.py'), 'w') as f:
            f.write(serializers_py)
        
        # Create views.py
        views_py = '''from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import HealthCheck
from .serializers import HealthCheckSerializer

@api_view(['GET'])
def health_check(request):
    """Health check endpoint for frontend to test API connection"""
    health = HealthCheck.objects.create()
    serializer = HealthCheckSerializer(health)
    
    return Response({
        'status': 'healthy',
        'message': 'Django backend is running successfully!',
        'data': serializer.data
    }, status=status.HTTP_200_OK)

@api_view(['GET', 'POST'])
def example_endpoint(request):
    """Example API endpoint"""
    if request.method == 'GET':
        return Response({
            'message': 'This is a GET request to the Django API',
            'data': {'example': 'data'}
        })
    elif request.method == 'POST':
        return Response({
            'message': 'This is a POST request to the Django API',
            'received_data': request.data
        })
'''
        with open(os.path.join(api_app_path, 'views.py'), 'w') as f:
            f.write(views_py)
        
        # Create urls.py
        urls_py = '''from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('example/', views.example_endpoint, name='example_endpoint'),
]
'''
        with open(os.path.join(api_app_path, 'urls.py'), 'w') as f:
            f.write(urls_py)
        
        # Create admin.py
        admin_py = '''from django.contrib import admin
from .models import HealthCheck

@admin.register(HealthCheck)
class HealthCheckAdmin(admin.ModelAdmin):
    list_display = ['id', 'timestamp', 'status']
    list_filter = ['status', 'timestamp']
    readonly_fields = ['timestamp']
'''
        with open(os.path.join(api_app_path, 'admin.py'), 'w') as f:
            f.write(admin_py)
    
    def _create_django_templates(self, backend_path, project_name, project_description):
        """Create Django templates within the backend directory"""
        templates_path = os.path.join(backend_path, 'templates')
        
        # Create base template
        base_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{% block title %}}{project_name}{{% endblock %}}</title>
    <link rel="stylesheet" href="{{% static 'css/styles.css' %}}">
    {{% block extra_css %}}{{% endblock %}}
</head>
<body>
    {{% block content %}}{{% endblock %}}
    
    {{% block extra_js %}}{{% endblock %}}
</body>
</html>
'''
        with open(os.path.join(templates_path, 'base.html'), 'w') as f:
            f.write(base_template)
        
        # Create index template
        safe_project_name = project_name.replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
        safe_description = (project_description or '').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
        
        description_content = ''
        if project_description and project_description.strip():
            description_content = f'    <p class="project-description">{safe_description}</p>'
        
        index_template = f'''{{% extends 'base.html' %}}
{{% load static %}}

{{% block title %}}Welcome | {safe_project_name}{{% endblock %}}

{{% block content %}}
<div class="welcome-container">
    <h1>Welcome to {safe_project_name}</h1>
{description_content}
    <p>This is your Django backend API. The frontend is served separately on port 5173.</p>
    <div class="cta-button">
        <a href="/admin/">Go to Admin</a>
        <a href="/api/">Browse API</a>
    </div>
</div>
{{% endblock %}}
'''
        with open(os.path.join(templates_path, 'index.html'), 'w') as f:
            f.write(index_template)
    
    def _create_django_static_files(self, backend_path):
        """Create Django static files within the backend directory"""
        static_css_path = os.path.join(backend_path, 'static', 'css')
        
        # Create basic CSS file
        css_content = '''/* Django Backend Styles */
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
    display: flex;
    gap: 1rem;
    justify-content: center;
    flex-wrap: wrap;
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
        with open(os.path.join(static_css_path, 'styles.css'), 'w') as f:
            f.write(css_content)
    
    def _create_root_project_files(self, project_path, project_name, project_description):
        """Create root-level project files"""
        # Create .gitignore
        with open(os.path.join(project_path, '.gitignore'), 'w') as f:
            f.write(self._generate_fullstack_gitignore_content())
        
        # Create README.md
        with open(os.path.join(project_path, 'README.md'), 'w') as f:
            f.write(self._generate_fullstack_readme_content(project_name, project_description))
        
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
        start_dev_script = '''#!/bin/bash
# Development startup script for dual-stack application

echo "🚀 Starting development servers..."

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Stopping development servers..."
    jobs -p | xargs -r kill
    exit
}

# Set up signal handling
trap cleanup SIGINT SIGTERM

# Check if npm dependencies are installed
if [ ! -d "frontend/vuejs/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend/vuejs && npm install && cd ../..
fi

# Start Django backend
echo "🐍 Starting Django backend on port 8000..."
cd backend/django && python manage.py runserver &
DJANGO_PID=$!

# Wait a moment for Django to start
sleep 3

# Start Vue frontend  
echo "⚡ Starting Vue frontend on port 5173..."
cd frontend/vuejs && npm run dev &
VUE_PID=$!

echo ""
echo "✅ Development servers started!"
echo "🌐 Frontend: http://localhost:5173"
echo "🔧 Backend API: http://localhost:8000"
echo "📱 Press Ctrl+C to stop both servers"

# Wait for background processes
wait
'''
        with open(os.path.join(project_path, 'start-dev.sh'), 'w') as f:
            f.write(start_dev_script)
        
        # Make script executable
        try:
            import stat
            os.chmod(os.path.join(project_path, 'start-dev.sh'), stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)
        except:
            pass
        
        # Create start-dev.bat script for Windows
        start_dev_bat = r'''@echo off
echo 🚀 Starting development servers...

REM Check if npm dependencies are installed
if not exist "frontend\\vuejs\\node_modules" (
    echo 📦 Installing frontend dependencies...
    cd frontend\\vuejs
    npm install
    cd ..\..
)

echo 🐍 Starting Django backend on port 8000...
start /B cmd /c "cd backend\\django && python manage.py runserver"

timeout /T 3 /NOBREAK >nul

echo ⚡ Starting Vue frontend on port 5173...
start /B cmd /c "cd frontend\\vuejs && npm run dev"

echo.
echo ✅ Development servers started!
echo 🌐 Frontend: http://localhost:5173
echo 🔧 Backend API: http://localhost:8000
echo 📱 Close this window to stop the servers
pause
'''
        with open(os.path.join(project_path, 'start-dev.bat'), 'w') as f:
            f.write(start_dev_bat)

    def _generate_django_pipfile_content(self):
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

    def _generate_django_project_views_content(self):
        """Generate content for Django project views.py file"""
        return """from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.generic import TemplateView

def home(request):
    \"\"\"Home page view.\"\"\"
    return JsonResponse({
        'message': 'Django backend is running!',
        'status': 'success'
    })

class HomeView(TemplateView):
    \"\"\"Class-based home page view.\"\"\"
    template_name = 'index.html'
"""

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
            updated_apps = current_apps + "    'rest_framework',\n    'corsheaders',\n    'api',\n"
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
            additional_settings = """
# CORS settings
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # Allow all for development
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
}
"""
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

    def _generate_fullstack_gitignore_content(self):
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

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# IDE
.idea/
.vscode/
*.swp
*.swo

# macOS
.DS_Store

# Windows
Thumbs.db

# Build outputs
dist/
.nuxt/
.next/
out/

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local
'''

    def _generate_fullstack_readme_content(self, project_name, project_description):
        return f'''# {project_name}

{project_description or "A full-stack web application with VueJS frontend and Django backend."}

## Tech Stack

### Frontend
- **Vue 3** with Composition API
- **Vite** for fast development and building
- **TailwindCSS** for styling
- **Pinia** for state management
- **Axios** for API communication
- **TypeScript** for type safety

### Backend
- **Django 4.x** web framework
- **Django REST Framework** for API development
- **SQLite** database (development)
- **CORS** enabled for frontend communication

## Getting Started

### Prerequisites

- Node.js >= 16.x
- Python >= 3.10
- pipenv

### Installation

1. **Frontend dependencies are automatically installed in the background during project creation.**
   You can start development immediately - dependencies will install while you work.
   If you need to reinstall them manually:
   ```bash
   cd frontend/vuejs
   npm install
   ```

2. **Install backend dependencies:**
   ```bash
   cd backend/django
   pipenv install
   ```

3. **Setup Django database:**
   ```bash
   cd backend/django
   pipenv shell
   python manage.py migrate
   python manage.py createsuperuser  # Optional
   ```

### Development

**Start both servers using the included scripts:**

**On Unix/Linux/macOS:**
```bash
./start-dev.sh
```

**On Windows:**
```bash
start-dev.bat
```

**Or start them separately:**

**Frontend (VueJS + Vite):**
```bash
cd frontend/vuejs
npm run dev
```
Frontend will be available at: http://localhost:5173

**Backend (Django):**
```bash
cd backend/django
pipenv shell
python manage.py runserver
```
Backend API will be available at: http://localhost:8000

### API Endpoints

- `GET /api/health/` - Health check endpoint
- `GET/POST /api/example/` - Example API endpoint

### Project Structure

```
{project_name}/
├── frontend/vuejs/          # VueJS frontend application
│   ├── src/
│   │   ├── components/      # Vue components
│   │   ├── views/          # Page views
│   │   ├── stores/         # Pinia stores
│   │   └── services/       # API services
│   └── package.json
├── backend/django/         # Django backend application
│   ├── api/               # Django API app
│   ├── {project_name}/    # Django project settings
│   └── manage.py
└── README.md
```

## Building for Production

**Frontend:**
```bash
cd frontend/vuejs
npm run build
```

**Backend:**
Configure production settings and deploy using your preferred method.
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
                        f.write(self._generate_basic_manage_py(project_name))
                    try:
                        os.chmod(manage_path, 0o755)
                    except:
                        pass
                
                # For legacy projects, create basic Django structure if missing
                settings_path = os.path.join(project_package_dir, 'settings.py')
                if not os.path.exists(settings_path):
                    with open(settings_path, 'w') as f:
                        f.write(self._generate_basic_settings_py(project_name))
                    logger.info(f"Created settings.py at {settings_path}")
                
                urls_path = os.path.join(project_package_dir, 'urls.py')
                if not os.path.exists(urls_path):
                    with open(urls_path, 'w') as f:
                        f.write(self._generate_basic_project_urls())
                    logger.info(f"Created urls.py at {urls_path}")
                
                views_path = os.path.join(project_package_dir, 'views.py')
                if not os.path.exists(views_path):
                    with open(views_path, 'w') as f:
                        f.write(self._generate_basic_project_views_content())
                    logger.info(f"Created views.py at {views_path}")
            
            logger.info(f"Project structure verification completed for {project_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error ensuring project structure: {str(e)}")
            import traceback
            logger.error(f"Stack trace: {traceback.format_exc()}")
            # Don't raise the exception, just return False
            return False 