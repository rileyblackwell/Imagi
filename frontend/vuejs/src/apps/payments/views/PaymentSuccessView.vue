<template>
  <PaymentLayout>
    <div class="payment-success-view min-h-screen relative overflow-hidden transition-colors duration-500">
      <!-- Atmosphere: one soft apricot wash over the porcelain canvas -->
      <div class="absolute inset-0 pointer-events-none" aria-hidden="true">
        <div class="success-glow-warm absolute -top-24 left-1/2 -translate-x-1/2 w-[760px] h-[440px]"></div>
      </div>

      <!-- Content Container -->
      <div class="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <!-- Success Section -->
        <div class="max-w-2xl mx-auto">
          <div v-if="isLoading" class="animate-fade-in-up">
            <div class="crisp-card rounded-2xl bg-white/85 dark:bg-white/[0.045] border border-blue-950/[0.08] dark:border-white/[0.1] backdrop-blur-sm p-12 text-center">
              <div class="flex justify-center">
                <svg class="animate-spin h-12 w-12 text-blue-950 dark:text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </div>
              <p class="mt-4 text-blue-950/65 dark:text-blue-100/65">Processing your payment...</p>
            </div>
          </div>
          
          <div v-else-if="paymentProcessed" class="animate-fade-in-up space-y-6">
            <!-- Success Header -->
            <div class="text-center mb-12">
              <div class="w-20 h-20 rounded-full bg-emerald-100 dark:bg-emerald-400/[0.14] ring-1 ring-emerald-200/80 dark:ring-emerald-300/[0.18] flex items-center justify-center mx-auto mb-6">
                <i class="fas fa-check text-3xl text-emerald-600 dark:text-emerald-300"></i>
              </div>
              <h1 class="font-display text-4xl sm:text-5xl font-semibold text-blue-950 dark:text-white mb-4 tracking-[-0.02em] leading-[1.05] text-balance">
                {{ isSubscription ? 'Subscription Activated!' : 'Payment Successful!' }}
              </h1>
              <p class="text-xl text-blue-950/65 dark:text-blue-100/65 leading-relaxed">
                {{ isSubscription ? 'Your subscription is now active. Welcome aboard!' : 'Thank you for your payment.' }}
              </p>
            </div>

            <!-- Success Details Card -->
            <div class="crisp-card rounded-2xl bg-emerald-50/80 dark:bg-emerald-400/[0.07] border border-emerald-200/70 dark:border-emerald-300/[0.18] backdrop-blur-sm p-8 text-center">
              <p v-if="isSubscription" class="text-lg text-emerald-900 dark:text-emerald-100">
                Your plan is now active. You can manage your subscription at any time.
              </p>
              <p v-else class="text-lg text-emerald-900 dark:text-emerald-100 mb-3">
                We've added <span class="font-semibold text-2xl">{{ creditsAdded }}</span> credits to your account!
              </p>
              <div v-if="!isSubscription" class="mt-6 pt-6 border-t border-emerald-200/70 dark:border-emerald-300/[0.18]">
                <p class="text-emerald-700 dark:text-emerald-300/80">Your new balance</p>
                <p class="font-display text-3xl font-semibold tabular-nums text-emerald-900 dark:text-emerald-100 mt-2">${{ balance.toLocaleString() }}</p>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="flex flex-col sm:flex-row items-center justify-center gap-4 mt-12">
              <button
                v-if="isSubscription"
                @click="manageSubscription"
                :disabled="portalLoading"
                class="inline-flex items-center justify-center gap-2 px-8 py-4 rounded-full font-medium bg-blue-950 text-[#fdf9f2] hover:bg-blue-900 dark:bg-[#f3ede2] dark:text-blue-950 dark:hover:bg-white transition-all duration-200 hover:-translate-y-0.5 active:translate-y-0 shadow-[0_1px_2px_rgba(23,37,84,0.25),0_8px_20px_-6px_rgba(23,37,84,0.35),inset_0_1px_0_rgba(255,255,255,0.12)] hover:shadow-[0_2px_3px_rgba(23,37,84,0.22),0_14px_28px_-8px_rgba(23,37,84,0.4),inset_0_1px_0_rgba(255,255,255,0.12)] dark:shadow-[0_1px_2px_rgba(0,0,0,0.5),0_10px_24px_-8px_rgba(0,0,0,0.55)] dark:hover:shadow-[0_2px_3px_rgba(0,0,0,0.5),0_14px_30px_-8px_rgba(0,0,0,0.6)] disabled:opacity-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0c0c0e]"
              >
                <i class="fas fa-cog"></i>
                <span>{{ portalLoading ? 'Loading...' : 'Manage Subscription' }}</span>
              </button>
              <router-link
                to="/imagi/projects"
                class="inline-flex items-center justify-center gap-2 px-8 py-4 rounded-full font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0c0c0e]"
                :class="isSubscription
                  ? 'border border-blue-950/[0.14] text-blue-950/80 hover:text-blue-950 hover:border-blue-950/30 hover:bg-blue-950/[0.03] dark:border-white/[0.16] dark:text-blue-100/80 dark:hover:text-white dark:hover:border-white/30 dark:hover:bg-white/[0.06] transition-colors'
                  : 'bg-blue-950 text-[#fdf9f2] hover:bg-blue-900 dark:bg-[#f3ede2] dark:text-blue-950 dark:hover:bg-white hover:-translate-y-0.5 active:translate-y-0 shadow-[0_1px_2px_rgba(23,37,84,0.25),0_8px_20px_-6px_rgba(23,37,84,0.35),inset_0_1px_0_rgba(255,255,255,0.12)] hover:shadow-[0_2px_3px_rgba(23,37,84,0.22),0_14px_28px_-8px_rgba(23,37,84,0.4),inset_0_1px_0_rgba(255,255,255,0.12)] dark:shadow-[0_1px_2px_rgba(0,0,0,0.5),0_10px_24px_-8px_rgba(0,0,0,0.55)] dark:hover:shadow-[0_2px_3px_rgba(0,0,0,0.5),0_14px_30px_-8px_rgba(0,0,0,0.6)]'"
              >
                <i class="fas fa-rocket"></i>
                <span>Start Building</span>
              </router-link>
            </div>
          </div>

          <div v-else-if="error" class="animate-fade-in-up">
            <!-- Error Header -->
            <div class="text-center mb-12">
              <div class="w-20 h-20 rounded-full bg-red-100 dark:bg-red-400/[0.14] ring-1 ring-red-200/80 dark:ring-red-300/[0.18] flex items-center justify-center mx-auto mb-6">
                <i class="fas fa-exclamation-triangle text-3xl text-red-600 dark:text-red-400"></i>
              </div>
              <h1 class="font-display text-4xl sm:text-5xl font-semibold text-blue-950 dark:text-white mb-4 tracking-[-0.02em] leading-[1.05] text-balance">Payment Processing Error</h1>
            </div>

            <!-- Error Details Card -->
            <div class="crisp-card rounded-2xl bg-red-50/80 dark:bg-red-500/10 border border-red-200/70 dark:border-red-400/25 backdrop-blur-sm p-8">
              <p class="text-red-700 dark:text-red-300/80 text-center">{{ error }}</p>
            </div>

            <!-- Action Buttons -->
            <div class="flex justify-center mt-12">
              <router-link
                to="/payments/pricing"
                class="inline-flex items-center justify-center gap-2 px-8 py-4 rounded-full font-medium bg-blue-950 text-[#fdf9f2] hover:bg-blue-900 dark:bg-[#f3ede2] dark:text-blue-950 dark:hover:bg-white transition-all duration-200 hover:-translate-y-0.5 active:translate-y-0 shadow-[0_1px_2px_rgba(23,37,84,0.25),0_8px_20px_-6px_rgba(23,37,84,0.35),inset_0_1px_0_rgba(255,255,255,0.12)] hover:shadow-[0_2px_3px_rgba(23,37,84,0.22),0_14px_28px_-8px_rgba(23,37,84,0.4),inset_0_1px_0_rgba(255,255,255,0.12)] dark:shadow-[0_1px_2px_rgba(0,0,0,0.5),0_10px_24px_-8px_rgba(0,0,0,0.55)] dark:hover:shadow-[0_2px_3px_rgba(0,0,0,0.5),0_14px_30px_-8px_rgba(0,0,0,0.6)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0c0c0e]"
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
import PaymentService from '../services/payment_service'
import PaymentLayout from '../layouts/PaymentLayout.vue'

const paymentStore = usePaymentStore()
const paymentService = new PaymentService()
const route = useRoute()

// State
const isLoading = ref(true)
const error = ref('')
const paymentProcessed = ref(false)
const isSubscription = ref(false)
const creditsAdded = ref(0)
const balance = ref(0)
const portalLoading = ref(false)

const manageSubscription = async () => {
  try {
    portalLoading.value = true
    const response = await paymentService.createPortalSession()
    if (response.url) {
      window.location.href = response.url
    }
  } catch (err: any) {
    console.error('Error creating portal session:', err)
  } finally {
    portalLoading.value = false
  }
}

// On mount, process the session if there's a session_id in the URL
onMounted(async () => {
  try {
    const sessionId = route.query.session_id as string
    const success = route.query.success as string

    if (!sessionId && !success) {
      isLoading.value = false
      return
    }

    if (sessionId) {
      // Get session status from API
      const status = await paymentStore.getSessionStatus(sessionId)

      if (status.status === 'complete') {
        paymentProcessed.value = true
        creditsAdded.value = status.credits_added || 0

        // Detect subscription vs one-time from the session mode
        isSubscription.value = status.mode === 'subscription'

        if (!isSubscription.value) {
          await paymentStore.initializePayments()
          balance.value = paymentStore.balance ?? 0
        }
      } else {
        error.value = 'Your payment is still being processed. Please check back later.'
      }
    } else if (success === 'true') {
      // Fallback: success=true without session_id
      paymentProcessed.value = true
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

@media (prefers-reduced-motion: reduce) {
  .animate-fade-in-up {
    animation: none;
  }
}

/* Soft warm wash echoing the home hero's apricot glow */
.success-glow-warm {
  background: radial-gradient(closest-side, rgba(251, 146, 60, 0.11), rgba(251, 146, 60, 0.03) 55%, transparent 75%);
  filter: blur(48px);
}

.dark .success-glow-warm {
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