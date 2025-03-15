<template>
  <PaymentLayout>
    <div class="payment-cancel-view">
      <div class="max-w-md mx-auto bg-white shadow rounded-lg p-8 mt-12">
        <div class="text-center mb-6">
          <div class="cancel-icon mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h1 class="text-2xl font-bold text-gray-800">Payment Cancelled</h1>
          <p class="text-gray-600 mt-2">
            Your payment has been cancelled and you have not been charged.
          </p>
        </div>
        
        <div class="text-center mb-8">
          <p class="text-gray-700">
            If you encountered any issues or have questions about our payment process, please contact our support team.
          </p>
        </div>
        
        <div class="flex flex-col space-y-4 justify-center">
          <router-link 
            to="/payments" 
            class="inline-flex items-center justify-center px-5 py-2 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Try Again
          </router-link>
          
          <router-link 
            to="/" 
            class="inline-flex items-center justify-center px-5 py-2 border border-gray-300 text-base font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
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
</style> 