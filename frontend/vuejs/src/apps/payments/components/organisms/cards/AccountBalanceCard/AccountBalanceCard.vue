<template>
  <div class="group relative transform transition-all duration-300 hover:-translate-y-1">
    <!-- Enhanced glass morphism effect with glow -->
    <div class="absolute -inset-0.5 rounded-2xl opacity-30 group-hover:opacity-70 blur group-hover:blur-md transition-all duration-300 bg-gradient-to-r from-indigo-500/50 to-violet-500/50"></div>
    
    <!-- Card with enhanced glass morphism -->
    <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
      <!-- Sleek gradient header -->
      <div class="h-1 w-full bg-gradient-to-r from-indigo-400 via-violet-400 to-indigo-400 opacity-80"></div>
      
      <!-- Subtle background effects -->
      <div class="absolute -top-32 -right-32 w-64 h-64 bg-gradient-to-br from-indigo-400/4 to-violet-400/4 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"></div>
      
      <div class="relative z-10 p-6 sm:p-8">
        <!-- Modern pill badge -->
        <div class="inline-flex items-center px-3 py-1 bg-gradient-to-r from-indigo-500/15 to-violet-500/15 border border-indigo-400/20 rounded-full mb-6 backdrop-blur-sm">
          <div class="w-1.5 h-1.5 bg-indigo-400 rounded-full mr-2 animate-pulse"></div>
          <span class="text-indigo-300 font-medium text-xs tracking-wide uppercase">{{ title }}</span>
        </div>
        
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
          <div class="flex-grow">
            <!-- Balance display with enhanced styling -->
            <div>
              <div class="text-sm text-gray-400 mb-1">{{ balanceLabel }}</div>
              <div class="flex items-baseline gap-2">
                <div v-if="loading" class="animate-pulse">
                  <div class="h-9 w-20 bg-dark-800/50 rounded-lg"></div>
                </div>
                <div v-else class="text-3xl font-bold bg-gradient-to-r from-indigo-300 to-violet-300 bg-clip-text text-transparent">
                  ${{ credits.toLocaleString() }}
                </div>
                <div class="text-sm text-indigo-400">USD</div>
              </div>
              
              <!-- Last updated info -->
              <div v-if="lastUpdated && showLastUpdated" class="text-xs text-gray-500 mt-2">
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