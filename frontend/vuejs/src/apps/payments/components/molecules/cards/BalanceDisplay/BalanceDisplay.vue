<template>
  <div class="rounded-2xl bg-white/85 dark:bg-white/[0.045] border border-blue-950/[0.08] dark:border-white/[0.1] backdrop-blur-sm p-4 transition-colors duration-300">
    <div v-if="loading" class="flex justify-center py-4">
      <PaymentSpinner />
    </div>
    <div v-else class="flex justify-between items-center">
      <div>
        <p class="text-blue-950 dark:text-white font-medium transition-colors duration-300">{{ title }}</p>
        <p class="text-sm text-blue-950/60 dark:text-blue-100/55 transition-colors duration-300">{{ subtitle }}</p>
      </div>
      <div class="text-2xl font-semibold tabular-nums text-blue-700 dark:text-blue-300 transition-colors duration-300">
        {{ formatCurrency(amount) }}
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import PaymentSpinner from '../atoms/Spinner.vue'

export default defineComponent({
  name: 'BalanceDisplay',
  components: {
    PaymentSpinner
  },
  props: {
    amount: {
      type: Number,
      required: true
    },
    title: {
      type: String,
      default: 'Available Credits'
    },
    subtitle: {
      type: String,
      default: ''
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  setup() {
    const formatCurrency = (value: number): string => {
      return `$${value.toFixed(2)}`
    }

    return {
      formatCurrency
    }
  }
})
</script> 