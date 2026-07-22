<template>
  <div class="balance-card rounded-2xl bg-white/85 dark:bg-white/[0.045] border border-blue-200/70 dark:border-blue-300/[0.14] backdrop-blur-sm p-6 sm:p-8 transition-all duration-300">
    <div class="mb-6">
      <span class="text-xs font-semibold uppercase tracking-[0.16em] text-blue-700 dark:text-blue-300/70 transition-colors duration-300">{{ title }}</span>
    </div>

    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
      <div class="flex-grow">
        <!-- Balance display with clean styling -->
        <div>
          <div class="text-sm text-blue-950/60 dark:text-blue-100/55 mb-2 transition-colors duration-300">{{ balanceLabel }}</div>
          <div class="flex items-baseline gap-2">
            <div v-if="loading" class="animate-pulse">
              <div class="h-9 w-20 bg-blue-950/10 dark:bg-white/10 rounded-lg"></div>
            </div>
            <div v-else class="font-display text-3xl sm:text-4xl font-semibold tracking-tight tabular-nums text-blue-950 dark:text-white transition-colors duration-300">
              ${{ credits.toLocaleString() }}
            </div>
            <div class="text-sm text-blue-950/60 dark:text-blue-100/55 transition-colors duration-300">USD</div>
          </div>

          <!-- Last updated info -->
          <div v-if="lastUpdated && showLastUpdated" class="text-xs text-blue-950/50 dark:text-blue-100/40 mt-2 transition-colors duration-300">
            Last updated: {{ formatDateTime(lastUpdated) }}
          </div>
        </div>
      </div>

      <!-- Action buttons -->
      <div v-if="showActions" class="flex flex-col sm:flex-row gap-3">
        <slot name="actions">
          <!-- Empty by default as "Add Credits" button has been removed -->
        </slot>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">

const props = defineProps({
  title: {
    type: String,
    default: 'Your Account'
  },
  balanceLabel: {
    type: String,
    default: 'Current Balance'
  },
  credits: {
    type: Number,
    default: 0
  },
  loading: {
    type: Boolean,
    default: false
  },
  lastUpdated: {
    type: [Date, String],
    default: null
  },
  showActions: {
    type: Boolean,
    default: true
  },
  showLastUpdated: {
    type: Boolean,
    default: true
  }
});

// Format date and time for last updated display
const formatDateTime = (date: Date | string) => {
  if (!date) return '';
  
  const dateObj = date instanceof Date ? date : new Date(date);
  return dateObj.toLocaleString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};
</script>

<style scoped>
/* Crisp, sharply-defined card: hairline edge + tight layered shadow */
.balance-card {
  box-shadow:
    0 0 0 1px rgba(15, 23, 42, 0.03),
    0 1px 2px rgba(15, 23, 42, 0.06),
    0 4px 10px -2px rgba(15, 23, 42, 0.07),
    0 12px 28px -10px rgba(15, 23, 42, 0.10);
}

.dark .balance-card {
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.04),
    0 1px 2px rgba(0, 0, 0, 0.5),
    0 4px 10px -2px rgba(0, 0, 0, 0.45),
    0 12px 28px -10px rgba(0, 0, 0, 0.55);
}
</style> 