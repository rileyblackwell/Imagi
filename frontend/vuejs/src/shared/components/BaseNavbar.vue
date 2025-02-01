<!-- BaseNavbar component -->
<template>
  <nav class="bg-dark-900 border-b border-dark-700">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <!-- Left side - Logo -->
        <div class="flex items-center">
          <router-link 
            to="/" 
            class="text-2xl font-bold text-white hover:text-primary-400 transition-colors mr-8"
          >
            Imagi
          </router-link>

          <!-- Products Dropdown - Only shown when authenticated -->
          <div v-if="isAuthenticated" class="relative">
            <button
              @click="toggleProductsMenu"
              class="inline-flex items-center px-4 py-2 text-sm font-medium text-white hover:text-primary-400 transition-colors"
              :class="{ 'text-primary-400': isProductsMenuOpen }"
            >
              Products
              <i class="fas fa-chevron-down ml-2 text-xs" :class="{ 'transform rotate-180': isProductsMenuOpen }"></i>
            </button>

            <!-- Dropdown Menu -->
            <div
              v-show="isProductsMenuOpen"
              class="absolute left-0 mt-2 w-56 rounded-lg bg-dark-800 border border-dark-700 shadow-lg z-50"
            >
              <router-link
                to="/builder"
                class="block px-4 py-3 text-sm text-white hover:bg-dark-700 transition-colors rounded-lg"
                @click="isProductsMenuOpen = false"
              >
                <i class="fas fa-magic mr-2"></i>
                Oasis Web App Builder
              </router-link>
            </div>
          </div>
        </div>

        <!-- Right side - Auth -->
        <div class="flex items-center space-x-4">
          <template v-if="isAuthenticated">
            <!-- Buy Credits Button -->
            <router-link
              to="/payments/checkout"
              class="inline-flex items-center px-4 py-2 border border-transparent rounded-lg text-sm font-medium text-white bg-primary-600 hover:bg-primary-500 transition-colors"
            >
              <i class="fas fa-coins mr-2"></i>
              Buy Credits
            </router-link>

            <!-- Logout Button -->
            <button
              @click="handleLogout"
              class="inline-flex items-center px-4 py-2 border border-transparent rounded-lg text-sm font-medium text-white bg-dark-800 hover:bg-dark-700 transition-colors"
            >
              <i class="fas fa-sign-out-alt mr-2"></i>
              Logout
            </button>
          </template>
          <template v-else>
            <router-link
              to="/auth/login"
              class="inline-flex items-center px-4 py-2 border border-transparent rounded-lg text-sm font-medium text-white bg-primary-600 hover:bg-primary-500 transition-colors"
            >
              <i class="fas fa-sign-in-alt mr-2"></i>
              Login
            </router-link>
          </template>
        </div>
      </div>
    </div>

    <!-- Overlay for closing dropdown when clicking outside -->
    <div
      v-if="isProductsMenuOpen"
      class="fixed inset-0 z-40"
      @click="isProductsMenuOpen = false"
    ></div>
  </nav>
</template>

<script>
import { useAuthStore } from '@/apps/auth/store'
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'BaseNavbar',
  setup() {
    const authStore = useAuthStore()
    const router = useRouter()
    const isProductsMenuOpen = ref(false)

    const isAuthenticated = computed(() => authStore.isAuthenticated)

    const handleLogout = async () => {
      try {
        await authStore.logout()
        router.push('/auth/login')
      } catch (error) {
        console.error('Logout failed:', error)
      }
    }

    const toggleProductsMenu = () => {
      isProductsMenuOpen.value = !isProductsMenuOpen.value
    }

    return {
      isAuthenticated,
      handleLogout,
      isProductsMenuOpen,
      toggleProductsMenu
    }
  }
}
</script>

<style scoped>
/* Add transition for dropdown chevron */
.fa-chevron-down {
  transition: transform 0.2s ease-in-out;
}
</style> 