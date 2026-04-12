<template>
  <div class="bg-dark-900 rounded-lg p-4">
    <div v-if="loading" class="flex justify-center py-4">
      <PaymentSpinner />
    </div>
    <div v-else class="flex justify-between items-center">
      <div>
        <p class="text-white font-medium">{{ title }}</p>
        <p class="text-sm text-gray-400">{{ subtitle }}</p>
      </div>
      <div class="text-2xl font-bold text-primary-400">
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