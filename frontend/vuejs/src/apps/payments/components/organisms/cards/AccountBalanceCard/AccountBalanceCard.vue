<template>
  <div class="rounded-2xl bg-white/50 dark:bg-white/[0.03] border border-gray-200 dark:border-white/[0.08] backdrop-blur-sm p-6 sm:p-8 transition-all duration-300 hover:border-gray-300 dark:hover:border-white/[0.12] hover:shadow-lg">
    <div class="mb-6">
      <span class="text-sm font-medium text-gray-600 dark:text-gray-400 uppercase tracking-wide">{{ title }}</span>
    </div>
    
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
      <div class="flex-grow">
        <!-- Balance display with clean styling -->
        <div>
          <div class="text-sm text-gray-500 dark:text-gray-400 mb-2">{{ balanceLabel }}</div>
          <div class="flex items-baseline gap-2">
            <div v-if="loading" class="animate-pulse">
              <div class="h-9 w-20 bg-gray-200 dark:bg-white/10 rounded-lg"></div>
            </div>
            <div v-else class="text-3xl sm:text-4xl font-semibold text-gray-900 dark:text-white">
              ${{ credits.toLocaleString() }}
            </div>
            <div class="text-sm text-gray-500 dark:text-gray-400">USD</div>
          </div>
          
          <!-- Last updated info -->
          <div v-if="lastUpdated && showLastUpdated" class="text-xs text-gray-500 dark:text-gray-500 mt-2">
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
/* You can add component-specific styles here if needed */
</style> 