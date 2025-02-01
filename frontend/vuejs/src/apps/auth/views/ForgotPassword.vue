<template>
  <!-- Form -->
  <form v-if="!success" @submit.prevent="handleSubmit" class="space-y-6">
    <!-- Email -->
    <div class="form-group">
      <label class="relative block">
        <span class="sr-only">Email</span>
        <span class="absolute inset-y-0 left-0 flex items-center pl-4">
          <i class="fas fa-envelope text-gray-400"></i>
        </span>
        <input
          type="email"
          v-model="email"
          required
          :disabled="loading"
          placeholder="Email Address"
          class="w-full py-3 pl-11 pr-4 bg-dark-800 border border-dark-700 rounded-lg text-white placeholder-gray-500
                 focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500
                 disabled:opacity-50 disabled:cursor-not-allowed"
        >
      </label>
      <p v-if="error" class="mt-1 text-sm text-red-500">{{ error }}</p>
    </div>

    <!-- Submit Button -->
    <button
      type="submit"
      :disabled="loading"
      class="w-full py-3 px-4 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg
             focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors
             disabled:opacity-50 disabled:cursor-not-allowed"
    >
      <span v-if="loading">
        <i class="fas fa-circle-notch fa-spin mr-2"></i>
        Sending...
      </span>
      <span v-else>Send Reset Link</span>
    </button>
  </form>

  <!-- Success Message -->
  <div v-else class="text-center space-y-4">
    <div class="text-success mb-4">
      <i class="fas fa-check-circle text-4xl"></i>
    </div>
    <h3 class="text-xl font-semibold text-white">Check Your Email</h3>
    <p class="text-gray-400">
      If an account exists with the email you provided, you will receive password reset instructions shortly.
    </p>
    <p class="text-gray-400">
      Please check your spam folder if you don't see the email in your inbox.
    </p>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useAuthStore } from '@/apps/auth/store'

export default {
  name: 'ForgotPassword',
  layoutConfig: {
    title: 'Reset Password',
    subtitle: 'Enter your email to receive password reset instructions',
    mainText: 'Remember your password?',
    mainLink: { to: '/auth/login', text: 'Sign in' }
  },
  setup() {
    const authStore = useAuthStore()
    const email = ref('')
    const loading = ref(false)
    const error = ref('')
    const success = ref(false)

    const handleSubmit = async () => {
      if (!email.value) {
        error.value = 'Email is required'
        return
      }

      loading.value = true
      error.value = ''
      
      try {
        await authStore.requestPasswordReset(email.value)
        success.value = true
      } catch (err) {
        error.value = err.message || 'Failed to send reset email'
      } finally {
        loading.value = false
      }
    }

    return {
      email,
      loading,
      error,
      success,
      handleSubmit
    }
  }
}
</script>

<style scoped>
.text-success {
  @apply text-green-500;
}
</style> 