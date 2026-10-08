<!-- Checkout success — on the Spotlight stage (see PaymentLayout's
     .pay-* classes). -->
<template>
  <PaymentLayout>
    <div class="editorial payment-success-view">
      <section class="pay-stage">
        <div class="sl-spot" aria-hidden="true"></div>
        <div class="sl-dots" aria-hidden="true"></div>

        <div class="pay-stage__inner">
          <div v-if="isLoading" class="pay-rise">
            <div class="pay-card">
              <div class="pay-spinner" aria-hidden="true"></div>
              <p class="mt-5">Processing your payment…</p>
            </div>
          </div>

          <div v-else-if="paymentProcessed" class="pay-rise">
            <div class="pay-mark pay-mark--ok"><i class="fas fa-check" aria-hidden="true"></i></div>
            <h1 class="sl-display pay-title">Subscription <span class="sl-run">activated</span></h1>
            <p class="sl-lede pay-lede">
              Your subscription is now active. Welcome aboard!
            </p>

            <div class="pay-card">
              <p class="m-0">
                Your plan is now active. You can manage your subscription at any time.
              </p>
              <!-- The webhook grants the plan, so it may land a moment after
                   this page does; show the allowance only once it has. -->
              <template v-if="planSummary">
                <p class="pay-card__label">Your plan</p>
                <p class="pay-card__value">{{ planSummary }}</p>
              </template>
            </div>

            <div class="pay-actions">
              <router-link to="/imagi/projects" class="btn-primary">
                <i class="fas fa-rocket"></i>
                <span>Start building</span>
              </router-link>
              <button
                type="button"
                class="btn-outline"
                :disabled="portalLoading"
                @click="manageSubscription"
              >
                <i class="fas fa-cog"></i>
                <span>{{ portalLoading ? 'Loading…' : 'Manage subscription' }}</span>
              </button>
            </div>
          </div>

          <div v-else-if="error" class="pay-rise">
            <div class="pay-mark pay-mark--bad"><i class="fas fa-exclamation-triangle" aria-hidden="true"></i></div>
            <h1 class="sl-display pay-title">Payment processing error</h1>

            <div class="pay-card pay-card--error">
              <p class="m-0">{{ error }}</p>
            </div>

            <div class="pay-actions">
              <router-link to="/payments/pricing" class="btn-primary">
                <i class="fas fa-arrow-left"></i>
                <span>Back to pricing</span>
              </router-link>
            </div>
          </div>
        </div>
      </section>
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
