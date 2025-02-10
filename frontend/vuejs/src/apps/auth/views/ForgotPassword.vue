<template>
  <div class="min-h-screen flex flex-col items-center justify-center bg-dark-900 px-4 sm:px-6 lg:px-8">
    <!-- Logo/Brand Section -->
    <div class="mb-8">
      <i class="fas fa-key text-primary-500 text-4xl"></i>
    </div>

    <div class="w-full max-w-md">
      <!-- Main Card -->
      <div class="bg-dark-800 shadow-xl rounded-lg px-8 pt-8 pb-10">
        <!-- Header -->
        <div class="text-center mb-8">
          <h2 class="text-2xl font-bold text-white mb-2">Forgot Your Password?</h2>
          <p class="text-gray-400 text-sm">
            No worries! Enter your email below and we'll send you instructions to reset your password.
          </p>
        </div>

        <form v-if="!success" @submit.prevent="handleSubmit" class="space-y-6">
          <!-- Email Input -->
          <div class="space-y-1">
            <label for="email" class="block text-sm font-medium text-gray-300">Email Address</label>
            <EmailInput
              v-model="email"
              id="email"
              placeholder="you@example.com"
              :disabled="loading"
              required
            />
          </div>

          <!-- Error Message -->
          <div v-if="error" 
               class="p-4 rounded-md bg-red-900/30 border border-red-800"
          >
            <div class="flex">
              <i class="fas fa-exclamation-circle text-red-400 mt-1"></i>
              <div class="ml-3">
                <p class="text-sm text-red-400">{{ error }}</p>
              </div>
            </div>
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="!isValidEmail || loading"
            class="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg
                   text-sm font-medium text-white bg-primary-600 hover:bg-primary-700
                   focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500
                   disabled:opacity-50 disabled:cursor-not-allowed transition-colors
                   relative"
          >
            <span v-if="loading" class="absolute left-4 top-1/2 transform -translate-y-1/2">
              <i class="fas fa-circle-notch fa-spin"></i>
            </span>
            <span :class="{ 'ml-6': loading }">
              {{ loading ? 'Sending Reset Link...' : 'Send Reset Link' }}
            </span>
          </button>
        </form>

        <!-- Success State -->
        <div v-else class="text-center space-y-6">
          <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-900/30 mb-4">
            <i class="fas fa-envelope-open-text text-green-500 text-3xl"></i>
          </div>
          <div class="space-y-3">
            <h3 class="text-xl font-semibold text-white">Check Your Email</h3>
            <div class="space-y-2">
              <p class="text-gray-400 text-sm">
                If an account exists with the email you provided, you will receive password reset instructions shortly.
              </p>
              <p class="text-gray-400 text-sm">
                Please check your spam folder if you don't see the email in your inbox.
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer Links -->
      <div class="mt-6 text-center space-y-4">
        <div class="flex items-center justify-center space-x-2 text-sm">
          <router-link
            to="/auth/login"
            class="text-primary-500 hover:text-primary-400 flex items-center transition-colors"
          >
            <i class="fas fa-arrow-left mr-2"></i>
            Back to Login
          </router-link>
        </div>
        <p class="text-gray-500 text-xs">
          Need help? <a href="#" class="text-primary-500 hover:text-primary-400">Contact Support</a>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '@/apps/auth/store'
import { EmailInput } from '@/apps/auth/components'

// ...existing code...
</script>

<style scoped>
/* Transitions */
.transition-colors {
  transition: all 200ms ease-in-out;
}

/* Custom focus styles */
input:focus {
  border-color: transparent;
  box-shadow: 0 0 0 2px var(--color-primary-500);
}

/* Button hover effect */
button:not(:disabled):hover {
  transform: scale(1.02);
  transition: transform 200ms;
}

/* Success icon animation */
@keyframes fadeInScale {
  0% {
    opacity: 0;
    transform: scale(0.9);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

.success-icon {
  animation: fadeInScale 0.3s ease-out forwards;
}
</style>