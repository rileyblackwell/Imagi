<!-- Where Stripe sends customers back. Waits for the payment to be
     confirmed, then says so. How it looks is decided by styles/payments.css. -->
<template>
  <div class="pay-theme pay-page">
    <div class="pay-backdrop" aria-hidden="true"></div>
    <main class="pay-shell pay-shell-narrow">
      <section class="pay-card pay-result" aria-live="polite">
        <template v-if="canceled">
          <h1 class="pay-card-title">{{ brand.checkout.canceledTitle }}</h1>
          <p class="pay-card-body">{{ brand.checkout.canceledBody }}</p>
        </template>
        <template v-else-if="state === 'checking'">
          <span class="pay-spinner" aria-hidden="true"></span>
          <h1 class="pay-card-title">Confirming your payment…</h1>
        </template>
        <template v-else-if="state === 'paid'">
          <span class="pay-check" aria-hidden="true"></span>
          <h1 class="pay-card-title">{{ subscribed ? brand.checkout.subscribedTitle : brand.checkout.paidTitle }}</h1>
          <p class="pay-card-body">
            <span v-if="amount && !subscribed">{{ amount }} · </span>{{ subscribed ? brand.checkout.subscribedBody : brand.checkout.paidBody }}
          </p>
        </template>
        <template v-else>
          <h1 class="pay-card-title">{{ brand.checkout.pendingTitle }}</h1>
          <p class="pay-card-body">{{ brand.checkout.pendingBody }}</p>
        </template>
        <router-link :to="backPath" class="pay-button pay-button-quiet">Back</router-link>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { brand } from '../brand'
import { fetchCheckoutStatus, formatMoney } from '../services/payments'
import '../styles/payments.css'

const props = withDefaults(defineProps<{ canceled?: boolean; backPath?: string }>(), {
  canceled: false,
  backPath: '/'
})

const route = useRoute()
const state = ref<'checking' | 'paid' | 'pending'>('checking')
const amount = ref('')
const subscribed = ref(false)

let attempts = 0
let timer: ReturnType<typeof setTimeout> | null = null

async function poll() {
  const sessionId = String(route.query.session_id || '')
  if (!sessionId) {
    state.value = 'pending'
    return
  }
  try {
    const status = await fetchCheckoutStatus(sessionId)
    if (status.status === 'paid' || status.status === 'fulfilled') {
      amount.value = formatMoney(status.amount_total_cents, status.currency)
      subscribed.value = status.mode === 'subscription'
      state.value = 'paid'
      return
    }
  } catch {
    // Keep trying; the payment may still be settling with Stripe.
  }
  attempts += 1
  if (attempts < 8) {
    timer = setTimeout(poll, 1500)
  } else {
    state.value = 'pending'
  }
}

onMounted(() => {
  if (!props.canceled) poll()
})
onBeforeUnmount(() => {
  if (timer) clearTimeout(timer)
})
</script>
