"""
Shared scaffold helpers for prebuilt app templates.
Generates common frontend (Vue) and backend (Django) file structures.
"""
from __future__ import annotations

from typing import Dict, List


def _frontend_scaffold(app_name: str, cap_name: str, welcome: str) -> List[Dict[str, str]]:
    return [
        {
            'name': f'frontend/vuejs/src/apps/{app_name}/index.ts',
            'type': 'typescript',
            'content': """// {cap} app entry point
export * from './router'
export * from './stores'
export * from './components'
export * from './views'
""".replace('{cap}', cap_name),
        },
        {
            'name': f'frontend/vuejs/src/apps/{app_name}/router/index.ts',
            'type': 'typescript',
            'content': f"""import type {{ RouteRecordRaw }} from 'vue-router'
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
""",
        },
        {
            'name': f'frontend/vuejs/src/apps/{app_name}/stores/index.ts',
            'type': 'typescript',
            'content': "export * from './{app_name}'\n".format(app_name=app_name),
        },
        {
            'name': f'frontend/vuejs/src/apps/{app_name}/stores/{app_name}.ts',
            'type': 'typescript',
            'content': f"""import {{ defineStore }} from 'pinia'
import {{ ref }} from 'vue'

export const use{cap_name}Store = defineStore('{app_name}', () => {{
  const loading = ref(false)
  const setLoading = (v: boolean) => (loading.value = v)
  return {{ loading, setLoading }}
}})
""",
        },
        {
            'name': f'frontend/vuejs/src/apps/{app_name}/components/index.ts',
            'type': 'typescript',
            'content': "export * from './atoms'\nexport * from './molecules'\nexport * from './organisms'\n",
        },
        {
            'name': f'frontend/vuejs/src/apps/{app_name}/components/atoms/index.ts',
            'type': 'typescript',
            'content': '// atoms\n',
        },
        {
            'name': f'frontend/vuejs/src/apps/{app_name}/components/molecules/index.ts',
            'type': 'typescript',
            'content': '// molecules\n',
        },
        {
            'name': f'frontend/vuejs/src/apps/{app_name}/components/organisms/index.ts',
            'type': 'typescript',
            'content': '// organisms\n',
        },
        {
            'name': f'frontend/vuejs/src/apps/{app_name}/views/{cap_name}View.vue',
            'type': 'vue',
            'content': f"""<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 py-12">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center mb-16">
        <h1 class="text-5xl font-bold text-gray-900 mb-6">{cap_name} App</h1>
        <p class="text-xl text-gray-600 max-w-3xl mx-auto">{welcome}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
</script>
""",
        },
        {
            'name': f"frontend/vuejs/src/apps/{app_name}/views/index.ts",
            'type': 'typescript',
            'content': f"export {{ default as {cap_name}View }} from './{cap_name}View.vue'\n",
        },
    ]


def _backend_scaffold(app_name: str, cap_name: str) -> List[Dict[str, str]]:
    app_module = f"apps.{app_name}"
    return [
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
