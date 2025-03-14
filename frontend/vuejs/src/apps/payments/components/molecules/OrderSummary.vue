<template>
  <div class="bg-dark-900 rounded-lg p-4">
    <div class="flex justify-between items-center mb-4">
      <div>
        <p class="text-white font-medium">{{ title }}</p>
        <p class="text-sm text-gray-400">{{ subtitle }}</p>
      </div>
      <p class="text-xl font-bold text-primary-400">{{ formatCurrency(amount) }}</p>
    </div>
    <div v-if="$slots.details" class="mb-4">
      <slot name="details"></slot>
    </div>
    <div class="border-t border-dark-700 pt-4">
      <div class="flex justify-between items-center">
        <p class="text-gray-400">{{ totalLabel }}</p>
        <p class="text-2xl font-bold text-primary-400">{{ formatCurrency(total) }}</p>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed } from 'vue'

export default defineComponent({
  name: 'OrderSummary',
  props: {
    amount: {
      type: Number,
      required: true
    },
    total: {
      type: Number,
      default: undefined
    },
    title: {
      type: String,
      default: 'Add Funds'
    },
    subtitle: {
      type: String,
      default: 'Credits for AI model usage'
    },
    totalLabel: {
      type: String,
      default: 'Total'
    }
  },
  setup(props) {
    const computedTotal = computed(() => {
      return props.total !== undefined ? props.total : props.amount
    })

    const formatCurrency = (value: number): string => {
      return `$${value.toFixed(2)}`
    }

    return {
      formatCurrency,
      total: computedTotal
    }
  }
})
</script> 