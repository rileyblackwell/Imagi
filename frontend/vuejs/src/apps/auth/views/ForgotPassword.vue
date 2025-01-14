<template>
  <div class="auth-form-container">
    <!-- Header -->
    <div class="text-center mb-8">
      <h2 class="text-3xl font-bold text-white mb-2">Reset Password</h2>
      <p class="text-gray-400">Enter your email to receive password reset instructions</p>
    </div>

    <!-- Form -->
    <form v-if="!success" @submit.prevent="handleSubmit" class="space-y-6">
      <FormInput
        v-model="email"
        type="email"
        placeholder="Email Address"
        icon="fa-envelope"
        required
        :disabled="loading"
        :error="error"
      />

      <BaseButton
        type="submit"
        variant="primary"
        block
        :loading="loading"
      >
        Send Reset Link
      </BaseButton>
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

    <!-- Links -->
    <div class="mt-8 space-y-4">
      <p class="text-center text-gray-400">
        Remember your password? 
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

<script setup>
import { ref } from 'vue'
import BaseButton from '@/components/common/BaseButton.vue'
import FormInput from '@/components/common/FormInput.vue'
import { useAuthStore } from '@/apps/auth/store/auth'

const authStore = useAuthStore()
const email = ref('')
const loading = ref(false)
const error = ref('')
const success = ref(false)

async function handleSubmit() {
  if (!email.value) {
    error.value = 'Email is required'
    return
  }

  loading.value = true
  error.value = ''
  
  try {
    await authStore.forgotPassword(email.value)
    success.value = true
  } catch (err) {
    error.value = err.message || 'Failed to send reset email'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-form-container {
  @apply w-full max-w-md mx-auto p-8 bg-dark-900 border border-dark-700 rounded-2xl;
}

.text-success {
  @apply text-green-500;
}
</style> 