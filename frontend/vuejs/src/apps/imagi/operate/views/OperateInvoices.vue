<!--
  OperateInvoices.vue - Invoice list with lifecycle actions: draft -> sent ->
  paid (which records the income in the ledger), with void as an off-ramp.
-->
<template>
  <div>
    <!-- Toolbar -->
    <div class="flex flex-col sm:flex-row gap-3 mb-6">
      <div class="relative flex-1">
        <i class="fas fa-magnifying-glass absolute left-3.5 top-1/2 -translate-y-1/2 text-xs text-blue-950/40 dark:text-blue-100/30"></i>
        <input
          v-model="search"
          type="search"
          placeholder="Search by number or customer..."
          class="pl-9"
          :class="ui.input"
          @input="debouncedReload"
        />
      </div>
      <select v-model="statusFilter" :class="ui.input" class="sm:w-44" @change="reload">
        <option value="">All statuses</option>
        <option value="draft">Draft</option>
        <option value="sent">Sent</option>
        <option value="overdue">Overdue</option>
        <option value="paid">Paid</option>
        <option value="void">Void</option>
      </select>
      <button type="button" :class="ui.primaryBtn" @click="openCreate">
        <i class="fas fa-plus text-xs"></i>
        New invoice
      </button>
    </div>

    <div v-if="loadError" :class="ui.errorBox" class="mb-6">{{ loadError }}</div>
    <div v-if="actionError" :class="ui.errorBox" class="mb-6">{{ actionError }}</div>

    <!-- Loading -->
    <div v-if="store.invoicesLoading && !store.invoices.length" class="flex justify-center py-16">
      <div class="w-6 h-6 border-2 border-blue-200 dark:border-blue-300/30 border-t-blue-600 dark:border-t-blue-300 rounded-full animate-spin"></div>
    </div>

    <!-- List -->
    <div v-else-if="store.invoices.length" class="space-y-3">
      <section
        v-for="invoice in store.invoices"
        :key="invoice.id"
        class="p-5"
        :class="ui.card"
      >
        <div class="flex flex-col sm:flex-row sm:items-center gap-4">
          <div class="w-10 h-10 shrink-0" :class="ui.iconTile">
            <i class="fas fa-receipt"></i>
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex flex-wrap items-center gap-2 mb-0.5">
              <p class="text-sm font-semibold text-blue-950 dark:text-white">{{ invoice.number }}</p>
              <StatusBadge :status="invoice.is_overdue ? 'overdue' : invoice.status" />
            </div>
            <p class="text-sm text-blue-950/70 dark:text-blue-100/70 truncate">{{ invoice.customer_name }}</p>
            <p class="text-xs text-blue-950/50 dark:text-blue-100/50 mt-0.5">
              Issued {{ formatDate(invoice.issue_date) }}
              <template v-if="invoice.due_date"> · due {{ formatDate(invoice.due_date) }}</template>
              <template v-if="invoice.paid_at"> · paid {{ formatDateTime(invoice.paid_at) }}</template>
            </p>
          </div>
          <p class="text-lg font-semibold text-blue-950 dark:text-white tabular-nums whitespace-nowrap">{{ formatMoney(invoice.total) }}</p>
          <div class="flex flex-wrap items-center gap-2">
            <!-- Lifecycle actions -->
            <button v-if="invoice.status === 'draft'" type="button" :class="ui.primaryBtn" :disabled="busyId === invoice.id" @click="setStatus(invoice, 'sent')">
              <i class="fas fa-paper-plane text-xs"></i>
              Mark sent
            </button>
            <button v-if="invoice.status === 'sent'" type="button" :class="ui.primaryBtn" :disabled="busyId === invoice.id" @click="setStatus(invoice, 'paid')">
              <i class="fas fa-circle-check text-xs"></i>
              Mark paid
            </button>
            <button v-if="invoice.status === 'draft'" type="button" :class="ui.secondaryBtn" @click="openEdit(invoice)">
              <i class="fas fa-pen text-xs"></i>
              Edit
            </button>
            <button v-if="invoice.status === 'void'" type="button" :class="ui.secondaryBtn" :disabled="busyId === invoice.id" @click="setStatus(invoice, 'draft')">
              <i class="fas fa-rotate-left text-xs"></i>
              Restore draft
            </button>
            <!-- Overflow: void/delete -->
            <button
              v-if="invoice.status === 'draft' || invoice.status === 'sent'"
              type="button"
              class="w-9 h-9 rounded-full flex items-center justify-center border border-blue-950/[0.14] dark:border-white/[0.16] text-blue-950/40 dark:text-blue-100/40 hover:text-red-600 dark:hover:text-red-300 hover:border-red-300 dark:hover:border-red-400/40 hover:bg-red-50 dark:hover:bg-red-500/10 transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0c0c0e]"
              :disabled="busyId === invoice.id"
              aria-label="Void invoice"
              title="Void invoice"
              @click="setStatus(invoice, 'void')"
            >
              <i class="fas fa-ban text-xs"></i>
            </button>
            <button
              v-if="invoice.status === 'draft' || invoice.status === 'void'"
              type="button"
              class="w-9 h-9 rounded-full flex items-center justify-center border border-blue-950/[0.14] dark:border-white/[0.16] text-blue-950/40 dark:text-blue-100/40 hover:text-red-600 dark:hover:text-red-300 hover:border-red-300 dark:hover:border-red-400/40 hover:bg-red-50 dark:hover:bg-red-500/10 transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0c0c0e]"
              aria-label="Delete invoice"
              title="Delete invoice"
              @click="confirmDelete(invoice)"
            >
              <i class="fas fa-trash-can text-xs"></i>
            </button>
          </div>
        </div>

        <!-- Line items -->
        <details v-if="invoice.line_items.length" class="mt-3">
          <summary class="rounded-md text-xs font-medium text-blue-950/50 dark:text-blue-100/50 cursor-pointer hover:text-blue-950 dark:hover:text-white transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0c0c0e]">
            {{ invoice.line_items.length }} line item{{ invoice.line_items.length === 1 ? '' : 's' }}
          </summary>
          <div class="mt-2 rounded-xl border border-blue-200/60 dark:border-white/[0.08] divide-y divide-blue-200/60 dark:divide-white/[0.08]">
            <div
              v-for="(item, index) in invoice.line_items"
              :key="index"
              class="flex items-center justify-between gap-4 px-4 py-2.5 text-sm"
            >
              <span class="text-blue-950/80 dark:text-blue-100/80 truncate">{{ item.description }}</span>
              <span class="text-blue-950/60 dark:text-blue-100/60 tabular-nums whitespace-nowrap">
                {{ item.quantity }} × {{ formatMoney(item.unit_price) }}
              </span>
            </div>
          </div>
        </details>
      </section>
    </div>

    <!-- Empty -->
    <section v-else class="py-16 text-center" :class="ui.card">
      <div class="w-14 h-14 mx-auto mb-4 text-xl" :class="ui.iconTile">
        <i class="fas fa-receipt"></i>
      </div>
      <h3 class="text-lg font-semibold text-blue-950 dark:text-white mb-2">No invoices yet</h3>
      <p class="text-sm text-blue-950/60 dark:text-blue-100/60 mb-6 max-w-sm mx-auto">
        Bill your customers and track what's owed. Marking an invoice paid records the income in your ledger.
      </p>
      <button type="button" :class="ui.primaryBtn" @click="openCreate">
        <i class="fas fa-plus text-xs"></i>
        Create your first invoice
      </button>
    </section>

    <!-- Create/edit modal -->
    <OperateModal
      v-if="showForm"
      :title="editing ? `Edit ${editing.number}` : 'New invoice'"
      wide
      @close="closeForm"
    >
      <InvoiceForm :invoice="editing" @close="closeForm" @saved="onSaved" />
    </OperateModal>

    <!-- Delete confirm -->
    <OperateModal v-if="deleting" title="Delete invoice" @close="deleting = null">
      <p class="text-sm text-blue-950/70 dark:text-blue-100/70 mb-6">
        Delete {{ deleting.number }} for {{ deleting.customer_name }}? This can't be undone.
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
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import InvoiceForm from '../components/InvoiceForm.vue'
import OperateModal from '../components/OperateModal.vue'
import StatusBadge from '../components/StatusBadge.vue'
import { extractError } from '../services/operateService'
import { useOperateStore } from '../stores/operate'
import type { Invoice, InvoiceStatus } from '../types'
import { formatDate, formatDateTime, formatMoney, ui } from '../utils/ui'

const route = useRoute()
const router = useRouter()
const store = useOperateStore()

const search = ref('')
const statusFilter = ref('')
const loadError = ref('')
const actionError = ref('')
const busyId = ref<number | null>(null)
const showForm = ref(false)
const editing = ref<Invoice | null>(null)
const deleting = ref<Invoice | null>(null)
const deleteBusy = ref(false)
const deleteError = ref('')

let searchTimer: ReturnType<typeof setTimeout> | undefined

function debouncedReload() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(reload, 300)
}

onBeforeUnmount(() => clearTimeout(searchTimer))

async function reload() {
  loadError.value = ''
  try {
    await store.fetchInvoices({
      search: search.value.trim() || undefined,
      status: statusFilter.value || undefined,
    })
  } catch (error) {
    loadError.value = extractError(error, 'Could not load invoices.')
  }
}

async function setStatus(invoice: Invoice, status: InvoiceStatus) {
  actionError.value = ''
  busyId.value = invoice.id
  try {
    await store.setInvoiceStatus(invoice.id, status)
  } catch (error) {
    actionError.value = extractError(error, 'Could not update the invoice.')
  } finally {
    busyId.value = null
  }
}

function openCreate() {
  editing.value = null
  showForm.value = true
}

function openEdit(invoice: Invoice) {
  editing.value = invoice
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

function confirmDelete(invoice: Invoice) {
  deleteError.value = ''
  deleting.value = invoice
}

async function doDelete() {
  if (!deleting.value) return
  deleteBusy.value = true
  deleteError.value = ''
  try {
    await store.deleteInvoice(deleting.value.id)
    deleting.value = null
  } catch (error) {
    deleteError.value = extractError(error, 'Could not delete the invoice.')
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
