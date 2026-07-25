"""
Prebuilt marketing page apps: about, contact.

These exist so the initial build can run several subagents at once. Each
subagent is given ONE file to rewrite, which is the property the whole
time-budgeted first build rests on: a single self-contained file can never
reference something the agent did not get around to writing, so a run cut off
by the clock still merges. If a subagent had to create its page *and* the
router entry pointing at it, a run stopped between the two would leave a
dangling import and the build would be discarded.

Scaffolding the app up front moves that risk out of the agent's way entirely —
the route exists and resolves from the moment the project is created, and the
agent's whole job is to replace the placeholder view with a real page.

Unlike 'home' and 'auth' these are frontend-only: they are static marketing
pages with nothing to serve, so they get no Django app, no INSTALLED_APPS
entry, and no migrations. The route path, name and title all come from
_frontend_scaffold's defaults ('/about', '/contact'), so only the placeholder
view differs from a generic app.
"""
from __future__ import annotations

from typing import Dict, List

from .shared import _frontend_scaffold


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


def _page_app_files(app_name: str, cap: str, welcome: str, view_content: str) -> List[Dict[str, str]]:
    """Frontend-only scaffold for a static page app."""
    files = _frontend_scaffold(app_name, cap, welcome)
    for f in files:
        if f['name'] == f'frontend/vuejs/src/apps/{app_name}/views/{cap}View.vue':
            f['content'] = view_content
    return files


def about_app_files() -> List[Dict[str, str]]:
    return _page_app_files(
        'about', 'About', 'The story behind this business.', ABOUT_VIEW_VUE
    )


def contact_app_files() -> List[Dict[str, str]]:
    return _page_app_files(
        'contact', 'Contact', 'Get in touch with this business.', CONTACT_VIEW_VUE
    )
