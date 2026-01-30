<!-- Dashboard layout for authenticated users -->
<template>
  <BaseLayout>
    <div class="min-h-screen flex">
      <!-- Sidebar -->
      <aside 
        class="fixed inset-y-0 left-0 z-30 flex flex-col transition-all duration-300 ease-in-out border-r border-gray-200 dark:border-dark-800/70 bg-white dark:bg-dark-950/95 backdrop-blur-md shadow-xl" 
        :class="[isSidebarCollapsed ? 'w-16' : 'w-56']"
      >
        <!-- Logo and Brand -->
        <div class="flex-shrink-0 h-16 flex items-center justify-center border-b border-gray-200 dark:border-dark-800/70">
          <ImagiLogo :icon-only="isSidebarCollapsed" size="md">
            {{ isSidebarCollapsed ? 'I' : 'Imagi' }}
          </ImagiLogo>
        </div>
        
        <!-- Navigation -->
        <nav class="flex-shrink-0 py-6">
          <div class="px-3 space-y-1">
            <router-link
              v-for="item in navigationItems"
              :key="item.name"
              :to="item.to"
              :class="[
                'group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-all duration-200',
                isActivePath(item) 
                  ? 'bg-primary-500/10 text-primary-400 shadow-sm' 
                  : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-dark-800/70 hover:text-gray-900 dark:hover:text-white'
              ]"
            >
              <i 
                :class="[
                  item.icon,
                  'text-lg transition-colors duration-200',
                  isActivePath(item) ? 'text-primary-400' : 'text-gray-600 dark:text-gray-500 group-hover:text-gray-900 dark:group-hover:text-white',
                  isSidebarCollapsed ? '' : 'mr-3'
                ]"
              ></i>
              <span 
                v-if="!isSidebarCollapsed" 
                class="truncate transition-opacity duration-200"
              >
                {{ item.name }}
              </span>
            </router-link>
          </div>
        </nav>

        <!-- Custom Sidebar Content -->
        <div class="flex-1 overflow-y-auto overflow-x-visible">
          <slot name="sidebar-content" :isSidebarCollapsed="isSidebarCollapsed"></slot>
        </div>

        <!-- Bottom Actions -->
        <div class="flex-shrink-0 border-t border-gray-200 dark:border-dark-800/70">
          <!-- Additional bottom actions from slot -->
          <slot name="sidebar-bottom"></slot>
          
          <!-- Collapse/Expand Button -->
          <div class="p-4">
            <button 
              @click="toggleSidebar"
              class="w-full flex items-center justify-center p-2 bg-gray-100 dark:bg-dark-800/70 hover:bg-gray-200 dark:hover:bg-dark-700/70 rounded-lg text-gray-700 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-all duration-200 shadow-sm"
              :title="isSidebarCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'"
            >
              <i 
                class="fas transition-transform duration-300" 
                :class="[isSidebarCollapsed ? 'fa-chevron-right' : 'fa-chevron-left']"
              ></i>
            </button>
          </div>
        </div>
      </aside>

      <!-- Main content -->
      <div 
        class="flex-1 flex flex-col min-h-screen transition-all duration-300 ease-in-out" 
        :class="[isSidebarCollapsed ? 'ml-16' : 'ml-56']"
      >
        <!-- Navbar -->
        <BaseNavbar 
          class="fixed top-0 right-0 z-20 bg-white/80 dark:bg-dark-900/80 backdrop-blur-md border-b border-gray-200 dark:border-dark-800/70 shadow-sm" 
          :class="[isSidebarCollapsed ? 'left-16' : 'left-56']"
        >
          <template #left>
            <!-- Navbar left section -->
          </template>
          <template #center>
            <!-- Pass through a navbar-center slot for centered content -->
            <div class="flex items-center justify-center">
              <slot name="navbar-center"></slot>
            </div>
          </template>
          <template #right>
            <!-- Pass through the navbar-right slot with proper spacing -->
            <div class="flex items-center justify-end pe-4">
              <slot name="navbar-right"></slot>
            </div>
          </template>
        </BaseNavbar>

        <!-- Main content area -->
        <main class="flex-1 flex flex-col relative mt-16 bg-white dark:bg-gradient-to-b dark:from-dark-950 dark:to-dark-900 overflow-hidden">
          <slot :isSidebarCollapsed="isSidebarCollapsed"></slot>
        </main>

        <!-- Footer -->
        <BaseFooter class="border-t border-gray-200 dark:border-dark-800/70 bg-gray-50 dark:bg-dark-900/50 backdrop-blur-sm" />
      </div>
    </div>
  </BaseLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/shared/stores/auth'
import BaseLayout from './BaseLayout.vue'
import { BaseNavbar, BaseFooter } from '@/shared/components'
import { ImagiLogo } from '@/shared/components/molecules'

interface NavigationItem {
  name: string
  to: string
  icon?: string
  exact?: boolean
  children?: NavigationItem[]
}

const props = defineProps<{
  navigationItems: NavigationItem[]
  storageKey?: string
}>()

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// Sidebar state
const isSidebarCollapsed = ref(false)

// Check if a navigation item is active
const isActivePath = (item: NavigationItem): boolean => {
  if (item.exact) {
    return route.path === item.to
  }
  
  // Check if current route starts with the navigation item path
  return route.path.startsWith(item.to)
}

// Toggle sidebar collapsed state
const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
  
  // Save preference if storage key is provided
  if (props.storageKey) {
    localStorage.setItem(props.storageKey, isSidebarCollapsed.value ? 'true' : 'false')
  }
}

// Initialize sidebar state from localStorage if available
onMounted(() => {
  if (props.storageKey) {
    const savedState = localStorage.getItem(props.storageKey)
    if (savedState !== null) {
      isSidebarCollapsed.value = savedState === 'true'
    }
  }

  // Only check authentication if the current route requires it
  if (!authStore.isAuthenticated && route.meta.requiresAuth) {
    router.push({ 
      name: 'login',
      query: { redirect: route.fullPath }
    })
  }
})
</script>

<style scoped>
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 300ms;
}

/* Ensure content fades smoothly */
.overflow-hidden {
  overflow: hidden;
}

/* Smooth width transitions */
.w-56 {
  width: 14rem;
}

.w-16 {
  width: 4rem;
}

/* Smooth margin transitions */
.ml-56 {
  margin-left: 14rem;
}

.ml-16 {
  margin-left: 4rem;
}

/* Ensure tooltips in collapsed sidebar are visible */
aside {
  overflow: visible !important;
}

/* Custom tooltips */
:deep(.sidebar-tooltip) {
  z-index: 100;
  visibility: visible;
}
</style>