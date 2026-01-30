<template>
  <DashboardLayout :navigationItems="[]" storageKey="docs_sidebar_collapsed" class="docs-layout">
    <template #sidebar-content="{ isSidebarCollapsed }">
      <!-- Categories -->
      <div class="p-4">
        <div v-for="category in navigation" :key="category.title" class="mb-6">
          <div class="text-xs font-semibold text-gray-900 dark:text-white uppercase tracking-wide mb-3 antialiased" v-if="!isSidebarCollapsed">
            {{ category.title }}
          </div>
          <ul class="space-y-1">
            <li v-for="item in category.items" :key="item.title">
              <router-link
                :to="item.to"
                class="block px-3 py-2.5 rounded-xl transition-colors duration-300 cursor-pointer antialiased"
                :class="[
                  isActiveRoute(item.to) 
                    ? 'bg-gray-100 dark:bg-white/[0.08] text-gray-900 dark:text-white border border-gray-200 dark:border-white/[0.12] font-semibold' 
                    : 'text-gray-900 dark:text-white border border-transparent font-medium'
                ]"
              >
                <div class="flex items-center">
                  <span v-if="!isSidebarCollapsed" class="text-sm tracking-tight leading-snug">{{ item.title }}</span>
                </div>
              </router-link>
            </li>
          </ul>
        </div>
      </div>
    </template>
    
    <!-- Navbar content -->
    <template #left>
      <DocsNavbar />
    </template>
    
    <!-- Minimal background with subtle texture (matching homepage) - extends to cover entire screen -->
    <div class="fixed inset-0 pointer-events-none z-0">
      <!-- Subtle gradient - very minimal -->
      <div class="absolute inset-0 bg-white dark:bg-[#0a0a0a] transition-colors duration-500"></div>
      <div class="absolute inset-0 bg-gradient-to-b from-gray-50/50 via-white to-white dark:from-[#0a0a0a] dark:via-[#0a0a0a] dark:to-[#0a0a0a] transition-colors duration-500"></div>
      
      <!-- Very subtle grid pattern for texture (dark mode only) -->
      <div class="absolute inset-0 opacity-[0.015] dark:opacity-[0.02]" 
           style="background-image: linear-gradient(rgba(128,128,128,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(128,128,128,0.1) 1px, transparent 1px); background-size: 64px 64px;"></div>
    </div>
    
    <!-- Main Content with Clean Background (matching homepage) -->
    <div class="min-h-screen relative overflow-hidden">
      <!-- Content -->
      <div class="relative z-10 p-6 md:p-8 lg:p-12 docs-content">
        <slot></slot>
      </div>
    </div>
  </DashboardLayout>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { DashboardLayout } from '@/shared/layouts'
import DocsNavbar from '../components/molecules/navbars/DocsNavbar.vue'

const route = useRoute()
const router = useRouter()

// Add class to document element for styling
onMounted(() => {
  document.documentElement.classList.add('docs-layout-active')
})

onUnmounted(() => {
  document.documentElement.classList.remove('docs-layout-active')
})

// Navigation structure
const navigation = [
  {
    title: 'Get Started',
    items: [
      { title: 'Welcome', to: '/docs', icon: 'fas fa-book' },
      { title: 'Quick Start', to: '/docs/quickstart', icon: 'fas fa-rocket' }
    ]
  },
  {
    title: 'Using Imagi',
    items: [
      { title: 'Creating Projects', to: '/docs/creating-projects', icon: 'fas fa-plus-circle' }
    ]
  }
]

// Check if a route is active (exact match or starts with path for nested routes)
const isActiveRoute = (path) => {
  // Special case for Welcome page at /docs
  if (path === '/docs') {
    return route.path === '/docs';
  }
  
  // For other routes, check for exact match
  return route.path === path;
}
</script>

<style>
/* Global override for docs sidebar - needs to be unscoped to override Tailwind classes */
.docs-layout-active aside {
  background-color: white !important;
}

.dark.docs-layout-active aside {
  background-color: #0a0a0a !important;
  border-color: rgba(255, 255, 255, 0.12) !important;
}

/* Ensure logo/brand border is visible in dark mode */
.dark.docs-layout-active aside .border-b {
  border-color: rgba(255, 255, 255, 0.12) !important;
}

/* Ensure collapse button has proper colors in dark mode */
.dark.docs-layout-active aside button {
  background-color: rgba(255, 255, 255, 0.08) !important;
  color: rgba(255, 255, 255, 0.9) !important;
}

.dark.docs-layout-active aside button:hover {
  background-color: rgba(255, 255, 255, 0.12) !important;
  color: white !important;
}
</style>

<style scoped>

/* Crisp, professional font rendering */
:deep(.p-4) {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
}

/* Custom scrollbar matching homepage */
:deep(nav) {
  scrollbar-width: thin;
  scrollbar-color: rgba(0, 0, 0, 0.12) transparent;
}

:deep(nav::-webkit-scrollbar) {
  width: 4px;
}

:deep(nav::-webkit-scrollbar-track) {
  background: transparent;
}

:deep(nav::-webkit-scrollbar-thumb) {
  background-color: rgba(0, 0, 0, 0.12);
  border-radius: 9999px;
  transition: background 0.2s ease;
}

:deep(nav::-webkit-scrollbar-thumb:hover) {
  background-color: rgba(0, 0, 0, 0.2);
}

:root.dark :deep(nav::-webkit-scrollbar-thumb) {
  background-color: rgba(255, 255, 255, 0.12);
}

:root.dark :deep(nav::-webkit-scrollbar-thumb:hover) {
  background-color: rgba(255, 255, 255, 0.2);
}

/* Global styles for documentation content */
.docs-content :deep(a) {
  text-decoration: none;
  color: theme('colors.gray.900');
  transition: color 0.2s;
}

.docs-content :deep(a:hover) {
  color: theme('colors.gray.700');
}

:root.dark .docs-content :deep(a) {
  color: theme('colors.white');
}

:root.dark .docs-content :deep(a:hover) {
  color: theme('colors.gray.300');
}

/* Fix for Tailwind prose default styling of links */
.docs-content :deep(.prose a) {
  text-decoration: none;
  font-weight: 500;
}

/* Enhanced prose styling for better readability */
.docs-content :deep(.prose) {
  color: theme('colors.gray.600');
}

:root.dark .docs-content :deep(.prose) {
  color: rgba(255, 255, 255, 0.6);
}

.docs-content :deep(.prose h1),
.docs-content :deep(.prose h2),
.docs-content :deep(.prose h3),
.docs-content :deep(.prose h4) {
  color: theme('colors.gray.900');
}

:root.dark .docs-content :deep(.prose h1),
:root.dark .docs-content :deep(.prose h2),
:root.dark .docs-content :deep(.prose h3),
:root.dark .docs-content :deep(.prose h4) {
  color: rgba(255, 255, 255, 0.9);
}

.docs-content :deep(.prose code) {
  background-color: theme('colors.gray.100');
  padding: 0.125rem 0.375rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  color: theme('colors.gray.900');
  border: 1px solid theme('colors.gray.200');
}

:root.dark .docs-content :deep(.prose code) {
  background-color: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.docs-content :deep(.prose pre) {
  background-color: theme('colors.gray.50');
  border: 1px solid theme('colors.gray.200');
  border-radius: 0.75rem;
}

:root.dark .docs-content :deep(.prose pre) {
  background-color: rgba(10, 10, 15, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(12px);
}

.docs-content :deep(.prose blockquote) {
  border-left: 4px solid theme('colors.emerald.500');
  background-color: theme('colors.emerald.50');
  border-radius: 0 0.5rem 0.5rem 0;
  padding: 1rem 1.5rem;
  margin: 1.5rem 0;
}

:root.dark .docs-content :deep(.prose blockquote) {
  background-color: rgba(16, 185, 129, 0.05);
}
</style>
