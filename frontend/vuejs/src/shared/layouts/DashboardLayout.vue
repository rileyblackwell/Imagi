<!-- Dashboard layout for authenticated users -->
<template>
  <BaseLayout>
    <div class="min-h-screen flex">
      <!-- Sidebar -->
      <aside 
        class="fixed inset-y-0 left-0 z-20 flex flex-col transition-all duration-300 ease-in-out border-r border-dark-800 bg-dark-950" 
        :class="[isSidebarCollapsed ? 'w-16' : 'w-64']"
      >
        <!-- Navigation -->
        <nav class="flex-shrink-0 py-6">
          <div class="px-3 space-y-1">
            <router-link
              v-for="item in navigationItems"
              :key="item.name"
              :to="item.to"
              :class="[
                'group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors duration-200',
                isActivePath(item) ? 'bg-dark-800 text-white' : 'text-gray-400 hover:bg-dark-800 hover:text-white'
              ]"
            >
              <i 
                :class="[
                  item.icon,
                  'text-lg transition-colors duration-200',
                  isActivePath(item) ? 'text-primary-400' : 'text-gray-400 group-hover:text-white',
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
        <div class="flex-1 overflow-hidden">
          <slot name="sidebar-content" :isSidebarCollapsed="isSidebarCollapsed"></slot>
        </div>

        <!-- Bottom Actions -->
        <div class="flex-shrink-0 border-t border-dark-800">
          <!-- Additional bottom actions from slot -->
          <slot name="sidebar-bottom"></slot>
          
          <!-- Collapse/Expand Button -->
          <div class="p-4">
            <button 
              @click="toggleSidebar"
              class="w-full flex items-center justify-center p-2 bg-dark-800 rounded-lg text-gray-400 hover:text-white transition-colors"
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
        :class="[isSidebarCollapsed ? 'ml-16' : 'ml-64']"
      >
        <!-- Navbar -->
        <BaseNavbar class="fixed top-0 right-0 left-0 z-10 bg-dark-900/80 backdrop-blur-sm border-b border-dark-800" :class="[isSidebarCollapsed ? 'ml-16' : 'ml-64']">
          <template #left>
            <!-- Navbar left section -->
          </template>
        </BaseNavbar>

        <!-- Main content area -->
        <main class="flex-1 relative mt-16 bg-dark-950">
          <slot :isSidebarCollapsed="isSidebarCollapsed"></slot>
        </main>

        <!-- Footer -->
        <BaseFooter class="border-t border-dark-800" />
      </div>
    </div>
  </BaseLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/apps/auth/store'
import BaseLayout from './BaseLayout.vue'
import { BaseNavbar, BaseFooter } from '@/shared/components'

interface NavigationItem {
  name: string
  to: string
  icon?: string
  exact?: boolean
}

const props = defineProps<{
  navigationItems: NavigationItem[]
  storageKey?: string
}>()

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const isSidebarCollapsed = ref(false)

const isActivePath = (item: NavigationItem) => {
  if (item.exact) {
    return route.path === item.to
  }
  return route.path.startsWith(item.to)
}

const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
  localStorage.setItem(props.storageKey || 'dashboardSidebarCollapsed', String(isSidebarCollapsed.value))
}

onMounted(() => {
  // Initialize sidebar state from localStorage
  const savedCollapsed = localStorage.getItem(props.storageKey || 'dashboardSidebarCollapsed')
  if (savedCollapsed !== null) {
    isSidebarCollapsed.value = savedCollapsed === 'true'
  }

  // Check authentication
  if (!authStore.isAuthenticated) {
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
.w-64 {
  width: 16rem;
}

.w-16 {
  width: 4rem;
}

/* Smooth margin transitions */
.ml-64 {
  margin-left: 16rem;
}

.ml-16 {
  margin-left: 4rem;
}
</style>