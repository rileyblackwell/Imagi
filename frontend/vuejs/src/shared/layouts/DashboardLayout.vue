<!-- Dashboard layout for authenticated users -->
<template>
  <BaseLayout>
    <div class="min-h-screen flex">
      <!-- Sidebar -->
      <aside
        class="fixed inset-y-0 left-0 z-30 flex flex-col transition-all duration-300 ease-in-out border-r border-gray-200 dark:border-dark-800/70 shadow-xl"
        :class="[
          isSidebarCollapsed
            ? 'w-16 bg-white dark:bg-[#0a0a0a]'
            : (extraWide
              ? 'w-[36rem] bg-white dark:bg-dark-950/95 backdrop-blur-md'
              : (wide
                ? 'w-80 bg-white dark:bg-dark-950/95 backdrop-blur-md'
                : 'w-72 bg-white dark:bg-dark-950/95 backdrop-blur-md')),
          mobileOverlay ? 'max-md:top-16 max-md:w-full max-md:bg-white max-md:dark:bg-[#0a0a0a] max-md:backdrop-blur-none' : '',
          mobileOverlay ? (isSidebarCollapsed ? 'max-md:-translate-x-full' : 'max-md:translate-x-0') : ''
        ]"
      >
        <!-- Logo and Brand -->
        <div
          v-if="!compactTop || isSidebarCollapsed"
          class="flex-shrink-0 flex items-center justify-end"
          :class="compactTop ? 'h-10 px-2' : 'h-16 px-4'"
        >
          <!-- Collapse/Expand Button -->
          <button 
            @click="toggleSidebar"
            class="sidebar-toggle-btn flex items-center justify-center w-8 h-8 rounded-md text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-dark-800/70 hover:text-gray-900 dark:hover:text-white transition-colors duration-200"
            :title="isSidebarCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'"
          >
            <i 
              class="fas text-sm transition-transform duration-300" 
              :class="[isSidebarCollapsed ? 'fa-chevron-right' : 'fa-chevron-left']"
            ></i>
          </button>
        </div>
        
        <!-- Navigation -->
        <nav v-if="navigationItems.length" class="flex-shrink-0 py-6">
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
        <div class="flex-1 overflow-hidden" :class="{ 'opacity-0 pointer-events-none': isSidebarCollapsed }">
          <slot name="sidebar-content" :isSidebarCollapsed="isSidebarCollapsed" :toggleSidebar="toggleSidebar"></slot>
        </div>

        <!-- Bottom Actions -->
        <div class="flex-shrink-0 border-t border-gray-200 dark:border-dark-800/70">
          <!-- Additional bottom actions from slot -->
          <slot name="sidebar-bottom"></slot>
        </div>
      </aside>

      <!-- Main content -->
      <div
        class="flex-1 flex flex-col min-h-screen transition-all duration-300 ease-in-out"
        :class="[
          isSidebarCollapsed ? 'ml-16' : (extraWide ? 'ml-[36rem]' : (wide ? 'ml-80' : 'ml-72')),
          mobileOverlay ? 'max-md:ml-0' : ''
        ]"
      >
        <!-- Navbar -->
        <BaseNavbar
          class="fixed top-0 right-0 z-20 bg-white/80 dark:bg-dark-900/80 backdrop-blur-md border-b border-gray-200 dark:border-dark-800/70 shadow-sm"
          :class="[
            isSidebarCollapsed ? 'left-16' : (extraWide ? 'left-[36rem]' : (wide ? 'left-80' : 'left-72')),
            mobileOverlay ? 'max-md:left-0' : ''
          ]"
        >
          <template #left>
            <slot
              name="navbar-left"
              :isSidebarCollapsed="isSidebarCollapsed"
              :toggleSidebar="toggleSidebar"
              :setSidebarCollapsed="setSidebarCollapsed"
            ></slot>
          </template>
          <template #center>
            <!-- Pass through a navbar-center slot for centered content -->
            <div class="flex items-center justify-center">
              <slot
                name="navbar-center"
                :isSidebarCollapsed="isSidebarCollapsed"
                :toggleSidebar="toggleSidebar"
                :setSidebarCollapsed="setSidebarCollapsed"
              ></slot>
            </div>
          </template>
          <template #right>
            <!-- Pass through the navbar-right slot; sits flush in the corner
                 (mirroring the logo on the left) with no extra end padding. -->
            <div class="flex items-center justify-end">
              <slot
                name="navbar-right"
                :isSidebarCollapsed="isSidebarCollapsed"
                :toggleSidebar="toggleSidebar"
                :setSidebarCollapsed="setSidebarCollapsed"
              ></slot>
            </div>
          </template>
        </BaseNavbar>

        <!-- Main content area -->
        <main class="flex-1 flex flex-col relative pt-16 bg-white dark:bg-gradient-to-b dark:from-dark-950 dark:to-dark-900 overflow-hidden">
          <slot :isSidebarCollapsed="isSidebarCollapsed"></slot>
        </main>

        <!-- Footer (hidden for full-screen app-shell views like the builder) -->
        <BaseFooter v-if="!appShell" class="border-t border-gray-200 dark:border-dark-800/70 bg-gray-50 dark:bg-dark-900/50 backdrop-blur-sm" />
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
  wide?: boolean
  extraWide?: boolean
  compactTop?: boolean
  // When true, the sidebar becomes a full-screen off-canvas overlay on mobile
  // (< md) instead of squeezing the main content. Opt-in so other layouts keep
  // their current behaviour.
  mobileOverlay?: boolean
  // When true, this is a full-screen app shell (e.g. the builder workspace):
  // the site footer is dropped so the content fills the viewport exactly.
  appShell?: boolean
}>()

const wide = computed(() => !!props.wide)
const extraWide = computed(() => !!props.extraWide)
const compactTop = computed(() => !!props.compactTop)
const mobileOverlay = computed(() => !!props.mobileOverlay)
const appShell = computed(() => !!props.appShell)

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
  setSidebarCollapsed(!isSidebarCollapsed.value)
}

// Set the sidebar collapsed state directly (used by the mobile view switcher)
const setSidebarCollapsed = (collapsed: boolean) => {
  isSidebarCollapsed.value = collapsed

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
/* Note: never redefine Tailwind utilities (.w-16, .ml-16, ...) in here. Scoped
   rules compile with a [data-v-*] attribute selector, so they out-rank
   responsive variants like max-md:ml-0 and silently break them. */

/* Ensure tooltips in collapsed sidebar are visible */
aside {
  overflow: visible !important;
}

/* Custom tooltips */
:deep(.sidebar-tooltip) {
  z-index: 100;
  visibility: visible;
}

/* Remove all outline and focus effects from sidebar toggle button */
.sidebar-toggle-btn {
  outline: 0 !important;
  outline-width: 0 !important;
  outline-style: none !important;
  outline-offset: 0 !important;
  outline-color: transparent !important;
  box-shadow: none !important;
  -webkit-tap-highlight-color: transparent !important;
}

.sidebar-toggle-btn:hover,
.sidebar-toggle-btn:focus,
.sidebar-toggle-btn:focus-visible,
.sidebar-toggle-btn:active {
  outline: 0 !important;
  outline-width: 0 !important;
  outline-style: none !important;
  outline-offset: 0 !important;
  outline-color: transparent !important;
  box-shadow: none !important;
  -webkit-box-shadow: none !important;
}
</style>