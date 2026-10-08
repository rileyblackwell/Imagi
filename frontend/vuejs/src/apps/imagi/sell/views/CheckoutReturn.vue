<!--
  CheckoutReturn.vue - Public landing page after a Stripe Checkout started
  from a payment link. Customers of the user's business land here (they are
  not Imagi users), so the page is minimal and self-contained.

  Success route: /checkout/:projectId/success?session_id=cs_...
  Cancel route:  /checkout/:projectId/cancel
-->
<template>
  <div class="spotlight checkout-return">
    <div class="sl-spot checkout-return__spot" aria-hidden="true"></div>
    <div class="sl-dots" aria-hidden="true"></div>

    <div class="checkout-return__card">
      <!-- Canceled -->
      <template v-if="canceled">
        <div class="checkout-return__mark checkout-return__mark--muted">
          <i class="fas fa-arrow-rotate-left"></i>
        </div>
        <h1 class="sl-display checkout-return__title">Checkout canceled</h1>
        <p class="checkout-return__body">
          No charge was made. You can close this page, or go back and try again.
        </p>
      </template>

      <!-- Checking -->
      <template v-else-if="checking">
        <div class="checkout-return__mark">
          <div class="checkout-return__spinner"></div>
        </div>
        <h1 class="sl-display checkout-return__title">Confirming your payment…</h1>
        <p class="checkout-return__body">This usually takes a moment.</p>
      </template>

      <!-- Paid -->
      <template v-else-if="paid">
        <div class="checkout-return__mark checkout-return__mark--ok">
          <i class="fas fa-check"></i>
        </div>
        <h1 class="sl-display checkout-return__title">Payment received</h1>
        <p class="checkout-return__body">
          Thanks! Your payment of
          <span class="checkout-return__amount">{{ formatMoney(amount, currency) }}</span>
          went through. A receipt is on its way from Stripe.
        </p>
      </template>

      <!-- Unknown / not yet confirmed -->
      <template v-else>
        <div class="checkout-return__mark checkout-return__mark--wait">
          <i class="fas fa-hourglass-half"></i>
        </div>
        <h1 class="sl-display checkout-return__title">Payment processing</h1>
        <p class="checkout-return__body mb-6">
          We haven't seen the confirmation yet. If you completed the payment, it will be
          recorded shortly.
        </p>
        <button type="button" class="checkout-return__btn" @click="check">
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
</script>

<style scoped>
/* The Spotlight stage (shared/styles/spotlight.css), kept minimal: this page
   is seen by the business's own customers, so no Imagi navbar or footer —
   just one card standing in the light. */
.checkout-return {
  position: relative;
  isolation: isolate;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 48px 20px;
}

.checkout-return .checkout-return__spot {
  background:
    radial-gradient(ellipse 42% 50% at 50% 18%, var(--sl-spot-core) 0%, var(--sl-spot-mid) 45%, transparent 75%),
    radial-gradient(ellipse 80% 60% at 50% -10%, var(--sl-spot-wide), transparent 65%);
}

.checkout-return__card {
  width: 100%;
  max-width: 28rem;
  padding: 40px 32px;
  border: 1px solid transparent;
  border-radius: 22px;
  background:
    var(--sl-prompt-bg) padding-box,
    var(--sl-prompt-edge) border-box;
  box-shadow: var(--sl-prompt-shadow);
  text-align: center;
}

.checkout-return__mark {
  display: grid;
  place-items: center;
  width: 56px;
  height: 56px;
  margin: 0 auto 22px;
  border-radius: 18px;
  border: 1px solid var(--sl-line-strong);
  background: var(--sl-chip-bg);
  font-size: 20px;
  color: var(--sl-coral);
}

.checkout-return__mark--muted { color: var(--sl-muted); }
.checkout-return__mark--ok { color: var(--sl-ok); }
.checkout-return__mark--wait { color: var(--sl-wait); }

.checkout-return__spinner {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 2px solid var(--sl-line-strong);
  border-top-color: var(--sl-coral);
  animation: checkout-return-spin 0.9s linear infinite;
}

@keyframes checkout-return-spin {
  to { transform: rotate(360deg); }
}

.checkout-return .checkout-return__title {
  margin-bottom: 10px;
  font-size: 30px;
  line-height: 1.05;
  letter-spacing: -0.03em;
}

.checkout-return__body {
  margin: 0;
  color: var(--sl-muted);
  font-size: 15px;
  line-height: 1.6;
}

.checkout-return__amount {
  font-weight: 650;
  color: var(--sl-text);
}

.checkout-return__btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border: 1px solid var(--sl-line-strong);
  border-radius: 999px;
  background: var(--sl-chip-bg);
  color: var(--sl-text);
  font-size: 14px;
  font-weight: 600;
  transition: background 0.18s ease, border-color 0.18s ease;
}

.checkout-return__btn:hover {
  background: var(--sl-chip-bg-hover);
  border-color: var(--sl-text);
}
</style>
