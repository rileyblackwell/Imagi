<template>
  <DashboardLayout :navigationItems="[]" storageKey="docs_sidebar_collapsed" class="docs-layout">
    <template #sidebar-content="{ isSidebarCollapsed }">
      <div class="px-3 pb-6 space-y-1">
        <router-link
          v-for="item in navigationItems"
          :key="item.to"
          :to="item.to"
          :class="[
            'group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-all duration-200 text-black',
            isActive(item.to) ? 'bg-gray-100 dark:bg-dark-800/70' : ''
          ]"
        >
          <i
            :class="[
              item.icon,
              'text-lg text-black',
              isSidebarCollapsed ? '' : 'mr-3'
            ]"
          ></i>
          <span v-if="!isSidebarCollapsed" class="truncate">{{ item.name }}</span>
        </router-link>
      </div>
    </template>

    <!-- Minimal background with subtle texture (matching homepage) -->
    <div class="fixed inset-0 pointer-events-none z-0">
      <div class="absolute inset-0 bg-white dark:bg-[#0a0a0a] transition-colors duration-500"></div>
      <div class="absolute inset-0 bg-gradient-to-b from-gray-50/50 via-white to-white dark:from-[#0a0a0a] dark:via-[#0a0a0a] dark:to-[#0a0a0a] transition-colors duration-500"></div>
      <div class="absolute inset-0 opacity-[0.015] dark:opacity-[0.02]"
           style="background-image: linear-gradient(rgba(128,128,128,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(128,128,128,0.1) 1px, transparent 1px); background-size: 64px 64px;"></div>
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
