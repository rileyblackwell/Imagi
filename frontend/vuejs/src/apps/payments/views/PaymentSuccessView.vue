<template>
  <PaymentLayout>
    <div class="payment-success-view">
      <div class="max-w-md mx-auto backdrop-blur-sm bg-white/10 border border-white/20 shadow-xl rounded-2xl p-8 mt-12 text-white">
        <div class="text-center mb-6">
          <div class="success-icon mb-4 relative">
            <div class="absolute inset-0 bg-green-500/20 rounded-full blur-xl transform scale-150 animate-pulse-slow"></div>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-20 w-20 mx-auto text-green-400 relative z-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h1 class="text-3xl font-bold text-white bg-gradient-to-r from-green-300 to-green-500 bg-clip-text text-transparent mb-2">Payment Successful!</h1>
          <p class="text-white/80 mt-2">Thank you for your payment.</p>
        </div>
        
        <div v-if="isLoading" class="flex justify-center p-4">
          <svg class="animate-spin h-10 w-10 text-primary-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>
        
        <div v-else-if="paymentProcessed" class="text-center">
          <div class="mb-8 p-6 bg-green-500/10 backdrop-blur-sm border border-green-400/30 rounded-xl">
            <p class="text-green-300 font-medium">
              We've added <span class="font-bold text-xl">{{ creditsAdded }}</span> credits to your account!
            </p>
            <p class="text-green-400 mt-3">Your new balance: <span class="font-bold text-xl">{{ balance }}</span></p>
          </div>
        </div>
        
        <div v-else-if="error" class="mb-8 p-6 bg-red-500/10 backdrop-blur-sm border border-red-400/30 rounded-xl text-red-300 text-center">
          {{ error }}
        </div>
        
        <div class="flex justify-center mt-8">
          <router-link 
            to="/payments" 
            class="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-xl shadow-lg shadow-primary-500/20 text-white bg-gradient-to-r from-primary-600 to-primary-500 hover:from-primary-500 hover:to-primary-400 transition-all duration-300 transform hover:scale-105 hover:shadow-lg"
          >
            Back to Payments
          </router-link>
        </div>
      </div>
    </div>
  </PaymentLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { usePaymentStore } from '../stores/payments'
import { usePaymentsStore } from '../stores'
import PaymentLayout from '../layouts/PaymentLayout.vue'

const paymentStore = usePaymentStore()
const paymentsStore = usePaymentsStore() // For balance tracking
const route = useRoute()

// State
const isLoading = ref(true)
const error = ref('')
const paymentProcessed = ref(false)
const creditsAdded = ref(0)
const balance = ref(0)

// On mount, process the session if there's a session_id in the URL
onMounted(async () => {
  try {
    // Get session_id from URL
    const sessionId = route.query.session_id as string
    
    if (!sessionId) {
      isLoading.value = false
      return
    }
    
    // Get session status from API
    const status = await paymentStore.getSessionStatus(sessionId)
    
    if (status.status === 'complete') {
      paymentProcessed.value = true
      creditsAdded.value = status.credits_added || 0
      
      // Initialize payment system with auto-refresh for accurate balance tracking
      await paymentsStore.initializePayments();
      
      // Set the balance using the current value from the payments store
      balance.value = paymentsStore.balance ?? 0;
    } else {
      error.value = 'Your payment is still being processed. Please check back later.'
    }
  } catch (err: any) {
    console.error('Error processing payment success:', err)
    error.value = err.message || 'There was an error processing your payment. Please contact support.'
  } finally {
    isLoading.value = false
  }
})
</script>

<style scoped>
.payment-success-view {
  padding: 1.5rem;
}

/* Pulsing animation for highlights */
@keyframes pulse-slow {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 0.8; }
}

.animate-pulse-slow {
  animation: pulse-slow 3s ease-in-out infinite;
}
</style> 