<!-- Form -->
<template>
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
          v-model="form.password_confirm"
          required
          :disabled="authStore.loading"
          placeholder="Confirm Password"
          class="w-full py-3 pl-11 pr-4 bg-dark-800 border border-dark-700 rounded-lg text-white placeholder-gray-500
                 focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500
                 disabled:opacity-50 disabled:cursor-not-allowed"
        >
      </label>
      <p v-if="errors.password_confirm" class="mt-1 text-sm text-red-500">{{ errors.password_confirm }}</p>
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
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/apps/auth/store'

export default {
  name: 'Register',
  layoutConfig: {
    title: 'Create Account',
    subtitle: 'Join Imagi today',
    mainText: 'Already have an account?',
    mainLink: { to: '/auth/login', text: 'Sign in' }
  },
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    
    const form = ref({
      username: '',
      password: '',
      password_confirm: '',
      agreeToTerms: false
    })
    
    const errors = ref({
      username: '',
      password: '',
      password_confirm: '',
      general: ''
    })

    const validateForm = () => {
      const newErrors = {}

      if (!form.value.username) {
        newErrors.username = 'Username is required'
      }

      if (!form.value.password) {
        newErrors.password = 'Password is required'
      }

      if (form.value.password !== form.value.password_confirm) {
        newErrors.password_confirm = 'Passwords do not match'
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
        password_confirm: '',
        general: ''
      }

      // Client-side validation
      if (!validateForm()) {
        return
      }

      try {
        await authStore.register({
          username: form.value.username,
          password: form.value.password,
          password_confirm: form.value.password_confirm
        })
        
        // Redirect to home page after successful registration
        await router.push('/')
      } catch (error) {
        console.error('Registration error:', error)
        
        // Handle different error formats
        if (typeof error === 'string') {
          errors.value.general = error
        } else if (error.non_field_errors) {
          errors.value.general = Array.isArray(error.non_field_errors) 
            ? error.non_field_errors[0] 
            : error.non_field_errors
        } else if (error.detail) {
          errors.value.general = error.detail
        } else if (typeof error === 'object') {
          // Handle field-specific errors
          Object.entries(error).forEach(([field, messages]) => {
            const message = Array.isArray(messages) ? messages[0] : messages
            if (field in errors.value) {
              errors.value[field] = message
            } else {
              errors.value.general = message
            }
          })
        }
        
        // If no error was set, show a generic error
        if (!Object.values(errors.value).some(e => e)) {
          errors.value.general = 'Registration failed. Please try again.'
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