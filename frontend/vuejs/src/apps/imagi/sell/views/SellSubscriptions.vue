<!--
  SellSubscriptions.vue - Customers' plans (fixed and pay as you go), as
  Stripe reports them: who's on which plan, its status, when it renews, and
  the usage reported in the last 30 days.
-->
<template>
  <div>
    <div class="flex flex-wrap items-center gap-2 mb-6">
      <button
        v-for="option in filters"
        :key="option.value"
        type="button"
        class="px-3.5 py-1.5 rounded-full text-xs font-semibold uppercase tracking-[0.1em] border transition-colors duration-150 focus-ring"
        :class="filter === option.value ? ui.chipOn : ui.chipOff"
        @click="setFilter(option.value)"
      >
        {{ option.label }}
      </button>
    </div>

    <div v-if="loadError" class="mb-4" :class="ui.errorBox">{{ loadError }}</div>

    <LoadingSpinner v-if="store.subscriptionsLoading && !store.subscriptions.length" />

    <div v-else-if="store.subscriptions.length" class="overflow-x-auto" :class="ui.card">
      <table class="w-full min-w-[640px]">
        <thead class="border-b border-[color:var(--sl-line)] text-left">
          <tr>
            <th :class="ui.tableHead">Customer</th>
            <th :class="ui.tableHead">Plan</th>
            <th :class="ui.tableHead">Status</th>
            <th :class="ui.tableHead">Renews</th>
            <th :class="ui.tableHead" class="text-right">Usage, 30 days</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-[color:var(--sl-line)]">
          <tr v-for="sub in store.subscriptions" :key="sub.id">
            <td :class="ui.tableCell" class="truncate max-w-[16rem]">{{ sub.customer_email || 'Unknown' }}</td>
            <td :class="ui.tableCell">
              {{ sub.product_name || 'Plan' }}
              <span v-if="sub.pricing_model === 'usage'" :class="ui.hintText"> · pay as you go</span>
            </td>
            <td :class="ui.tableCell">
              <span
                class="inline-flex items-center px-2.5 py-0.5 rounded-full border text-[11px] font-semibold uppercase tracking-[0.1em] whitespace-nowrap"
                :class="statusTone(sub)"
              >
                {{ statusLabel(sub) }}
              </span>
            </td>
            <td :class="ui.tableCell" class="whitespace-nowrap">
              {{ sub.current_period_end && sub.is_active ? formatDate(sub.current_period_end) : '—' }}
            </td>
            <td :class="ui.tableCell" class="text-right tabular-nums">
              {{ sub.pricing_model === 'usage' ? sub.usage_units_30d.toLocaleString() : '—' }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <EmptyState
      v-else
      icon="fas fa-arrows-rotate"
      title="No subscribers yet"
      description="When customers subscribe from your app's plans page, they show up here with their plan, its status and when it renews."
      :accent="accent"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { EmptyState, LoadingSpinner } from '@/shared/components'
import { statusTones } from '@/shared/styles'
import { extractError } from '../services/sellService'
import { useSellStore } from '../stores/sell'
import type { Subscription } from '../types'
import { accent, ui } from '../utils/ui'

const store = useSellStore()
const filter = ref('active')
const loadError = ref('')

const filters = [
  { value: 'active', label: 'Active' },
  { value: '', label: 'All' },
  { value: 'canceled', label: 'Canceled' },
]

const LABELS: Record<string, string> = {
  active: 'Active',
  trialing: 'Trial',
  past_due: 'Past due',
  canceled: 'Canceled',
  unpaid: 'Unpaid',
  incomplete: 'Incomplete',
  incomplete_expired: 'Expired',
  paused: 'Paused',
}

function statusLabel(sub: Subscription): string {
  if (sub.is_active && sub.cancel_at_period_end) return 'Ends soon'
  return LABELS[sub.status] || sub.status
}

function statusTone(sub: Subscription): string {
  if (sub.status === 'past_due' || sub.status === 'unpaid') return statusTones.danger
  if (sub.is_active && sub.cancel_at_period_end) return statusTones.pending
  if (sub.is_active) return statusTones.success
  return statusTones.neutral
}

function formatDate(value: string): string {
  return new Date(value).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
}

async function load() {
  loadError.value = ''
  try {
    await store.fetchSubscriptions(filter.value ? { status: filter.value } : {})
  } catch (error) {
    loadError.value = extractError(error, 'Could not load subscriptions.')
  }
}

function setFilter(value: string) {
  filter.value = value
  load()
}

onMounted(load)
</script>
