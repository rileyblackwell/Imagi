<template>
  <div class="auth-form-container">
    <!-- Header -->
    <div class="text-center mb-8">
      <h2 class="text-3xl font-bold text-white mb-2">Welcome back!</h2>
      <p class="text-gray-400">Sign in to continue to Imagi</p>
    </div>

    <!-- Form -->
    <form @submit.prevent="handleSubmit" class="space-y-6">
      <!-- Username -->
      <div class="form-group">
        <label class="relative block">
          <span class="sr-only">Username</span>
          <span class="absolute inset-y-0 left-0 flex items-center pl-4">
            <i class="fas fa-user text-gray-400"></i>
          </span>
          <input
            type="text"
            v-model="form.username"
            required
            :disabled="authStore.isLoading"
            placeholder="Username"
            class="w-full py-3 pl-11 pr-4 bg-dark-800 border border-dark-700 rounded-lg text-white placeholder-gray-500
                   focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500
                   disabled:opacity-50 disabled:cursor-not-allowed"
          >
        </label>
        <p v-if="errors.username" class="mt-1 text-sm text-red-500">{{ errors.username }}</p>
      </div>

      <!-- Password -->
      <div class="form-group">
        <label class="relative block">
          <span class="sr-only">Password</span>
          <span class="absolute inset-y-0 left-0 flex items-center pl-4">
            <i class="fas fa-lock text-gray-400"></i>
          </span>
          <input
            type="password"
            v-model="form.password"
            required
            :disabled="authStore.isLoading"
            placeholder="Password"
            class="w-full py-3 pl-11 pr-4 bg-dark-800 border border-dark-700 rounded-lg text-white placeholder-gray-500
                   focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500
                   disabled:opacity-50 disabled:cursor-not-allowed"
          >
        </label>
        <p v-if="errors.password" class="mt-1 text-sm text-red-500">{{ errors.password }}</p>
      </div>

      <!-- Submit Button -->
      <button
        type="submit"
        :disabled="authStore.isLoading"
        class="w-full py-3 px-4 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg
               focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors
               disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <span v-if="authStore.isLoading">
          <i class="fas fa-circle-notch fa-spin mr-2"></i>
          Signing in...
        </span>
        <span v-else>Sign In</span>
      </button>

      <!-- Error Message -->
      <p v-if="authStore.authError" class="text-center text-sm text-red-500">
        {{ authStore.authError }}
      </p>
    </form>

    <!-- Links -->
    <div class="mt-8 space-y-4">
      <p class="text-center text-gray-400">
        New to Imagi? 
        <router-link to="/auth/register" class="text-primary-400 hover:text-primary-300 font-medium">
          Create an account
        </router-link>
      </p>
      <div class="flex flex-col items-center space-y-2">
        <div class="w-full border-t border-dark-700"></div>
        <router-link to="/auth/forgot-password" class="text-gray-400 hover:text-gray-300">
          Forgot your password?
        </router-link>
        <router-link to="/" class="text-gray-400 hover:text-gray-300">
          Back to Home
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/apps/auth/store/auth'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const authStore = useAuthStore()
    
    const form = ref({
      username: '',
      password: ''
    })
    
    const errors = ref({
      username: '',
      password: ''
    })

    const handleSubmit = async () => {
      // Reset errors
      errors.value = {
        username: '',
        password: ''
      }

      try {
        await authStore.login(form.value)
        
        // Redirect to the intended page or dashboard
        const redirectPath = route.query.redirect || '/dashboard'
        await router.push(redirectPath)
      } catch (error) {
        // Handle specific field errors if they exist
        if (error.response?.data?.errors) {
          errors.value = error.response.data.errors
        }
      }
    }

    return {
      form,
      errors,
      authStore,
      handleSubmit
    }
  }
}
</script>

<style scoped>
.auth-form-container {
  @apply w-full max-w-md mx-auto p-8 bg-dark-900 border border-dark-700 rounded-2xl;
}
</style> 