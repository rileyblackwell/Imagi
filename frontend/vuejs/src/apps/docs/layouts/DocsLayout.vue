<template>
  <DashboardLayout
    storageKey="docs_sidebar_collapsed"
    class="docs-layout spotlight"
    aside-width-class="w-64"
    content-offset-class="md:ml-64"
    mobile-default-collapsed
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

    <!-- The Spotlight stage: the page floor, and a soft light falling on the
         top of the reading column (matching the home page) -->
    <div class="fixed inset-0 pointer-events-none z-0" aria-hidden="true">
      <div class="docs-canvas absolute inset-0"></div>
      <div class="docs-light absolute inset-x-0 top-0"></div>
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
/* The canvas sits in a fixed layer outside the .editorial element, but inside
   .spotlight (the layout root), so it reads the Spotlight tokens directly. */
.docs-canvas {
  background: var(--sl-bg);
}

.docs-light {
  height: 520px;
  background:
    radial-gradient(ellipse 55% 70% at 55% -10%, var(--sl-spot-core) 0%, var(--sl-spot-mid) 40%, transparent 72%);
  opacity: 0.85;
}

/* Running text that sets no colour of its own (the Getting Started lists)
   would otherwise inherit App.vue's near-black and read louder than the prose
   around it. */
.docs-content {
  color: var(--ink-70);
}

.docs-content :deep(a) {
  text-decoration: none;
}
</style>

<style>
/* The docs shell sits inside DashboardLayout, so these few rules reach the
   sidebar slot content from outside the scoped block. Colours are Spotlight
   tokens, set on the layout root. */
.docs-layout .docs-sidebar-label {
  font-size: 0.68rem;
  font-weight: 600;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--sl-faint);
}

.docs-layout .docs-nav-link {
  position: relative;
  display: block;
  padding: 0.5rem 0.75rem;
  border-radius: 10px;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--sl-muted);
  transition: color 0.18s ease, background 0.18s ease;
}

.docs-layout .docs-nav-link:hover {
  color: var(--sl-text);
  background: var(--sl-chip-bg);
}

/* Selected page: a lit chip with the gradient pip beside its label. */
.docs-layout .docs-nav-link.is-active {
  padding-left: 1.4rem;
  color: var(--sl-text);
  background: var(--sl-chip-bg-hover);
}

.docs-layout .docs-nav-link.is-active::before {
  content: '';
  position: absolute;
  left: 0.65rem;
  top: 50%;
  width: 6px;
  height: 6px;
  margin-top: -3px;
  border-radius: 50%;
  background: var(--sl-grad);
  box-shadow: 0 0 8px var(--sl-coral);
}

.docs-layout .docs-nav-link:focus-visible {
  outline: 2px solid var(--sl-focus);
  outline-offset: 2px;
}
</style>
