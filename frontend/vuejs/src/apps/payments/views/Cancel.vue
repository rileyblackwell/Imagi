<template>
  <div class="max-w-3xl mx-auto px-4 py-8">
    <div class="bg-dark-800 rounded-lg shadow-xl overflow-hidden border border-dark-700">
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
          <button
            @click="tryAgain"
            class="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
          >
            Try Again
          </button>
          <button
            @click="goToDashboard"
            class="px-6 py-3 bg-dark-900 text-white rounded-lg hover:bg-dark-700 focus:outline-none focus:ring-2 focus:ring-dark-700 focus:ring-offset-2"
          >
            Return to Dashboard
          </button>
        </div>

        <!-- Help Text -->
        <p class="mt-8 text-sm text-gray-500">
          If you experienced any issues, please contact our support team at
          <a href="mailto:support@imagi.ai" class="text-primary-500 hover:text-primary-400">support@imagi.ai</a>
        </p>
      </div>
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
      // Get the stored amount if available
      const storedAmount = localStorage.getItem('payment_amount')
      if (storedAmount) {
        router.push({ 
          name: 'payments-checkout',
          query: { amount: storedAmount }
        })
      } else {
        router.push({ name: 'payments-credits' })
      }
    }

    const goToDashboard = () => {
      // Clear stored amount
      localStorage.removeItem('payment_amount')
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