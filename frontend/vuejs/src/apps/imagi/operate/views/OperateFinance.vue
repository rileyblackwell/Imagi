<!--
  OperateFinance.vue - The financial ledger: filterable list of income and
  expense transactions with a running summary for the current filter.
-->
<template>
  <div>
    <!-- Summary for the current filter -->
    <section v-if="summary" class="grid grid-cols-3 gap-4 mb-6">
      <div class="p-5" :class="ui.card">
        <p class="text-xs font-semibold uppercase tracking-[0.14em] text-blue-950/50 dark:text-blue-100/50 mb-2">Income</p>
        <p class="text-2xl font-semibold text-emerald-700 dark:text-emerald-300 tabular-nums">{{ formatMoney(summary.income) }}</p>
      </div>
      <div class="p-5" :class="ui.card">
        <p class="text-xs font-semibold uppercase tracking-[0.14em] text-blue-950/50 dark:text-blue-100/50 mb-2">Expenses</p>
        <p class="text-2xl font-semibold text-red-600 dark:text-red-300 tabular-nums">{{ formatMoney(summary.expenses) }}</p>
      </div>
      <div class="p-5" :class="ui.card">
        <p class="text-xs font-semibold uppercase tracking-[0.14em] text-blue-950/50 dark:text-blue-100/50 mb-2">Net</p>
        <p class="text-2xl font-semibold tabular-nums" :class="summary.net < 0 ? 'text-red-600 dark:text-red-300' : 'text-blue-950 dark:text-white'">{{ formatMoney(summary.net) }}</p>
      </div>
    </section>

    <!-- Toolbar -->
    <div class="flex flex-col sm:flex-row gap-3 mb-6">
      <div class="relative flex-1">
        <i class="fas fa-magnifying-glass absolute left-3.5 top-1/2 -translate-y-1/2 text-xs text-blue-950/40 dark:text-white/30"></i>
        <input
          v-model="search"
          type="search"
          placeholder="Search the ledger..."
          class="pl-9"
          :class="ui.input"
          @input="debouncedReload"
        />
      </div>
      <select v-model="kindFilter" :class="ui.input" class="sm:w-44" @change="reload">
        <option value="">All types</option>
        <option value="income">Income</option>
        <option value="expense">Expenses</option>
      </select>
      <button type="button" :class="ui.primaryBtn" @click="openCreate">
        <i class="fas fa-plus text-xs"></i>
        Record transaction
      </button>
    </div>

    <div v-if="loadError" :class="ui.errorBox" class="mb-6">{{ loadError }}</div>

    <!-- Loading -->
    <div v-if="store.transactionsLoading && !store.transactions.length" class="flex justify-center py-16">
      <div class="w-6 h-6 border-2 border-amber-200 dark:border-amber-300/30 border-t-amber-600 dark:border-t-amber-300 rounded-full animate-spin"></div>
    </div>

    <!-- Ledger -->
    <section v-else-if="store.transactions.length" :class="ui.card" class="divide-y divide-blue-200/60 dark:divide-white/[0.08]">
      <div
        v-for="transaction in store.transactions"
        :key="transaction.id"
        class="flex items-center gap-4 px-5 py-4"
      >
        <div
          class="w-9 h-9 shrink-0 rounded-xl flex items-center justify-center border"
          :class="transaction.kind === 'income'
            ? 'bg-emerald-50 dark:bg-emerald-500/10 border-emerald-200/60 dark:border-emerald-400/25 text-emerald-600 dark:text-emerald-300'
            : 'bg-red-50 dark:bg-red-500/10 border-red-200/60 dark:border-red-400/25 text-red-600 dark:text-red-300'"
        >
          <i :class="['fas', transaction.kind === 'income' ? 'fa-arrow-trend-up' : 'fa-arrow-trend-down']" class="text-sm"></i>
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-blue-950 dark:text-white truncate">{{ transaction.description }}</p>
          <p class="text-xs text-blue-950/50 dark:text-blue-100/50">
            {{ CATEGORY_LABELS[transaction.category] ?? transaction.category }} · {{ formatDate(transaction.occurred_on) }}
            <template v-if="transaction.invoice_number"> · from {{ transaction.invoice_number }}</template>
          </p>
        </div>
        <p
          class="text-sm font-semibold tabular-nums whitespace-nowrap"
          :class="transaction.kind === 'income' ? 'text-emerald-700 dark:text-emerald-300' : 'text-red-600 dark:text-red-300'"
        >
          {{ transaction.kind === 'income' ? '+' : '−' }}{{ formatMoney(transaction.amount) }}
        </p>
        <div class="flex items-center gap-1">
          <button
            type="button"
            class="w-8 h-8 rounded-lg flex items-center justify-center text-blue-950/40 dark:text-white/40 hover:text-blue-950 dark:hover:text-white hover:bg-blue-50 dark:hover:bg-white/[0.08] transition-colors duration-200"
            aria-label="Edit transaction"
            @click="openEdit(transaction)"
          >
            <i class="fas fa-pen text-xs"></i>
          </button>
          <button
            type="button"
            class="w-8 h-8 rounded-lg flex items-center justify-center text-blue-950/40 dark:text-white/40 hover:text-red-600 dark:hover:text-red-300 hover:bg-red-50 dark:hover:bg-red-500/10 transition-colors duration-200"
            aria-label="Delete transaction"
            @click="confirmDelete(transaction)"
          >
            <i class="fas fa-trash-can text-xs"></i>
          </button>
        </div>
      </div>
    </section>

    <!-- Empty -->
    <section v-else class="py-16 text-center" :class="ui.card">
      <div class="w-14 h-14 mx-auto mb-4 text-xl" :class="ui.iconTile">
        <i class="fas fa-file-invoice-dollar"></i>
      </div>
      <h3 class="text-lg font-semibold text-blue-950 dark:text-white mb-2">Your ledger is empty</h3>
      <p class="text-sm text-blue-950/60 dark:text-blue-100/60 mb-6 max-w-sm mx-auto">
        Track money in and out of the business. Marking invoices paid also records income here automatically.
      </p>
      <button type="button" :class="ui.primaryBtn" @click="openCreate">
        <i class="fas fa-plus text-xs"></i>
        Record your first transaction
      </button>
    </section>

    <!-- Create/edit modal -->
    <OperateModal
      v-if="showForm"
      :title="editing ? 'Edit transaction' : 'Record transaction'"
      @close="closeForm"
    >
      <TransactionForm :transaction="editing" @close="closeForm" @saved="onSaved" />
    </OperateModal>

    <!-- Delete confirm -->
    <OperateModal v-if="deleting" title="Delete transaction" @close="deleting = null">
      <p class="text-sm text-blue-950/70 dark:text-blue-100/70 mb-6">
        Remove "{{ deleting.description }}" ({{ formatMoney(deleting.amount) }}) from the ledger? This can't be undone.
      </p>
      <div v-if="deleteError" :class="ui.errorBox" class="mb-4">{{ deleteError }}</div>
      <div class="flex justify-end gap-3">
        <button type="button" :class="ui.secondaryBtn" @click="deleting = null">Cancel</button>
        <button type="button" :class="ui.dangerBtn" :disabled="deleteBusy" @click="doDelete">
          <i v-if="deleteBusy" class="fas fa-circle-notch fa-spin text-xs"></i>
          Delete
        </button>
      </div>
    </OperateModal>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import OperateModal from '../components/OperateModal.vue'
import TransactionForm from '../components/TransactionForm.vue'
import { extractError } from '../services/operateService'
import { useOperateStore } from '../stores/operate'
import type { Transaction } from '../types'
import { CATEGORY_LABELS } from '../types'
import { formatDate, formatMoney, ui } from '../utils/ui'

const route = useRoute()
const router = useRouter()
const store = useOperateStore()

const search = ref('')
const kindFilter = ref('')
const loadError = ref('')
const showForm = ref(false)
const editing = ref<Transaction | null>(null)
const deleting = ref<Transaction | null>(null)
const deleteBusy = ref(false)
const deleteError = ref('')

const summary = computed(() => store.transactionsSummary)

let searchTimer: ReturnType<typeof setTimeout> | undefined

function debouncedReload() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(reload, 300)
}

onBeforeUnmount(() => clearTimeout(searchTimer))

async function reload() {
  loadError.value = ''
  try {
    await store.fetchTransactions({
      search: search.value.trim() || undefined,
      kind: kindFilter.value || undefined,
    })
  } catch (error) {
    loadError.value = extractError(error, 'Could not load the ledger.')
  }
}

function openCreate() {
  editing.value = null
  showForm.value = true
}

function openEdit(transaction: Transaction) {
  editing.value = transaction
  showForm.value = true
}

function closeForm() {
  showForm.value = false
  editing.value = null
}

async function onSaved() {
  closeForm()
  await reload()
}

function confirmDelete(transaction: Transaction) {
  deleteError.value = ''
  deleting.value = transaction
}

async function doDelete() {
  if (!deleting.value) return
  deleteBusy.value = true
  deleteError.value = ''
  try {
    await store.deleteTransaction(deleting.value.id)
    deleting.value = null
    await reload()
  } catch (error) {
    deleteError.value = extractError(error, 'Could not delete the transaction.')
  } finally {
    deleteBusy.value = false
  }
}

onMounted(async () => {
  await reload()
  // ?new=1 (from the dashboard quick action) opens the create form.
  if (route.query.new === '1') {
    openCreate()
    router.replace({ query: { ...route.query, new: undefined } })
  }
})
</script>
