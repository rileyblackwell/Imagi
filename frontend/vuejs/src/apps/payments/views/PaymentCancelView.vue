<template>
  <PaymentLayout>
    <div class="payment-cancel-view">
      <div class="max-w-md mx-auto backdrop-blur-sm bg-white/10 border border-white/20 shadow-xl rounded-2xl p-8 mt-12 text-white">
        <div class="text-center mb-6">
          <div class="cancel-icon mb-4 relative">
            <div class="absolute inset-0 bg-red-500/20 rounded-full blur-xl transform scale-150 animate-pulse-slow"></div>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-20 w-20 mx-auto text-red-400 relative z-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h1 class="text-3xl font-bold text-white bg-gradient-to-r from-red-300 to-red-500 bg-clip-text text-transparent mb-2">Payment Cancelled</h1>
          <p class="text-white/80 mt-2">
            Your payment has been cancelled and you have not been charged.
          </p>
        </div>
        
        <div class="text-center mb-8 p-6 bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl">
          <p class="text-white/80">
            If you encountered any issues or have questions about our payment process, please contact our support team.
          </p>
        </div>
        
        <div class="flex flex-col space-y-4 justify-center">
          <router-link 
            to="/payments" 
            class="inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-xl shadow-lg shadow-primary-500/20 text-white bg-gradient-to-r from-primary-600 to-primary-500 hover:from-primary-500 hover:to-primary-400 transition-all duration-300 transform hover:scale-105"
          >
            Try Again
          </router-link>
          
          <router-link 
            to="/" 
            class="inline-flex items-center justify-center px-6 py-3 border border-white/20 text-base font-medium rounded-xl shadow-sm text-white/90 bg-white/5 backdrop-blur-sm hover:bg-white/10 transition-all duration-300 transform hover:scale-105"
          >
            Back to Home
          </router-link>
        </div>
      </div>
    </div>
  </PaymentLayout>
</template>

<script setup lang="ts">
import PaymentLayout from '../layouts/PaymentLayout.vue'
// No special logic needed for the cancel page
</script>

<style scoped>
.payment-cancel-view {
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