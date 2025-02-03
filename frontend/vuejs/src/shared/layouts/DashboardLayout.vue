<!-- Dashboard layout for authenticated users -->
<template>
  <BaseLayout>
    <div class="min-h-screen flex">
      <!-- Sidebar -->
      <aside 
        class="fixed inset-y-0 left-0 z-20 flex flex-col transition-all duration-300 border-r border-dark-800 bg-dark-950" 
        :class="[isSidebarCollapsed ? 'w-16' : 'w-64']"
      >
        <!-- Navigation -->
        <nav class="flex-1 py-6 overflow-y-auto">
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
        
        <!-- Collapse button -->
        <div class="flex-shrink-0 p-4 border-t border-dark-800">
          <button 
            @click="toggleSidebar"
            class="w-full flex items-center justify-center p-2 bg-dark-800 rounded-lg text-gray-400 hover:text-white transition-colors"
          >
            <i class="fas" :class="isSidebarCollapsed ? 'fa-chevron-right' : 'fa-chevron-left'"></i>
          </button>
        </div>
      </aside>

      <!-- Main content -->
      <div class="flex-1 flex flex-col" :class="[isSidebarCollapsed ? 'ml-16' : 'ml-64']">
        <!-- Navbar -->
        <BaseNavbar class="bg-dark-900/80 backdrop-blur-sm border-b border-dark-800">
          <template #left>
            <!-- Navbar left section without title -->
          </template>
        </BaseNavbar>

        <!-- Main content area -->
        <main class="flex-1 relative overflow-y-auto bg-dark-950 pt-20">
          <div class="py-6">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <slot></slot>
            </div>
          </div>
        </main>

        <!-- Footer -->
        <BaseFooter class="border-t border-dark-800" />
      </div>
    </div>
  </BaseLayout>
</template>

<script>
import BaseLayout from './BaseLayout.vue'
import { BaseNavbar, BaseFooter } from '@/shared/components'
import { ref, onMounted } from 'vue'
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
      isSidebarCollapsed,
      toggleSidebar
    }
  }
}
</script> 