<template>
  <div>
    <AuthHeader 
      title="Welcome back!"
      subtitle="Sign in to continue to Imagi"
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

      <!-- Error Message -->
      <p v-if="errors.general" class="text-center text-sm text-red-500">
        {{ errors.general }}
      </p>

      <!-- Submit Button -->
      <button
        type="submit"
        :disabled="authStore.loading"
        class="w-full py-3 px-4 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg
               focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors
               disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <span v-if="authStore.loading">
          <i class="fas fa-circle-notch fa-spin mr-2"></i>
          Signing in...
        </span>
        <span v-else>Sign In</span>
      </button>
    </form>

    <!-- Links -->
    <AuthLinks
      main-text="New to Imagi?"
      :main-link="{ to: '/auth/register', text: 'Create an account' }"
    >
      <template #additional-links>
        <router-link to="/auth/forgot-password" class="text-gray-400 hover:text-gray-300">
          Forgot your password?
        </router-link>
      </template>
    </AuthLinks>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/apps/auth/store'
import AuthHeader from '../components/AuthHeader.vue'
import AuthLinks from '../components/AuthLinks.vue'

export default {
  name: 'Login',
  components: {
    AuthHeader,
    AuthLinks
  },
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
      password: '',
      general: ''
    })

    const handleSubmit = async () => {
      // Reset errors
      errors.value = {
        username: '',
        password: '',
        general: ''
      }

      try {
        const result = await authStore.login(form.value)
        const redirectPath = route.query.redirect || '/'
        router.push(redirectPath)
      } catch (error) {
        console.error('Login error:', error)
        if (typeof error === 'object') {
          // Handle field-specific errors
          Object.keys(error).forEach(field => {
            if (field in errors.value) {
              errors.value[field] = error[field]
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