<!--
  TransactionForm.vue - Create/edit a ledger entry (income or expense).
-->
<template>
  <form class="space-y-4" @submit.prevent="submit">
    <div v-if="error" :class="ui.errorBox">{{ error }}</div>

    <!-- Kind toggle -->
    <div>
      <label :class="ui.label">Type</label>
      <div class="grid grid-cols-2 gap-2">
        <button
          v-for="option in kindOptions"
          :key="option.value"
          type="button"
          class="px-4 py-2.5 rounded-xl border text-sm font-medium transition-colors duration-200"
          :class="form.kind === option.value
            ? 'border-amber-300 dark:border-amber-400/40 bg-amber-50 dark:bg-amber-400/10 text-amber-700 dark:text-amber-300'
            : 'border-blue-200/70 dark:border-white/[0.12] text-blue-950/60 dark:text-blue-100/60 hover:text-blue-950 dark:hover:text-white'"
          @click="setKind(option.value)"
        >
          <i :class="['fas', option.icon]" class="text-xs mr-1.5"></i>
          {{ option.label }}
        </button>
      </div>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div>
        <label :class="ui.label" for="tx-amount">Amount</label>
        <input
          id="tx-amount"
          v-model="form.amount"
          type="number"
          min="0.01"
          step="0.01"
          required
          placeholder="0.00"
          :class="ui.input"
        />
      </div>
      <div>
        <label :class="ui.label" for="tx-date">Date</label>
        <input id="tx-date" v-model="form.occurred_on" type="date" required :class="ui.input" />
      </div>
    </div>

    <div>
      <label :class="ui.label" for="tx-description">Description</label>
      <input
        id="tx-description"
        v-model="form.description"
        type="text"
        required
        maxlength="255"
        placeholder="e.g. Website subscription"
        :class="ui.input"
      />
    </div>

    <div>
      <label :class="ui.label" for="tx-category">Category</label>
      <select id="tx-category" v-model="form.category" :class="ui.input">
        <option v-for="option in categoryOptions" :key="option.value" :value="option.value">
          {{ option.label }}
        </option>
      </select>
    </div>

    <div>
      <label :class="ui.label" for="tx-notes">Notes <span class="normal-case tracking-normal font-normal">(optional)</span></label>
      <textarea id="tx-notes" v-model="form.notes" rows="2" :class="ui.input"></textarea>
    </div>

    <div class="flex justify-end gap-3 pt-2">
      <button type="button" :class="ui.secondaryBtn" @click="$emit('close')">Cancel</button>
      <button type="submit" :disabled="saving" :class="ui.primaryBtn">
        <i v-if="saving" class="fas fa-circle-notch fa-spin text-xs"></i>
        {{ transaction ? 'Save changes' : 'Add transaction' }}
      </button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { extractError } from '../services/operateService'
import { useOperateStore } from '../stores/operate'
import type { Transaction, TransactionCategory, TransactionKind } from '../types'
import { EXPENSE_CATEGORIES, INCOME_CATEGORIES } from '../types'
import { todayISO, ui } from '../utils/ui'

const props = defineProps<{
  /** When set, the form edits this entry; otherwise it creates one. */
  transaction?: Transaction | null
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'saved'): void
}>()

const store = useOperateStore()
const saving = ref(false)
const error = ref('')

const kindOptions: { value: TransactionKind; label: string; icon: string }[] = [
  { value: 'income', label: 'Income', icon: 'fa-arrow-trend-up' },
  { value: 'expense', label: 'Expense', icon: 'fa-arrow-trend-down' },
]

const form = reactive({
  kind: (props.transaction?.kind ?? 'income') as TransactionKind,
  category: (props.transaction?.category ?? 'sales') as TransactionCategory,
  description: props.transaction?.description ?? '',
  amount: props.transaction?.amount ?? '',
  occurred_on: props.transaction?.occurred_on ?? todayISO(),
  notes: props.transaction?.notes ?? '',
})

const categoryOptions = computed(() =>
  form.kind === 'income' ? INCOME_CATEGORIES : EXPENSE_CATEGORIES
)

function setKind(kind: TransactionKind) {
  if (form.kind === kind) return
  form.kind = kind
  form.category = kind === 'income' ? 'sales' : 'supplies'
}

async function submit() {
  saving.value = true
  error.value = ''
  try {
    const payload = {
      kind: form.kind,
      category: form.category,
      description: form.description.trim(),
      amount: String(form.amount),
      occurred_on: form.occurred_on,
      notes: form.notes.trim(),
    }
    if (props.transaction) {
      await store.updateTransaction(props.transaction.id, payload)
    } else {
      await store.createTransaction(payload)
    }
    emit('saved')
  } catch (err) {
    error.value = extractError(err, 'Could not save the transaction.')
  } finally {
    saving.value = false
  }
}
</script>
