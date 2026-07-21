<!--
  SellOverview.vue - Sell dashboard: revenue and order stats for the last
  30 days, plus the most recent orders.
-->
<template>
  <div>
    <!-- Loading -->
    <div v-if="store.overviewLoading && !overview" class="flex justify-center py-16">
      <div class="w-6 h-6 border-2 border-emerald-200 dark:border-emerald-300/30 border-t-emerald-600 dark:border-t-emerald-300 rounded-full animate-spin"></div>
    </div>

    <template v-else-if="overview">
      <!-- Stats -->
      <section class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div v-for="stat in statCards" :key="stat.label" class="p-5" :class="ui.card">
          <div class="flex items-center gap-2 mb-2">
            <i :class="['fas', stat.icon]" class="text-xs text-emerald-600 dark:text-emerald-300"></i>
            <p class="text-xs font-semibold uppercase tracking-[0.14em] text-blue-950/50 dark:text-blue-100/50">{{ stat.label }}</p>
          </div>
          <p class="text-2xl font-semibold text-blue-950 dark:text-white tabular-nums">{{ stat.value }}</p>
          <p class="text-xs text-blue-950/50 dark:text-blue-100/50 mt-1">{{ stat.caption }}</p>
        </div>
      </section>

      <!-- Quick actions -->
      <section class="flex flex-wrap gap-3 mb-8">
        <router-link :to="{ name: 'sell-products', params: { projectName: route.params.projectName }, query: { new: '1' } }" :class="ui.primaryBtn">
          <i class="fas fa-plus text-xs"></i>
          Add product
        </router-link>
        <router-link :to="{ name: 'sell-orders', params: { projectName: route.params.projectName } }" :class="ui.secondaryBtn">
          <i class="fas fa-receipt text-xs"></i>
          View orders
        </router-link>
        <router-link :to="{ name: 'sell-customers', params: { projectName: route.params.projectName } }" :class="ui.secondaryBtn">
          <i class="fas fa-address-book text-xs"></i>
          Customers
        </router-link>
        <router-link :to="{ name: 'sell-payments', params: { projectName: route.params.projectName } }" :class="ui.secondaryBtn">
          <i class="fas fa-credit-card text-xs"></i>
          Add payments to your app
        </router-link>
        <a
          v-if="overview.stats.configured"
          href="https://dashboard.stripe.com"
          target="_blank"
          rel="noopener noreferrer"
          :class="ui.secondaryBtn"
        >
          <i class="fab fa-stripe-s text-xs"></i>
          Open Stripe dashboard
          <i class="fas fa-arrow-up-right-from-square text-[10px] opacity-60"></i>
        </a>
      </section>

      <!-- Recent orders -->
      <section class="p-6" :class="ui.card">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-base font-semibold text-blue-950 dark:text-white">Recent orders</h2>
          <router-link
            :to="{ name: 'sell-orders', params: { projectName: route.params.projectName } }"
            class="rounded-sm text-sm font-medium text-blue-950/70 dark:text-blue-100/70 hover:text-blue-950 dark:hover:text-white underline underline-offset-4 decoration-blue-950/25 dark:decoration-blue-100/30 hover:decoration-blue-950/60 dark:hover:decoration-blue-100/70 transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0c0c0e]"
          >
            View all
          </router-link>
        </div>
        <div v-if="overview.recent_orders.length" class="space-y-3">
          <div
            v-for="order in overview.recent_orders"
            :key="order.id"
            class="flex items-center gap-3 p-3 rounded-xl border border-blue-200/60 dark:border-white/[0.08]"
          >
            <div class="w-9 h-9 shrink-0" :class="ui.iconTile">
              <i class="fas fa-receipt text-sm"></i>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-blue-950 dark:text-white truncate">
                {{ orderSummary(order) }}
              </p>
              <p class="text-xs text-blue-950/50 dark:text-blue-100/50">
                {{ order.customer_email || 'No email yet' }} · {{ formatDateTime(order.created_at) }}
              </p>
            </div>
            <span class="text-sm font-semibold text-blue-950 dark:text-white tabular-nums">
              {{ formatMoney(order.amount_total_cents, order.currency) }}
            </span>
            <OrderStatusBadge :status="order.status" />
          </div>
        </div>
        <div v-else class="py-10 text-center">
          <p class="text-sm text-blue-950/60 dark:text-blue-100/60 mb-4">
            No orders yet. Add a product and share its payment link, or hook your app up to the storefront API.
          </p>
          <router-link :to="{ name: 'sell-products', params: { projectName: route.params.projectName }, query: { new: '1' } }" :class="ui.secondaryBtn">
            Add your first product
          </router-link>
        </div>
      </section>
    </template>

    <div v-else-if="loadError" :class="ui.errorBox">{{ loadError }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import OrderStatusBadge from '../components/OrderStatusBadge.vue'
import { extractError } from '../services/sellService'
import { useSellStore } from '../stores/sell'
import type { Order } from '../types'
import { formatDateTime, formatMoney, ui } from '../utils/ui'

const route = useRoute()
const store = useSellStore()
const loadError = ref('')

const overview = computed(() => store.overview)

function orderSummary(order: Order): string {
  const first = order.items[0]
  if (!first) return `Order #${order.id}`
  const extra = order.items.length - 1
  return extra > 0 ? `${first.product_name} + ${extra} more` : `${first.quantity} × ${first.product_name}`
}

const statCards = computed(() => {
  const stats = overview.value?.stats
  if (!stats) return []
  return [
    {
      label: 'Revenue',
      icon: 'fa-sack-dollar',
      value: formatMoney(stats.revenue_cents_30d, stats.currency),
      caption: 'last 30 days',
    },
    {
      label: 'Paid orders',
      icon: 'fa-circle-check',
      value: stats.orders_paid_30d.toLocaleString(),
      caption: 'last 30 days',
    },
    {
      label: 'Products',
      icon: 'fa-box-open',
      value: stats.products_active.toLocaleString(),
      caption: `${stats.products_total.toLocaleString()} in catalog`,
    },
    {
      label: 'Customers',
      icon: 'fa-address-book',
      value: stats.customers_total.toLocaleString(),
      caption: `${stats.orders_pending} pending order${stats.orders_pending === 1 ? '' : 's'}`,
    },
  ]
})

onMounted(async () => {
  try {
    await store.fetchOverview()
  } catch (error) {
    loadError.value = extractError(error, 'Could not load the sell overview.')
  }
})
</script>
