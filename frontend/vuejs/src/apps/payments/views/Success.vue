<template>
  <div class="success-container">
    <div class="max-w-3xl mx-auto px-4 py-8">
      <base-card>
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
          <div class="bg-dark-800 rounded-lg p-6 mb-8 max-w-md mx-auto">
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
            <base-button @click="goToBuilder" variant="primary">
              Start Building
            </base-button>
            <base-button @click="goToDashboard" variant="secondary">
              View Dashboard
            </base-button>
          </div>
        </div>
      </base-card>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

export default {
  name: 'PaymentSuccess',
  setup() {
    const router = useRouter()
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
          const { data } = await axios.get(`/api/payments/get-balance/`)
          newBalance.value = data.balance
          
          // Calculate amount and credits from URL params or payment intent
          // This assumes the payment was successful and balance was updated
          amount.value = parseFloat(urlParams.get('amount') || 0)
          credits.value = Math.floor(amount.value * 10) // $1 = 10 credits
        } else {
          router.push({ name: 'dashboard' })
        }
      } catch (error) {
        console.error('Failed to fetch payment details:', error)
        router.push({ name: 'dashboard' })
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
.success-container {
  min-height: calc(100vh - 64px);
}

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