<template>
  <div class="balance-display">
    <div class="text-sm text-blue-950/70 dark:text-blue-100/55 mb-2 transition-colors duration-300">{{ label }}</div>
    <div v-if="loading" class="animate-pulse-slow py-1">
      <div class="h-10 w-32 bg-blue-950/10 dark:bg-white/10 rounded-lg"></div>
    </div>
    <div v-else class="font-display font-semibold text-3xl tracking-tight tabular-nums text-blue-950 dark:text-white transition-colors duration-300">
      {{ formattedBalance }}
    </div>
    <div v-if="showLastUpdated && lastUpdated" class="text-sm text-blue-950/60 dark:text-blue-100/55 mt-2 transition-colors duration-300">
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

/* Pulsing animation for loading state */
@keyframes pulse-slow {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 0.9; }
}

.animate-pulse-slow {
  animation: pulse-slow 1.5s ease-in-out infinite;
}

@media (prefers-reduced-motion: reduce) {
  .animate-pulse-slow {
    animation: none;
  }
}
</style> 