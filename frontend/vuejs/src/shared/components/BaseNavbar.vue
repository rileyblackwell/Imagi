<!-- BaseNavbar component -->
<template>
  <nav class="bg-dark-900 border-b border-dark-700">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <!-- Left side - Logo -->
        <div class="flex-shrink-0 flex items-center">
          <router-link 
            to="/" 
            class="text-2xl font-bold text-white hover:text-primary-400 transition-colors"
          >
            Imagi
          </router-link>
        </div>

        <!-- Right side - Auth -->
        <div class="flex items-center">
          <template v-if="isAuthenticated">
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
  </nav>
</template>

<script>
import { useAuthStore } from '@/apps/auth/store'
import { computed } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'BaseNavbar',
  setup() {
    const authStore = useAuthStore()
    const router = useRouter()

    const isAuthenticated = computed(() => authStore.isAuthenticated)

    const handleLogout = async () => {
      try {
        await authStore.logout()
        router.push('/auth/login')
      } catch (error) {
        console.error('Logout failed:', error)
      }
    }

    return {
      isAuthenticated,
      handleLogout
    }
  }
}
</script> 