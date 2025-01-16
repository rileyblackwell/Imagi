<template>
  <div>
    <AuthHeader 
      title="Create Account"
      subtitle="Join Imagi today"
    />

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
            :disabled="authStore.loading"
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
            :disabled="authStore.loading"
            placeholder="Password"
            class="w-full py-3 pl-11 pr-4 bg-dark-800 border border-dark-700 rounded-lg text-white placeholder-gray-500
                   focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500
                   disabled:opacity-50 disabled:cursor-not-allowed"
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
            :disabled="authStore.loading"
            placeholder="Confirm Password"
            class="w-full py-3 pl-11 pr-4 bg-dark-800 border border-dark-700 rounded-lg text-white placeholder-gray-500
                   focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500
                   disabled:opacity-50 disabled:cursor-not-allowed"
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
            :disabled="authStore.loading"
            class="w-4 h-4 border border-dark-600 rounded bg-dark-800 text-primary-600 focus:ring-primary-500
                   disabled:opacity-50 disabled:cursor-not-allowed"
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

      <!-- Error Message -->
      <p v-if="errors.general" class="text-center text-sm text-red-500">
        {{ errors.general }}
      </p>

      <!-- Submit Button -->
      <button
        type="submit"
        :disabled="authStore.loading || !form.agreeToTerms"
        class="w-full py-3 px-4 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg
               focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors
               disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <span v-if="authStore.loading">
          <i class="fas fa-circle-notch fa-spin mr-2"></i>
          Creating account...
        </span>
        <span v-else>Create Account</span>
      </button>
    </form>

    <!-- Links -->
    <AuthLinks
      main-text="Already have an account?"
      :main-link="{ to: '/auth/login', text: 'Sign in' }"
    />
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/apps/auth/store'
import AuthHeader from '../components/AuthHeader.vue'
import AuthLinks from '../components/AuthLinks.vue'

export default {
  name: 'Register',
  components: {
    AuthHeader,
    AuthLinks
  },
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    
    const form = ref({
      username: '',
      password: '',
      confirmPassword: '',
      agreeToTerms: false
    })
    
    const errors = ref({
      username: '',
      password: '',
      confirmPassword: '',
      general: ''
    })

    const validateForm = () => {
      const newErrors = {}

      if (form.value.password !== form.value.confirmPassword) {
        newErrors.confirmPassword = 'Passwords do not match'
      }

      if (form.value.password.length < 8) {
        newErrors.password = 'Password must be at least 8 characters long'
      }

      if (!form.value.agreeToTerms) {
        newErrors.general = 'You must agree to the Terms of Service and Privacy Policy'
      }

      errors.value = { ...errors.value, ...newErrors }
      return Object.keys(newErrors).length === 0
    }

    const handleSubmit = async () => {
      // Reset errors
      errors.value = {
        username: '',
        password: '',
        confirmPassword: '',
        general: ''
      }

      // Client-side validation
      if (!validateForm()) {
        return
      }

      try {
        await authStore.register({
          username: form.value.username,
          password: form.value.password
        })
        
        // Redirect to home page after successful registration
        await router.push('/')
      } catch (error) {
        console.error('Registration error:', error)
        if (typeof error === 'object') {
          // Handle field-specific errors
          Object.keys(error).forEach(field => {
            if (field in errors.value) {
              errors.value[field] = Array.isArray(error[field]) 
                ? error[field][0] 
                : error[field]
            } else {
              errors.value.general = error[field]
            }
          })
        } else {
          // Handle string error
          errors.value.general = error.toString()
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