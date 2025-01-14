<template>
  <header class="app-header">
    <nav class="max-w-7xl mx-auto px-4 py-6 flex justify-between items-center">
      <router-link to="/" class="flex items-center">
        <div class="h-12 w-12 rounded-lg bg-gradient-to-r from-primary-400 to-primary-600 flex items-center justify-center text-white font-bold text-2xl">
          I
        </div>
      </router-link>
      
      <div class="flex items-center gap-8">
        <router-link 
          v-for="item in navItems" 
          :key="item.path"
          :to="item.path"
          class="text-gray-300 hover:text-white transition-colors"
          :class="{ 'text-white': isCurrentRoute(item.path) }"
        >
          {{ item.name }}
        </router-link>
        
        <template v-if="isAuthenticated">
          <router-link 
            to="/dashboard"
            class="text-gray-300 hover:text-white transition-colors"
          >
            Dashboard
          </router-link>
          <button 
            @click="handleLogout"
            class="text-gray-300 hover:text-white transition-colors"
          >
            Sign Out
          </button>
        </template>
        <template v-else>
          <router-link 
            to="/auth/login"
            class="text-gray-300 hover:text-white transition-colors"
          >
            Sign In
          </router-link>
          <router-link 
            to="/auth/register"
            class="px-6 py-2 bg-gradient-to-r from-cyan-500 to-blue-500 text-white rounded-lg 
                   font-semibold hover:from-cyan-600 hover:to-blue-600 transition-all 
                   transform hover:scale-105 shadow-lg hover:shadow-cyan-500/25"
          >
            Sign Up
          </router-link>
        </template>
      </div>
    </nav>
  </header>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { computed } from 'vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const navItems = [
  { name: 'Home', path: '/' },
  { name: 'About', path: '/about' },
]

const isAuthenticated = computed(() => authStore.isAuthenticated)

const isCurrentRoute = (path) => {
  return route.path === path
}

const handleLogout = async () => {
  try {
    await authStore.logout()
    router.push('/')
  } catch (error) {
    console.error('Logout failed:', error)
  }
}
</script>

<style>
.app-header {
  @apply bg-gray-900/80 backdrop-blur-lg border-b border-gray-800 sticky top-0 z-50;
}
</style> 