<!--
  ProductForm.vue - Create/edit a catalog product. Prices are entered in
  dollars (or the project currency's main unit) and stored as cents.
-->
<template>
  <form class="space-y-5" @submit.prevent="submit">
    <div>
      <label :class="ui.label" for="product-name">Name</label>
      <input
        id="product-name"
        v-model="form.name"
        type="text"
        required
        maxlength="255"
        placeholder="e.g. House Blend — 12oz bag"
        :class="ui.input"
      />
    </div>

    <div>
      <label :class="ui.label" for="product-description">Description <span class="normal-case tracking-normal font-normal">(optional)</span></label>
      <textarea
        id="product-description"
        v-model="form.description"
        rows="3"
        placeholder="Shown to customers on the Stripe checkout page."
        :class="ui.input"
      ></textarea>
    </div>

    <div>
      <label :class="ui.label">How customers pay</label>
      <div class="grid grid-cols-3 gap-2">
        <button
          v-for="option in billingOptions"
          :key="option.value"
          type="button"
          class="px-3 py-2.5 rounded-xl border text-sm font-medium transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#141418]"
          :class="form.billing_interval === option.value
            ? 'border-emerald-400 dark:border-emerald-400/60 bg-emerald-50 dark:bg-emerald-400/10 text-emerald-800 dark:text-emerald-200'
            : 'border-blue-950/[0.14] dark:border-white/[0.14] bg-white dark:bg-white/[0.06] text-blue-950/70 dark:text-blue-100/70 hover:border-blue-950/30 dark:hover:border-white/25'"
          @click="form.billing_interval = option.value"
        >
          {{ option.label }}
        </button>
      </div>
      <p class="text-xs text-blue-950/50 dark:text-blue-100/50 mt-1.5">
        {{ form.billing_interval === 'one_time'
          ? 'Charged once at checkout.'
          : 'Stripe bills the customer automatically each ' + (form.billing_interval === 'month' ? 'month' : 'year') + '.' }}
      </p>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
      <div>
        <label :class="ui.label" for="product-price">
          Price ({{ currency.toUpperCase() }}){{ form.billing_interval === 'month' ? ' per month' : form.billing_interval === 'year' ? ' per year' : '' }}
        </label>
        <input
          id="product-price"
          v-model="priceInput"
          type="number"
          min="0.50"
          step="0.01"
          required
          placeholder="12.00"
          :class="ui.input"
        />
        <p class="text-xs text-blue-950/50 dark:text-blue-100/50 mt-1.5">At least 0.50 — Stripe's minimum charge.</p>
      </div>
      <div>
        <label :class="ui.label" for="product-image">Image URL <span class="normal-case tracking-normal font-normal">(optional)</span></label>
        <input
          id="product-image"
          v-model="form.image_url"
          type="url"
          placeholder="https://…"
          :class="ui.input"
        />
        <p class="text-xs text-blue-950/50 dark:text-blue-100/50 mt-1.5">Shown on the checkout page.</p>
      </div>
    </div>

    <label class="flex items-center gap-2.5 text-sm text-blue-950/80 dark:text-blue-100/80 cursor-pointer">
      <input v-model="form.is_active" type="checkbox" class="rounded border-blue-950/30 dark:border-white/30 text-blue-950 dark:text-blue-400 focus:ring-blue-500/40 dark:focus:ring-blue-300/50" />
      Available for purchase
    </label>

    <div v-if="error" :class="ui.errorBox">{{ error }}</div>

    <div class="flex items-center justify-end gap-3 pt-1">
      <button type="button" :class="ui.secondaryBtn" @click="$emit('close')">Cancel</button>
      <button type="submit" :class="ui.primaryBtn" :disabled="saving">
        <i v-if="saving" class="fas fa-circle-notch animate-spin"></i>
        {{ product ? 'Save product' : 'Add product' }}
      </button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { extractError } from '../services/sellService'
import { useSellStore } from '../stores/sell'
import type { BillingInterval, Product } from '../types'
import { ui } from '../utils/ui'

const props = defineProps<{
  product?: Product | null
  currency: string
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'saved', product: Product): void
}>()

const store = useSellStore()

const billingOptions: Array<{ value: BillingInterval; label: string }> = [
  { value: 'one_time', label: 'One-time' },
  { value: 'month', label: 'Monthly' },
  { value: 'year', label: 'Yearly' },
]

const form = reactive({
  name: props.product?.name ?? '',
  description: props.product?.description ?? '',
  image_url: props.product?.image_url ?? '',
  billing_interval: (props.product?.billing_interval ?? 'one_time') as BillingInterval,
  is_active: props.product?.is_active ?? true,
})

const priceInput = ref(
  props.product ? (props.product.price_cents / 100).toFixed(2) : ''
)

const saving = ref(false)
const error = ref('')

async function submit() {
  saving.value = true
  error.value = ''
  try {
    const payload = {
      name: form.name.trim(),
      description: form.description.trim(),
      image_url: form.image_url.trim(),
      billing_interval: form.billing_interval,
      is_active: form.is_active,
      price_cents: Math.round(parseFloat(priceInput.value || '0') * 100),
    }
    const product = props.product
      ? await store.updateProduct(props.product.id, payload)
      : await store.createProduct(payload)
    emit('saved', product)
  } catch (err) {
    error.value = extractError(err, 'Could not save the product.')
  } finally {
    saving.value = false
  }
}
</script>
