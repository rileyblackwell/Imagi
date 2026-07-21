<!--
  OperateDashboard.vue - The central hub: financial health, cash flow,
  what needs attention (invoices/tasks), and a pulse from the other
  workspace modules.
-->
<template>
  <div>
    <!-- Loading -->
    <div v-if="store.dashboardLoading && !dashboard" class="flex justify-center py-16">
      <div class="w-6 h-6 border-2 border-blue-200 dark:border-blue-300/30 border-t-blue-600 dark:border-t-blue-300 rounded-full animate-spin"></div>
    </div>

    <template v-else-if="dashboard">
      <!-- Headline stats -->
      <section class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div v-for="stat in statCards" :key="stat.label" class="p-5" :class="ui.card">
          <div class="flex items-center gap-2 mb-2">
            <i :class="['fas', stat.icon]" class="text-xs text-orange-600 dark:text-orange-300"></i>
            <p class="text-xs font-semibold uppercase tracking-[0.14em] text-blue-950/50 dark:text-blue-100/50">{{ stat.label }}</p>
          </div>
          <p class="text-2xl font-semibold tabular-nums" :class="stat.tone ?? 'text-blue-950 dark:text-white'">{{ stat.value }}</p>
          <p class="text-xs text-blue-950/50 dark:text-blue-100/50 mt-1">{{ stat.caption }}</p>
        </div>
      </section>

      <!-- Quick actions -->
      <section class="flex flex-wrap gap-3 mb-6">
        <router-link :to="{ name: 'operate-finance', params: { projectName: route.params.projectName }, query: { new: '1' } }" :class="ui.primaryBtn">
          <i class="fas fa-plus text-xs"></i>
          Record transaction
        </router-link>
        <router-link :to="{ name: 'operate-invoices', params: { projectName: route.params.projectName }, query: { new: '1' } }" :class="ui.secondaryBtn">
          <i class="fas fa-receipt text-xs"></i>
          New invoice
        </router-link>
        <router-link :to="{ name: 'operate-tasks', params: { projectName: route.params.projectName }, query: { new: '1' } }" :class="ui.secondaryBtn">
          <i class="fas fa-list-check text-xs"></i>
          Add task
        </router-link>
      </section>

      <!-- Cash flow -->
      <section class="p-6 mb-6" :class="ui.card">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-base font-semibold text-blue-950 dark:text-white">Cash flow</h2>
          <p class="text-xs text-blue-950/50 dark:text-blue-100/50">last {{ dashboard.cashflow.length }} months</p>
        </div>
        <CashflowChart :points="dashboard.cashflow" />
      </section>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <!-- Open invoices -->
        <section class="p-6" :class="ui.card">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-base font-semibold text-blue-950 dark:text-white">Awaiting payment</h2>
            <router-link
              :to="{ name: 'operate-invoices', params: { projectName: route.params.projectName } }"
              class="rounded-md text-sm font-medium text-blue-950/70 dark:text-blue-100/70 hover:text-blue-950 dark:hover:text-white underline decoration-blue-950/20 dark:decoration-blue-100/25 hover:decoration-blue-950/50 dark:hover:decoration-blue-100/60 underline-offset-4 transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0c0c0e]"
            >
              View all
            </router-link>
          </div>
          <div v-if="dashboard.open_invoices.length" class="space-y-3">
            <div
              v-for="invoice in dashboard.open_invoices"
              :key="invoice.id"
              class="flex items-center gap-3 p-3 rounded-xl border border-blue-200/60 dark:border-white/[0.08]"
            >
              <div class="w-9 h-9 shrink-0" :class="ui.iconTile">
                <i class="fas fa-receipt text-sm"></i>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-blue-950 dark:text-white truncate">{{ invoice.number }} · {{ invoice.customer_name }}</p>
                <p class="text-xs text-blue-950/50 dark:text-blue-100/50">
                  {{ formatMoney(invoice.total) }}<template v-if="invoice.due_date"> · due {{ formatDate(invoice.due_date) }}</template>
                </p>
              </div>
              <StatusBadge :status="invoice.is_overdue ? 'overdue' : invoice.status" />
            </div>
          </div>
          <div v-else class="py-10 text-center">
            <p class="text-sm text-blue-950/60 dark:text-blue-100/60 mb-4">No invoices awaiting payment.</p>
            <router-link :to="{ name: 'operate-invoices', params: { projectName: route.params.projectName }, query: { new: '1' } }" :class="ui.secondaryBtn">
              Create an invoice
            </router-link>
          </div>
        </section>

        <!-- Upcoming tasks -->
        <section class="p-6" :class="ui.card">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-base font-semibold text-blue-950 dark:text-white">Up next</h2>
            <router-link
              :to="{ name: 'operate-tasks', params: { projectName: route.params.projectName } }"
              class="rounded-md text-sm font-medium text-blue-950/70 dark:text-blue-100/70 hover:text-blue-950 dark:hover:text-white underline decoration-blue-950/20 dark:decoration-blue-100/25 hover:decoration-blue-950/50 dark:hover:decoration-blue-100/60 underline-offset-4 transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0c0c0e]"
            >
              View all
            </router-link>
          </div>
          <div v-if="dashboard.upcoming_tasks.length" class="space-y-3">
            <div
              v-for="task in dashboard.upcoming_tasks"
              :key="task.id"
              class="flex items-center gap-3 p-3 rounded-xl border border-blue-200/60 dark:border-white/[0.08]"
            >
              <div class="w-9 h-9 shrink-0" :class="ui.iconTile">
                <i class="fas fa-list-check text-sm"></i>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-blue-950 dark:text-white truncate">{{ task.title }}</p>
                <p class="text-xs" :class="task.is_overdue ? 'text-red-600 dark:text-red-300' : 'text-blue-950/50 dark:text-blue-100/50'">
                  <template v-if="task.due_date">{{ task.is_overdue ? 'overdue — ' : 'due ' }}{{ formatDate(task.due_date) }}</template>
                  <template v-else>no due date</template>
                  · {{ task.priority }} priority
                </p>
              </div>
              <StatusBadge :status="task.status" />
            </div>
          </div>
          <div v-else class="py-10 text-center">
            <p class="text-sm text-blue-950/60 dark:text-blue-100/60 mb-4">Nothing on the list. Add the work that keeps the business running.</p>
            <router-link :to="{ name: 'operate-tasks', params: { projectName: route.params.projectName }, query: { new: '1' } }" :class="ui.secondaryBtn">
              Add a task
            </router-link>
          </div>
        </section>
      </div>

      <!-- Across your business -->
      <section class="p-6" :class="ui.card">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-base font-semibold text-blue-950 dark:text-white">Across your business</h2>
          <div class="flex items-center gap-4">
            <router-link
              :to="{ name: 'sell-overview', params: { projectName: route.params.projectName } }"
              class="rounded-md text-sm font-medium text-blue-950/70 dark:text-blue-100/70 hover:text-blue-950 dark:hover:text-white underline decoration-blue-950/20 dark:decoration-blue-100/25 hover:decoration-blue-950/50 dark:hover:decoration-blue-100/60 underline-offset-4 transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0c0c0e]"
            >
              Open Sell
            </router-link>
            <router-link
              :to="{ name: 'marketing-overview', params: { projectName: route.params.projectName } }"
              class="rounded-md text-sm font-medium text-blue-950/70 dark:text-blue-100/70 hover:text-blue-950 dark:hover:text-white underline decoration-blue-950/20 dark:decoration-blue-100/25 hover:decoration-blue-950/50 dark:hover:decoration-blue-100/60 underline-offset-4 transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0c0c0e]"
            >
              Open Market
            </router-link>
          </div>
        </div>
        <div class="grid grid-cols-2 lg:grid-cols-3 gap-4">
          <div v-for="stat in pulseCards" :key="stat.label" class="p-4 rounded-xl border border-blue-200/60 dark:border-white/[0.08]">
            <div class="flex items-center gap-2 mb-1.5">
              <i :class="['fas', stat.icon, stat.iconClass]" class="text-xs"></i>
              <p class="text-xs font-semibold uppercase tracking-[0.14em] text-blue-950/50 dark:text-blue-100/50">{{ stat.label }}</p>
            </div>
            <p class="text-xl font-semibold text-blue-950 dark:text-white tabular-nums">{{ stat.value }}</p>
            <p class="text-xs text-blue-950/50 dark:text-blue-100/50 mt-0.5">{{ stat.caption }}</p>
          </div>
        </div>
        <p v-if="!dashboard.sell.configured || !dashboard.marketing.configured" class="text-xs text-blue-950/50 dark:text-blue-100/50 mt-3">
          <template v-if="!dashboard.sell.configured">Connect Stripe in the Sell workspace to start taking payments.</template>
          <template v-if="!dashboard.sell.configured && !dashboard.marketing.configured"> · </template>
          <template v-if="!dashboard.marketing.configured">Connect Twilio in the Market workspace to start reaching customers.</template>
        </p>
      </section>
    </template>

    <div v-else-if="loadError" :class="ui.errorBox">{{ loadError }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import CashflowChart from '../components/CashflowChart.vue'
import StatusBadge from '../components/StatusBadge.vue'
import { extractError } from '../services/operateService'
import { useOperateStore } from '../stores/operate'
import { formatDate, formatMoney, ui } from '../utils/ui'

const route = useRoute()
const store = useOperateStore()
const loadError = ref('')

const dashboard = computed(() => store.dashboard)

const statCards = computed(() => {
  const data = dashboard.value
  if (!data) return []
  const net = data.finance.net_30d
  return [
    {
      label: 'Income',
      icon: 'fa-arrow-trend-up',
      value: formatMoney(data.finance.income_30d),
      caption: 'last 30 days',
    },
    {
      label: 'Expenses',
      icon: 'fa-arrow-trend-down',
      value: formatMoney(data.finance.expenses_30d),
      caption: 'last 30 days',
    },
    {
      label: 'Net',
      icon: 'fa-scale-balanced',
      value: formatMoney(net),
      caption: 'last 30 days',
      tone: net < 0 ? 'text-red-600 dark:text-red-300' : 'text-emerald-700 dark:text-emerald-300',
    },
    {
      label: 'Outstanding',
      icon: 'fa-file-invoice-dollar',
      value: formatMoney(data.invoices.outstanding_total),
      caption: data.invoices.overdue_count
        ? `${data.invoices.overdue_count} overdue invoice${data.invoices.overdue_count === 1 ? '' : 's'}`
        : `${data.invoices.outstanding_count} invoice${data.invoices.outstanding_count === 1 ? '' : 's'} awaiting payment`,
      tone: data.invoices.overdue_count ? 'text-red-600 dark:text-red-300' : undefined,
    },
  ]
})

const SELL_ICON = 'text-emerald-600 dark:text-emerald-300'
const MARKET_ICON = 'text-violet-600 dark:text-violet-300'

const pulseCards = computed(() => {
  const data = dashboard.value
  if (!data) return []
  return [
    {
      label: 'Sales revenue',
      icon: 'fa-hand-holding-dollar',
      iconClass: SELL_ICON,
      value: formatMoney(data.sell.revenue_30d, data.sell.currency),
      caption: 'Stripe, last 30 days',
    },
    {
      label: 'Orders',
      icon: 'fa-receipt',
      iconClass: SELL_ICON,
      value: data.sell.orders_paid_30d.toLocaleString(),
      caption: data.sell.orders_pending
        ? `${data.sell.orders_pending} awaiting payment`
        : 'paid, last 30 days',
    },
    {
      label: 'Customers',
      icon: 'fa-user-group',
      iconClass: SELL_ICON,
      value: data.sell.customers_total.toLocaleString(),
      caption: `${data.sell.products_active} active product${data.sell.products_active === 1 ? '' : 's'}`,
    },
    {
      label: 'Audience',
      icon: 'fa-address-book',
      iconClass: MARKET_ICON,
      value: data.marketing.contacts_total.toLocaleString(),
      caption: `${data.marketing.contacts_subscribed.toLocaleString()} subscribed`,
    },
    {
      label: 'Messages',
      icon: 'fa-paper-plane',
      iconClass: MARKET_ICON,
      value: data.marketing.messages_sent_30d.toLocaleString(),
      caption: 'sent, last 30 days',
    },
    {
      label: 'Replies',
      icon: 'fa-reply',
      iconClass: MARKET_ICON,
      value: data.marketing.replies_30d.toLocaleString(),
      caption: `${data.marketing.campaigns_active} active campaign${data.marketing.campaigns_active === 1 ? '' : 's'}`,
    },
  ]
})

onMounted(async () => {
  try {
    await store.fetchDashboard()
  } catch (error) {
    loadError.value = extractError(error, 'Could not load the operate dashboard.')
  }
})
</script>
