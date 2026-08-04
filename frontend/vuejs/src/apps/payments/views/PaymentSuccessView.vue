<template>
  <PaymentLayout>
    <div class="editorial payment-success-view min-h-screen relative">
      <!-- Atmosphere: one soft apricot wash over the porcelain canvas -->

      <!-- Content Container -->
      <div class="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <!-- Success Section -->
        <div class="max-w-2xl mx-auto">
          <div v-if="isLoading" class="animate-fade-in-up">
            <div class="panel p-12 text-center">
              <div class="flex justify-center">
                <svg class="animate-spin h-12 w-12 text-[color:var(--ink)]" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </div>
              <p class="mt-4 text-[color:var(--ink-55)]">Processing your payment...</p>
            </div>
          </div>
          
          <div v-else-if="paymentProcessed" class="animate-fade-in-up space-y-6">
            <!-- Success Header -->
            <div class="text-center mb-12">
              <div class="w-20 h-20 rounded-full bg-emerald-100 dark:bg-emerald-400/[0.14] ring-1 ring-emerald-200/80 dark:ring-emerald-300/[0.18] flex items-center justify-center mx-auto mb-6">
                <i class="fas fa-check text-3xl text-emerald-600 dark:text-emerald-300"></i>
              </div>
              <h1 class="display text-4xl sm:text-5xl mb-4">
                Subscription Activated!
              </h1>
              <p class="text-xl text-[color:var(--ink-55)] leading-relaxed">
                Your subscription is now active. Welcome aboard!
              </p>
            </div>

            <!-- Success Details Card -->
            <div class="panel p-8 text-center">
              <p class="text-lg text-emerald-900 dark:text-emerald-100">
                Your plan is now active. You can manage your subscription at any time.
              </p>
              <!-- The webhook grants the plan, so it may land a moment after
                   this page does; show the allowance only once it has. -->
              <div v-if="planSummary" class="mt-6 pt-6 border-t border-[color:var(--rule)]">
                <p class="text-emerald-700 dark:text-emerald-300/80">Your plan</p>
                <p class="display text-3xl mt-2">{{ planSummary }}</p>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="flex flex-col sm:flex-row items-center justify-center gap-4 mt-12">
              <button
                @click="manageSubscription"
                :disabled="portalLoading"
                class="btn-primary"
              >
                <i class="fas fa-cog"></i>
                <span>{{ portalLoading ? 'Loading...' : 'Manage Subscription' }}</span>
              </button>
              <router-link
                to="/imagi/projects"
                class="btn-outline"
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
              <h1 class="display text-4xl sm:text-5xl mb-4">Payment Processing Error</h1>
            </div>

            <!-- Error Details Card -->
            <div class="panel panel--error p-8">
              <p class="text-red-700 dark:text-red-300/80 text-center">{{ error }}</p>
            </div>

            <!-- Action Buttons -->
            <div class="flex justify-center mt-12">
              <router-link
                to="/payments/pricing"
                class="btn-primary"
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
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { usePaymentStore } from '../stores/payments'
import { useUsageStore, formatUsd } from '@/shared/stores/usage'
import PaymentService from '../services/payment_service'
import PaymentLayout from '../layouts/PaymentLayout.vue'

const paymentStore = usePaymentStore()
const usageStore = useUsageStore()
const paymentService = new PaymentService()
const route = useRoute()

// State
const isLoading = ref(true)
const error = ref('')
const paymentProcessed = ref(false)
const portalLoading = ref(false)

/** "Pro — $10 of usage per week", or null until the plan webhook has landed.
 *  Quoted per week because that is the window the meter actually enforces. */
const planSummary = computed(() => {
  const plan = usageStore.plan
  if (!plan || plan.id === 'free') return null
  const limits = usageStore.plans.find((p) => p.id === plan.id)
  if (!limits || limits.weeklyUsd === null) return plan.name
  return `${plan.name} — ${formatUsd(limits.weeklyUsd)} of usage per week`
})

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
        // Stripe's subscription webhook grants the plan; read it back so the
        // page can name the allowance. It may not have landed yet, in which
        // case planSummary stays null rather than claiming the free tier.
        await usageStore.fetchUsage()
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
/* A hairline panel, matching the auth form and the rest of the public pages —
   no floating card, no tinted fill. */
.panel--error {
  border-color: rgba(220, 38, 38, 0.35);
}

.panel {
  border: 1px solid var(--rule);
  border-radius: 1rem;
  background: var(--paper-raised);
}
</style>
