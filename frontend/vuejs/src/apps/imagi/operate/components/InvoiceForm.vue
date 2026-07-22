<!--
  InvoiceForm.vue - Create/edit a draft invoice with line items.
-->
<template>
  <form class="space-y-4" @submit.prevent="submit">
    <div v-if="error" :class="ui.errorBox">{{ error }}</div>

    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div>
        <label :class="ui.label" for="inv-customer">Customer</label>
        <input
          id="inv-customer"
          v-model="form.customer_name"
          type="text"
          required
          maxlength="255"
          placeholder="Customer or company name"
          :class="ui.input"
        />
      </div>
      <div>
        <label :class="ui.label" for="inv-email">Email <span class="normal-case tracking-normal font-normal">(optional)</span></label>
        <input id="inv-email" v-model="form.customer_email" type="email" placeholder="billing@example.com" :class="ui.input" />
      </div>
      <div>
        <label :class="ui.label" for="inv-issued">Issue date</label>
        <input id="inv-issued" v-model="form.issue_date" type="date" required :class="ui.input" />
      </div>
      <div>
        <label :class="ui.label" for="inv-due">Due date <span class="normal-case tracking-normal font-normal">(optional)</span></label>
        <input id="inv-due" v-model="form.due_date" type="date" :class="ui.input" />
      </div>
    </div>

    <!-- Line items -->
    <div>
      <label :class="ui.label">Line items</label>
      <div class="space-y-2">
        <div
          v-for="(item, index) in form.line_items"
          :key="index"
          class="flex gap-2 items-start"
        >
          <input
            v-model="item.description"
            type="text"
            required
            placeholder="Description"
            class="flex-1"
            :class="ui.input"
            :aria-label="`Line item ${index + 1} description`"
          />
          <input
            v-model="item.quantity"
            type="number"
            min="0.01"
            step="0.01"
            required
            placeholder="Qty"
            class="w-20"
            :class="ui.input"
            :aria-label="`Line item ${index + 1} quantity`"
          />
          <input
            v-model="item.unit_price"
            type="number"
            min="0"
            step="0.01"
            required
            placeholder="Price"
            class="w-28"
            :class="ui.input"
            :aria-label="`Line item ${index + 1} unit price`"
          />
          <button
            type="button"
            class="w-10 h-10 shrink-0 rounded-xl flex items-center justify-center text-blue-950/40 dark:text-blue-100/40 hover:text-red-600 dark:hover:text-red-300 hover:bg-red-50 dark:hover:bg-red-500/10 transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#16161a] disabled:opacity-40"
            :disabled="form.line_items.length === 1"
            :aria-label="`Remove line item ${index + 1}`"
            @click="removeItem(index)"
          >
            <i class="fas fa-trash-can text-sm"></i>
          </button>
        </div>
      </div>
      <div class="flex items-center justify-between mt-3">
        <button type="button" :class="ui.secondaryBtn" @click="addItem">
          <i class="fas fa-plus text-xs"></i>
          Add line item
        </button>
        <p class="text-sm font-semibold text-blue-950 dark:text-white tabular-nums">
          Total: {{ formatMoney(total) }}
        </p>
      </div>
    </div>

    <div>
      <label :class="ui.label" for="inv-notes">Notes <span class="normal-case tracking-normal font-normal">(optional)</span></label>
      <textarea id="inv-notes" v-model="form.notes" rows="2" placeholder="Payment terms, thank-you note..." :class="ui.input"></textarea>
    </div>

    <div class="flex justify-end gap-3 pt-2">
      <button type="button" :class="ui.secondaryBtn" @click="$emit('close')">Cancel</button>
      <button type="submit" :disabled="saving" :class="ui.primaryBtn">
        <i v-if="saving" class="fas fa-circle-notch fa-spin text-xs"></i>
        {{ invoice ? 'Save changes' : 'Create draft' }}
      </button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { extractError } from '../services/operateService'
import { useOperateStore } from '../stores/operate'
import type { Invoice } from '../types'
import { formatMoney, todayISO, ui } from '../utils/ui'

interface EditableLineItem {
  description: string
  quantity: string
  unit_price: string
}

const props = defineProps<{
  /** When set, the form edits this draft; otherwise it creates one. */
  invoice?: Invoice | null
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'saved'): void
}>()

const store = useOperateStore()
const saving = ref(false)
const error = ref('')

function emptyItem(): EditableLineItem {
  return { description: '', quantity: '1', unit_price: '' }
}

const form = reactive({
  customer_name: props.invoice?.customer_name ?? '',
  customer_email: props.invoice?.customer_email ?? '',
  issue_date: props.invoice?.issue_date ?? todayISO(),
  due_date: props.invoice?.due_date ?? '',
  notes: props.invoice?.notes ?? '',
  line_items: (props.invoice?.line_items?.length
    ? props.invoice.line_items.map(item => ({
        description: item.description,
        quantity: String(item.quantity),
        unit_price: String(item.unit_price),
      }))
    : [emptyItem()]) as EditableLineItem[],
})

const total = computed(() =>
  form.line_items.reduce((sum, item) => {
    const quantity = Number.parseFloat(item.quantity) || 0
    const price = Number.parseFloat(item.unit_price) || 0
    return sum + quantity * price
  }, 0)
)

function addItem() {
  form.line_items.push(emptyItem())
}

function removeItem(index: number) {
  if (form.line_items.length > 1) form.line_items.splice(index, 1)
}

async function submit() {
  saving.value = true
  error.value = ''
  try {
    const payload = {
      customer_name: form.customer_name.trim(),
      customer_email: form.customer_email.trim(),
      issue_date: form.issue_date,
      due_date: form.due_date || null,
      notes: form.notes.trim(),
      line_items: form.line_items.map(item => ({
        description: item.description.trim(),
        quantity: item.quantity,
        unit_price: item.unit_price || '0',
      })),
    }
    if (props.invoice) {
      await store.updateInvoice(props.invoice.id, payload)
    } else {
      await store.createInvoice(payload)
    }
    emit('saved')
  } catch (err) {
    error.value = extractError(err, 'Could not save the invoice.')
  } finally {
    saving.value = false
  }
}
</script>
