<template>
  <DashboardLayout :navigationItems="[]" storageKey="docs_sidebar_collapsed">
    <template #sidebar-content="{ isSidebarCollapsed }">
      <!-- Categories -->
      <div class="p-4">
        <div v-for="category in navigation" :key="category.title" class="mb-6">
          <div class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-3" v-if="!isSidebarCollapsed">
            {{ category.title }}
          </div>
          <ul class="space-y-1">
            <li v-for="item in category.items" :key="item.title">
              <router-link
                :to="item.to"
                class="group block px-3 py-2 rounded-xl transition-all duration-200 cursor-pointer"
                :class="[
                  isActiveRoute(item.to) 
                    ? 'bg-gradient-to-r from-indigo-500/20 to-violet-500/20 text-indigo-300 border border-indigo-400/20' 
                    : 'hover:bg-white/5 text-gray-300 hover:text-white border border-transparent hover:border-white/10'
                ]"
              >
                <div class="flex items-center">
                  <i :class="[item.icon, isSidebarCollapsed ? '' : 'mr-3', 'w-4 text-center text-sm']"></i>
                  <span v-if="!isSidebarCollapsed" class="text-sm font-medium">{{ item.title }}</span>
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
    
    <!-- Main Content with enhanced background -->
    <div class="min-h-screen bg-dark-950 relative overflow-hidden">
      <!-- Enhanced Background Effects -->
      <div class="absolute inset-0 pointer-events-none">
        <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.02]"></div>
        <div class="absolute inset-0 bg-gradient-to-br from-indigo-950/5 via-dark-900 to-violet-950/5"></div>
        
        <!-- Subtle floating orbs -->
        <div class="absolute top-[20%] right-[10%] w-[600px] h-[600px] rounded-full bg-indigo-600/3 blur-[120px] animate-pulse-slow"></div>
        <div class="absolute bottom-[30%] left-[15%] w-[400px] h-[400px] rounded-full bg-violet-600/3 blur-[100px] animate-pulse-slow animation-delay-150"></div>
      </div>
      
      <!-- Content with better spacing -->
      <div class="relative z-10 p-6 md:p-8 lg:p-12 docs-content">
        <slot></slot>
      </div>
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

/* Float animation for background orbs */
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

.animate-pulse-slow {
  animation: pulse 3s ease-in-out infinite;
}

.animation-delay-150 {
  animation-delay: 150ms;
}

/* Global styles for documentation content */
.docs-content :deep(a) {
  text-decoration: none;
  color: theme('colors.indigo.400');
  transition: color 0.2s;
}

.docs-content :deep(a:hover) {
  color: theme('colors.indigo.300');
}

/* Fix for Tailwind prose default styling of links */
.docs-content :deep(.prose a) {
  text-decoration: none;
  font-weight: 500;
}

.docs-content :deep(.prose a:hover) {
  color: theme('colors.indigo.300');
}

/* Enhanced prose styling for better readability */
.docs-content :deep(.prose) {
  color: theme('colors.gray.300');
}

.docs-content :deep(.prose h1),
.docs-content :deep(.prose h2),
.docs-content :deep(.prose h3),
.docs-content :deep(.prose h4) {
  color: theme('colors.white');
}

.docs-content :deep(.prose code) {
  background-color: theme('colors.dark.800');
  padding: 0.125rem 0.375rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  color: theme('colors.indigo.300');
}

.docs-content :deep(.prose pre) {
  background-color: theme('colors.dark.900');
  border: 1px solid theme('colors.white' / 0.1);
  border-radius: 0.75rem;
}

.docs-content :deep(.prose blockquote) {
  border-left: 4px solid theme('colors.indigo.500');
  background-color: theme('colors.indigo.500' / 0.05);
  border-radius: 0 0.5rem 0.5rem 0;
  padding: 1rem 1.5rem;
  margin: 1.5rem 0;
}
</style> 