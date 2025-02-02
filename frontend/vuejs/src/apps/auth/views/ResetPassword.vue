<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/apps/auth/store'
import PasswordInput from '../components/PasswordInput.vue'
import PasswordRequirements from '../components/PasswordRequirements.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const passwordRequirements = ref(null)

const form = ref({
  password: '',
  confirmPassword: ''
})

const loading = ref(false)
const error = ref('')
const success = ref(false)

const isFormValid = computed(() => {
  return passwordRequirements.value?.isValid &&
         form.value.password === form.value.confirmPassword
})

async function handleSubmit() {
  if (!isFormValid.value) {
    error.value = 'Please ensure all password requirements are met and passwords match'
    return
  }

  loading.value = true
  error.value = ''
  
  try {
    await authStore.resetPassword({
      token: route.query.token,
      password: form.value.password
    })
    success.value = true
    setTimeout(() => {
      router.push('/auth/login')
    }, 3000)
  } catch (err) {
    error.value = err.message || 'Failed to reset password. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-dark-900 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8 bg-dark-800 p-8 rounded-lg shadow-lg">
      <div class="text-center">
        <h2 class="text-3xl font-bold text-white">Reset Password</h2>
        <p class="mt-2 text-sm text-gray-400">
          Enter your new password below
        </p>
      </div>

      <form v-if="!success" @submit.prevent="handleSubmit" class="mt-8 space-y-6">
        <!-- Password Requirements -->
        <PasswordRequirements
          ref="passwordRequirements"
          :password="form.password"
        />

        <!-- Password Input -->
        <PasswordInput
          v-model="form.password"
          label="New Password"
          placeholder="New Password"
          required
        />

        <!-- Confirm Password Input -->
        <PasswordInput
          v-model="form.confirmPassword"
          label="Confirm New Password"
          placeholder="Confirm New Password"
          required
        />

        <!-- Error Message -->
        <div v-if="error" class="rounded-md bg-red-900/50 p-4">
          <div class="flex">
            <i class="fas fa-exclamation-circle text-red-400 mt-0.5"></i>
            <div class="ml-3">
              <h3 class="text-sm font-medium text-red-400">
                {{ error }}
              </h3>
            </div>
          </div>
        </div>

        <!-- Submit Button -->
        <button
          type="submit"
          :disabled="!isFormValid || loading"
          class="group relative w-full flex justify-center py-3 px-4 border border-transparent
                 text-sm font-medium rounded-lg text-white bg-primary-600 hover:bg-primary-700
                 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500
                 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="loading" class="absolute inset-y-0 left-0 flex items-center pl-3">
            <i class="fas fa-circle-notch fa-spin"></i>
          </span>
          {{ loading ? 'Resetting Password...' : 'Reset Password' }}
        </button>
      </form>

      <!-- Success Message -->
      <div v-else class="text-center space-y-4">
        <div class="text-green-500 text-5xl mb-4">
          <i class="fas fa-check-circle"></i>
        </div>
        <h3 class="text-xl font-semibold text-white">Password Reset Successful!</h3>
        <p class="text-gray-400">
          Your password has been successfully reset.
        </p>
        <router-link
          to="/auth/login"
          class="mt-4 inline-block px-4 py-2 border border-transparent text-sm font-medium rounded-lg
                 text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2
                 focus:ring-offset-2 focus:ring-primary-500"
        >
          Go to Login
        </router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.reset-password-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-lg);
  background: var(--color-background-alt);
}

.reset-password-container {
  width: 100%;
  max-width: 400px;
  padding: var(--spacing-xl);
  background: var(--color-background);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-lg);
}

.reset-password-container h1 {
  margin-bottom: var(--spacing-xs);
  text-align: center;
}

.lead {
  text-align: center;
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-xl);
}

.reset-password-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.error-message {
  color: var(--color-error);
  font-size: var(--font-size-sm);
  margin-bottom: var(--spacing-md);
}

.success-message {
  text-align: center;
  color: var(--color-success);
  margin: var(--spacing-xl) 0;
}

.success-message i {
  font-size: var(--font-size-3xl);
  margin-bottom: var(--spacing-md);
}

.success-message p {
  color: var(--color-text);
  margin-bottom: var(--spacing-sm);
}

.auth-footer {
  margin-top: var(--spacing-xl);
  text-align: center;
}

.auth-footer p {
  color: var(--color-text-secondary);
}

.auth-footer a {
  color: var(--color-primary);
  text-decoration: none;
  margin-left: var(--spacing-xs);
}

.auth-footer a:hover {
  text-decoration: underline;
}
</style> 