<template>
  <PaymentLayout>
    <div class="payment-success-view min-h-screen bg-white dark:bg-[#0a0a0a] relative overflow-hidden transition-colors duration-500">
      <!-- Minimal background with subtle texture - matching checkout page -->
      <div class="fixed inset-0 pointer-events-none">
        <!-- Subtle gradient - very minimal -->
        <div class="absolute inset-0 bg-gradient-to-b from-gray-50/50 via-white to-white dark:from-[#0a0a0a] dark:via-[#0a0a0a] dark:to-[#0a0a0a] transition-colors duration-500"></div>
        
        <!-- Very subtle grid pattern for texture -->
        <div class="absolute inset-0 opacity-[0.015] dark:opacity-[0.02]" 
             style="background-image: linear-gradient(rgba(128,128,128,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(128,128,128,0.1) 1px, transparent 1px); background-size: 64px 64px;"></div>
      </div>

      <!-- Content Container -->
      <div class="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <!-- Success Section -->
        <div class="max-w-2xl mx-auto">
          <div v-if="isLoading" class="animate-fade-in-up">
            <div class="rounded-2xl bg-white/50 dark:bg-white/[0.03] border border-gray-200 dark:border-white/[0.08] backdrop-blur-sm p-12 text-center">
              <div class="flex justify-center">
                <svg class="animate-spin h-12 w-12 text-gray-900 dark:text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </div>
              <p class="mt-4 text-gray-600 dark:text-gray-400">Processing your payment...</p>
            </div>
          </div>
          
          <div v-else-if="paymentProcessed" class="animate-fade-in-up space-y-6">
            <!-- Success Header -->
            <div class="text-center mb-12">
              <div class="w-20 h-20 rounded-full bg-emerald-100 dark:bg-emerald-900/20 flex items-center justify-center mx-auto mb-6">
                <i class="fas fa-check text-3xl text-emerald-600 dark:text-emerald-400"></i>
              </div>
              <h1 class="text-4xl sm:text-5xl font-semibold text-gray-900 dark:text-white mb-4 tracking-tight">Payment Successful!</h1>
              <p class="text-xl text-gray-500 dark:text-white/60">Thank you for your payment.</p>
            </div>
            
            <!-- Success Details Card -->
            <div class="rounded-2xl bg-emerald-50 dark:bg-emerald-900/10 border border-emerald-200 dark:border-emerald-800/30 p-8 text-center">
              <p class="text-lg text-emerald-900 dark:text-emerald-100 mb-3">
                We've added <span class="font-semibold text-2xl">{{ creditsAdded }}</span> credits to your account!
              </p>
              <div class="mt-6 pt-6 border-t border-emerald-200 dark:border-emerald-800/30">
                <p class="text-emerald-700 dark:text-emerald-300/80">Your new balance</p>
                <p class="text-3xl font-semibold text-emerald-900 dark:text-emerald-100 mt-2">${{ balance.toLocaleString() }}</p>
              </div>
            </div>
            
            <!-- Action Buttons -->
            <div class="flex justify-center mt-12">
              <router-link 
                to="/payments/checkout" 
                class="inline-flex items-center gap-2 px-8 py-4 rounded-xl bg-gray-900 dark:bg-white text-white dark:text-gray-900 font-medium transition-all duration-200 hover:scale-105 hover:shadow-lg"
              >
                <i class="fas fa-arrow-left"></i>
                <span>Back to Payments</span>
              </router-link>
            </div>
          </div>
          
          <div v-else-if="error" class="animate-fade-in-up">
            <!-- Error Header -->
            <div class="text-center mb-12">
              <div class="w-20 h-20 rounded-full bg-red-100 dark:bg-red-900/20 flex items-center justify-center mx-auto mb-6">
                <i class="fas fa-exclamation-triangle text-3xl text-red-600 dark:text-red-400"></i>
              </div>
              <h1 class="text-4xl sm:text-5xl font-semibold text-gray-900 dark:text-white mb-4 tracking-tight">Payment Processing Error</h1>
            </div>
            
            <!-- Error Details Card -->
            <div class="rounded-2xl bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800/30 p-8">
              <p class="text-red-700 dark:text-red-300/80 text-center">{{ error }}</p>
            </div>
            
            <!-- Action Buttons -->
            <div class="flex justify-center mt-12">
              <router-link 
                to="/payments/checkout" 
                class="inline-flex items-center gap-2 px-8 py-4 rounded-xl bg-gray-900 dark:bg-white text-white dark:text-gray-900 font-medium transition-all duration-200 hover:scale-105 hover:shadow-lg"
              >
                <i class="fas fa-arrow-left"></i>
                <span>Back to Payments</span>
              </router-link>
            </div>
          </div>
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

const paymentStore = usePaymentStore() // Single store instance
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
      await paymentStore.initializePayments();
      
      // Set the balance using the current value from the payments store
      balance.value = paymentStore.balance ?? 0;
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
/* Clean scrollbar - matching checkout page */
:deep(::-webkit-scrollbar) {
  width: 8px;
}

:deep(::-webkit-scrollbar-track) {
  background: transparent;
}

:deep(::-webkit-scrollbar-thumb) {
  background: rgba(0, 0, 0, 0.12);
  border-radius: 4px;
  transition: background 0.2s ease;
}

:deep(::-webkit-scrollbar-thumb:hover) {
  background: rgba(0, 0, 0, 0.2);
}

:root.dark :deep(::-webkit-scrollbar-thumb) {
  background: rgba(255, 255, 255, 0.12);
}

:root.dark :deep(::-webkit-scrollbar-thumb:hover) {
  background: rgba(255, 255, 255, 0.2);
}

/* Simple fade-in-up animation */
@keyframes fade-in-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in-up {
  animation: fade-in-up 0.6s ease-out forwards;
}

/* Smooth scroll behavior */
:deep(html) {
  scroll-behavior: smooth;
}
</style> 