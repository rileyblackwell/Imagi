<template>
  <div class="rounded-2xl bg-white/85 dark:bg-white/[0.045] border border-blue-950/[0.08] dark:border-white/[0.1] backdrop-blur-sm p-4 transition-colors duration-300">
    <div class="flex justify-between items-center mb-4">
      <div>
        <p class="text-blue-950 dark:text-white font-medium transition-colors duration-300">{{ title }}</p>
        <p class="text-sm text-blue-950/60 dark:text-blue-100/55 transition-colors duration-300">{{ subtitle }}</p>
      </div>
      <p class="text-xl font-semibold tabular-nums text-blue-700 dark:text-blue-300 transition-colors duration-300">{{ formatCurrency(amount) }}</p>
    </div>
    <div v-if="$slots.details" class="mb-4">
      <slot name="details"></slot>
    </div>
    <div class="border-t border-blue-950/[0.08] dark:border-white/[0.1] pt-4">
      <div class="flex justify-between items-center">
        <p class="text-blue-950/60 dark:text-blue-100/55 transition-colors duration-300">{{ totalLabel }}</p>
        <p class="text-2xl font-semibold tabular-nums text-blue-950 dark:text-white transition-colors duration-300">{{ formatCurrency(displayTotal) }}</p>
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
      displayTotal: computedTotal
    }
  }
})
</script> 