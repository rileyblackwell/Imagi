<!--
  SellOrders.vue - Order history with status filtering, plus per-order
  actions: mark fulfilled, and sync from Stripe when webhooks can't reach us.
-->
<template>
  <div>
    <!-- Filter -->
    <div class="flex flex-wrap items-center gap-2 mb-6">
      <button
        v-for="option in statusFilters"
        :key="option.value"
        type="button"
        class="px-3.5 py-1.5 rounded-full text-xs font-semibold uppercase tracking-[0.1em] border transition-colors duration-150 focus-ring"
        :class="statusFilter === option.value
          ? 'border-emerald-300 dark:border-emerald-400/40 bg-emerald-50 dark:bg-emerald-400/10 text-emerald-700 dark:text-emerald-300'
          : 'border-blue-950/[0.14] dark:border-white/[0.16] text-blue-950/60 dark:text-blue-100/60 hover:text-blue-950 dark:hover:text-white hover:border-blue-950/30 dark:hover:border-white/30'"
        @click="setFilter(option.value)"
      >
        {{ option.label }}
      </button>
    </div>

    <div v-if="actionError" class="mb-4" :class="ui.errorBox">{{ actionError }}</div>

    <!-- Loading -->
    <LoadingSpinner v-if="store.ordersLoading && !store.orders.length" />

    <!-- Orders -->
    <div v-else-if="store.orders.length" class="space-y-3">
      <div v-for="order in store.orders" :key="order.id" class="p-5" :class="ui.card">
        <div class="flex flex-col sm:flex-row sm:items-center gap-3">
          <div class="flex items-center gap-3 flex-1 min-w-0">
            <div class="w-10 h-10 shrink-0" :class="ui.iconTile">
              <i class="fas fa-receipt text-sm"></i>
            </div>
            <div class="min-w-0">
              <p class="text-sm font-semibold text-blue-950 dark:text-white truncate">
                Order #{{ order.id }} · {{ itemsSummary(order) }}
              </p>
              <p class="text-xs text-blue-950/50 dark:text-blue-100/50">
                {{ order.customer_name || order.customer_email || 'Customer pending' }} · {{ formatDateTime(order.created_at) }}
              </p>
            </div>
          </div>
          <div class="flex items-center gap-3 shrink-0">
            <span class="text-sm font-semibold text-blue-950 dark:text-white tabular-nums">
              {{ formatMoney(order.amount_total_cents, order.currency) }}
            </span>
            <OrderStatusBadge :status="order.status" />
            <button
              v-if="order.status === 'paid'"
              type="button"
              class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium text-blue-950/80 dark:text-blue-100/80 hover:text-blue-950 dark:hover:text-white hover:bg-blue-950/[0.03] dark:hover:bg-white/[0.06] border border-blue-950/[0.14] dark:border-white/[0.16] hover:border-blue-950/30 dark:hover:border-white/30 transition-colors duration-150 focus-ring"
              :disabled="busyOrderId === order.id"
              @click="fulfill(order.id)"
            >
              <i :class="['fas', busyOrderId === order.id ? 'fa-circle-notch animate-spin' : 'fa-check']"></i>
              Mark fulfilled
            </button>
            <button
              v-if="order.status === 'pending' && order.stripe_checkout_session_id"
              type="button"
              class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium text-blue-950/80 dark:text-blue-100/80 hover:text-blue-950 dark:hover:text-white hover:bg-blue-950/[0.03] dark:hover:bg-white/[0.06] border border-blue-950/[0.14] dark:border-white/[0.16] hover:border-blue-950/30 dark:hover:border-white/30 transition-colors duration-150 focus-ring"
              title="Check the payment status with Stripe"
              :disabled="busyOrderId === order.id"
              @click="sync(order.id)"
            >
              <i :class="['fas', busyOrderId === order.id ? 'fa-circle-notch animate-spin' : 'fa-rotate']"></i>
              Refresh status
            </button>
          </div>
        </div>
        <!-- Items -->
        <div v-if="order.items.length" class="mt-3 pl-[52px]">
          <p v-for="item in order.items" :key="item.id" class="text-xs text-blue-950/60 dark:text-blue-100/60">
            {{ item.quantity }} × {{ item.product_name }} — {{ formatMoney(item.unit_price_cents * item.quantity, order.currency) }}
          </p>
        </div>
      </div>

      <p class="text-xs text-blue-950/50 dark:text-blue-100/50 text-center pt-2">
        Showing {{ store.orders.length }} of {{ store.ordersTotal }} order{{ store.ordersTotal === 1 ? '' : 's' }}
      </p>
    </div>

    <!-- Empty -->
    <EmptyState
      v-else
      icon="fas fa-receipt"
      :title="statusFilter ? 'No orders with this status' : 'No orders yet'"
      :description="statusFilter
        ? 'Try a different filter.'
        : 'When customers pay through a payment link or your app’s checkout, orders show up here.'"
      :accent="accent"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { EmptyState, LoadingSpinner } from '@/shared/components'
import OrderStatusBadge from '../components/OrderStatusBadge.vue'
import { extractError } from '../services/sellService'
import { useSellStore } from '../stores/sell'
import type { Order } from '../types'
import { accent, formatDateTime, formatMoney, ui } from '../utils/ui'

const store = useSellStore()

const statusFilter = ref('')
const busyOrderId = ref<number | null>(null)
const actionError = ref('')

const statusFilters = [
  { value: '', label: 'All' },
  { value: 'pending', label: 'Pending' },
  { value: 'paid', label: 'Paid' },
  { value: 'fulfilled', label: 'Fulfilled' },
  { value: 'canceled', label: 'Canceled' },
  { value: 'refunded', label: 'Refunded' },
]

function itemsSummary(order: Order): string {
  const first = order.items[0]
  if (!first) return 'No items'
  const extra = order.items.length - 1
  return extra > 0 ? `${first.product_name} + ${extra} more` : `${first.quantity} × ${first.product_name}`
}

async function fetchOrders() {
  actionError.value = ''
  try {
    await store.fetchOrders(statusFilter.value ? { status: statusFilter.value } : {})
  } catch (error) {
    actionError.value = extractError(error, 'Could not load orders.')
  }
}

function setFilter(value: string) {
  statusFilter.value = value
  fetchOrders()
}

async function fulfill(orderId: number) {
  busyOrderId.value = orderId
  actionError.value = ''
  try {
    await store.fulfillOrder(orderId)
  } catch (error) {
    actionError.value = extractError(error, 'Could not mark the order fulfilled.')
  } finally {
    busyOrderId.value = null
  }
}

async function sync(orderId: number) {
  busyOrderId.value = orderId
  actionError.value = ''
  try {
    await store.syncOrder(orderId)
  } catch (error) {
    actionError.value = extractError(error, 'Could not refresh the order from Stripe.')
  } finally {
    busyOrderId.value = null
  }
}

onMounted(fetchOrders)
</script>
