<template>
  <div class="max-w-3xl mx-auto px-4 py-8">
    <div class="bg-dark-800 rounded-lg shadow-xl overflow-hidden border border-dark-700">
      <div class="text-center py-8">
        <!-- Success Animation -->
        <div class="success-animation mb-6">
          <svg class="checkmark" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 52 52">
            <circle class="checkmark-circle" cx="26" cy="26" r="25" fill="none"/>
            <path class="checkmark-check" fill="none" d="M14.1 27.2l7.1 7.2 16.7-16.8"/>
          </svg>
        </div>

        <h1 class="text-3xl font-bold text-white mb-4">Payment Successful!</h1>
        <p class="text-gray-400 mb-8">Your payment has been processed and credits have been added to your account.</p>

        <!-- Payment Details -->
        <div class="bg-dark-900 rounded-lg p-6 mb-8 max-w-md mx-auto">
          <div class="space-y-4">
            <div class="flex justify-between items-center">
              <span class="text-gray-400">Amount Added:</span>
              <span class="text-xl font-semibold text-white">${{ amount }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-400">Credits Added:</span>
              <span class="text-xl font-semibold text-primary-500">{{ credits }} credits</span>
            </div>
            <div class="border-t border-dark-700 pt-4">
              <div class="flex justify-between items-center">
                <span class="text-gray-400">New Balance:</span>
                <span class="text-2xl font-bold text-white">${{ newBalance }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex flex-col sm:flex-row gap-4 justify-center">
          <button
            @click="goToBuilder"
            class="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
          >
            Start Building
          </button>
          <button
            @click="goToDashboard"
            class="px-6 py-3 bg-dark-900 text-white rounded-lg hover:bg-dark-700 focus:outline-none focus:ring-2 focus:ring-dark-700 focus:ring-offset-2"
          >
            View Dashboard
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import PaymentService from '../services/payment_service'
import { useToast } from '../composables/useToast'

export default {
  name: 'PaymentSuccess',
  setup() {
    const router = useRouter()
    const paymentService = new PaymentService()
    const toast = useToast()
    const amount = ref(0)
    const credits = ref(0)
    const newBalance = ref(0)

    const goToBuilder = () => {
      router.push({ name: 'builder' })
    }

    const goToDashboard = () => {
      router.push({ name: 'dashboard' })
    }

    onMounted(async () => {
      try {
        // Get payment details from URL params
        const urlParams = new URLSearchParams(window.location.search)
        const paymentIntent = urlParams.get('payment_intent')
        
        if (paymentIntent) {
          // Verify the payment
          await paymentService.verifyPayment(paymentIntent)
          
          // Get updated balance
          const { balance } = await paymentService.getBalance()
          newBalance.value = balance
          
          // Calculate amount and credits from URL params or payment intent
          amount.value = parseFloat(urlParams.get('amount') || 0)
          credits.value = Math.floor(amount.value * 10) // $1 = 10 credits
          
          // Clear stored amount
          localStorage.removeItem('payment_amount')
        } else {
          toast.error('Invalid payment session')
          router.push({ name: 'payments-credits' })
        }
      } catch (error) {
        console.error('Failed to process payment success:', error)
        toast.error('Failed to verify payment')
        router.push({ name: 'payments-credits' })
      }
    })

    return {
      amount,
      credits,
      newBalance,
      goToBuilder,
      goToDashboard
    }
  }
}
</script>

<style scoped>
.success-animation {
  position: relative;
  width: 80px;
  height: 80px;
  margin: 0 auto;
}

.checkmark {
  width: 80px;
  height: 80px;
}

.checkmark-circle {
  stroke: #00ffc6;
  stroke-width: 2;
  stroke-dasharray: 166;
  stroke-dashoffset: 166;
  animation: stroke 0.6s cubic-bezier(0.65, 0, 0.45, 1) forwards;
}

.checkmark-check {
  stroke: #00ffc6;
  stroke-width: 2;
  stroke-dasharray: 48;
  stroke-dashoffset: 48;
  animation: stroke 0.3s cubic-bezier(0.65, 0, 0.45, 1) 0.8s forwards;
}

@keyframes stroke {
  100% {
    stroke-dashoffset: 0;
  }
}
</style> 