<template>
  <DashboardLayout
    storageKey="docs_sidebar_collapsed"
    class="spotlight"
    aside-width-class="w-64"
    content-offset-class="md:ml-64"
    mobile-default-collapsed
    site-nav
  >
    <!-- Section header: a quiet uppercase eyebrow, aligned with the nav labels
         below it (icon dropped for a cleaner, text-forward panel). -->
    <template #sidebar-header>
      <div class="pl-3">
        <span class="text-[0.68rem] font-semibold uppercase tracking-[0.2em] text-sl-faint">Documentation</span>
      </div>
    </template>

    <template #sidebar-content>
      <nav class="px-3 pt-3 pb-6 space-y-0.5">
        <router-link
          v-for="item in navigationItems"
          :key="item.to"
          :to="item.to"
          class="relative block rounded-[10px] py-2 pr-3 text-[0.875rem] font-medium
            [transition:color_0.18s_ease,background_0.18s_ease] focus-visible:!outline-offset-2"
          :class="isActive(item.to) ? activeLink : 'pl-3 text-sl-muted hover:text-sl-text hover:bg-sl-chip-bg'"
        >
          <span class="truncate">{{ item.name }}</span>
        </router-link>
      </nav>
    </template>

    <!-- The Spotlight stage: the page floor, and a soft light falling on the
         top of the reading column (matching the home page) -->
    <div class="fixed inset-0 pointer-events-none z-0" aria-hidden="true">
      <div class="absolute inset-0 bg-sl-bg"></div>
      <div
        class="absolute inset-x-0 top-0 h-[520px] opacity-[0.85]
          bg-[radial-gradient(ellipse_55%_70%_at_55%_-10%,var(--sl-spot-core)_0%,var(--sl-spot-mid)_40%,transparent_72%)]"
      ></div>
    </div>

    <div class="editorial min-h-screen relative">
      <!-- Running text that sets no colour of its own (the Getting Started
           lists) would otherwise inherit App.vue's near-black and read louder
           than the prose around it. -->
      <div class="docs-content relative z-10 p-6 md:p-8 lg:p-12 text-ed-ink-70">
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

// Selected page: a lit chip with the gradient pip beside its label.
const activeLink =
  "pl-[1.4rem] text-sl-text bg-sl-chip-bg-hover before:absolute before:left-[0.65rem] before:top-1/2 before:mt-[-3px] before:h-1.5 before:w-1.5 before:rounded-[50%] before:bg-sl-grad before:shadow-[0_0_8px_var(--sl-coral)] before:content-['']"
</script>

<style scoped>
/* Links in the docs pages (slot content) are never underlined, even over a
   link's own hover:underline; this rule's weight (0-2-1) is what wins that. */
.docs-content :deep(a) {
  text-decoration: none;
}
</style>
