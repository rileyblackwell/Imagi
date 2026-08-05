"""
Home app prebuilt template.
Generates frontend (Vue) and backend (Django) files for the home app.

The home app owns the site's three public pages — home ('/'), about ('/about')
and contact ('/contact'). They live together because they are one thing: the
marketing front of the business, sharing a header, a footer and a navigation
between them. The workspace's page menu reads the app directory as the folder,
so this is also what makes it read 'home / about' rather than an 'about' app
holding a single page.

All three views are scaffolded up front, routed and resolving, because the
initial build hands each of its parallel subagents ONE file to rewrite. That is
the property the whole time-budgeted first build rests on: a single
self-contained file can never reference something the agent did not get around
to writing, so a run cut off by the clock still merges. If a subagent had to
create its page *and* the router entry pointing at it, a run stopped between
the two would leave a dangling import and the build would be discarded. The
router below is written once, here, and no agent ever touches it.
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
          <router-link to="/about" class="text-sm font-medium text-gray-700 hover:text-gray-900">
            About
          </router-link>
          <router-link to="/contact" class="text-sm font-medium text-gray-700 hover:text-gray-900">
            Contact
          </router-link>
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


def _placeholder_view(heading: str, blurb: str) -> str:
    """A self-contained placeholder page, styled like the home scaffold.

    Imports nothing: this is what the project serves if the first build never
    runs (no API key configured) or if this page's subagent is discarded, so
    it has to stand on its own.
    """
    return f"""<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex flex-col">
    <header class="w-full">
      <nav class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-5 flex items-center justify-between">
        <router-link to="/" class="text-xl font-bold text-gray-900">Home</router-link>
        <div class="flex items-center gap-4">
          <router-link to="/about" class="text-sm font-medium text-gray-700 hover:text-gray-900">
            About
          </router-link>
          <router-link to="/contact" class="text-sm font-medium text-gray-700 hover:text-gray-900">
            Contact
          </router-link>
        </div>
      </nav>
    </header>

    <main class="flex-grow flex items-center">
      <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-16 text-center">
        <h1 class="text-5xl font-bold text-gray-900 mb-6">{heading}</h1>
        <p class="text-xl text-gray-600 max-w-3xl mx-auto">{blurb}</p>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
</script>
"""


ABOUT_VIEW_VUE = _placeholder_view(
    'About', 'The story behind this business.'
)

CONTACT_VIEW_VUE = _placeholder_view(
    'Contact', 'Get in touch with this business.'
)


# The one router for all three public pages. Written out in full rather than
# patched from the generic scaffold: it is the file that must be correct and
# complete before any subagent starts.
HOME_ROUTER_TS = """import type { RouteRecordRaw } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import AboutView from '../views/AboutView.vue'
import ContactView from '../views/ContactView.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home-view',
    component: HomeView,
    meta: { requiresAuth: false, title: 'Home' }
  },
  {
    path: '/about',
    name: 'about-view',
    component: AboutView,
    meta: { requiresAuth: false, title: 'About' }
  },
  {
    path: '/contact',
    name: 'contact-view',
    component: ContactView,
    meta: { requiresAuth: false, title: 'Contact' }
  }
]

export { routes }
"""

HOME_VIEWS_INDEX_TS = """export { default as HomeView } from './HomeView.vue'
export { default as AboutView } from './AboutView.vue'
export { default as ContactView } from './ContactView.vue'
"""


def home_app_files() -> List[Dict[str, str]]:
    app_name = 'home'
    cap = 'Home'
    welcome = 'Welcome to your project home app.'
    files: List[Dict[str, str]] = []
    files += _frontend_scaffold(app_name, cap, welcome)
    files += _backend_scaffold(app_name, cap)
    views_dir = f'frontend/vuejs/src/apps/{app_name}/views'
    for f in files:
        # Serve all three public pages, not the generic single '/home' route
        if f['name'] == f'frontend/vuejs/src/apps/{app_name}/router/index.ts':
            f['content'] = HOME_ROUTER_TS
        # Override the generic view with a landing page that links to the
        # prebuilt auth app's sign-in and register pages
        elif f['name'] == f'{views_dir}/{cap}View.vue':
            f['content'] = HOME_VIEW_VUE
        elif f['name'] == f'{views_dir}/index.ts':
            f['content'] = HOME_VIEWS_INDEX_TS
    files += [
        {
            'name': f'{views_dir}/AboutView.vue',
            'type': 'vue',
            'content': ABOUT_VIEW_VUE,
        },
        {
            'name': f'{views_dir}/ContactView.vue',
            'type': 'vue',
            'content': CONTACT_VIEW_VUE,
        },
    ]
    return files
