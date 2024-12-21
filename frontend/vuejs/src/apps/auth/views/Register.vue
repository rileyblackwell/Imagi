<template>
  <div class="auth-form-container">
    <!-- Header -->
    <div class="text-center mb-8">
      <h2 class="text-3xl font-bold text-white mb-2">Create Account</h2>
      <p class="text-gray-400">Join Imagi today</p>
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
            placeholder="Username"
            class="w-full py-3 pl-11 pr-4 bg-dark-800 border border-dark-700 rounded-lg text-white placeholder-gray-500
                   focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
          >
        </label>
        <p v-if="errors.username" class="mt-1 text-sm text-red-500">{{ errors.username }}</p>
      </div>

      <!-- Email -->
      <div class="form-group">
        <label class="relative block">
          <span class="sr-only">Email</span>
          <span class="absolute inset-y-0 left-0 flex items-center pl-4">
            <i class="fas fa-envelope text-gray-400"></i>
          </span>
          <input
            type="email"
            v-model="form.email"
            required
            placeholder="Email"
            class="w-full py-3 pl-11 pr-4 bg-dark-800 border border-dark-700 rounded-lg text-white placeholder-gray-500
                   focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
          >
        </label>
        <p v-if="errors.email" class="mt-1 text-sm text-red-500">{{ errors.email }}</p>
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
            placeholder="Password"
            class="w-full py-3 pl-11 pr-4 bg-dark-800 border border-dark-700 rounded-lg text-white placeholder-gray-500
                   focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
          >
        </label>
        <p v-if="errors.password" class="mt-1 text-sm text-red-500">{{ errors.password }}</p>
      </div>

      <!-- Confirm Password -->
      <div class="form-group">
        <label class="relative block">
          <span class="sr-only">Confirm Password</span>
          <span class="absolute inset-y-0 left-0 flex items-center pl-4">
            <i class="fas fa-lock text-gray-400"></i>
          </span>
          <input
            type="password"
            v-model="form.confirmPassword"
            required
            placeholder="Confirm Password"
            class="w-full py-3 pl-11 pr-4 bg-dark-800 border border-dark-700 rounded-lg text-white placeholder-gray-500
                   focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
          >
        </label>
        <p v-if="errors.confirmPassword" class="mt-1 text-sm text-red-500">{{ errors.confirmPassword }}</p>
      </div>

      <!-- Terms Agreement -->
      <div class="flex items-start">
        <div class="flex items-center h-5">
          <input
            type="checkbox"
            v-model="form.agreeToTerms"
            required
            class="w-4 h-4 border border-dark-600 rounded bg-dark-800 text-primary-600 focus:ring-primary-500"
          >
        </div>
        <div class="ml-3">
          <label class="text-sm text-gray-400">
            I agree to the 
            <router-link to="/terms" class="text-primary-400 hover:text-primary-300">Terms of Service</router-link>
            and
            <router-link to="/privacy" class="text-primary-400 hover:text-primary-300">Privacy Policy</router-link>
          </label>
        </div>
      </div>

      <!-- Submit Button -->
      <button
        type="submit"
        :disabled="isLoading || !form.agreeToTerms"
        class="w-full py-3 px-4 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg
               focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors
               disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <span v-if="isLoading">
          <i class="fas fa-circle-notch fa-spin mr-2"></i>
          Creating account...
        </span>
        <span v-else>Create Account</span>
      </button>

      <!-- Error Message -->
      <p v-if="errors.general" class="text-center text-sm text-red-500">
        {{ errors.general }}
      </p>
    </form>

    <!-- Links -->
    <div class="mt-8 space-y-4">
      <p class="text-center text-gray-400">
        Already have an account? 
        <router-link to="/auth/login" class="text-primary-400 hover:text-primary-300 font-medium">
          Sign in
        </router-link>
      </p>
      <div class="flex flex-col items-center space-y-2">
        <div class="w-full border-t border-dark-700"></div>
        <router-link to="/" class="text-gray-400 hover:text-gray-300">
          Back to Home
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'Register',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    
    const form = ref({
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
      agreeToTerms: false
    })
    
    const errors = ref({
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
      general: ''
    })
    
    const isLoading = ref(false)

    const validateForm = () => {
      const newErrors = {}

      if (form.value.password !== form.value.confirmPassword) {
        newErrors.confirmPassword = 'Passwords do not match'
      }

      if (form.value.password.length < 8) {
        newErrors.password = 'Password must be at least 8 characters long'
      }

      errors.value = { ...errors.value, ...newErrors }
      return Object.keys(newErrors).length === 0
    }

    const handleSubmit = async () => {
      // Reset errors
      errors.value = {
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
        general: ''
      }

      if (!validateForm()) {
        return
      }

      try {
        isLoading.value = true
        await authStore.register({
          username: form.value.username,
          email: form.value.email,
          password: form.value.password
        })
        
        // Redirect to dashboard after successful registration
        await router.push('/dashboard')
      } catch (error) {
        if (error.response?.data?.errors) {
          errors.value = error.response.data.errors
        } else {
          errors.value.general = 'An error occurred during registration. Please try again.'
        }
      } finally {
        isLoading.value = false
      }
    }

    return {
      form,
      errors,
      isLoading,
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