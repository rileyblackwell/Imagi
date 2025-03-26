<template>
  <div class="credit-balance-display" :title="`Balance last updated: ${lastUpdatedText}`">
    <i class="fas fa-coins"></i>
    <span class="balance-text">Credits:</span>
    <span class="balance-amount">{{ formattedBalance }}</span>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { usePaymentsStore } from '@/apps/payments/store';

const paymentsStore = usePaymentsStore();
const isLoading = ref(false);

// Format the balance
const formattedBalance = computed(() => {
  return `$${paymentsStore.balance.toFixed(2)}`;
});

// Format last updated time
const lastUpdatedText = computed(() => {
  if (!paymentsStore.lastUpdated) return 'Never';
  return new Date(paymentsStore.lastUpdated).toLocaleString();
});

// Initialize on component mount
onMounted(async () => {
  isLoading.value = true;
  try {
    // Initialize and enable auto-refresh
    await paymentsStore.initializePayments();
    paymentsStore.toggleAutoRefresh(true);
  } finally {
    isLoading.value = false;
  }
});

// Clean up - but don't stop auto-refresh as it might be used elsewhere
onUnmounted(() => {
  // Keep auto-refresh running for other components
});
</script>

<style scoped>
.credit-balance-display {
  display: flex;
  align-items: center;
  padding: 0.5rem 0.75rem;
  background-color: rgba(23, 25, 35, 0.8);
  border-radius: 0.375rem;
  border: 1px solid rgba(75, 85, 99, 0.5);
  font-size: 0.875rem;
  font-weight: 500;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  white-space: nowrap;
  position: fixed;
  top: 0.75rem;
  right: 1.5rem;
  z-index: 100;
  transition: all 0.2s ease;
}

.credit-balance-display:hover {
  background-color: rgba(31, 35, 50, 0.9);
  border-color: rgba(99, 102, 241, 0.6);
}

.balance-text {
  color: #a1a1aa;
  margin: 0 0.25rem 0 0.5rem;
}

.balance-amount {
  font-family: 'SF Mono', 'Menlo', monospace;
  color: #f9fafb;
  font-weight: 600;
}

.fa-coins {
  color: #f59e0b;
  font-size: 0.875rem;
}
</style> 