<!-- Dashboard layout for authenticated users -->
<template>
  <BaseLayout>
    <!-- App-shell views (the builder workspace) pin the shell to the dynamic
         viewport height and clip overflow so the document itself can never
         scroll — otherwise the vh/dvh mismatch on mobile leaves a few dozen
         scrollable pixels that slide the content up under the fixed navbar. -->
    <div class="flex" :class="appShell ? 'h-dvh overflow-hidden' : 'min-h-screen'">
      <!-- Sidebar -->
      <aside
        class="fixed inset-y-0 left-0 z-30 flex flex-col transition-all duration-300 ease-in-out border-r border-blue-950/[0.08] dark:border-white/[0.08] shadow-xl"
        :class="[
          isSidebarCollapsed
            ? 'w-16 bg-white dark:bg-[#0a0a0a]'
            : (wide
              ? 'w-[22rem] bg-white dark:bg-[#0a0a0a]/95 backdrop-blur-md'
              : 'w-72 bg-white dark:bg-[#0a0a0a]/95 backdrop-blur-md'),
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
            class="sidebar-toggle-btn flex items-center justify-center w-8 h-8 rounded-md text-blue-950/60 dark:text-blue-100/60 hover:bg-blue-950/[0.04] dark:hover:bg-white/[0.06] hover:text-blue-950 dark:hover:text-white transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0a0a0a]"
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
                'group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0a0a0a]',
                isActivePath(item)
                  ? 'bg-blue-50/80 dark:bg-blue-400/10 text-blue-700 dark:text-blue-300 shadow-sm'
                  : 'text-blue-950/65 dark:text-blue-100/65 hover:bg-blue-950/[0.04] dark:hover:bg-white/[0.06] hover:text-blue-950 dark:hover:text-white'
              ]"
            >
              <i 
                :class="[
                  item.icon,
                  'text-lg transition-colors duration-200',
                  isActivePath(item) ? 'text-blue-700 dark:text-blue-300' : 'text-blue-950/50 dark:text-blue-100/40 group-hover:text-blue-950 dark:group-hover:text-white',
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
        <div class="flex-shrink-0 border-t border-blue-950/[0.08] dark:border-white/[0.08]">
          <!-- Additional bottom actions from slot -->
          <slot name="sidebar-bottom"></slot>
        </div>
      </aside>

      <!-- Main content -->
      <div
        class="flex-1 flex flex-col transition-all duration-300 ease-in-out"
        :class="[
          appShell ? 'h-full min-h-0 overflow-hidden' : 'min-h-screen',
          isSidebarCollapsed ? 'ml-16' : (wide ? 'ml-[22rem]' : 'ml-72'),
          mobileOverlay ? 'max-md:ml-0' : ''
        ]"
      >
        <!-- Navbar -->
        <BaseNavbar
          class="fixed top-0 right-0 z-20 bg-white/80 dark:bg-[#0a0a0a]/80 backdrop-blur-md border-b border-blue-950/[0.08] dark:border-white/[0.08]"
          :class="[
            isSidebarCollapsed ? 'left-16' : (wide ? 'left-[22rem]' : 'left-72'),
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
        <main
          class="flex-1 flex flex-col relative pt-16 bg-white dark:bg-[#0a0a0a] overflow-hidden"
          :class="appShell ? 'min-h-0' : ''"
        >
          <slot :isSidebarCollapsed="isSidebarCollapsed"></slot>
        </main>

        <!-- Footer (hidden for full-screen app-shell views like the builder);
             BaseFooter supplies its own white / dark #0a0a0a canvas + hairline. -->
        <BaseFooter v-if="!appShell" />
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

/* No tap flash on the toggle; keyboard focus shows the canonical ring via
   the focus-visible utilities on the button itself. */
.sidebar-toggle-btn {
  -webkit-tap-highlight-color: transparent;
}
</style>