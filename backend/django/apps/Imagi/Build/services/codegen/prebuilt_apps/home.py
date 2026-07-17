"""
Home app prebuilt template.
Generates frontend (Vue) and backend (Django) files for the home app.
"""
from __future__ import annotations

from typing import Dict, List

from .shared import _frontend_scaffold, _backend_scaffold


HOME_VIEW_VUE = """<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex flex-col">
    <!-- Header with auth links -->
    <header class="w-full">
      <nav class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-5 flex items-center justify-between">
        <router-link to="/" class="text-xl font-bold text-gray-900">Home</router-link>
        <div class="flex items-center gap-4">
          <template v-if="authStore.isAuthenticated">
            <span class="text-sm text-gray-600">{{ authStore.user?.username }}</span>
            <button
              class="text-sm font-medium text-gray-700 hover:text-gray-900"
              @click="authStore.logout($router)"
            >
              Sign out
            </button>
          </template>
          <template v-else>
            <router-link to="/auth/signin" class="text-sm font-medium text-gray-700 hover:text-gray-900">
              Sign in
            </router-link>
            <router-link
              to="/auth/register"
              class="text-sm font-medium px-4 py-2 rounded-lg bg-gray-900 text-white hover:bg-gray-700 transition-colors"
            >
              Create account
            </router-link>
          </template>
        </div>
      </nav>
    </header>

    <!-- Hero -->
    <main class="flex-grow flex items-center">
      <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-16 text-center">
        <h1 class="text-5xl font-bold text-gray-900 mb-6">Welcome</h1>
        <p class="text-xl text-gray-600 max-w-3xl mx-auto mb-10">
          Welcome to your new project. Sign in or create an account to get started.
        </p>
        <div class="flex items-center justify-center gap-4">
          <router-link
            to="/auth/register"
            class="px-8 py-4 rounded-xl bg-gray-900 text-white font-medium hover:bg-gray-700 transition-colors"
          >
            Get started
          </router-link>
          <router-link
            to="/auth/signin"
            class="px-8 py-4 rounded-xl border border-gray-300 text-gray-900 font-medium hover:bg-gray-100 transition-colors"
          >
            Sign in
          </router-link>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '../../auth/stores/index'

const authStore = useAuthStore()
</script>
"""


def home_app_files() -> List[Dict[str, str]]:
    app_name = 'home'
    cap = 'Home'
    welcome = 'Welcome to your project home app.'
    files: List[Dict[str, str]] = []
    files += _frontend_scaffold(app_name, cap, welcome)
    files += _backend_scaffold(app_name, cap)
    for f in files:
        # Override the home app router to serve '/' instead of '/home'
        if f['name'] == f'frontend/vuejs/src/apps/{app_name}/router/index.ts':
            f['content'] = f['content'].replace("path: '/home'", "path: '/'")
        # Override the generic view with a landing page that links to the
        # prebuilt auth app's sign-in and register pages
        elif f['name'] == f'frontend/vuejs/src/apps/{app_name}/views/{cap}View.vue':
            f['content'] = HOME_VIEW_VUE
    return files
