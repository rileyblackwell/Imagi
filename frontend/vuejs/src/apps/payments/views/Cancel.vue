<template>
  <div class="cancel-container">
    <div class="max-w-3xl mx-auto px-4 py-8">
      <base-card>
        <div class="text-center py-8">
          <!-- Cancel Icon -->
          <div class="cancel-icon mb-6">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-20 w-20 mx-auto text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>

          <h1 class="text-3xl font-bold text-white mb-4">Payment Cancelled</h1>
          <p class="text-gray-400 mb-8">Your payment was cancelled and no charges have been made to your account.</p>

          <!-- Actions -->
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <base-button @click="tryAgain" variant="primary">
              Try Again
            </base-button>
            <base-button @click="goToDashboard" variant="secondary">
              Return to Dashboard
            </base-button>
          </div>

          <!-- Help Text -->
          <p class="mt-8 text-sm text-gray-500">
            If you experienced any issues, please contact our support team at
            <a href="mailto:support@imagi.ai" class="text-primary-500 hover:text-primary-400">support@imagi.ai</a>
          </p>
        </div>
      </base-card>
    </div>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'

export default {
  name: 'PaymentCancel',
  setup() {
    const router = useRouter()

    const tryAgain = () => {
      router.push({ name: 'checkout' })
    }

    const goToDashboard = () => {
      router.push({ name: 'dashboard' })
    }

    return {
      tryAgain,
      goToDashboard
    }
  }
}
</script>

<style scoped>
.cancel-container {
  min-height: calc(100vh - 64px);
}

.cancel-icon {
  animation: shake 0.5s cubic-bezier(.36,.07,.19,.97) both;
}

@keyframes shake {
  10%, 90% {
    transform: translate3d(-1px, 0, 0);
  }
  20%, 80% {
    transform: translate3d(2px, 0, 0);
  }
  30%, 50%, 70% {
    transform: translate3d(-4px, 0, 0);
  }
  40%, 60% {
    transform: translate3d(4px, 0, 0);
  }
}
</style> 