<template>
  <PaymentLayout>
    <div class="payment-cancel-view min-h-screen relative overflow-hidden transition-colors duration-500">
      <!-- Atmosphere: one soft apricot wash over the porcelain canvas -->
      <div class="absolute inset-0 pointer-events-none" aria-hidden="true">
        <div class="cancel-glow-warm absolute -top-24 left-1/2 -translate-x-1/2 w-[760px] h-[440px]"></div>
      </div>

      <!-- Content Container -->
      <div class="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <!-- Cancel Section -->
        <div class="max-w-2xl mx-auto animate-fade-in-up">
          <!-- Cancel Header -->
          <div class="text-center mb-12">
            <div class="w-20 h-20 rounded-full bg-orange-100 dark:bg-orange-400/[0.16] ring-1 ring-orange-200/80 dark:ring-orange-400/30 flex items-center justify-center mx-auto mb-6">
              <i class="fas fa-exclamation-triangle text-3xl text-orange-600 dark:text-orange-300"></i>
            </div>
            <h1 class="font-display text-4xl sm:text-5xl font-semibold text-blue-950 dark:text-white mb-4 tracking-[-0.02em] leading-[1.05] text-balance">Payment Cancelled</h1>
            <p class="text-xl text-blue-950/65 dark:text-blue-100/65 leading-relaxed">
              Your payment has been cancelled and you have not been charged.
            </p>
          </div>

          <!-- Info Card -->
          <div class="crisp-card rounded-2xl bg-white/85 dark:bg-white/[0.045] border border-blue-950/[0.08] dark:border-white/[0.1] backdrop-blur-sm p-8 mb-12">
            <p class="text-blue-950/65 dark:text-blue-100/65 text-center leading-relaxed">
              If you encountered any issues or have questions about our payment process, please contact our support team.
            </p>
          </div>

          <!-- Action Buttons -->
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <router-link
              to="/payments/pricing"
              class="inline-flex items-center justify-center gap-2 px-8 py-4 rounded-full font-medium bg-blue-950 text-[#fdf9f2] hover:bg-blue-900 dark:bg-[#f3ede2] dark:text-blue-950 dark:hover:bg-white transition-all duration-200 hover:-translate-y-0.5 active:translate-y-0 shadow-[0_1px_2px_rgba(23,37,84,0.25),0_8px_20px_-6px_rgba(23,37,84,0.35),inset_0_1px_0_rgba(255,255,255,0.12)] hover:shadow-[0_2px_3px_rgba(23,37,84,0.22),0_14px_28px_-8px_rgba(23,37,84,0.4),inset_0_1px_0_rgba(255,255,255,0.12)] dark:shadow-[0_1px_2px_rgba(0,0,0,0.5),0_10px_24px_-8px_rgba(0,0,0,0.55)] dark:hover:shadow-[0_2px_3px_rgba(0,0,0,0.5),0_14px_30px_-8px_rgba(0,0,0,0.6)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0c0c0e]"
            >
              <i class="fas fa-redo"></i>
              <span>Try Again</span>
            </router-link>

            <router-link
              to="/"
              class="inline-flex items-center justify-center gap-2 px-8 py-4 rounded-full font-medium border border-blue-950/[0.14] text-blue-950/80 hover:text-blue-950 hover:border-blue-950/30 hover:bg-blue-950/[0.03] dark:border-white/[0.16] dark:text-blue-100/80 dark:hover:text-white dark:hover:border-white/30 dark:hover:bg-white/[0.06] transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0c0c0e]"
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

@media (prefers-reduced-motion: reduce) {
  .animate-fade-in-up {
    animation: none;
  }
}

/* Soft warm wash echoing the home hero's apricot glow */
.cancel-glow-warm {
  background: radial-gradient(closest-side, rgba(251, 146, 60, 0.11), rgba(251, 146, 60, 0.03) 55%, transparent 75%);
  filter: blur(48px);
}

.dark .cancel-glow-warm {
  background: radial-gradient(closest-side, rgba(251, 146, 60, 0.06), rgba(251, 146, 60, 0.02) 55%, transparent 75%);
}

/* Crisp, sharply-defined cards: hairline edge + tight layered shadow */
.crisp-card {
  box-shadow:
    0 0 0 1px rgba(15, 23, 42, 0.03),
    0 1px 2px rgba(15, 23, 42, 0.06),
    0 4px 10px -2px rgba(15, 23, 42, 0.07),
    0 12px 28px -10px rgba(15, 23, 42, 0.10);
}

.dark .crisp-card {
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.04),
    0 1px 2px rgba(0, 0, 0, 0.5),
    0 4px 10px -2px rgba(0, 0, 0, 0.45),
    0 12px 28px -10px rgba(0, 0, 0, 0.55);
}

/* Smooth scroll behavior */
:deep(html) {
  scroll-behavior: smooth;
}
</style> 