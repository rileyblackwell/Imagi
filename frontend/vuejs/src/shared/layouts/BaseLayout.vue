<template>
  <div class="min-h-screen flex flex-col bg-dark-900">
    <!-- Navigation -->
    <nav class="fixed top-0 left-0 right-0 z-50 bg-dark-900/80 backdrop-blur-lg border-b border-dark-700">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <!-- Logo -->
          <router-link to="/" class="flex items-center space-x-2">
            <img src="@/shared/assets/images/logo.webp" alt="Imagi Logo" class="h-8 w-auto" />
            <span class="text-xl font-bold text-white">Imagi</span>
          </router-link>

          <!-- Navigation Links -->
          <div class="hidden md:flex items-center space-x-8">
            <slot name="navbar-links">
              <!-- Default navigation links -->
              <template v-if="isAuthenticated">
                <div class="relative group">
                  <button class="home-nav-btn flex items-center space-x-1">
                    <i class="fas fa-th"></i>
                    <span>Products</span>
                  </button>
                  <div class="absolute left-0 mt-2 w-48 rounded-lg bg-dark-800 border border-dark-700 shadow-lg opacity-0 group-hover:opacity-100 transform group-hover:translate-y-0 translate-y-2 transition-all duration-200">
                    <router-link to="/builder" class="block px-4 py-2 text-sm text-gray-300 hover:bg-dark-700">
                      <i class="fas fa-magic mr-2"></i>
                      Imagi Oasis
                    </router-link>
                  </div>
                </div>
                <button @click="handleBuyCredits" class="home-nav-btn">
                  <i class="fas fa-coins mr-1"></i>
                  <span>Buy Credits</span>
                </button>
              </template>
            </slot>
          </div>

          <!-- Auth Buttons -->
          <div class="flex items-center space-x-4">
            <slot name="auth-buttons">
              <!-- Default auth buttons -->
              <template v-if="isAuthenticated">
                <button @click="logout" class="home-nav-btn">
                  <i class="fas fa-sign-out-alt mr-1"></i>
                  <span>Logout</span>
                </button>
              </template>
              <template v-else>
                <router-link to="/auth/login" class="home-nav-btn">
                  <i class="fas fa-sign-in-alt mr-1"></i>
                  <span>Login</span>
                </router-link>
              </template>
            </slot>
          </div>
        </div>
      </div>
    </nav>

    <!-- Dashboard Layout (Only shown for dashboard routes) -->
    <template v-if="isDashboardRoute">
      <div class="flex min-h-screen pt-16">
        <!-- Sidebar -->
        <aside class="w-64 bg-dark-800 border-r border-dark-700 transition-all duration-300" :class="{ 'w-16': isSidebarCollapsed }">
          <div class="p-4 border-b border-dark-700 flex justify-end">
            <button @click="toggleSidebar" class="text-gray-400 hover:text-white">
              <i class="fas" :class="isSidebarCollapsed ? 'fa-chevron-right' : 'fa-chevron-left'"></i>
            </button>
          </div>
          <nav class="p-4">
            <router-link
              v-for="item in dashboardNavItems"
              :key="item.path"
              :to="item.path"
              class="flex items-center space-x-2 text-gray-400 hover:text-white py-2 px-3 rounded-lg transition-colors"
              :class="{ 'bg-dark-700': isCurrentRoute(item.path) }"
            >
              <i :class="item.icon"></i>
              <span v-if="!isSidebarCollapsed">{{ item.label }}</span>
            </router-link>
          </nav>
        </aside>

        <!-- Dashboard Content -->
        <main class="flex-1 p-8">
          <slot>
            <!-- Default content -->
          </slot>
        </main>
      </div>
    </template>

    <!-- Standard Layout -->
    <template v-else>
      <!-- Hero Section -->
      <section class="relative pt-32 overflow-hidden">
        <slot name="hero">
          <!-- Default hero content -->
        </slot>
      </section>

      <!-- Main Content -->
      <main>
        <slot>
          <!-- Default content -->
        </slot>
      </main>
    </template>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/apps/auth/store/auth'

export default {
  name: 'BaseLayout',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const authStore = useAuthStore()
    const isSidebarCollapsed = ref(false)

    const dashboardNavItems = [
      { path: '/dashboard', label: 'Dashboard', icon: 'fas fa-home' },
      { path: '/dashboard/projects', label: 'Projects', icon: 'fas fa-project-diagram' },
      { path: '/dashboard/settings', label: 'Settings', icon: 'fas fa-cog' },
      { path: '/dashboard/billing', label: 'Billing', icon: 'fas fa-credit-card' }
    ]

    const isDashboardRoute = computed(() => {
      return route.path.startsWith('/dashboard')
    })

    const isCurrentRoute = (path) => {
      return route.path === path
    }

    const toggleSidebar = () => {
      isSidebarCollapsed.value = !isSidebarCollapsed.value
    }

    const handleBuyCredits = () => {
      if (!authStore.isAuthenticated) {
        router.push({ 
          path: '/auth/login',
          query: { redirect: '/payments/checkout' }
        })
      } else {
        router.push('/payments/checkout')
      }
    }

    return {
      isAuthenticated: computed(() => authStore.isAuthenticated),
      logout: () => authStore.logout(),
      isDashboardRoute,
      isCurrentRoute,
      isSidebarCollapsed,
      toggleSidebar,
      dashboardNavItems,
      handleBuyCredits
    }
  }
}
</script>

<style>
.home-nav-btn {
  @apply inline-flex items-center px-4 py-2 text-sm font-medium text-gray-300 rounded-lg 
         bg-dark-800 hover:bg-dark-700 hover:text-white transition-colors;
}

.home-nav-btn i {
  @apply text-primary-400;
}

.page-enter-active,
.page-leave-active {
  transition: opacity 0.2s ease;
}

.page-enter-from,
.page-leave-to {
  opacity: 0;
}
</style> 