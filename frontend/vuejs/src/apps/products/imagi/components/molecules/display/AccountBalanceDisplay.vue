<template>
  <div class="account-balance-display" role="status" aria-live="polite">
    <div class="relative group">
      <!-- Aurora background accents -->
      <div class="absolute -inset-1 rounded-2xl opacity-60 blur-2xl pointer-events-none">
        <div class="absolute -top-6 -right-10 w-40 h-40 rounded-full bg-indigo-500/15 mix-blend-screen"></div>
        <div class="absolute -bottom-10 -left-12 w-48 h-48 rounded-full bg-violet-500/15 mix-blend-screen"></div>
      </div>

      <!-- Modern glass card (no rolling flash) -->
      <div class="balance-card relative overflow-hidden">
        <!-- gradient border via mask -->
        <div class="gradient-border"></div>

        <div class="content-row">
          <!-- Icon block -->
          <div class="icon-wrap">
            <div class="icon-core" :class="schemeClasses.iconBg">
              <i class="fas fa-wallet text-white text-sm"></i>
            </div>
            <div class="icon-pulse" :class="schemeClasses.iconPulse"></div>
          </div>

          <!-- Text block -->
          <div class="text-wrap">
            <div class="label-row">
              <span class="label">Balance</span>
            </div>
            <div class="value-row">
              <span class="value tabular-nums">{{ formattedBalance }}</span>
            </div>
            <div class="meter" aria-hidden="true">
              <div class="meter-fill bg-gradient-to-r" :class="schemeClasses.meterFill" :style="{ width: meterWidth }"></div>
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

// Balance thresholds for color scheme states
const balanceValue = computed(() => (paymentsStore.balance ?? 0));
const scheme = computed(() => {
  if (balanceValue.value < 5) return 'low'; // danger
  if (balanceValue.value < 20) return 'warn'; // warning
  return 'ok'; // default
});

// Dynamic classes per state (keeps indigo/violet brand accents around container)
const schemeClasses = computed(() => {
  switch (scheme.value) {
    case 'low':
      return {
        iconBg: 'bg-gradient-to-br from-rose-500/90 via-rose-400/85 to-rose-600/80 group-hover:shadow-rose-500/30',
        iconPulse: 'bg-gradient-to-br from-rose-500/25 to-rose-400/25',
        meterFill: 'from-rose-500/70 to-rose-400/70'
      } as const;
    case 'warn':
      return {
        iconBg: 'bg-gradient-to-br from-amber-500/90 via-amber-400/85 to-amber-600/80 group-hover:shadow-amber-500/30',
        iconPulse: 'bg-gradient-to-br from-amber-500/25 to-amber-400/25',
        meterFill: 'from-amber-500/70 to-amber-400/70'
      } as const;
    default:
      return {
        iconBg: 'bg-gradient-to-br from-emerald-500/90 via-emerald-400/85 to-emerald-600/80 group-hover:shadow-emerald-500/30',
        iconPulse: 'bg-gradient-to-br from-emerald-500/25 to-emerald-400/25',
        meterFill: 'from-emerald-500/70 to-emerald-400/70'
      } as const;
  }
});

// Progress meter width based on thresholds (>=20 => 100%)
const meterWidth = computed(() => {
  const v = Math.max(0, Math.min(1, balanceValue.value / 20));
  return `${Math.round(v * 100)}%`;
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
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: 1000;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  transition: all 0.3s ease;
}

/* Card base */
.balance-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.4rem 0.6rem;
  border-radius: 0.875rem; /* rounded-xl */
  background: linear-gradient(180deg, rgba(8, 8, 12, 0.82), rgba(8, 8, 12, 0.68));
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  box-shadow: 0 10px 30px rgba(0,0,0,0.5);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.balance-card:hover { transform: translateY(-2px); box-shadow: 0 14px 40px rgba(67, 56, 202, 0.25); }

/* Gradient border using mask */
.gradient-border {
  position: absolute;
  inset: 0;
  border-radius: inherit;
  padding: 1px;
  background: linear-gradient(130deg, rgba(99,102,241,0.6), rgba(139,92,246,0.6));
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  -webkit-mask-composite: xor;
          mask-composite: exclude;
  pointer-events: none;
}

/* (rolling sheen removed) */

/* Layout rows */
.content-row { display: flex; align-items: center; gap: 0.75rem; position: relative; z-index: 1; }
.icon-wrap { position: relative; width: 1.75rem; height: 1.75rem; }
.icon-core {
  position: relative;
  width: 100%; height: 100%;
  border-radius: 0.75rem;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 8px 20px rgba(0,0,0,0.4);
  border: 1px solid rgba(255,255,255,0.18);
}
.icon-core::after {
  content: '';
  position: absolute; inset: 0;
  border-radius: inherit;
  background: linear-gradient(180deg, rgba(255,255,255,0.15), rgba(255,255,255,0));
  opacity: 0.35;
}
.icon-pulse { position: absolute; inset: -4px; border-radius: 0.9rem; filter: blur(8px); opacity: 0; transition: opacity 0.4s ease; }
.balance-card:hover .icon-pulse { opacity: 1; }

.text-wrap { display: flex; flex-direction: column; gap: 0.12rem; min-width: 8.5rem; }
.label-row { display: flex; align-items: center; gap: 0.4rem; }
.label { font-size: 9.5px; letter-spacing: 0.12em; text-transform: uppercase; color: #cbd5e1; /* slate-300 */ }
.value-row { display: flex; align-items: baseline; gap: 0.25rem; }
.value {
  color: #f8fafc; /* slate-50 */
  font-weight: 800;
  font-size: 0.9rem;
  text-shadow: 0 0 14px rgba(99, 102, 241, 0.28), 0 1px 2px rgba(0, 0, 0, 0.5);
}

/* Progress meter */
.meter {
  position: relative; margin-top: 3px; height: 2px; width: 100%; border-radius: 9999px;
  background: rgba(148,163,184,0.15); /* slate-400/15 */
  overflow: hidden;
}
.meter-fill {
  position: absolute; left: 0; top: 0; bottom: 0; border-radius: inherit;
}

/* Utilities */
.tabular-nums { font-variant-numeric: tabular-nums; font-feature-settings: "tnum" 1; }

/* Animation for slow pulsing effect */
@keyframes pulse-slow { 0%,100%{opacity:0; transform:scale(1);} 50%{opacity:0.7; transform:scale(1.05);} }
.animate-pulse-slow { animation: pulse-slow 3s infinite ease-in-out; }
</style>