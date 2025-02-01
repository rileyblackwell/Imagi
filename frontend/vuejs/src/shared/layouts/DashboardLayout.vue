<!-- Dashboard layout for authenticated users -->
<template>
  <BaseLayout>
    <div class="flex h-screen bg-dark-950">
      <!-- Sidebar -->
      <aside class="w-64 bg-dark-900 border-r border-dark-800">
        <div class="h-16 flex items-center px-6 border-b border-dark-800">
          <router-link to="/dashboard" class="flex items-center gap-3">
            <img src="@/shared/assets/images/logo.webp" alt="Imagi Logo" class="h-8 w-auto" />
            <span class="text-xl font-bold bg-gradient-to-r from-primary-300 to-primary-500 text-transparent bg-clip-text">
              Imagi
            </span>
          </router-link>
        </div>
        <nav class="mt-6">
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
              {{ item.name }}
            </router-link>
          </div>
        </nav>
      </aside>

      <!-- Main content -->
      <div class="flex-1 flex flex-col overflow-hidden">
        <!-- Top navigation -->
        <header class="bg-dark-900 border-b border-dark-800">
          <div class="px-4 sm:px-6 lg:px-8">
            <div class="h-16 flex items-center justify-between">
              <!-- Left section -->
              <div class="flex-1 flex">
                <h1 class="text-xl font-semibold text-white">{{ pageTitle }}</h1>
              </div>
              
              <!-- Right section -->
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
            </div>
          </div>
        </header>

        <!-- Page content -->
        <main class="flex-1 overflow-y-auto bg-dark-950 p-6">
          <slot></slot>
        </main>
      </div>
    </div>
  </BaseLayout>
</template>

<script>
import BaseLayout from './BaseLayout.vue'
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/apps/auth/store/auth'

export default {
  name: 'DashboardLayout',
  components: {
    BaseLayout
  },
  setup() {
    const route = useRoute()
    const authStore = useAuthStore()

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

    return {
      navigationItems,
      pageTitle,
      userName,
      userAvatar
    }
  }
}
</script> 