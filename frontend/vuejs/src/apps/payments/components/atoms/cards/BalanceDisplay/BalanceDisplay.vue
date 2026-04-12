<template>
  <div class="balance-display">
    <div class="text-sm text-white/70 mb-2">{{ label }}</div>
    <div v-if="loading" class="animate-pulse-slow py-1">
      <div class="h-10 w-32 bg-dark-800/80 rounded-lg"></div>
    </div>
    <div v-else class="font-bold text-3xl bg-gradient-to-r from-primary-300 to-primary-500 bg-clip-text text-transparent">
      {{ formattedBalance }}
    </div>
    <div v-if="showLastUpdated && lastUpdated" class="text-sm text-white/60 mt-2">
      Last updated: {{ formatDate(lastUpdated) }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps({
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
  },
  showLastUpdated: {
    type: Boolean,
    default: false
  },
  lastUpdated: {
    type: [Date, String],
    default: null
  },
  type: {
    type: String,
    default: 'credits', // 'credits' or 'currency'
    validator: (value: string) => ['credits', 'currency'].includes(value)
  }
});

const formattedBalance = computed(() => {
  if (props.type === 'currency') {
    return `$${props.balance.toFixed(2)}`;
  }
  return `${props.balance} credits`;
});

// Format date to readable format
const formatDate = (dateStr: string | Date) => {
  if (!dateStr) return '';
  const date = dateStr instanceof Date ? dateStr : new Date(dateStr);
  return date.toLocaleDateString(undefined, { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};
</script>

<style scoped>
.balance-display {
  transition: all 0.3s ease;
}

/* Gradient animation for text */
@keyframes gradient-shift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.bg-gradient-to-r {
  background-size: 200% auto;
  animation: gradient-shift 8s ease infinite;
}

/* Pulsing animation for loading state */
@keyframes pulse-slow {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 0.9; }
}

.animate-pulse-slow {
  animation: pulse-slow 1.5s ease-in-out infinite;
}
</style> 