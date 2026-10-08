<!-- The store: one-time purchases from the price list. How it looks is
     decided entirely by styles/payments.css. -->
<template>
  <div class="pay-theme pay-page">
    <div class="pay-backdrop" aria-hidden="true"></div>
    <main class="pay-shell">
      <header class="pay-head">
        <p class="pay-eyebrow">{{ brand.store.eyebrow }}</p>
        <h1 class="pay-title">{{ brand.store.title }}</h1>
        <p class="pay-subtitle">{{ brand.store.subtitle }}</p>
      </header>

      <div v-if="loading" class="pay-status" role="status">
        <span class="pay-spinner" aria-hidden="true"></span>
        <span class="pay-sr">Loading products</span>
      </div>
      <p v-else-if="error" class="pay-error" role="alert">{{ error }}</p>
      <p v-else-if="!products.length" class="pay-empty">{{ brand.store.empty }}</p>

      <div v-else class="pay-grid">
        <article v-for="product in products" :key="product.id" class="pay-card">
          <img v-if="product.image_url" :src="product.image_url" :alt="product.name" class="pay-card-image" />
          <h2 class="pay-card-title">{{ product.name }}</h2>
          <p v-if="product.description" class="pay-card-body">{{ product.description }}</p>
          <div class="pay-card-foot">
            <span class="pay-amount">{{ formatMoney(product.price_cents, currency) }}</span>
            <button
              type="button"
              class="pay-button"
              :disabled="busyId !== null"
              @click="buy(product)"
            >
              {{ busyId === product.id ? 'Opening checkout…' : brand.store.buy }}
            </button>
          </div>
        </article>
      </div>

      <p class="pay-secure">{{ brand.secureNote }}</p>
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useAuthStore } from '@/shared/stores/auth'
import { brand } from '../brand'
import { fetchCatalog, formatMoney, isPlan, startCheckout, type Price } from '../services/payments'
import '../styles/payments.css'

const auth = useAuthStore()

const loading = ref(true)
const error = ref('')
const currency = ref('usd')
const products = ref<Price[]>([])
const busyId = ref<number | null>(null)

onMounted(async () => {
  try {
    const catalog = await fetchCatalog()
    currency.value = catalog.currency
    products.value = catalog.products.filter(price => !isPlan(price))
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Could not load the store.'
  } finally {
    loading.value = false
  }
})

async function buy(product: Price) {
  busyId.value = product.id
  error.value = ''
  try {
    await startCheckout([{ product_id: product.id, quantity: 1 }], '/store', auth.user?.email || '')
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Could not start the checkout.'
    busyId.value = null
  }
}
</script>
