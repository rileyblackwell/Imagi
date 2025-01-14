<template>
  <div class="min-h-screen flex flex-col">
    <!-- Header -->
    <header class="bg-dark-900/80 backdrop-blur-sm border-b border-dark-800 sticky top-0 z-50">
      <nav class="container mx-auto px-4 py-4">
        <div class="flex items-center justify-between">
          <!-- Logo -->
          <router-link to="/" class="flex items-center gap-3">
            <img src="@/shared/assets/images/logo.webp" alt="Imagi Logo" class="h-8 w-auto" />
            <span class="text-xl font-bold bg-gradient-to-r from-primary-300 to-primary-500 text-transparent bg-clip-text">
              Imagi
            </span>
          </router-link>

          <!-- Navigation -->
          <div class="hidden md:flex items-center space-x-8">
            <router-link 
              v-for="item in navigation" 
              :key="item.name"
              :to="item.to"
              class="text-dark-300 hover:text-primary-400 transition-colors"
            >
              {{ item.name }}
            </router-link>
          </div>

          <!-- Auth Buttons -->
          <div class="flex items-center gap-4">
            <router-link 
              v-if="!isAuthenticated"
              to="/auth/login" 
              class="text-dark-300 hover:text-primary-400 transition-colors"
            >
              Log in
            </router-link>
            <router-link 
              v-if="!isAuthenticated"
              to="/auth/register" 
              class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              Get Started
            </router-link>
            <button
              v-else
              @click="handleLogout"
              class="text-dark-300 hover:text-primary-400 transition-colors"
            >
              Log out
            </button>
          </div>
        </div>
      </nav>
    </header>

    <!-- Main Content -->
    <main class="flex-grow">
      <router-view></router-view>
    </main>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'MainLayout',
  
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    
    const navigation = ref([
      { name: 'Features', to: '/features' },
      { name: 'Pricing', to: '/pricing' },
      { name: 'Docs', to: '/docs' },
      { name: 'Blog', to: '/blog' }
    ])
    
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
      navigation,
      isAuthenticated,
      handleLogout
    }
  }
}
</script> 