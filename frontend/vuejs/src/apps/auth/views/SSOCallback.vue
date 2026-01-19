<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-950 via-violet-950/20 to-slate-950">
    <div class="text-center space-y-6">
      <!-- Loading spinner -->
      <div class="relative w-20 h-20 mx-auto">
        <div class="absolute inset-0 rounded-full border-4 border-violet-500/20"></div>
        <div class="absolute inset-0 rounded-full border-4 border-t-violet-500 animate-spin"></div>
      </div>
      
      <!-- Loading text -->
      <div class="space-y-2">
        <h2 class="text-xl font-semibold text-white">
          {{ errorMessage ? 'Authentication Failed' : 'Completing sign in...' }}
        </h2>
        <p v-if="errorMessage" class="text-red-400 text-sm">
          {{ errorMessage }}
        </p>
        <p v-else class="text-white/50 text-sm">
          Please wait while we complete your authentication
        </p>
      </div>
      
      <!-- Error action -->
      <div v-if="errorMessage" class="pt-4">
        <button
          @click="goToLogin"
          class="px-6 py-3 rounded-xl bg-violet-600 hover:bg-violet-700 text-white font-medium transition-colors duration-300"
        >
          Return to Login
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/apps/auth/stores/index'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const errorMessage = ref('')

const goToLogin = () => {
  router.push('/auth/login')
}

onMounted(async () => {
  try {
    // Get token from query params
    const token = route.query.token as string
    const ssoError = route.query.sso_error as string
    const redirectPath = route.query.redirect as string
    
    // Handle SSO errors
    if (ssoError) {
      switch (ssoError) {
        case 'oauth_not_configured':
          errorMessage.value = 'Google sign-in is not configured yet. Please use email/password.'
          break
        case 'no_account':
          errorMessage.value = 'No account found with this Google email. Please register first.'
          break
        case 'no_email':
          errorMessage.value = 'Google account does not have a verified email address.'
          break
        case 'server_error':
          errorMessage.value = 'An error occurred during authentication. Please try again.'
          break
        default:
          errorMessage.value = 'Authentication failed. Please try again.'
      }
      
      // Redirect to login after showing error
      setTimeout(() => {
        router.push(`/auth/login?sso_error=${ssoError}`)
      }, 3000)
      return
    }
    
    // Validate token
    if (!token || typeof token !== 'string' || token.trim() === '') {
      errorMessage.value = 'Invalid authentication token received.'
      setTimeout(goToLogin, 2000)
      return
    }
    
    // Store token in localStorage (matching existing token storage format)
    localStorage.setItem('token', JSON.stringify(token))
    
    // Initialize auth store to fetch user data
    try {
      await authStore.init()
    } catch (error) {
      console.error('Failed to initialize auth store:', error)
    }
    
    // Redirect to the appropriate page
    if (redirectPath && typeof redirectPath === 'string') {
      await router.push(redirectPath)
    } else {
      await router.push('/')
    }
  } catch (error) {
    console.error('SSO callback error:', error)
    errorMessage.value = 'An unexpected error occurred. Please try again.'
    setTimeout(goToLogin, 2000)
  }
})
</script>

<style scoped>
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>
