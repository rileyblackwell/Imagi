<template>
  <DashboardLayout :navigationItems="[]" storageKey="docs_sidebar_collapsed">
    <template #sidebar-content="{ isSidebarCollapsed }">
      <!-- Categories -->
      <div class="p-4">
        <div v-for="category in navigation" :key="category.title" class="mb-6">
          <div class="text-xs font-medium text-white/40 uppercase tracking-wider mb-3" v-if="!isSidebarCollapsed">
            {{ category.title }}
          </div>
          <ul class="space-y-1">
            <li v-for="item in category.items" :key="item.title">
              <router-link
                :to="item.to"
                class="group block px-3 py-2.5 rounded-xl transition-all duration-300 cursor-pointer"
                :class="[
                  isActiveRoute(item.to) 
                    ? 'bg-gradient-to-r from-violet-500/15 to-fuchsia-500/15 text-white border border-violet-400/20' 
                    : 'hover:bg-white/[0.04] text-white/60 hover:text-white border border-transparent hover:border-white/[0.08]'
                ]"
              >
                <div class="flex items-center">
                  <i :class="[item.icon, isSidebarCollapsed ? '' : 'mr-3', 'w-4 text-center text-sm', isActiveRoute(item.to) ? 'text-violet-400' : 'text-white/50 group-hover:text-violet-400/70']"></i>
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
    
    <!-- Main Content with Premium Background -->
    <div class="min-h-screen bg-[#050508] relative overflow-hidden">
      <!-- Premium Background System (matching homepage) -->
      <div class="fixed inset-0 pointer-events-none">
        <!-- Base gradient mesh -->
        <div class="absolute inset-0 bg-[radial-gradient(ellipse_120%_80%_at_50%_-20%,rgba(120,119,198,0.12),transparent_50%)]"></div>
        <div class="absolute inset-0 bg-[radial-gradient(ellipse_80%_50%_at_80%_50%,rgba(78,68,206,0.06),transparent_40%)]"></div>
        <div class="absolute inset-0 bg-[radial-gradient(ellipse_60%_40%_at_10%_80%,rgba(167,139,250,0.05),transparent_35%)]"></div>
        
        <!-- Subtle grain texture -->
        <div class="absolute inset-0 opacity-[0.015]" style="background-image: url('data:image/svg+xml,%3Csvg viewBox=%220 0 256 256%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cfilter id=%22noise%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.8%22 numOctaves=%224%22 stitchTiles=%22stitch%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23noise)%22/%3E%3C/svg%3E');"></div>
        
        <!-- Floating orbs -->
        <div class="absolute top-[20%] right-[10%] w-[500px] h-[500px] rounded-full bg-gradient-to-br from-indigo-600/5 to-violet-600/3 blur-[120px] animate-float-slow"></div>
        <div class="absolute bottom-[10%] left-[5%] w-[400px] h-[400px] rounded-full bg-gradient-to-tr from-fuchsia-600/4 to-purple-600/2 blur-[100px] animate-float-delayed"></div>
        <div class="absolute top-[60%] right-[30%] w-[300px] h-[300px] rounded-full bg-gradient-to-bl from-violet-500/3 to-indigo-500/2 blur-[80px] animate-float-reverse"></div>
      </div>
      
      <!-- Content -->
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
/* Float animations matching homepage */
@keyframes float-slow {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(30px, -20px) scale(1.02);
  }
  66% {
    transform: translate(-20px, 10px) scale(0.98);
  }
}

@keyframes float-delayed {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  50% {
    transform: translate(-25px, -30px) scale(1.03);
  }
}

@keyframes float-reverse {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(20px, 15px);
  }
}

.animate-float-slow {
  animation: float-slow 25s ease-in-out infinite;
}

.animate-float-delayed {
  animation: float-delayed 30s ease-in-out infinite;
  animation-delay: -5s;
}

.animate-float-reverse {
  animation: float-reverse 20s ease-in-out infinite;
  animation-delay: -10s;
}

/* Custom scrollbar */
:deep(nav) {
  scrollbar-width: thin;
  scrollbar-color: rgba(139, 92, 246, 0.3) transparent;
}

:deep(nav::-webkit-scrollbar) {
  width: 4px;
}

:deep(nav::-webkit-scrollbar-track) {
  background: transparent;
}

:deep(nav::-webkit-scrollbar-thumb) {
  background-color: rgba(139, 92, 246, 0.3);
  border-radius: 9999px;
}

:deep(nav::-webkit-scrollbar-thumb:hover) {
  background-color: rgba(139, 92, 246, 0.5);
}

/* Global styles for documentation content */
.docs-content :deep(a) {
  text-decoration: none;
  color: theme('colors.violet.400');
  transition: color 0.2s;
}

.docs-content :deep(a:hover) {
  color: theme('colors.violet.300');
}

/* Fix for Tailwind prose default styling of links */
.docs-content :deep(.prose a) {
  text-decoration: none;
  font-weight: 500;
}

.docs-content :deep(.prose a:hover) {
  color: theme('colors.violet.300');
}

/* Enhanced prose styling for better readability */
.docs-content :deep(.prose) {
  color: rgba(255, 255, 255, 0.5);
}

.docs-content :deep(.prose h1),
.docs-content :deep(.prose h2),
.docs-content :deep(.prose h3),
.docs-content :deep(.prose h4) {
  color: rgba(255, 255, 255, 0.9);
}

.docs-content :deep(.prose code) {
  background-color: rgba(255, 255, 255, 0.05);
  padding: 0.125rem 0.375rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  color: theme('colors.violet.300');
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.docs-content :deep(.prose pre) {
  background-color: rgba(10, 10, 15, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 0.75rem;
  backdrop-filter: blur(12px);
}

.docs-content :deep(.prose blockquote) {
  border-left: 4px solid theme('colors.violet.500');
  background-color: rgba(139, 92, 246, 0.05);
  border-radius: 0 0.5rem 0.5rem 0;
  padding: 1rem 1.5rem;
  margin: 1.5rem 0;
}
</style>
