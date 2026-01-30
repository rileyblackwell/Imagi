<template>
  <div class="account-balance-display" role="status" aria-live="polite">
    <div class="relative group">
      <!-- Modern glass card -->
      <div class="balance-card relative overflow-hidden">
        <!-- gradient border via mask -->
        <div class="gradient-border"></div>

        <div class="content-row">
          <!-- Text block -->
          <div class="text-wrap">
            <div class="label-row">
              <span class="label">Balance</span>
            </div>
            <div class="value-row">
              <span class="value tabular-nums">{{ formattedBalance }}</span>
            </div>
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

// Format the balance as USD with 3 decimals for small changes
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

// Format number as USD with standard 2 decimal places
function formatBalance(balance: number): string {
  // Use currency style with 2 decimal places
  try {
    return new Intl.NumberFormat(undefined, {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(balance);
  } catch (_) {
    // Fallback
    return `$${balance.toFixed(2)}`;
  }
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
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  transition: all 0.3s ease;
  margin-right: 1.5rem;
}

/* Card base */
.balance-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* Gradient border using mask - subtle for navbar */
.gradient-border {
  display: none;
}

/* Layout rows */
.content-row { display: flex; align-items: center; gap: 0.625rem; position: relative; z-index: 1; }

.text-wrap { display: flex; flex-direction: column; gap: 0.125rem; min-width: 5.5rem; }
.label-row { display: flex; align-items: center; gap: 0.3rem; }
.label { font-size: 10px; letter-spacing: 0.08em; text-transform: uppercase; color: rgba(255, 255, 255, 0.5); font-weight: 600; }
.value-row { display: flex; align-items: center; gap: 0.25rem; }
.value {
  color: rgba(255, 255, 255, 0.95);
  font-weight: 700;
  font-size: 1rem;
  line-height: 1;
}


/* Utilities */
.tabular-nums { font-variant-numeric: tabular-nums; font-feature-settings: "tnum" 1; }

/* Animation for slow pulsing effect */
@keyframes pulse-slow { 0%,100%{opacity:0; transform:scale(1);} 50%{opacity:0.7; transform:scale(1.05);} }
.animate-pulse-slow { animation: pulse-slow 3s infinite ease-in-out; }
</style>