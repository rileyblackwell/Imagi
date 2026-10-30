<!--
  CheckoutReturn.vue - Public landing page after a Stripe Checkout started
  from a payment link. Customers of the user's business land here (they are
  not Imagi users), so the page is minimal and self-contained.

  Success route: /checkout/:projectId/success?session_id=cs_...
  Cancel route:  /checkout/:projectId/cancel
-->
<template>
  <!-- The Spotlight stage, kept minimal: this page is seen by the business's
       own customers, so no Imagi navbar or footer — just one card standing in
       the light. -->
  <div class="spotlight relative isolate flex min-h-screen items-center justify-center overflow-hidden px-5 py-12">
    <!-- `!` beats .sl-spot's own background -->
    <div
      class="sl-spot ![background:radial-gradient(ellipse_42%_50%_at_50%_18%,var(--sl-spot-core)_0%,var(--sl-spot-mid)_45%,transparent_75%),radial-gradient(ellipse_80%_60%_at_50%_-10%,var(--sl-spot-wide),transparent_65%)]"
      aria-hidden="true"
    ></div>
    <div class="sl-dots" aria-hidden="true"></div>

    <div
      class="w-full max-w-md rounded-[22px] border border-transparent px-8 py-10 text-center shadow-sl-prompt
        [background:var(--sl-prompt-bg)_padding-box,var(--sl-prompt-edge)_border-box]"
    >
      <!-- Canceled -->
      <template v-if="canceled">
        <div :class="mark" class="text-sl-muted">
          <i class="fas fa-arrow-rotate-left"></i>
        </div>
        <h1 :class="title">Checkout canceled</h1>
        <p :class="body">
          No charge was made. You can close this page, or go back and try again.
        </p>
      </template>

      <!-- Checking -->
      <template v-else-if="checking">
        <div :class="mark" class="text-sl-coral">
          <div class="checkout-return__spinner h-6 w-6 rounded-[50%] border-2 border-sl-line-strong border-t-sl-coral"></div>
        </div>
        <h1 :class="title">Confirming your payment…</h1>
        <p :class="body">This usually takes a moment.</p>
      </template>

      <!-- Paid -->
      <template v-else-if="paid">
        <div :class="mark" class="text-sl-ok">
          <i class="fas fa-check"></i>
        </div>
        <h1 :class="title">Payment received</h1>
        <p :class="body">
          Thanks! Your payment of
          <span class="font-[650] text-sl-text">{{ formatMoney(amount, currency) }}</span>
          went through. A receipt is on its way from Stripe.
        </p>
      </template>

      <!-- Unknown / not yet confirmed -->
      <template v-else>
        <div :class="mark" class="text-sl-wait">
          <i class="fas fa-hourglass-half"></i>
        </div>
        <h1 :class="title">Payment processing</h1>
        <p :class="body">
          We haven't seen the confirmation yet. If you completed the payment, it will be
          recorded shortly.
        </p>
        <button
          type="button"
          class="inline-flex items-center gap-2 rounded-[999px] border border-sl-line-strong bg-sl-chip-bg px-[18px] py-2.5
            text-[14px] font-semibold text-sl-text [transition:background_0.18s_ease,border-color_0.18s_ease]
            hover:border-sl-text hover:bg-sl-chip-bg-hover"
          @click="check"
        >
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
import { formatMoney } from '../utils/ui'

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

// Shared by every state: the status mark (each adds its colour), the
// headline (`!` beats .sl-display's `margin: 0`) and the line under it.
const mark =
  'mx-auto mb-[22px] grid h-14 w-14 place-items-center rounded-[18px] border border-sl-line-strong bg-sl-chip-bg text-[20px]'
const title = 'sl-display !mb-2.5 text-[30px] leading-[1.05] tracking-[-0.03em]'
const body = 'm-0 text-[15px] leading-[1.6] text-sl-muted'
</script>

<style scoped>
/* The checking spinner's turn: keyframes stay in CSS (scoped names are hashed). */
.checkout-return__spinner {
  animation: checkout-return-spin 0.9s linear infinite;
}

@keyframes checkout-return-spin {
  to { transform: rotate(360deg); }
}
</style>
