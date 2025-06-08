<template>
  <div class="account-balance-display">
    <div class="relative group">
      <!-- Premium glow effect -->
      <div class="absolute -inset-0.5 bg-gradient-to-r from-indigo-500/30 via-violet-500/30 to-fuchsia-500/30 rounded-2xl opacity-0 group-hover:opacity-60 blur transition-all duration-500"></div>
      
      <!-- Main balance container with enhanced glassmorphism -->
      <div class="balance-container relative bg-gradient-to-br from-dark-900/95 via-dark-850/90 to-dark-900/95 backdrop-blur-2xl px-4 py-2.5 flex items-center rounded-xl border border-white/15 hover:border-indigo-400/40 transition-all duration-300 shadow-2xl shadow-black/40 hover:shadow-indigo-500/20 transform hover:scale-[1.02] overflow-hidden">
        <!-- Sleek gradient top accent -->
        <div class="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-indigo-400/60 via-violet-400/60 to-fuchsia-400/60 opacity-80"></div>
        
        <!-- Enhanced glassmorphism overlay -->
        <div class="absolute inset-0 bg-gradient-to-br from-white/[0.03] via-transparent to-white/[0.01] pointer-events-none"></div>
        
        <!-- Premium gradient icon with enhanced styling -->
        <div class="mr-3 flex-shrink-0 relative">
          <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500/90 via-violet-500/80 to-fuchsia-500/70 flex items-center justify-center shadow-lg ring-1 ring-white/20 transition-all duration-300 group-hover:shadow-indigo-500/30 group-hover:scale-105">
            <i class="fas fa-wallet text-white text-xs"></i>
          </div>
          <!-- Enhanced pulse animation around the icon -->
          <div class="absolute -inset-1 rounded-lg bg-gradient-to-br from-indigo-500/20 to-violet-500/20 animate-pulse-slow opacity-0 group-hover:opacity-100 transition-opacity duration-500 blur-sm"></div>
        </div>
        
        <div class="relative flex-1">
          <div class="text-[9px] font-semibold text-gray-400 tracking-wider uppercase mb-0.5">
            Balance
          </div>
          <div class="text-sm font-bold text-white leading-tight flex items-baseline">
            <span class="highlight-text">{{ formattedBalance }}</span>
            <span class="ml-1 text-[10px] font-medium text-gray-400/80">credits</span>
          </div>
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
  // Don't automatically fetch balance on mount - balance should only be fetched
  // when user visits specific pages or after specific actions like AI model usage
  // The balance will be available if it was already fetched by the page that displays this component
})

onBeforeUnmount(() => {
  // No interval to clean up anymore
})
</script>

<style scoped>
.account-balance-display {
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: 1000;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  transition: all 0.3s ease;
}

.balance-container {
  position: relative;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}

/* Enhanced highlight text with premium gradient */
.highlight-text {
  background: linear-gradient(135deg, #ffffff 0%, #a5b4fc 50%, #c084fc 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  font-weight: 700;
  letter-spacing: 0.02em;
  text-shadow: 0 0 20px rgba(139, 92, 246, 0.3);
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