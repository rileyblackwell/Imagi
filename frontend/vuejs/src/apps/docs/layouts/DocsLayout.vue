<template>
  <DashboardLayout :navigationItems="[]" storageKey="docs_sidebar_collapsed">
    <template #sidebar-content="{ isSidebarCollapsed }">
      <!-- Categories -->
      <div class="p-4">
        <div v-for="category in navigation" :key="category.title" class="mb-6">
          <div class="text-sm font-medium text-gray-400 uppercase tracking-wider mb-3" v-if="!isSidebarCollapsed">
            {{ category.title }}
          </div>
          <ul class="space-y-2">
            <li v-for="item in category.items" :key="item.title">
              <router-link
                :to="item.to"
                class="block px-4 py-2 rounded-lg transition-colors cursor-pointer"
                :class="[
                  isActiveRoute(item.to) 
                    ? 'bg-primary-500/20 text-primary-400' 
                    : 'hover:bg-dark-800 text-gray-300 hover:text-white'
                ]"
              >
                <div class="flex items-center">
                  <i :class="[item.icon, isSidebarCollapsed ? '' : 'mr-3', 'w-5 text-center']"></i>
                  <span v-if="!isSidebarCollapsed">{{ item.title }}</span>
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
    
    <!-- Main Content -->
    <div class="p-4 md:p-8 lg:p-10 docs-content">
      <slot></slot>
    </div>
  </DashboardLayout>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import { DashboardLayout } from '@/shared/layouts'
import DocsNavbar from '../components/molecules/navbars/DocsNavbar.vue'

const route = useRoute()
const router = useRouter()



// Navigation structure
const navigation = [
  {
    title: 'Getting Started',
    items: [
      { title: 'Introduction', to: '/docs', icon: 'fas fa-book' },
      { title: 'Quick Start', to: '/docs/quickstart', icon: 'fas fa-rocket' },
      { title: 'Key Concepts', to: '/docs/concepts', icon: 'fas fa-lightbulb' }
    ]
  },
  {
    title: 'Using Imagi Oasis',
    items: [
      { title: 'Creating Projects', to: '/docs/creating-projects', icon: 'fas fa-plus-circle' },
      { title: 'Project Structure', to: '/docs/project-structure', icon: 'fas fa-sitemap' },
      { title: 'Building UIs', to: '/docs/building-ui', icon: 'fas fa-paint-brush' },
      { title: 'Adding Backend Logic', to: '/docs/backend', icon: 'fas fa-server' },
      { title: 'Deployment', to: '/docs/deployment', icon: 'fas fa-cloud-upload-alt' }
    ]
  },
  {
    title: 'Advanced',
    items: [
      { title: 'Best Practices', to: '/docs/best-practices', icon: 'fas fa-check-circle' }
    ]
  }
]

// Check if a route is active (exact match or starts with path for nested routes)
const isActiveRoute = (path) => {
  // Special case for Introduction page at /docs
  if (path === '/docs') {
    return route.path === '/docs';
  }
  
  // For other routes, check for exact match
  return route.path === path;
}
</script>

<style scoped>
/* Custom scrollbar for sidebar */
:deep(nav) {
  scrollbar-width: thin;
  scrollbar-color: theme('colors.gray.700') transparent;
}

:deep(nav::-webkit-scrollbar) {
  width: 4px;
}

:deep(nav::-webkit-scrollbar-track) {
  background: transparent;
}

:deep(nav::-webkit-scrollbar-thumb) {
  background-color: theme('colors.gray.700');
  border-radius: 9999px;
}

:deep(nav::-webkit-scrollbar-thumb:hover) {
  background-color: theme('colors.gray.600');
}

/* Global styles for documentation content */
.docs-content :deep(a) {
  text-decoration: none;
  color: theme('colors.primary.400');
  transition: color 0.2s;
}

.docs-content :deep(a:hover) {
  color: theme('colors.primary.300');
}

/* Fix for Tailwind prose default styling of links */
.docs-content :deep(.prose a) {
  text-decoration: none;
  font-weight: 500;
}

.docs-content :deep(.prose a:hover) {
  color: theme('colors.primary.300');
}
</style> 