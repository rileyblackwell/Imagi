<template>
  <PaymentLayout>
    <div class="editorial payment-cancel-view min-h-screen relative">
      <!-- Atmosphere: one soft apricot wash over the porcelain canvas -->

      <!-- Content Container -->
      <div class="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <!-- Cancel Section -->
        <div class="max-w-2xl mx-auto animate-fade-in-up">
          <!-- Cancel Header -->
          <div class="text-center mb-12">
            <div class="w-20 h-20 rounded-full bg-orange-100 dark:bg-orange-400/[0.16] ring-1 ring-orange-200/80 dark:ring-orange-400/30 flex items-center justify-center mx-auto mb-6">
              <i class="fas fa-exclamation-triangle text-3xl text-orange-600 dark:text-orange-300"></i>
            </div>
            <h1 class="display text-4xl sm:text-5xl mb-4">Payment Cancelled</h1>
            <p class="text-xl text-[color:var(--ink-55)] leading-relaxed">
              Your payment has been cancelled and you have not been charged.
            </p>
          </div>

          <!-- Info Card -->
          <div class="panel p-8 mb-12">
            <p class="text-[color:var(--ink-55)] text-center leading-relaxed">
              If you encountered any issues or have questions about our payment process, please contact our support team.
            </p>
          </div>

          <!-- Action Buttons -->
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <router-link
              to="/payments/pricing"
              class="btn-primary"
            >
              <i class="fas fa-redo"></i>
              <span>Try Again</span>
            </router-link>

            <router-link
              to="/"
              class="btn-outline"
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
/* A hairline panel, matching the auth form and the rest of the public pages —
   no floating card, no tinted fill. */
.panel {
  border: 1px solid var(--rule);
  border-radius: 1rem;
  background: var(--paper-raised);
}
</style>
