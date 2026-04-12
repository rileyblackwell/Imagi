<template>
  <PaymentLayout>
    <div class="payment-cancel-view min-h-screen bg-white dark:bg-[#0a0a0a] relative overflow-hidden transition-colors duration-500">
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
        <!-- Cancel Section -->
        <div class="max-w-2xl mx-auto animate-fade-in-up">
          <!-- Cancel Header -->
          <div class="text-center mb-12">
            <div class="w-20 h-20 rounded-full bg-orange-100 dark:bg-orange-900/20 flex items-center justify-center mx-auto mb-6">
              <i class="fas fa-exclamation-triangle text-3xl text-orange-600 dark:text-orange-400"></i>
            </div>
            <h1 class="text-4xl sm:text-5xl font-semibold text-gray-900 dark:text-white mb-4 tracking-tight">Payment Cancelled</h1>
            <p class="text-xl text-gray-500 dark:text-white/60">
              Your payment has been cancelled and you have not been charged.
            </p>
          </div>
          
          <!-- Info Card -->
          <div class="rounded-2xl bg-gray-50 dark:bg-white/[0.03] border border-gray-200 dark:border-white/[0.08] p-8 mb-12">
            <p class="text-gray-600 dark:text-gray-400 text-center">
              If you encountered any issues or have questions about our payment process, please contact our support team.
            </p>
          </div>
          
          <!-- Action Buttons -->
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <router-link 
              to="/payments/checkout" 
              class="inline-flex items-center justify-center gap-2 px-8 py-4 rounded-xl bg-gray-900 dark:bg-white text-white dark:text-gray-900 font-medium transition-all duration-200 hover:scale-105 hover:shadow-lg"
            >
              <i class="fas fa-redo"></i>
              <span>Try Again</span>
            </router-link>
            
            <router-link 
              to="/" 
              class="inline-flex items-center justify-center gap-2 px-8 py-4 rounded-xl bg-white/50 dark:bg-white/[0.03] border border-gray-200 dark:border-white/[0.08] text-gray-900 dark:text-white font-medium transition-all duration-200 hover:scale-105 hover:shadow-lg"
            >
              <i class="fas fa-home"></i>
              <span>Back to Home</span>
            </router-link>
          </div>
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