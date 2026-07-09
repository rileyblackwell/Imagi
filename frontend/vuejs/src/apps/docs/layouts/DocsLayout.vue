<template>
  <DashboardLayout :navigationItems="[]" storageKey="docs_sidebar_collapsed" class="docs-layout">
    <template #sidebar-content="{ isSidebarCollapsed }">
      <div class="px-3 pb-6 space-y-1">
        <router-link
          v-for="item in navigationItems"
          :key="item.to"
          :to="item.to"
          :class="[
            'group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-all duration-200',
            isActive(item.to)
              ? 'bg-blue-50 dark:bg-blue-500/10 text-blue-700 dark:text-blue-300'
              : 'text-blue-950/70 dark:text-white/70 hover:bg-blue-50/70 dark:hover:bg-white/[0.04] hover:text-blue-950 dark:hover:text-white'
          ]"
        >
          <i
            :class="[
              item.icon,
              'text-lg',
              isSidebarCollapsed ? '' : 'mr-3'
            ]"
          ></i>
          <span v-if="!isSidebarCollapsed" class="truncate">{{ item.name }}</span>
        </router-link>
      </div>
    </template>

    <!-- Minimal background with a subtle baby-blue wash (matching homepage) -->
    <div class="fixed inset-0 pointer-events-none z-0">
      <div class="absolute inset-0 bg-white dark:bg-[#0a0a0a] transition-colors duration-500"></div>
      <div class="absolute inset-x-0 top-0 h-[480px] bg-gradient-to-b from-blue-50/70 via-white to-white dark:from-blue-400/[0.06] dark:via-[#0a0a0a] dark:to-[#0a0a0a] transition-colors duration-500"></div>
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
  { name: 'Welcome', to: '/docs', icon: 'fas fa-book' },
  { name: 'Quick Start', to: '/docs/quickstart', icon: 'fas fa-rocket' },
  { name: 'Creating Projects', to: '/docs/creating-projects', icon: 'fas fa-plus-circle' }
]

const isActive = (path) => route.path === path
</script>

<style scoped>
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

/* Alternating blue / orange accent borders for cards in a grid, echoing the home page */
.docs-content :deep(.grid > .crisp-card:nth-child(2n)) {
  border-color: rgba(254, 215, 170, 0.7);
}

:root.dark .docs-content :deep(.grid > .crisp-card:nth-child(2n)) {
  border-color: rgba(253, 186, 116, 0.16);
}
</style>

<style>
.docs-layout aside.w-72 {
  width: 14rem;
}
.docs-layout aside nav.py-6 {
  padding-top: 0;
  padding-bottom: 0;
}
.docs-layout .ml-72 {
  margin-left: 14rem;
}
.docs-layout .left-72 {
  left: 14rem;
}
</style>
