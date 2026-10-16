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


# The site's look, shared by every page: the layout's header and footer and
# each page's own content take their colours, corners and fonts from these
# variables, so pages built at the same time by different threads still read
# as one site. The first build fills in the business's own colours as soon as
# it has them (theme_css).
THEME_CSS_TEMPLATE = """/* The site's look, shared by the header, the footer and every page.
   Style pages with these variables (for example var(--site-accent)) rather
   than fixed colours, so the whole site stays consistent. */
:root {
  --site-accent: __ACCENT__;
  --site-on-accent: __ACCENT_TEXT__;
  --site-bg: __BACKGROUND__;
  --site-surface: #ffffff;
  --site-text: #0f172a;
  --site-muted: #475569;
  --site-border: #e2e8f0;
  --site-radius: 14px;
  --site-font-heading: ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  --site-font-body: ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}
"""

DEFAULT_ACCENT = '#2563eb'
DEFAULT_BACKGROUND = '#f8fafc'


def _text_on(hex_colour: str) -> str:
    """Black or white, whichever reads better on this colour."""
    r, g, b = (int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5))

    def lin(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    luminance = 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)
    return '#0f172a' if luminance > 0.4 else '#ffffff'


def theme_css(accent: str = DEFAULT_ACCENT, background: str = DEFAULT_BACKGROUND) -> str:
    """The shared theme with these colours (each a '#rrggbb' hex)."""
    return (
        THEME_CSS_TEMPLATE.replace('__ACCENT__', accent)
        .replace('__ACCENT_TEXT__', _text_on(accent))
        .replace('__BACKGROUND__', background)
    )


THEME_CSS = theme_css()

# Every page of the site renders inside this layout (the home router nests
# its routes under it), so the header, navigation and footer are written once
# and are the same on every page. The sign-in links live here too. Pages
# write only their own content. The header shows the first few pages and
# folds the rest into a More menu, so a long page list never crowds it.
SITE_LAYOUT_VUE = """<template>
  <div class="site min-h-screen flex flex-col">
    <header class="site-header">
      <nav class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4" aria-label="Main">
        <div class="flex items-center justify-between gap-6">
          <router-link to="/" class="site-brand min-w-0 truncate lg:shrink-0 text-xl font-bold tracking-tight">{{ brand.name }}</router-link>
          <div class="hidden lg:flex min-w-0 flex-1 items-center justify-end gap-x-6">
            <router-link v-for="p in primary" :key="p.path" :to="p.path" class="site-link text-sm font-medium whitespace-nowrap">{{ p.label }}</router-link>
            <div v-if="more.length" class="relative">
              <button type="button" class="site-link text-sm font-medium" :aria-expanded="moreOpen" @click="moreOpen = !moreOpen">More</button>
              <div v-if="moreOpen" class="site-menu absolute right-0 z-30 mt-3 flex w-56 flex-col gap-1 p-2">
                <router-link v-for="p in more" :key="p.path" :to="p.path" class="site-menu-link px-3 py-2 text-sm font-medium">{{ p.label }}</router-link>
              </div>
            </div>
            <template v-if="authStore.isAuthenticated">
              <span class="site-muted text-sm">{{ authStore.user?.username }}</span>
              <button type="button" class="site-link text-sm font-medium" @click="authStore.logout($router)">Sign out</button>
            </template>
            <template v-else>
              <router-link to="/auth/signin" class="site-link text-sm font-medium whitespace-nowrap">Sign in</router-link>
              <router-link to="/auth/register" class="site-button px-4 py-2 text-sm font-semibold whitespace-nowrap">Create account</router-link>
            </template>
          </div>
          <button
            type="button"
            class="lg:hidden -mr-2 p-2 site-link"
            :aria-expanded="menuOpen"
            aria-label="Menu"
            @click="menuOpen = !menuOpen"
          >
            <svg class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true">
              <path v-if="menuOpen" d="M6 6l12 12M18 6L6 18" />
              <path v-else d="M4 7h16M4 12h16M4 17h16" />
            </svg>
          </button>
        </div>
        <div v-if="menuOpen" class="site-menu lg:hidden mt-4 flex flex-col gap-1 p-2">
          <router-link v-for="p in links" :key="p.path" :to="p.path" class="site-menu-link px-3 py-2 font-medium">{{ p.label }}</router-link>
          <button v-if="authStore.isAuthenticated" type="button" class="site-menu-link px-3 py-2 text-left font-medium" @click="authStore.logout($router)">Sign out</button>
          <template v-else>
            <router-link to="/auth/signin" class="site-menu-link px-3 py-2 font-medium">Sign in</router-link>
            <router-link to="/auth/register" class="site-button px-3 py-2 text-center font-semibold">Create account</router-link>
          </template>
        </div>
      </nav>
    </header>

    <main class="flex-grow">
      <router-view />
    </main>

    <footer class="site-footer">
      <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 flex flex-col gap-6 sm:flex-row sm:items-start sm:justify-between">
        <div class="site-brand text-lg font-bold">{{ brand.name }}</div>
        <div class="flex flex-wrap gap-x-6 gap-y-2">
          <router-link v-for="p in sitePages" :key="p.path" :to="p.path" class="site-muted text-sm hover:underline">{{ p.label }}</router-link>
        </div>
        <div class="site-muted text-sm">&copy; {{ year }} {{ brand.name }}</div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../../auth/stores/index'
import { brand } from '../../auth/brand'
import { sitePages } from '../site-pages'
import '../styles/theme.css'

// Pages shown in the header before the rest fold into More.
const HEADER_LINKS = 6

const authStore = useAuthStore()
const route = useRoute()
const menuOpen = ref(false)
const moreOpen = ref(false)
const year = new Date().getFullYear()
const links = computed(() => sitePages.filter((p) => p.path !== '/'))
const primary = computed(() =>
  links.value.length > HEADER_LINKS + 1 ? links.value.slice(0, HEADER_LINKS) : links.value
)
const more = computed(() => links.value.slice(primary.value.length))

watch(() => route.fullPath, () => {
  menuOpen.value = false
  moreOpen.value = false
})
</script>

<style scoped>
.site {
  background: var(--site-bg);
  color: var(--site-text);
  font-family: var(--site-font-body);
}
.site-header {
  position: sticky;
  top: 0;
  z-index: 20;
  background: color-mix(in srgb, var(--site-bg) 88%, transparent);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--site-border);
}
.site-brand {
  font-family: var(--site-font-heading);
  color: var(--site-text);
}
.site-link {
  color: var(--site-muted);
  transition: color 0.15s;
}
.site-link:hover,
.site-link.router-link-exact-active {
  color: var(--site-text);
}
.site-muted {
  color: var(--site-muted);
}
.site-button {
  background: var(--site-accent);
  color: var(--site-on-accent);
  border-radius: var(--site-radius);
  transition: opacity 0.15s;
}
.site-button:hover {
  opacity: 0.9;
}
.site-menu {
  background: var(--site-surface);
  border: 1px solid var(--site-border);
  border-radius: var(--site-radius);
  box-shadow: 0 12px 32px rgb(15 23 42 / 0.12);
}
.site-menu-link {
  color: var(--site-text);
  border-radius: calc(var(--site-radius) - 4px);
}
.site-menu-link:hover {
  background: var(--site-bg);
}
.site-footer {
  border-top: 1px solid var(--site-border);
}
a:focus-visible,
button:focus-visible {
  outline: 2px solid var(--site-accent);
  outline-offset: 2px;
}
</style>
"""

# The home page's starting content. The header, navigation and footer come
# from the shared layout, so a page is just its own content.
HOME_VIEW_VUE = """<template>
  <section class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-24 text-center">
    <h1 class="text-4xl sm:text-5xl font-bold mb-6" style="font-family: var(--site-font-heading)">Welcome</h1>
    <p class="text-xl max-w-3xl mx-auto mb-10" style="color: var(--site-muted)">
      Welcome to your new project. Sign in or create an account to get started.
    </p>
    <div class="flex flex-wrap items-center justify-center gap-4">
      <router-link
        to="/auth/register"
        class="px-8 py-4 font-semibold"
        style="background: var(--site-accent); color: var(--site-on-accent); border-radius: var(--site-radius)"
      >
        Get started
      </router-link>
      <router-link
        to="/auth/signin"
        class="px-8 py-4 font-semibold"
        style="border: 1px solid var(--site-border); border-radius: var(--site-radius)"
      >
        Sign in
      </router-link>
    </div>
  </section>
</template>

<script setup lang="ts">
</script>
"""


def _placeholder_view(heading: str, blurb: str) -> str:
    """A self-contained placeholder page's content.

    Imports nothing: this is what the project serves if the first build never
    runs (no API key configured) or if this page's subagent is discarded, so
    it has to stand on its own. The shared layout supplies the header.
    """
    return f"""<template>
  <section class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-24 text-center">
    <h1 class="text-5xl font-bold mb-6" style="font-family: var(--site-font-heading)">{heading}</h1>
    <p class="text-xl max-w-3xl mx-auto" style="color: var(--site-muted)">{blurb}</p>
  </section>
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
import SiteLayout from '../layouts/SiteLayout.vue'
import HomeView from '../views/HomeView.vue'
import AboutView from '../views/AboutView.vue'
import ContactView from '../views/ContactView.vue'

// Every page renders inside SiteLayout, which holds the shared header,
// navigation and footer.
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: SiteLayout,
    children: [
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
  }
]

export { routes }
"""

HOME_VIEWS_INDEX_TS = """export { default as HomeView } from './HomeView.vue'
export { default as AboutView } from './AboutView.vue'
export { default as ContactView } from './ContactView.vue'
"""


SITE_PAGES_TS = """// Kept by Imagi: the site's pages that are ready, in navigation order.
// Build navigation from this list instead of hard-coding links.
export interface SitePage {
  path: string
  label: string
}

export const sitePages: SitePage[] = [
  { path: "/", label: "Home" },
  { path: "/about", label: "About" },
  { path: "/contact", label: "Contact" },
]
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
            # The header, navigation and footer every page renders inside.
            'name': f'frontend/vuejs/src/apps/{app_name}/layouts/SiteLayout.vue',
            'type': 'vue',
            'content': SITE_LAYOUT_VUE,
        },
        {
            # The site's shared colours, corners and fonts.
            'name': f'frontend/vuejs/src/apps/{app_name}/styles/theme.css',
            'type': 'css',
            'content': THEME_CSS,
        },
        {
            # The navigation list the first build's pages render; the build
            # rewrites it as pages are planned and finish (initial_page_plan).
            'name': f'frontend/vuejs/src/apps/{app_name}/site-pages.ts',
            'type': 'typescript',
            'content': SITE_PAGES_TS,
        },
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
