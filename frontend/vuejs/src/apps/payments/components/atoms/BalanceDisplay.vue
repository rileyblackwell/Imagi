<template>
  <div class="balance-display">
    <div class="text-sm text-gray-400 mb-1">{{ label }}</div>
    <div class="font-semibold text-2xl text-white">
      <span v-if="loading" class="animate-pulse">Loading...</span>
      <span v-else>{{ formattedBalance }}</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BalanceDisplay',
  props: {
    balance: {
      type: Number,
      default: 0
    },
    loading: {
      type: Boolean,
      default: false
    },
    label: {
      type: String,
      default: 'Current Balance'
    }
  },
  computed: {
    formattedBalance() {
      return `$${this.balance.toFixed(2)}`
    }
  }
}
</script>

<style scoped>
.balance-display {
  transition: all 0.3s ease;
}
</style> 