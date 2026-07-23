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
        <span class="text-[11px] font-semibold uppercase tracking-[0.16em] text-blue-950/60 dark:text-blue-100/55">
          Documentation
        </span>
      </div>
    </template>

    <template #sidebar-content>
      <nav class="px-3 pt-3 pb-6 space-y-0.5">
        <router-link
          v-for="item in navigationItems"
          :key="item.to"
          :to="item.to"
          :class="[
            'group flex items-center px-3 py-2 text-sm font-medium rounded-xl transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0a0a0a]',
            isActive(item.to)
              ? 'docs-nav-active text-blue-950 dark:text-white'
              : 'text-blue-950/65 dark:text-blue-100/60 hover:bg-blue-950/[0.04] dark:hover:bg-white/[0.06] hover:text-blue-950 dark:hover:text-white'
          ]"
        >
          <span class="truncate">{{ item.name }}</span>
        </router-link>
      </nav>
    </template>

    <!-- Warm porcelain canvas with a soft baby-blue wash and film grain (matching the home page) -->
    <div class="fixed inset-0 pointer-events-none z-0" aria-hidden="true">
      <div class="docs-canvas absolute inset-0 transition-colors duration-500"></div>
      <div class="docs-wash-cool absolute -top-32 right-[-10%] w-[700px] h-[480px]"></div>
      <div class="grain-overlay absolute inset-0"></div>
    </div>

    <div class="min-h-screen relative overflow-hidden">
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
/* Warm porcelain canvas fading to white so it hands off to the footer,
   mirroring the home page (footer is bg-white / dark #0a0a0a). */
.docs-canvas {
  background: linear-gradient(180deg, #fdf9f2 0%, #faf7f1 45%, #ffffff 100%);
}

:root.dark .docs-canvas {
  background: linear-gradient(180deg, #0c0c0e 0%, #0a0b0f 50%, #0a0a0a 100%);
}

/* Soft baby-blue atmosphere wash, much fainter in dark mode */
.docs-wash-cool {
  background: radial-gradient(closest-side, rgba(158, 205, 243, 0.22), rgba(158, 205, 243, 0.06) 55%, transparent 75%);
  filter: blur(48px);
}

:root.dark .docs-wash-cool {
  background: radial-gradient(closest-side, rgba(96, 165, 250, 0.07), rgba(96, 165, 250, 0.02) 55%, transparent 75%);
}

/* Fine film grain keeps the soft gradients from banding and adds texture */
.grain-overlay {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160' viewBox='0 0 160 160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='160' height='160' filter='url(%23n)' opacity='0.5'/%3E%3C/svg%3E");
  background-size: 160px 160px;
  opacity: 0.035;
  mix-blend-mode: multiply;
}

:root.dark .grain-overlay {
  opacity: 0.05;
  mix-blend-mode: overlay;
}

.docs-content :deep(a) {
  text-decoration: none;
}

/* Crisp, sharply-defined cards matching the home page */
.docs-content :deep(.crisp-card) {
  box-shadow:
    0 0 0 1px rgba(15, 23, 42, 0.03),
    0 1px 2px rgba(15, 23, 42, 0.06),
    0 4px 10px -2px rgba(15, 23, 42, 0.07),
    0 12px 28px -10px rgba(15, 23, 42, 0.10);
}

:root.dark .docs-content :deep(.crisp-card) {
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.04),
    0 1px 2px rgba(0, 0, 0, 0.5),
    0 4px 10px -2px rgba(0, 0, 0, 0.45),
    0 12px 28px -10px rgba(0, 0, 0, 0.55);
}

/* Link cards lift on hover with the home page's stronger lift-card shadow */
.docs-content :deep(a.crisp-card:hover) {
  box-shadow:
    0 0 0 1px rgba(15, 23, 42, 0.04),
    0 2px 4px rgba(15, 23, 42, 0.06),
    0 10px 20px -4px rgba(15, 23, 42, 0.1),
    0 24px 44px -12px rgba(15, 23, 42, 0.14);
}

:root.dark .docs-content :deep(a.crisp-card:hover) {
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.06),
    0 2px 4px rgba(0, 0, 0, 0.5),
    0 12px 24px -4px rgba(0, 0, 0, 0.5),
    0 28px 48px -12px rgba(0, 0, 0, 0.6);
}

/* Alternating blue / orange accent borders for cards in a grid, echoing the home page */
.docs-content :deep(.grid > .crisp-card:nth-child(2n)) {
  border-color: rgba(254, 215, 170, 0.7);
}

:root.dark .docs-content :deep(.grid > .crisp-card:nth-child(2n)) {
  border-color: rgba(253, 186, 116, 0.14);
}

/* Even grid cards swap their icon tile to the warm orange tint */
.docs-content :deep(.grid > .crisp-card:nth-child(2n) .nav-tile) {
  background: #ffedd5;
  color: #ea580c;
  --tw-ring-color: rgba(124, 45, 18, 0.08);
}

:root.dark .docs-content :deep(.grid > .crisp-card:nth-child(2n) .nav-tile) {
  background: rgba(251, 146, 60, 0.14);
  color: #fdba74;
  --tw-ring-color: rgba(253, 186, 116, 0.18);
}
</style>

<style>
/* Active nav item: a quiet raised card (matching the home page's crisp-card
   language) rather than a heavy solid pill — clearly selected, still calm. */
.docs-layout .docs-nav-active {
  background: #ffffff;
  box-shadow:
    0 0 0 1px rgba(15, 23, 42, 0.05),
    0 1px 2px rgba(15, 23, 42, 0.06),
    0 3px 8px -3px rgba(15, 23, 42, 0.12);
}

.dark .docs-layout .docs-nav-active {
  background: rgba(255, 255, 255, 0.07);
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.08),
    0 1px 2px rgba(0, 0, 0, 0.4);
}

/* Brand-tinted text selection, matching the home page */
.docs-layout ::selection {
  background: rgba(158, 205, 243, 0.55);
  color: #172554;
}

.dark .docs-layout ::selection {
  background: rgba(96, 165, 250, 0.4);
  color: #eff6ff;
}
</style>
