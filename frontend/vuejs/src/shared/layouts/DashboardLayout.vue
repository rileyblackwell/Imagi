<!-- Dashboard layout for authenticated users -->
<template>
  <BaseLayout>
    <div class="flex h-screen bg-dark-950">
      <!-- Sidebar -->
      <aside class="transition-all duration-300 flex flex-col" :class="[isSidebarCollapsed ? 'w-16' : 'w-64', 'bg-dark-900 border-r border-dark-800']">
        <!-- Navigation -->
        <nav class="flex-1 mt-6">
          <div class="px-3 space-y-1">
            <router-link
              v-for="item in navigationItems"
              :key="item.name"
              :to="item.to"
              :class="[
                $route.path === item.to
                  ? 'bg-dark-800 text-white'
                  : 'text-gray-400 hover:bg-dark-800 hover:text-white',
                'group flex items-center px-3 py-2 text-sm font-medium rounded-md'
              ]"
            >
              <component
                :is="item.icon"
                :class="[
                  $route.path === item.to ? 'text-primary-400' : 'text-gray-400 group-hover:text-white',
                  'mr-3 h-5 w-5'
                ]"
              />
              <span v-if="!isSidebarCollapsed">{{ item.name }}</span>
            </router-link>
          </div>
        </nav>
        
        <!-- Collapse button at bottom of sidebar -->
        <div class="p-4 border-t border-dark-800">
          <button 
            @click="toggleSidebar"
            class="w-full flex items-center justify-center p-2 bg-dark-800 rounded-lg text-gray-400 hover:text-white transition-colors"
          >
            <i class="fas" :class="isSidebarCollapsed ? 'fa-chevron-right' : 'fa-chevron-left'"></i>
          </button>
        </div>
      </aside>

      <!-- Main content -->
      <div class="flex-1 flex flex-col overflow-hidden">
        <!-- Top navigation -->
        <div class="flex-shrink-0">
          <BaseNavbar>
            <!-- Left section -->
            <template #left>
              <h1 class="text-xl font-semibold text-white">{{ pageTitle }}</h1>
            </template>
            
            <!-- Right section -->
            <template #right>
              <div class="flex items-center space-x-4">
                <!-- User dropdown -->
                <div class="relative">
                  <button
                    class="flex items-center space-x-3 text-gray-400 hover:text-white focus:outline-none"
                  >
                    <img
                      class="h-8 w-8 rounded-full"
                      :src="userAvatar"
                      alt=""
                    />
                    <span class="text-sm font-medium">{{ userName }}</span>
                  </button>
                </div>
              </div>
            </template>
          </BaseNavbar>
        </div>

        <!-- Page content -->
        <main class="flex-1 overflow-y-auto bg-dark-950">
          <div class="h-full">
            <slot></slot>
          </div>
        </main>

        <!-- Footer -->
        <div class="flex-shrink-0">
          <BaseFooter />
        </div>
      </div>
    </div>
  </BaseLayout>
</template>

<script>
import BaseLayout from './BaseLayout.vue'
import { BaseNavbar, BaseFooter } from '@/shared/components'
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/apps/auth/store'

export default {
  name: 'DashboardLayout',
  components: {
    BaseLayout,
    BaseNavbar,
    BaseFooter
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const authStore = useAuthStore()
    const isSidebarCollapsed = ref(false)

    const navigationItems = [
      { name: 'Dashboard', to: '/dashboard', icon: 'HomeIcon' },
      { name: 'Projects', to: '/dashboard/projects', icon: 'FolderIcon' },
      { name: 'Settings', to: '/dashboard/settings', icon: 'CogIcon' }
    ]

    const pageTitle = computed(() => {
      return route.meta.title || 'Dashboard'
    })

    const userName = computed(() => {
      return authStore.user?.name || 'User'
    })

    const userAvatar = computed(() => {
      return authStore.user?.avatar || 'https://via.placeholder.com/40'
    })

    const toggleSidebar = () => {
      isSidebarCollapsed.value = !isSidebarCollapsed.value
      localStorage.setItem('dashboardSidebarCollapsed', isSidebarCollapsed.value)
    }

    // Check authentication on mount
    onMounted(async () => {
      if (!authStore.isAuthenticated) {
        router.push({ 
          name: 'login',
          query: { redirect: route.fullPath }
        })
      }

      // Initialize sidebar state from localStorage
      const savedCollapsed = localStorage.getItem('dashboardSidebarCollapsed')
      if (savedCollapsed !== null) {
        isSidebarCollapsed.value = savedCollapsed === 'true'
      }
    })

    return {
      navigationItems,
      pageTitle,
      userName,
      userAvatar,
      isSidebarCollapsed,
      toggleSidebar
    }
  }
}
</script> 