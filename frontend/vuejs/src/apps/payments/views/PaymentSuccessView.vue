<template>
  <PaymentLayout>
    <div class="payment-success-view">
      <div class="max-w-md mx-auto bg-white shadow rounded-lg p-8 mt-12">
        <div class="text-center mb-6">
          <div class="success-icon mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h1 class="text-2xl font-bold text-gray-800">Payment Successful!</h1>
          <p class="text-gray-600 mt-2">Thank you for your payment.</p>
        </div>
        
        <div v-if="isLoading" class="flex justify-center p-4">
          <svg class="animate-spin h-8 w-8 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>
        
        <div v-else-if="paymentProcessed" class="text-center">
          <div class="mb-4 p-4 bg-green-50 rounded-lg">
            <p class="text-green-800">
              We've added <span class="font-bold">{{ creditsAdded }}</span> credits to your account!
            </p>
            <p class="text-green-700 mt-1">Your new balance: <span class="font-bold">{{ balance }}</span></p>
          </div>
        </div>
        
        <div v-else-if="error" class="mb-4 p-4 bg-red-50 rounded-lg text-red-600 text-center">
          {{ error }}
        </div>
        
        <div class="flex justify-center mt-6">
          <router-link 
            to="/payments" 
            class="inline-flex items-center px-5 py-2 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
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
import PaymentLayout from '../layouts/PaymentLayout.vue'

const store = usePaymentStore()
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
    const status = await store.getSessionStatus(sessionId)
    
    if (status.status === 'complete') {
      paymentProcessed.value = true
      creditsAdded.value = status.credits_added || 0
      
      // Fetch the latest balance
      await store.fetchBalance()
      balance.value = store.balance || 0
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
</style> 