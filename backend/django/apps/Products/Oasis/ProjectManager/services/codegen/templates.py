"""
Template and content generators for ProjectCreationService.

This module centralizes all large string templates and content generation
used to scaffold VueJS frontend and Django backend projects.
"""
from __future__ import annotations

import os
import json
from typing import Dict

# =============================
# VueJS Frontend Templates
# =============================

def vite_config() -> str:
    return """import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
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
"""


def tailwind_config() -> str:
    return (
        "/** @type {import('tailwindcss').Config} */\n"
        "export default {\n"
        "  content: [\n"
        "    \"./index.html\",\n"
        "    \"./src/**/*.{vue,js,ts,jsx,tsx}\",\n"
        "  ],\n"
        "  theme: {\n"
        "    extend: {},\n"
        "  },\n"
        "  plugins: [],\n"
        "}\n"
    )


def django_additional_settings() -> str:
    """Django CORS and DRF settings snippet to append to settings.py."""
    return (
        """
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
    )


def postcss_config() -> str:
    return (
        "export default {\n"
        "  plugins: {\n"
        "    tailwindcss: {},\n"
        "    autoprefixer: {},\n"
        "  },\n"
        "}\n"
    )


def index_html(project_name: str) -> str:
    return (
        f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{project_name}</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>
"""
    )


def vue_main_js() -> str:
    return """import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './assets/css/main.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
"""


def vue_app_vue(project_name: str, project_description: str | None) -> str:
    return """<template>
  <div id=\"app\" class=\"min-h-screen bg-gray-50\">
    <RouterView />
  </div>
</template>

<script setup lang=\"ts\">
import { RouterView } from 'vue-router'
</script>
"""


def vue_router_index() -> str:
    return """import { createRouter, createWebHistory } from 'vue-router'
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
"""


def vue_store_main() -> str:
    return """import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useMainStore = defineStore('main', () => {
  const message = ref('Hello from Pinia store!')

  function updateMessage(newMessage) {
    message.value = newMessage
  }

  return { message, updateMessage }
})
"""


def vue_api_service() -> str:
    return """import axios from 'axios'

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
"""


def vue_home_view(project_name: str, project_description: str | None) -> str:
    safe_project_name = project_name.replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
    safe_description = (project_description or '').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
    content = (
        "<template>\n"
        "  <div class=\"min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100\">\n"
        "    <div class=\"container mx-auto px-4 py-16\">\n"
        "      <div class=\"max-w-4xl mx-auto text-center\">\n"
        "        <h1 class=\"text-5xl font-bold text-gray-900 mb-6\">\n"
        "          Welcome to " + safe_project_name + "\n"
        "        </h1>\n\n"
        "        <p v-if=\"description\" class=\"text-xl text-gray-600 mb-8 max-w-2xl mx-auto\">\n"
        "          " + safe_description + "\n"
        "        </p>\n\n"
        "        <div class=\"bg-white rounded-2xl shadow-xl p-8 mb-8\">\n"
        "          <h2 class=\"text-2xl font-semibold text-gray-800 mb-4\">\n"
        "            Your VueJS + Django Application\n"
        "          </h2>\n"
        "          <p class=\"text-gray-600 mb-6\">\n"
        "            This project includes a modern VueJS frontend with Vite, TailwindCSS, and Pinia, \n"
        "            connected to a Django REST API backend.\n"
        "          </p>\n\n"
        "          <div class=\"grid md:grid-cols-2 gap-6\">\n"
        "            <div class=\"bg-blue-50 p-6 rounded-xl\">\n"
        "              <h3 class=\"text-lg font-medium text-blue-900 mb-2\">Frontend Tech Stack</h3>\n"
        "              <ul class=\"text-blue-700 space-y-1\">\n"
        "                <li>• Vue 3 with Composition API</li>\n"
        "                <li>• Vite for fast development</li>\n"
        "                <li>• TailwindCSS for styling</li>\n"
        "                <li>• Pinia for state management</li>\n"
        "                <li>• Axios for API calls</li>\n"
        "              </ul>\n"
        "            </div>\n\n"
        "            <div class=\"bg-green-50 p-6 rounded-xl\">\n"
        "              <h3 class=\"text-lg font-medium text-green-900 mb-2\">Backend Tech Stack</h3>\n"
        "              <ul class=\"text-green-700 space-y-1\">\n"
        "                <li>• Django 4.x framework</li>\n"
        "                <li>• Django REST Framework</li>\n"
        "                <li>• SQLite database</li>\n"
        "                <li>• CORS enabled</li>\n"
        "                <li>• Token authentication</li>\n"
        "              </ul>\n"
        "            </div>\n"
        "          </div>\n"
        "        </div>\n\n"
        "        <div class=\"flex flex-col sm:flex-row gap-4 justify-center\">\n"
        "          <button\n"
        "            @click=\"testApiConnection\"\n"
        "            :disabled=\"loading\"\n"
        "            class=\"bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-6 py-3 rounded-lg font-medium transition-colors\"\n"
        "          >\n"
        "            {{ loading ? 'Testing...' : 'Test API Connection' }}\n"
        "          </button>\n\n"
        "          <button\n"
        "            @click=\"updateStoreMessage\"\n"
        "            class=\"bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg font-medium transition-colors\"\n"
        "          >\n"
        "            Test Pinia Store\n"
        "          </button>\n"
        "        </div>\n\n"
        "        <div v-if=\"apiStatus\" class=\"mt-6 p-4 rounded-lg\" :class=\"apiStatus.success ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'\">\n"
        "          {{ apiStatus.message }}\n"
        "        </div>\n\n"
        "        <div class=\"mt-6 p-4 bg-gray-100 rounded-lg\">\n"
        "          <p class=\"text-gray-700\">Store Message: {{ mainStore.message }}</p>\n"
        "        </div>\n"
        "      </div>\n"
        "    </div>\n"
        "  </div>\n"
        "</template>\n\n"
        "<script setup>\n"
        "import { ref } from 'vue'\n"
        "import { useMainStore } from '@/stores/main'\n"
        "import api from '@/services/api'\n\n"
        "const mainStore = useMainStore()\n"
        "const loading = ref(false)\n"
        "const apiStatus = ref(null)\n"
        "const description = '" + safe_description + "'\n\n"
        "async function testApiConnection() {\n"
        "  loading.value = true\n"
        "  apiStatus.value = null\n\n"
        "  try {\n"
        "    const response = await api.get('/health/')\n"
        "    apiStatus.value = {\n"
        "      success: true,\n"
        "      message: 'API connection successful! Backend is running.'\n"
        "    }\n"
        "  } catch (error) {\n"
        "    apiStatus.value = {\n"
        "      success: false,\n"
        "      message: 'API connection failed. Make sure the Django backend is running on port 8000.'\n"
        "    }\n"
        "  } finally {\n"
        "    loading.value = false\n"
        "  }\n"
        "}\n\n"
        "function updateStoreMessage() {\n"
        "  const messages = [\n"
        "    'Pinia store is working!',\n"
        "    'State management is active!',\n"
        "    'VueJS + Pinia = ❤️',\n"
        "    'Store updated successfully!'\n"
        "  ]\n"
        "  const randomMessage = messages[Math.floor(Math.random() * messages.length)]\n"
        "  mainStore.updateMessage(randomMessage)\n"
        "}\n"
        "</script>\n"
    )
    return content


def vue_main_css() -> str:
    return """@tailwind base;
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
"""

# =============================
# VueJS Scaffolding Helpers (file writers)
# =============================

def _sanitize_project_name(name: str) -> str:
    """Convert project name to a valid identifier for package names."""
    sanitized = ''.join(c if c.isalnum() else '_' for c in name)
    if not sanitized or not sanitized[0].isalpha():
        sanitized = 'project_' + sanitized
    return sanitized


def create_vuejs_frontend_files(frontend_path: str, project_name: str, project_description: str | None) -> None:
    """Create VueJS frontend with Vite, Pinia, TailwindCSS, and Axios (vanilla JS)."""
    # package.json (vanilla JS, no TypeScript)
    package_json = {
        "name": f"{_sanitize_project_name(project_name).lower()}-frontend",
        "private": True,
        "version": "0.0.0",
        "type": "module",
        "scripts": {
            "dev": "vite",
            "build": "vite build",
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
            "@vitejs/plugin-vue": "^4.5.0",
            "autoprefixer": "^10.4.16",
            "postcss": "^8.4.32",
            "tailwindcss": "^3.3.6",
            "vite": "^5.0.0"
        }
    }

    with open(os.path.join(frontend_path, 'package.json'), 'w') as f:
        f.write(json.dumps(package_json, indent=2))

    # vite.config.js
    with open(os.path.join(frontend_path, 'vite.config.js'), 'w') as f:
        f.write(vite_config())

    # jsconfig.json for better VS Code support
    jsconfig = {
        "compilerOptions": {
            "target": "ESNext",
            "lib": ["ESNext", "DOM", "DOM.Iterable"],
            "module": "ESNext",
            "moduleResolution": "bundler",
            "resolveJsonModule": True,
            "jsx": "preserve",
            "baseUrl": ".",
            "paths": {
                "@/*": ["./src/*"]
            }
        },
        "include": ["src/**/*.js", "src/**/*.vue"],
        "exclude": ["node_modules", "dist"]
    }

    with open(os.path.join(frontend_path, 'jsconfig.json'), 'w') as f:
        f.write(json.dumps(jsconfig, indent=2))

    # Tailwind and PostCSS
    with open(os.path.join(frontend_path, 'tailwind.config.js'), 'w') as f:
        f.write(tailwind_config())

    with open(os.path.join(frontend_path, 'postcss.config.js'), 'w') as f:
        f.write(postcss_config())

    # index.html
    with open(os.path.join(frontend_path, 'index.html'), 'w') as f:
        f.write(index_html(project_name))

    # src files
    create_vuejs_src_files(frontend_path, project_name, project_description)


def create_vuejs_src_files(frontend_path: str, project_name: str, project_description: str | None) -> None:
    """Create VueJS source files structure under src/."""
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

    # main.js
    with open(os.path.join(src_path, 'main.js'), 'w') as f:
        f.write(vue_main_js())

    # App.vue
    with open(os.path.join(src_path, 'App.vue'), 'w') as f:
        f.write(vue_app_vue(project_name, project_description))

    # router/index.js
    with open(os.path.join(src_path, 'router', 'index.js'), 'w') as f:
        f.write(vue_router_index())

    # stores/main.js
    with open(os.path.join(src_path, 'stores', 'main.js'), 'w') as f:
        f.write(vue_store_main())

    # services/api.js
    with open(os.path.join(src_path, 'services', 'api.js'), 'w') as f:
        f.write(vue_api_service())

    # views/HomeView.vue
    with open(os.path.join(src_path, 'views', 'HomeView.vue'), 'w') as f:
        f.write(vue_home_view(project_name, project_description))

    # assets/css/main.css
    with open(os.path.join(src_path, 'assets', 'css', 'main.css'), 'w') as f:
        f.write(vue_main_css())


# =============================
# Dev Scripts
# =============================

def start_dev_sh() -> str:
    return (
        "#!/bin/bash\n"
        "# Development startup script for dual-stack application\n\n"
        "echo \"🚀 Starting development servers...\"\n\n"
        "# Function to cleanup background processes\n"
        "cleanup() {\n"
        "    echo \"\"\n"
        "    echo \"🛑 Stopping development servers...\"\n"
        "    jobs -p | xargs -r kill\n"
        "    exit\n"
        "}\n\n"
        "# Set up signal handling\n"
        "trap cleanup SIGINT SIGTERM\n\n"
        "# Check if npm dependencies are installed\n"
        "if [ ! -d \"frontend/vuejs/node_modules\" ]; then\n"
        "    echo \"📦 Installing frontend dependencies...\"\n"
        "    cd frontend/vuejs && npm install && cd ../..\n"
        "fi\n\n"
        "# Start Django backend\n"
        "echo \"🐍 Starting Django backend on port 8000...\"\n"
        "cd backend/django && python manage.py runserver &\n"
        "DJANGO_PID=$!\n\n"
        "# Wait a moment for Django to start\n"
        "sleep 3\n\n"
        "# Start Vue frontend  \n"
        "echo \"⚡ Starting Vue frontend on port 5173...\"\n"
        "cd frontend/vuejs && npm run dev &\n"
        "VUE_PID=$!\n\n"
        "echo \"\"\n"
        "echo \"✅ Development servers started!\"\n"
        "echo \"🌐 Frontend: http://localhost:5173\"\n"
        "echo \"🔧 Backend API: http://localhost:8000\"\n"
        "echo \"📱 Press Ctrl+C to stop both servers\"\n\n"
        "# Wait for background processes\n"
        "wait\n"
    )


# =============================
# Django Backend Templates
# =============================

def django_pipfile() -> str:
    return (
        "[[source]]\n"
        "url = \"https://pypi.org/simple\"\n"
        "verify_ssl = true\n"
        "name = \"pypi\"\n\n"
        "[packages]\n"
        "django = \"~=4.2.3\"\n"
        "djangorestframework = \"~=3.14.0\"\n"
        "django-cors-headers = \"~=4.1.0\"\n\n"
        "[dev-packages]\n\n"
        "[requires]\n"
        "python_version = \"3.10\"\n"
    )


def django_project_views() -> str:
    return (
        "from django.shortcuts import render\n"
        "from django.http import HttpResponse, JsonResponse\n"
        "from django.views.generic import TemplateView\n\n"
        "def home(request):\n"
        "    \"\"\"Home page view.\"\"\"\n"
        "    return JsonResponse({\n"
        "        'message': 'Django backend is running!',\n"
        "        'status': 'success'\n"
        "    })\n\n"
        "class HomeView(TemplateView):\n"
        "    \"\"\"Class-based home page view.\"\"\"\n"
        "    template_name = 'index.html'\n"
    )


def django_base_template(project_name: str) -> str:
    return (
        f"<!DOCTYPE html>\n"
        f"<html lang=\"en\">\n"
        f"<head>\n"
        f"    <meta charset=\"UTF-8\">\n"
        f"    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
        f"    <title>{{% block title %}}{project_name}{{% endblock %}}</title>\n"
        f"    <link rel=\"stylesheet\" href=\"{{% static 'css/styles.css' %}}\">\n"
        f"    {{% block extra_css %}}{{% endblock %}}\n"
        f"</head>\n"
        f"<body>\n"
        f"    {{% block content %}}{{% endblock %}}\n\n"
        f"    {{% block extra_js %}}{{% endblock %}}\n"
        f"</body>\n"
        f"</html>\n"
    )


def django_index_template(project_name: str, project_description: str | None) -> str:
    safe_project_name = project_name.replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
    safe_description = (project_description or '').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
    description_content = ''
    if (project_description or '').strip():
        description_content = f"    <p class=\"project-description\">{safe_description}</p>"
    return (
        "{% extends 'base.html' %}\n"
        "{% load static %}\n\n"
        "{% block title %}Welcome | "
        + safe_project_name
        + "{% endblock %}\n\n"
        "{% block content %}\n"
        "<div class=\"welcome-container\">\n"
        "    <h1>Welcome to "
        + safe_project_name
        + "</h1>\n"
        + description_content
        + "\n    <p>This is your Django backend API. The frontend is served separately on port 5173.</p>\n"
        "    <div class=\"cta-button\">\n"
        "        <a href=\"/admin/\">Go to Admin</a>\n"
        "        <a href=\"/api/\">Browse API</a>\n"
        "    </div>\n"
        "</div>\n"
        "{% endblock %}\n"
    )


def django_static_css() -> str:
    return (
        "/* Django Backend Styles */\n"
        ":root {\n"
        "    --primary-color: #4f46e5;\n"
        "    --secondary-color: #818cf8;\n"
        "    --text-color: #1f2937;\n"
        "    --bg-color: #ffffff;\n"
        "}\n\n"
        "body {\n"
        "    font-family: system-ui, -apple-system, sans-serif;\n"
        "    color: var(--text-color);\n"
        "    background-color: var(--bg-color);\n"
        "    line-height: 1.5;\n"
        "    margin: 0;\n"
        "    padding: 0;\n"
        "}\n\n"
        ".welcome-container {\n"
        "    max-width: 800px;\n"
        "    margin: 5rem auto;\n"
        "    padding: 2rem;\n"
        "    background-color: #f9fafb;\n"
        "    border-radius: 0.5rem;\n"
        "    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);\n"
        "    text-align: center;\n"
        "}\n\n"
        "h1 {\n"
        "    color: var(--primary-color);\n"
        "    margin-bottom: 1rem;\n"
        "}\n\n"
        ".project-description {\n"
        "    font-size: 1.125rem;\n"
        "    color: #6b7280;\n"
        "    margin: 1.5rem 0;\n"
        "    font-style: italic;\n"
        "    line-height: 1.6;\n"
        "}\n\n"
        ".cta-button {\n"
        "    margin-top: 2rem;\n"
        "    display: flex;\n"
        "    gap: 1rem;\n"
        "    justify-content: center;\n"
        "    flex-wrap: wrap;\n"
        "}\n\n"
        ".cta-button a {\n"
        "    display: inline-block;\n"
        "    background-color: var(--primary-color);\n"
        "    color: white;\n"
        "    padding: 0.75rem 1.5rem;\n"
        "    border-radius: 0.375rem;\n"
        "    text-decoration: none;\n"
        "    font-weight: 500;\n"
        "    transition: background-color 0.2s;\n"
        "}\n\n"
        ".cta-button a:hover {\n"
        "    background-color: var(--secondary-color);\n"
        "}\n"
    )


# =============================
# Files for API app
# =============================

def api_apps_py() -> str:
    return (
        "from django.apps import AppConfig\n\n"
        "class ApiConfig(AppConfig):\n"
        "    default_auto_field = 'django.db.models.BigAutoField'\n"
        "    name = 'api'\n"
    )


def api_models_py() -> str:
    return (
        "from django.db import models\n\n"
        "class HealthCheck(models.Model):\n"
        "    \"\"\"Simple model for API health checks\"\"\"\n"
        "    timestamp = models.DateTimeField(auto_now_add=True)\n"
        "    status = models.CharField(max_length=20, default='healthy')\n\n"
        "    def __str__(self):\n"
        "        return f\"Health check at {self.timestamp}\"\n"
    )


def api_serializers_py() -> str:
    return (
        "from rest_framework import serializers\n"
        "from .models import HealthCheck\n\n"
        "class HealthCheckSerializer(serializers.ModelSerializer):\n"
        "    class Meta:\n"
        "        model = HealthCheck\n"
        "        fields = ['id', 'timestamp', 'status']\n"
    )


def api_views_py() -> str:
    return (
        "from rest_framework.decorators import api_view\n"
        "from rest_framework.response import Response\n"
        "from rest_framework import status\n"
        "from .models import HealthCheck\n"
        "from .serializers import HealthCheckSerializer\n\n"
        "@api_view(['GET'])\n"
        "def health_check(request):\n"
        "    \"\"\"Health check endpoint for frontend to test API connection\"\"\"\n"
        "    health = HealthCheck.objects.create()\n"
        "    serializer = HealthCheckSerializer(health)\n\n"
        "    return Response({\n"
        "        'status': 'healthy',\n"
        "        'message': 'Django backend is running successfully!',\n"
        "        'data': serializer.data\n"
        "    }, status=status.HTTP_200_OK)\n\n"
        "@api_view(['GET', 'POST'])\n"
        "def example_endpoint(request):\n"
        "    \"\"\"Example API endpoint\"\"\"\n"
        "    if request.method == 'GET':\n"
        "        return Response({\n"
        "            'message': 'This is a GET request to the Django API',\n"
        "            'data': {'example': 'data'}\n"
        "        })\n"
        "    elif request.method == 'POST':\n"
        "        return Response({\n"
        "            'message': 'This is a POST request to the Django API',\n"
        "            'received_data': request.data\n"
        "        })\n"
    )


def api_urls_py() -> str:
    return (
        "from django.urls import path\n"
        "from . import views\n\n"
        "urlpatterns = [\n"
        "    path('health/', views.health_check, name='health_check'),\n"
        "    path('example/', views.example_endpoint, name='example_endpoint'),\n"
        "]\n"
    )


def api_admin_py() -> str:
    return (
        "from django.contrib import admin\n"
        "from .models import HealthCheck\n\n"
        "@admin.register(HealthCheck)\n"
        "class HealthCheckAdmin(admin.ModelAdmin):\n"
        "    list_display = ['id', 'timestamp', 'status']\n"
        "    list_filter = ['status', 'timestamp']\n"
        "    readonly_fields = ['timestamp']\n"
    )


# =============================
# Miscellaneous project templates
# =============================

def fullstack_gitignore() -> str:
    return (
        "# Python\n"
        "__pycache__/\n"
        "*.py[cod]\n"
        "*$py.class\n"
        "*.so\n"
        ".Python\n"
        "env/\n"
        "build/\n"
        "develop-eggs/\n"
        "dist/\n"
        "downloads/\n"
        "eggs/\n"
        ".eggs/\n"
        "lib/\n"
        "lib64/\n"
        "parts/\n"
        "sdist/\n"
        "var/\n"
        "*.egg-info/\n"
        ".installed.cfg\n"
        "*.egg\n\n"
        "# Django\n"
        "*.log\n"
        "local_settings.py\n"
        "db.sqlite3\n"
        "db.sqlite3-journal\n"
        "media\n\n"
        "# Virtual Environment\n"
        "venv/\n"
        "ENV/\n\n"
        "# Node.js\n"
        "node_modules/\n"
        "npm-debug.log*\n"
        "yarn-debug.log*\n"
        "yarn-error.log*\n\n"
        "# IDE\n"
        ".idea/\n"
        ".vscode/\n"
        "*.swp\n"
        "*.swo\n\n"
        "# macOS\n"
        ".DS_Store\n\n"
        "# Windows\n"
        "Thumbs.db\n\n"
        "# Build outputs\n"
        "dist/\n"
        ".nuxt/\n"
        ".next/\n"
        "out/\n\n"
        "# Environment variables\n"
        ".env\n"
        ".env.local\n"
        ".env.development.local\n"
        ".env.test.local\n"
        ".env.production.local\n"
    )


def fullstack_readme(project_name: str, project_description: str | None) -> str:
    return (
        f"# {project_name}\n\n"
        f"{project_description or 'A full-stack web application with VueJS frontend and Django backend.'}\n\n"
        f"## Tech Stack\n\n"
        f"### Frontend\n"
        f"- **Vue 3** with Composition API\n"
        f"- **Vite** for fast development and building\n"
        f"- **TailwindCSS** for styling\n"
        f"- **Pinia** for state management\n"
        f"- **Axios** for API communication\n"
        f"- **TypeScript** for type safety\n\n"
        f"### Backend\n"
        f"- **Django 4.x** web framework\n"
        f"- **Django REST Framework** for API development\n"
        f"- **SQLite** database (development)\n"
        f"- **CORS** enabled for frontend communication\n\n"
        f"## Getting Started\n\n"
        f"### Prerequisites\n\n"
        f"- Node.js >= 16.x\n"
        f"- Python >= 3.10\n"
        f"- pipenv\n\n"
        f"### Installation\n\n"
        f"1. **Frontend dependencies are automatically installed in the background during project creation.**\n"
        f"   You can start development immediately - dependencies will install while you work.\n"
        f"   If you need to reinstall them manually:\n"
        f"   ```bash\n"
        f"   cd frontend/vuejs\n"
        f"   npm install\n"
        f"   ```\n\n"
        f"2. **Install backend dependencies:**\n"
        f"   ```bash\n"
        f"   cd backend/django\n"
        f"   pipenv install\n"
        f"   ```\n\n"
        f"3. **Setup Django database:**\n"
        f"   ```bash\n"
        f"   cd backend/django\n"
        f"   pipenv shell\n"
        f"   python manage.py migrate\n"
        f"   python manage.py createsuperuser  # Optional\n"
        f"   ```\n\n"
        f"### Development\n\n"
        f"**Start both servers using the included script:**\n\n"
        f"```bash\n"
        f"./start-dev.sh\n"
        f"```\n\n"
        f"**Or start them separately:**\n\n"
        f"**Frontend (VueJS + Vite):**\n"
        f"```bash\n"
        f"cd frontend/vuejs\n"
        f"npm run dev\n"
        f"```\n"
        f"Frontend will be available at: http://localhost:5173\n\n"
        f"**Backend (Django):**\n"
        f"```bash\n"
        f"cd backend/django\n"
        f"pipenv shell\n"
        f"python manage.py runserver\n"
        f"```\n"
        f"Backend API will be available at: http://localhost:8000\n\n"
        f"### API Endpoints\n\n"
        f"- `GET /api/health/` - Health check endpoint\n"
        f"- `GET/POST /api/example/` - Example API endpoint\n\n"
        f"### Project Structure\n\n"
        f"```\n"
        f"{project_name}/\n"
        f"├── frontend/vuejs/          # VueJS frontend application\n"
        f"│   ├── src/\n"
        f"│   │   ├── components/      # Vue components\n"
        f"│   │   ├── views/          # Page views\n"
        f"│   │   ├── stores/         # Pinia stores\n"
        f"│   │   └── services/       # API services\n"
        f"│   └── package.json\n"
        f"├── backend/django/         # Django backend application\n"
        f"│   ├── api/               # Django API app\n"
        f"│   ├── {project_name}/    # Django project settings\n"
        f"│   └── manage.py\n"
        f"└── README.md\n"
        f"```\n\n"
        f"## Building for Production\n\n"
        f"**Frontend:**\n"
        f"```bash\n"
        f"cd frontend/vuejs\n"
        f"npm run build\n"
        f"```\n\n"
        f"**Backend:**\n"
        f"Configure production settings and deploy using your preferred method.\n"
    )


# =============================
# Legacy/basic helpers
# =============================

def basic_model_py() -> str:
    return """from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
"""


def basic_views_py() -> str:
    return '''from django.shortcuts import render
from django.http import JsonResponse
from .models import Item

def index(request):
    # Render the index page
    items = Item.objects.all()
    return render(request, 'core/index.html', {'items': items})

def item_list(request):
    # Return a JSON list of items
    items = Item.objects.all().values('id', 'name', 'description')
    return JsonResponse({'items': list(items)})
'''


def basic_urls_py() -> str:
    return """from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/items/', views.item_list, name='item-list'),
]
"""


def basic_project_urls_py() -> str:
    return """from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
]
"""


def basic_project_views_py() -> str:
    return '''from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView

def home(request):
    # Home page view.
    return render(request, 'index.html')

class HomeView(TemplateView):
    # Class-based home page view.
    template_name = 'index.html'
'''


def basic_manage_py(project_name: str) -> str:
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


def basic_settings_py(project_name: str) -> str:
    secret_key = ''.join(['x' for _ in range(50)])
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
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = '{project_name}.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
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
