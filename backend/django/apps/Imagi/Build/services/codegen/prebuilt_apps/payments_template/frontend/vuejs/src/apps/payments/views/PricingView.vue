<!-- The plans page: subscriptions and pay-as-you-go plans from the price
     list. How it looks is decided entirely by styles/payments.css. -->
<template>
  <div class="pay-theme pay-page">
    <div class="pay-backdrop" aria-hidden="true"></div>
    <main class="pay-shell">
      <header class="pay-head">
        <p class="pay-eyebrow">{{ brand.pricing.eyebrow }}</p>
        <h1 class="pay-title">{{ brand.pricing.title }}</h1>
        <p class="pay-subtitle">{{ brand.pricing.subtitle }}</p>
      </header>

      <div v-if="loading" class="pay-status" role="status">
        <span class="pay-spinner" aria-hidden="true"></span>
        <span class="pay-sr">Loading plans</span>
      </div>
      <p v-else-if="error" class="pay-error" role="alert">{{ error }}</p>
      <p v-else-if="!plans.length" class="pay-empty">No plans are available yet. Check back soon.</p>

      <div v-else class="pay-grid">
        <article v-for="plan in plans" :key="plan.id" class="pay-card">
          <h2 class="pay-card-title">{{ plan.name }}</h2>
          <p class="pay-price">
            <span class="pay-amount">{{ describePrice(plan, currency).amount }}</span>
            <span class="pay-per">{{ describePrice(plan, currency).per }}</span>
          </p>
          <p v-if="plan.description" class="pay-card-body">{{ plan.description }}</p>
          <button
            type="button"
            class="pay-button"
            :disabled="busyId !== null"
            @click="subscribe(plan)"
          >
            {{ busyId === plan.id ? 'Opening checkout…' : brand.pricing.subscribe }}
          </button>
        </article>
      </div>

      <p v-if="!isSignedIn && plans.length" class="pay-note">{{ brand.pricing.signInNote }}</p>
      <p class="pay-secure">{{ brand.secureNote }}</p>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/shared/stores/auth'
import { brand } from '../brand'
import { describePrice, fetchCatalog, isPlan, startCheckout, type Price } from '../services/payments'
import '../styles/payments.css'

const router = useRouter()
const auth = useAuthStore()

const loading = ref(true)
const error = ref('')
const currency = ref('usd')
const plans = ref<Price[]>([])
const busyId = ref<number | null>(null)

const isSignedIn = computed(() => Boolean(auth.isAuthenticated && auth.user))

onMounted(async () => {
  try {
    const catalog = await fetchCatalog()
    currency.value = catalog.currency
    plans.value = catalog.products.filter(isPlan)
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Could not load the plans.'
  } finally {
    loading.value = false
  }
})

async function subscribe(plan: Price) {
  // A plan belongs to an account, so the customer signs in first.
  if (!isSignedIn.value) {
    router.push({ path: '/auth/signin', query: { redirect: '/pricing' } })
    return
  }
  busyId.value = plan.id
  error.value = ''
  try {
    await startCheckout([{ product_id: plan.id }], '/pricing', auth.user?.email || '')
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Could not start the checkout.'
    busyId.value = null
  }
}
</script>
