<template>
  <div class="account-balance-display">
    <div
      class="balance-container bg-dark-850/95 backdrop-blur-xl px-3.5 py-2.5 flex items-center rounded-lg border border-slate-700/30 transition-all duration-300 shadow-xl hover:shadow-primary-500/10"
    >
      <!-- Professional gradient icon -->
      <div class="mr-3 flex-shrink-0">
        <div class="w-7 h-7 rounded-full professional-gradient flex items-center justify-center shadow-md ring-1 ring-white/10">
          <i class="fas fa-wallet text-white text-xs"></i>
        </div>
      </div>
      <div>
        <div class="text-xs font-medium text-slate-400 tracking-wide uppercase">
          Account Balance
        </div>
        <div class="text-sm font-semibold text-white leading-tight flex items-baseline">
          <span class="highlight-text">{{ formattedBalance }}</span>
          <span class="ml-1 text-[10px] font-normal text-slate-400">credits</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed } from 'vue';
import { usePaymentsStore } from '@/apps/payments/store';

const paymentsStore = usePaymentsStore();
const isLoading = ref(false);
const refreshIntervalId = ref(null);

// Format the balance
const formattedBalance = computed(() => {
  return formatBalance(paymentsStore.balance || 0);
});

// Format number with commas for thousands
function formatBalance(balance: number): string {
  return balance.toLocaleString();
}

// Function to fetch balance
async function fetchBalance(showLoading = true) {
  if (showLoading) {
    isLoading.value = true;
  }
  
  try {
    // Fetch without auto-refresh, only get current balance
    await paymentsStore.fetchBalance(false, false);
  } catch (error) {
    console.error('Error fetching balance:', error);
  } finally {
    if (showLoading) {
      isLoading.value = false;
    }
  }
}

// Initialize on component mount
onMounted(() => {
  // Initial balance fetch without showing loading state
  fetchBalance(false)
})

onBeforeUnmount(() => {
  // Clean up any interval
  if (refreshIntervalId.value) {
    clearInterval(refreshIntervalId.value)
    refreshIntervalId.value = null
  }
})
</script>

<style scoped>
.account-balance-display {
  position: fixed;
  top: 1rem;
  right: 1.5rem;
  z-index: 1000;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  transition: all 0.2s ease;
}

.balance-container {
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(12px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2), 0 2px 4px rgba(0, 0, 0, 0.15);
}

.balance-container:hover {
  transform: translateY(-1px);
  border-color: rgba(99, 102, 241, 0.4);
}

.balance-container::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(120deg, rgba(99, 102, 241, 0.04), transparent 70%);
  z-index: -1;
  pointer-events: none;
}

/* Professional gradient with subtle color hints */
.professional-gradient {
  background: linear-gradient(135deg, #5046e5, #6366f1);
  box-shadow: 0 2px 10px rgba(99, 102, 241, 0.3);
}

/* Highlight text with subtle gradient */
.highlight-text {
  background: linear-gradient(90deg, #f9fafb, #e2e8f0);
  -webkit-background-clip: text;
  background-clip: text;
  color: white;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  letter-spacing: 0.01em;
}

/* Add subtle glass effect */
.balance-container::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(
    45deg,
    rgba(255, 255, 255, 0.03) 0%,
    rgba(255, 255, 255, 0) 40%
  );
  pointer-events: none;
}
</style> 