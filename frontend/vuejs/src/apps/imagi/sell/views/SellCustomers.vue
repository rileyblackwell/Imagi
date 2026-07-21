<!--
  SellCustomers.vue - Lightweight CRM: everyone who bought through checkout,
  plus manually added contacts, with order history per customer.
-->
<template>
  <div>
    <!-- Toolbar -->
    <div class="flex flex-col sm:flex-row sm:items-center gap-3 mb-6">
      <div class="relative flex-1 max-w-sm">
        <i class="fas fa-magnifying-glass absolute left-3.5 top-1/2 -translate-y-1/2 text-xs text-blue-950/40 dark:text-blue-100/30"></i>
        <input
          v-model="search"
          type="search"
          placeholder="Search customers…"
          class="pl-9"
          :class="ui.input"
          @input="debouncedFetch"
        />
      </div>
      <div class="flex-1"></div>
      <button type="button" :class="ui.primaryBtn" @click="openCreate">
        <i class="fas fa-user-plus text-xs"></i>
        Add customer
      </button>
    </div>

    <div v-if="actionError" class="mb-4" :class="ui.errorBox">{{ actionError }}</div>

    <!-- Loading -->
    <div v-if="store.customersLoading && !store.customers.length" class="flex justify-center py-16">
      <div class="w-6 h-6 border-2 border-emerald-200 dark:border-emerald-300/30 border-t-emerald-600 dark:border-t-emerald-300 rounded-full animate-spin"></div>
    </div>

    <!-- Customers -->
    <div v-else-if="store.customers.length" class="space-y-3">
      <div
        v-for="customer in store.customers"
        :key="customer.id"
        class="p-5 flex flex-col sm:flex-row sm:items-center gap-3 cursor-pointer hover:border-emerald-200 dark:hover:border-emerald-400/30 transition-colors duration-200"
        :class="ui.card"
        @click="openDetail(customer)"
      >
        <div class="flex items-center gap-3 flex-1 min-w-0">
          <div class="w-10 h-10 shrink-0" :class="ui.iconTile">
            <i class="fas fa-user text-sm"></i>
          </div>
          <div class="min-w-0">
            <p class="text-sm font-semibold text-blue-950 dark:text-white truncate">{{ customer.display_name }}</p>
            <p class="text-xs text-blue-950/50 dark:text-blue-100/50 truncate">{{ customer.email }}</p>
          </div>
        </div>
        <div class="flex items-center gap-4 shrink-0 text-right">
          <div>
            <p class="text-sm font-semibold text-blue-950 dark:text-white tabular-nums">
              {{ formatMoney(customer.total_spent_cents, store.currency) }}
            </p>
            <p class="text-xs text-blue-950/50 dark:text-blue-100/50">
              {{ customer.orders_count }} order{{ customer.orders_count === 1 ? '' : 's' }}
            </p>
          </div>
          <span
            class="inline-flex items-center px-2.5 py-0.5 rounded-full border text-[11px] font-semibold uppercase tracking-[0.1em]"
            :class="customer.source === 'checkout'
              ? 'border-emerald-200/80 dark:border-emerald-400/25 bg-emerald-50/80 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-300'
              : 'border-blue-200/80 dark:border-blue-400/25 bg-blue-50/80 dark:bg-blue-400/10 text-blue-700 dark:text-blue-300'"
          >
            {{ customer.source === 'checkout' ? 'Buyer' : 'Manual' }}
          </span>
        </div>
      </div>

      <p class="text-xs text-blue-950/50 dark:text-blue-100/50 text-center pt-2">
        Showing {{ store.customers.length }} of {{ store.customersTotal }} customer{{ store.customersTotal === 1 ? '' : 's' }}
      </p>
    </div>

    <!-- Empty -->
    <div v-else class="py-16 text-center" :class="ui.card">
      <div class="w-14 h-14 mx-auto mb-4 text-xl" :class="ui.iconTile">
        <i class="fas fa-address-book"></i>
      </div>
      <h3 class="text-lg font-semibold text-blue-950 dark:text-white mb-2">No customers yet</h3>
      <p class="text-sm text-blue-950/60 dark:text-blue-100/60 max-w-md mx-auto">
        Customers appear automatically when someone completes a checkout, or add them yourself.
      </p>
    </div>

    <!-- Add/edit modal -->
    <SellModal v-if="showForm" :title="editingCustomer ? 'Edit customer' : 'Add customer'" @close="closeForm">
      <form class="space-y-5" @submit.prevent="save">
        <div>
          <label :class="ui.label" for="customer-name">Name</label>
          <input id="customer-name" v-model="form.name" type="text" maxlength="255" :class="ui.input" />
        </div>
        <div>
          <label :class="ui.label" for="customer-email">Email</label>
          <input id="customer-email" v-model="form.email" type="email" required :class="ui.input" />
        </div>
        <div>
          <label :class="ui.label" for="customer-phone">Phone <span class="normal-case tracking-normal font-normal">(optional)</span></label>
          <input id="customer-phone" v-model="form.phone" type="tel" maxlength="20" :class="ui.input" />
        </div>
        <div>
          <label :class="ui.label" for="customer-notes">Notes <span class="normal-case tracking-normal font-normal">(optional)</span></label>
          <textarea id="customer-notes" v-model="form.notes" rows="3" :class="ui.input"></textarea>
        </div>
        <div v-if="formError" :class="ui.errorBox">{{ formError }}</div>
        <div class="flex items-center justify-end gap-3">
          <button
            v-if="editingCustomer"
            type="button"
            class="mr-auto"
            :class="ui.dangerBtn"
            :disabled="saving"
            @click="remove"
          >
            Delete
          </button>
          <button type="button" :class="ui.secondaryBtn" @click="closeForm">Cancel</button>
          <button type="submit" :class="ui.primaryBtn" :disabled="saving">
            <i v-if="saving" class="fas fa-circle-notch animate-spin"></i>
            {{ editingCustomer ? 'Save' : 'Add customer' }}
          </button>
        </div>
      </form>
    </SellModal>

    <!-- Detail modal -->
    <SellModal v-if="detailCustomer" :title="detailCustomer.display_name" wide @close="detailCustomer = null">
      <div class="space-y-5">
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <span :class="ui.label">Email</span>
            <p class="text-sm text-blue-950 dark:text-white break-all">{{ detailCustomer.email }}</p>
          </div>
          <div>
            <span :class="ui.label">Phone</span>
            <p class="text-sm text-blue-950 dark:text-white">{{ detailCustomer.phone || '—' }}</p>
          </div>
          <div>
            <span :class="ui.label">Total spent</span>
            <p class="text-sm text-blue-950 dark:text-white tabular-nums">
              {{ formatMoney(detailCustomer.total_spent_cents, store.currency) }}
            </p>
          </div>
        </div>
        <div v-if="detailCustomer.notes">
          <span :class="ui.label">Notes</span>
          <p class="text-sm text-blue-950/70 dark:text-blue-100/70 whitespace-pre-line">{{ detailCustomer.notes }}</p>
        </div>

        <div>
          <span :class="ui.label">Orders</span>
          <div v-if="detailLoading" class="flex justify-center py-6">
            <div class="w-5 h-5 border-2 border-emerald-200 dark:border-emerald-300/30 border-t-emerald-600 dark:border-t-emerald-300 rounded-full animate-spin"></div>
          </div>
          <div v-else-if="detailOrders.length" class="space-y-2">
            <div
              v-for="order in detailOrders"
              :key="order.id"
              class="flex items-center gap-3 p-3 rounded-xl border border-blue-200/60 dark:border-white/[0.08]"
            >
              <div class="flex-1 min-w-0">
                <p class="text-sm text-blue-950 dark:text-white truncate">
                  Order #{{ order.id }} · {{ formatDateTime(order.created_at) }}
                </p>
              </div>
              <span class="text-sm font-semibold text-blue-950 dark:text-white tabular-nums">
                {{ formatMoney(order.amount_total_cents, order.currency) }}
              </span>
              <OrderStatusBadge :status="order.status" />
            </div>
          </div>
          <p v-else class="text-sm text-blue-950/60 dark:text-blue-100/60 py-2">No orders yet.</p>
        </div>

        <div class="flex items-center justify-end gap-3 pt-1">
          <button type="button" :class="ui.secondaryBtn" @click="openEditFromDetail">
            <i class="fas fa-pen text-xs"></i>
            Edit customer
          </button>
        </div>
      </div>
    </SellModal>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import OrderStatusBadge from '../components/OrderStatusBadge.vue'
import SellModal from '../components/SellModal.vue'
import { extractError } from '../services/sellService'
import { useSellStore } from '../stores/sell'
import type { Customer, Order } from '../types'
import { formatDateTime, formatMoney, ui } from '../utils/ui'

const store = useSellStore()

const search = ref('')
const actionError = ref('')

const showForm = ref(false)
const editingCustomer = ref<Customer | null>(null)
const saving = ref(false)
const formError = ref('')
const form = reactive({ name: '', email: '', phone: '', notes: '' })

const detailCustomer = ref<Customer | null>(null)
const detailOrders = ref<Order[]>([])
const detailLoading = ref(false)

let searchTimer: ReturnType<typeof setTimeout> | undefined

function debouncedFetch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(fetchCustomers, 300)
}

async function fetchCustomers() {
  actionError.value = ''
  try {
    await store.fetchCustomers(search.value ? { search: search.value } : {})
  } catch (error) {
    actionError.value = extractError(error, 'Could not load customers.')
  }
}

function openCreate() {
  editingCustomer.value = null
  Object.assign(form, { name: '', email: '', phone: '', notes: '' })
  formError.value = ''
  showForm.value = true
}

function openEditFromDetail() {
  if (!detailCustomer.value) return
  editingCustomer.value = detailCustomer.value
  Object.assign(form, {
    name: detailCustomer.value.name,
    email: detailCustomer.value.email,
    phone: detailCustomer.value.phone,
    notes: detailCustomer.value.notes,
  })
  formError.value = ''
  detailCustomer.value = null
  showForm.value = true
}

function closeForm() {
  showForm.value = false
  editingCustomer.value = null
}

async function save() {
  saving.value = true
  formError.value = ''
  try {
    const payload = {
      name: form.name.trim(),
      email: form.email.trim(),
      phone: form.phone.trim(),
      notes: form.notes.trim(),
    }
    if (editingCustomer.value) {
      await store.updateCustomer(editingCustomer.value.id, payload)
    } else {
      await store.createCustomer(payload)
    }
    closeForm()
    await fetchCustomers()
  } catch (error) {
    formError.value = extractError(error, 'Could not save the customer.')
  } finally {
    saving.value = false
  }
}

async function remove() {
  if (!editingCustomer.value) return
  saving.value = true
  formError.value = ''
  try {
    await store.deleteCustomer(editingCustomer.value.id)
    closeForm()
  } catch (error) {
    formError.value = extractError(error, 'Could not delete the customer.')
  } finally {
    saving.value = false
  }
}

async function openDetail(customer: Customer) {
  detailCustomer.value = customer
  detailLoading.value = true
  detailOrders.value = []
  try {
    const { customer: fresh, orders } = await store.getCustomer(customer.id)
    detailCustomer.value = fresh
    detailOrders.value = orders
  } catch (error) {
    actionError.value = extractError(error, 'Could not load the customer.')
    detailCustomer.value = null
  } finally {
    detailLoading.value = false
  }
}

onMounted(fetchCustomers)
</script>
