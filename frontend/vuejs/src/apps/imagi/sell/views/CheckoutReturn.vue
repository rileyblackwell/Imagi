<!--
  CheckoutReturn.vue - Public landing page after a Stripe Checkout started
  from a payment link. Customers of the user's business land here (they are
  not Imagi users), so the page is minimal and self-contained.

  Success route: /checkout/:projectId/success?session_id=cs_...
  Cancel route:  /checkout/:projectId/cancel
-->
<template>
  <div class="min-h-screen flex items-center justify-center px-6 bg-[linear-gradient(180deg,#fdf9f2_0%,#faf7f1_60%,#ffffff_100%)] dark:bg-[linear-gradient(180deg,#0c0c0e_0%,#0a0b0f_60%,#0a0a0a_100%)] transition-colors duration-500">
    <div class="w-full max-w-md p-8 text-center crisp-card rounded-2xl bg-white/85 dark:bg-white/[0.045] backdrop-blur-sm border border-blue-200/70 dark:border-blue-300/[0.14]">
      <!-- Canceled -->
      <template v-if="canceled">
        <div class="w-14 h-14 mx-auto mb-5 rounded-full flex items-center justify-center border bg-blue-950/[0.03] dark:bg-white/[0.04] border-blue-950/10 dark:border-white/15 text-blue-950/50 dark:text-blue-100/50">
          <i class="fas fa-arrow-rotate-left text-xl"></i>
        </div>
        <h1 class="font-display text-2xl font-semibold tracking-[-0.02em] leading-[1.05] text-blue-950 dark:text-white mb-2">Checkout canceled</h1>
        <p class="text-sm text-blue-950/60 dark:text-blue-100/60">
          No charge was made. You can close this page, or go back and try again.
        </p>
      </template>

      <!-- Checking -->
      <template v-else-if="checking">
        <div class="w-14 h-14 mx-auto mb-5 rounded-full flex items-center justify-center border bg-emerald-50 dark:bg-emerald-400/10 border-emerald-200/60 dark:border-emerald-400/25">
          <div class="w-6 h-6 border-2 border-emerald-200 dark:border-emerald-300/30 border-t-emerald-600 dark:border-t-emerald-300 rounded-full animate-spin"></div>
        </div>
        <h1 class="font-display text-2xl font-semibold tracking-[-0.02em] leading-[1.05] text-blue-950 dark:text-white mb-2">Confirming your payment…</h1>
        <p class="text-sm text-blue-950/60 dark:text-blue-100/60">This usually takes a moment.</p>
      </template>

      <!-- Paid -->
      <template v-else-if="paid">
        <div class="w-14 h-14 mx-auto mb-5 rounded-full flex items-center justify-center border bg-emerald-50 dark:bg-emerald-400/10 border-emerald-200/60 dark:border-emerald-400/25 text-emerald-600 dark:text-emerald-300">
          <i class="fas fa-check text-xl"></i>
        </div>
        <h1 class="font-display text-2xl font-semibold tracking-[-0.02em] leading-[1.05] text-blue-950 dark:text-white mb-2">Payment received</h1>
        <p class="text-sm text-blue-950/60 dark:text-blue-100/60">
          Thanks! Your payment of
          <span class="font-semibold text-blue-950 dark:text-white">{{ formatMoney(amount, currency) }}</span>
          went through. A receipt is on its way from Stripe.
        </p>
      </template>

      <!-- Unknown / not yet confirmed -->
      <template v-else>
        <div class="w-14 h-14 mx-auto mb-5 rounded-full flex items-center justify-center border bg-amber-50 dark:bg-amber-400/10 border-amber-200/60 dark:border-amber-400/25 text-amber-600 dark:text-amber-300">
          <i class="fas fa-hourglass-half text-xl"></i>
        </div>
        <h1 class="font-display text-2xl font-semibold tracking-[-0.02em] leading-[1.05] text-blue-950 dark:text-white mb-2">Payment processing</h1>
        <p class="text-sm text-blue-950/60 dark:text-blue-100/60 mb-6">
          We haven't seen the confirmation yet. If you completed the payment, it will be
          recorded shortly.
        </p>
        <button type="button" :class="ui.secondaryBtn" @click="check">
          <i class="fas fa-rotate text-xs"></i>
          Check again
        </button>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import SellService from '../services/sellService'
import { formatMoney, ui } from '../utils/ui'

const props = defineProps<{
  canceled?: boolean
}>()

const route = useRoute()

const checking = ref(!props.canceled)
const paid = ref(false)
const amount = ref(0)
const currency = ref('usd')

async function check() {
  const projectId = Number(route.params.projectId)
  const sessionId = String(route.query.session_id ?? '')
  if (!projectId || !sessionId) {
    checking.value = false
    return
  }
  checking.value = true
  try {
    const result = await SellService.getSessionStatus(projectId, sessionId)
    paid.value = result.status === 'paid' || result.status === 'fulfilled'
    amount.value = result.amount_total_cents
    currency.value = result.currency
  } catch {
    paid.value = false
  } finally {
    checking.value = false
  }
}

onMounted(() => {
  if (!props.canceled) check()
})
</script>

<style scoped>
.crisp-card {
  box-shadow:
    0 0 0 1px rgba(15, 23, 42, 0.03),
    0 1px 2px rgba(15, 23, 42, 0.06),
    0 4px 10px -2px rgba(15, 23, 42, 0.07),
    0 12px 28px -10px rgba(15, 23, 42, 0.10);
}

:global(.dark) .crisp-card {
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.04),
    0 1px 2px rgba(0, 0, 0, 0.5),
    0 4px 10px -2px rgba(0, 0, 0, 0.45),
    0 12px 28px -10px rgba(0, 0, 0, 0.55);
}
</style>
