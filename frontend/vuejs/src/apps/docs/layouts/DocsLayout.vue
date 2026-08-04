<template>
  <DashboardLayout
    :navigationItems="[]"
    storageKey="docs_sidebar_collapsed"
    class="docs-layout"
    aside-width-class="w-64"
    content-offset-class="md:ml-64"
    nav-offset-class="md:left-64"
    mobile-default-collapsed
    full-width-nav
  >
    <!-- Section header: a quiet uppercase eyebrow, aligned with the nav labels
         below it (icon dropped for a cleaner, text-forward panel). -->
    <template #sidebar-header>
      <div class="pl-3">
        <span class="docs-sidebar-label">Documentation</span>
      </div>
    </template>

    <template #sidebar-content>
      <nav class="px-3 pt-3 pb-6 space-y-0.5">
        <router-link
          v-for="item in navigationItems"
          :key="item.to"
          :to="item.to"
          :class="[
            'docs-nav-link',
            isActive(item.to) ? 'is-active' : ''
          ]"
        >
          <span class="truncate">{{ item.name }}</span>
        </router-link>
      </nav>
    </template>

    <!-- Warm porcelain canvas with a soft baby-blue wash and film grain (matching the home page) -->
    <div class="fixed inset-0 pointer-events-none z-0" aria-hidden="true">
      <div class="docs-canvas absolute inset-0"></div>
      <div class="grain-overlay absolute inset-0"></div>
    </div>

    <div class="editorial min-h-screen relative">
      <div class="relative z-10 p-6 md:p-8 lg:p-12 docs-content">
        <slot></slot>
      </div>
    </div>
  </DashboardLayout>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { DashboardLayout } from '@/shared/layouts'

const route = useRoute()

const navigationItems = [
  { name: 'Welcome', to: '/docs' },
  { name: 'Building with AI', to: '/docs/building' },
  { name: 'Running Your Business', to: '/docs/running-your-business' },
  { name: 'Models & Reasoning', to: '/docs/models' },
  { name: 'Plans & Usage', to: '/docs/plans' }
]

const isActive = (path) => route.path === path
</script>

<style scoped>
/* The canvas and grain sit in a fixed layer *outside* the .editorial element,
   so they can't read its custom properties — these carry literal values that
   mirror --paper and the shared grain. */
.docs-canvas {
  background: #fbfaf7;
}

:root.dark .docs-canvas {
  background: #08080a;
}

.docs-content :deep(a) {
  text-decoration: none;
}
</style>

<style>
/* The docs shell sits inside DashboardLayout, so these few rules reach the
   sidebar slot content from outside the scoped block. */
.docs-layout .docs-sidebar-label {
  font-size: 0.68rem;
  font-weight: 600;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: rgba(19, 26, 44, 0.42);
}

.dark .docs-layout .docs-sidebar-label {
  color: rgba(246, 244, 240, 0.4);
}

.docs-layout .docs-nav-link {
  display: block;
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
  font-weight: 500;
  border-left: 1px solid rgba(19, 26, 44, 0.11);
  color: rgba(19, 26, 44, 0.58);
  transition: color 0.18s ease, border-color 0.18s ease;
}

.dark .docs-layout .docs-nav-link {
  border-left-color: rgba(255, 255, 255, 0.1);
  color: rgba(246, 244, 240, 0.56);
}

.docs-layout .docs-nav-link:hover {
  color: rgba(19, 26, 44, 1);
}

.dark .docs-layout .docs-nav-link:hover {
  color: rgba(246, 244, 240, 1);
}

/* Selected page is marked by the accent rule, not a raised pill. */
.docs-layout .docs-nav-link.is-active {
  border-left-color: #c2410c;
  color: rgba(19, 26, 44, 1);
}

.dark .docs-layout .docs-nav-link.is-active {
  border-left-color: #fbbf24;
  color: rgba(246, 244, 240, 1);
}

.docs-layout .docs-nav-link:focus-visible {
  outline: 2px solid #c2410c;
  outline-offset: 2px;
}
</style>
