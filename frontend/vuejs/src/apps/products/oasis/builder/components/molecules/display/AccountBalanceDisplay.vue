<template>
  <div class="account-balance-display">
    <div
      class="balance-container group bg-dark-900/90 backdrop-blur-xl px-4 py-3 flex items-center rounded-xl border border-dark-700/50 hover:border-primary-500/30 transition-all duration-300 shadow-lg hover:shadow-primary-500/20 transform hover:scale-[1.02]"
    >
      <!-- Subtle glow effect on hover -->
      <div class="absolute -inset-0.5 bg-gradient-to-r from-primary-500/30 to-violet-500/30 rounded-xl blur opacity-0 group-hover:opacity-75 transition duration-300"></div>
      
      <!-- Professional gradient icon with improved styling -->
      <div class="mr-3 flex-shrink-0 relative">
        <div class="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-violet-600 flex items-center justify-center shadow-md ring-1 ring-white/10">
          <i class="fas fa-wallet text-white text-xs"></i>
        </div>
        <!-- Subtle pulse animation around the icon -->
        <div class="absolute -inset-0.5 rounded-full bg-primary-500/20 animate-pulse-slow opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
      </div>
      
      <div class="relative">
        <div class="text-xs font-medium text-gray-400 tracking-wide uppercase">
          Account Balance
        </div>
        <div class="text-sm font-semibold text-white leading-tight flex items-baseline">
          <span class="highlight-text">{{ formattedBalance }}</span>
          <span class="ml-1 text-[10px] font-normal text-gray-400">credits</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed, watch } from 'vue';
import { usePaymentStore } from '@/apps/payments/stores/payments';
import { useBalanceStore } from '@/shared/stores/balance';
import { useAgentStore } from '../../../stores/agentStore';

const paymentsStore = usePaymentStore();
const balanceStore = useBalanceStore();
const agentStore = useAgentStore();
const isLoading = ref(false);
const refreshIntervalId = ref<number | null>(null);

// Format the balance
const formattedBalance = computed(() => {
  return formatBalance(paymentsStore.balance || 0);
});

// Watch for changes in the agent's processing state to trigger balance refresh
watch(() => agentStore.isProcessing, (newValue, oldValue) => {
  // When processing changes from true to false, refresh the balance
  if (oldValue === true && newValue === false) {
    // Force refresh balance after AI operation completes
    setTimeout(() => {
      fetchBalance(false, true);
    }, 500); // Small delay to ensure backend has processed the transaction
  }
});

// Format number with more precision to show small changes
function formatBalance(balance: number): string {
  // Show 3 decimal places to make $0.005 changes visible
  return balance.toLocaleString(undefined, { 
    minimumFractionDigits: 3,
    maximumFractionDigits: 3 
  });
}

// Function to fetch balance with improved force refresh parameter
async function fetchBalance(showLoading = true, forceRefresh = false) {
  if (showLoading) {
    isLoading.value = true;
  }
  
  try {
    // Check if balance is already loaded, if not fetch it
    if (paymentsStore.balance === null) {
      await paymentsStore.fetchBalance()
    }
    
    // Use both stores to maximize chance of successful update
    if (forceRefresh) {
      // Signal that a transaction is in progress to bypass cache
      balanceStore.beginTransaction();
    }
    
    // Attempt to fetch balance from both stores
    const fetchPromises = [
      paymentsStore.fetchBalance(false, forceRefresh),
      balanceStore.fetchBalance(false, forceRefresh)
    ];
    
    // Wait for both to complete
    await Promise.allSettled(fetchPromises);
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
  // Initial balance fetch with force refresh to ensure accuracy
  fetchBalance(false, true);
  
  // Periodic refresh removed to prevent excessive API calls
})

onBeforeUnmount(() => {
  // No interval to clean up anymore
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
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3), 0 2px 4px rgba(0, 0, 0, 0.2);
}

/* Highlight text with subtle gradient */
.highlight-text {
  background: linear-gradient(90deg, #ffffff, #e2e8f0);
  -webkit-background-clip: text;
  background-clip: text;
  color: white;
  font-weight: 600;
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

/* Animation for slow pulsing effect */
@keyframes pulse-slow {
  0%, 100% { 
    opacity: 0;
    transform: scale(1);
  }
  50% { 
    opacity: 0.7;
    transform: scale(1.1);
  }
}

.animate-pulse-slow {
  animation: pulse-slow 3s infinite ease-in-out;
}
</style> 