<!--
  SellProducts.vue - The project's catalog: create/edit products and copy
  shareable Stripe Checkout links for them.
-->
<template>
  <div>
    <!-- Toolbar -->
    <div class="flex flex-col sm:flex-row sm:items-center gap-3 mb-6">
      <div class="relative flex-1 max-w-sm">
        <i class="fas fa-magnifying-glass absolute left-3.5 top-1/2 -translate-y-1/2 text-xs text-blue-950/40 dark:text-white/30"></i>
        <input
          v-model="search"
          type="search"
          placeholder="Search products…"
          class="pl-9"
          :class="ui.input"
          @input="debouncedFetch"
        />
      </div>
      <div class="flex-1"></div>
      <button type="button" :class="ui.primaryBtn" @click="openCreate">
        <i class="fas fa-plus text-xs"></i>
        Add product
      </button>
    </div>

    <div v-if="linkNotice" class="mb-4" :class="ui.successBox">{{ linkNotice }}</div>
    <div v-if="actionError" class="mb-4" :class="ui.errorBox">{{ actionError }}</div>

    <!-- Loading -->
    <div v-if="store.productsLoading && !store.products.length" class="flex justify-center py-16">
      <div class="w-6 h-6 border-2 border-emerald-200 dark:border-emerald-300/30 border-t-emerald-600 dark:border-t-emerald-300 rounded-full animate-spin"></div>
    </div>

    <!-- Catalog -->
    <div v-else-if="store.products.length" class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div v-for="product in store.products" :key="product.id" class="p-5 flex gap-4" :class="ui.card">
        <div class="w-14 h-14 shrink-0 rounded-xl overflow-hidden" :class="product.image_url ? '' : ui.iconTile">
          <img v-if="product.image_url" :src="product.image_url" :alt="product.name" class="w-full h-full object-cover" />
          <i v-else class="fas fa-box-open"></i>
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0">
              <p class="text-sm font-semibold text-blue-950 dark:text-white truncate">{{ product.name }}</p>
              <p class="text-sm text-blue-950/60 dark:text-blue-100/60 tabular-nums">
                {{ formatMoney(product.price_cents, store.currency) }}<span v-if="product.billing_interval === 'month'"> / month</span><span v-else-if="product.billing_interval === 'year'"> / year</span>
              </p>
            </div>
            <div class="flex items-center gap-1.5 shrink-0">
              <span
                v-if="product.billing_interval !== 'one_time'"
                class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full border border-blue-200/80 dark:border-blue-400/25 bg-blue-50/80 dark:bg-blue-400/10 text-[11px] font-semibold uppercase tracking-[0.1em] whitespace-nowrap text-blue-700 dark:text-blue-300"
              >
                <i class="fas fa-arrows-rotate text-[9px]"></i>
                Subscription
              </span>
              <span
                class="inline-flex items-center px-2.5 py-0.5 rounded-full border text-[11px] font-semibold uppercase tracking-[0.1em] whitespace-nowrap"
                :class="product.is_active
                  ? 'border-emerald-200/80 dark:border-emerald-400/25 bg-emerald-50/80 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-300'
                  : 'border-blue-950/10 dark:border-white/15 bg-blue-950/[0.03] dark:bg-white/[0.04] text-blue-950/60 dark:text-white/60'"
              >
                {{ product.is_active ? 'Active' : 'Hidden' }}
              </span>
            </div>
          </div>
          <p v-if="product.description" class="text-xs text-blue-950/50 dark:text-blue-100/50 mt-1 line-clamp-2">{{ product.description }}</p>
          <div class="flex flex-wrap items-center gap-2 mt-3">
            <button
              type="button"
              class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-emerald-700 dark:text-emerald-300 hover:bg-emerald-50 dark:hover:bg-emerald-400/10 border border-emerald-200/70 dark:border-emerald-400/25 transition-colors duration-150 disabled:opacity-50"
              :disabled="!product.is_active || linkLoadingId === product.id || !store.isConfigured"
              :title="store.isConfigured ? 'Create a Stripe Checkout link and copy it' : 'Connect Stripe in Settings first'"
              @click="copyPaymentLink(product.id)"
            >
              <i :class="['fas', linkLoadingId === product.id ? 'fa-circle-notch animate-spin' : 'fa-link']"></i>
              Copy payment link
            </button>
            <button
              type="button"
              class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-blue-950/70 dark:text-blue-100/70 hover:bg-blue-50 dark:hover:bg-white/[0.08] border border-blue-200/70 dark:border-white/[0.12] transition-colors duration-150"
              @click="openEdit(product)"
            >
              <i class="fas fa-pen"></i>
              Edit
            </button>
            <button
              type="button"
              class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-red-600 dark:text-red-300 hover:bg-red-50 dark:hover:bg-red-500/10 border border-red-200/80 dark:border-red-400/25 transition-colors duration-150"
              @click="confirmDelete(product)"
            >
              <i class="fas fa-trash"></i>
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty -->
    <div v-else class="py-16 text-center" :class="ui.card">
      <div class="w-14 h-14 mx-auto mb-4 text-xl" :class="ui.iconTile">
        <i class="fas fa-box-open"></i>
      </div>
      <h3 class="text-lg font-semibold text-blue-950 dark:text-white mb-2">No products yet</h3>
      <p class="text-sm text-blue-950/60 dark:text-blue-100/60 mb-6 max-w-md mx-auto">
        Add what your business sells. Each product gets a shareable Stripe Checkout link, and your app can list them through the storefront API.
      </p>
      <button type="button" :class="ui.primaryBtn" @click="openCreate">
        <i class="fas fa-plus text-xs"></i>
        Add your first product
      </button>
    </div>

    <!-- Create/edit modal -->
    <SellModal
      v-if="showForm"
      :title="editingProduct ? 'Edit product' : 'Add product'"
      @close="closeForm"
    >
      <ProductForm
        :product="editingProduct"
        :currency="store.currency"
        @close="closeForm"
        @saved="onSaved"
      />
    </SellModal>

    <!-- Delete confirmation -->
    <SellModal v-if="deletingProduct" title="Delete product" @close="deletingProduct = null">
      <p class="text-sm text-blue-950/70 dark:text-blue-100/70 mb-6">
        Delete “{{ deletingProduct.name }}”? Existing orders keep their history, but the
        product can no longer be bought. To stop selling it temporarily, edit it and
        uncheck “Available for purchase” instead.
      </p>
      <div class="flex items-center justify-end gap-3">
        <button type="button" :class="ui.secondaryBtn" @click="deletingProduct = null">Cancel</button>
        <button type="button" :class="ui.dangerBtn" :disabled="deleting" @click="doDelete">
          <i v-if="deleting" class="fas fa-circle-notch animate-spin"></i>
          Delete product
        </button>
      </div>
    </SellModal>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import ProductForm from '../components/ProductForm.vue'
import SellModal from '../components/SellModal.vue'
import { extractError } from '../services/sellService'
import { useSellStore } from '../stores/sell'
import type { Product } from '../types'
import { formatMoney, ui } from '../utils/ui'

const route = useRoute()
const store = useSellStore()

const search = ref('')
const showForm = ref(false)
const editingProduct = ref<Product | null>(null)
const deletingProduct = ref<Product | null>(null)
const deleting = ref(false)
const linkLoadingId = ref<number | null>(null)
const linkNotice = ref('')
const actionError = ref('')

let searchTimer: ReturnType<typeof setTimeout> | undefined

function debouncedFetch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(fetchProducts, 300)
}

async function fetchProducts() {
  actionError.value = ''
  try {
    await store.fetchProducts(search.value ? { search: search.value } : {})
  } catch (error) {
    actionError.value = extractError(error, 'Could not load products.')
  }
}

function openCreate() {
  editingProduct.value = null
  showForm.value = true
}

function openEdit(product: Product) {
  editingProduct.value = product
  showForm.value = true
}

function closeForm() {
  showForm.value = false
  editingProduct.value = null
}

async function onSaved() {
  closeForm()
  await fetchProducts()
}

function confirmDelete(product: Product) {
  deletingProduct.value = product
}

async function doDelete() {
  if (!deletingProduct.value) return
  deleting.value = true
  actionError.value = ''
  try {
    await store.deleteProduct(deletingProduct.value.id)
    deletingProduct.value = null
  } catch (error) {
    actionError.value = extractError(error, 'Could not delete the product.')
  } finally {
    deleting.value = false
  }
}

async function copyPaymentLink(productId: number) {
  linkLoadingId.value = productId
  linkNotice.value = ''
  actionError.value = ''
  try {
    const { checkout_url } = await store.createPaymentLink(productId)
    try {
      await navigator.clipboard.writeText(checkout_url)
      linkNotice.value = 'Payment link copied — share it anywhere. It opens a Stripe Checkout page for this product.'
    } catch {
      linkNotice.value = `Payment link created: ${checkout_url}`
    }
    setTimeout(() => { linkNotice.value = '' }, 8000)
  } catch (error) {
    actionError.value = extractError(error, 'Could not create a payment link.')
  } finally {
    linkLoadingId.value = null
  }
}

onMounted(async () => {
  await fetchProducts()
  if (route.query.new === '1') openCreate()
})
</script>
