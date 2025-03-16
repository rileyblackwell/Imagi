<template>
  <div class="relative group">
    <!-- Enhanced glass morphism effect with glow -->
    <div class="absolute -inset-0.5 rounded-xl opacity-30 group-hover:opacity-70 blur group-hover:blur-md transition-all duration-300 bg-gradient-to-r from-primary-500/50 to-violet-500/50"></div>
    
    <!-- Card with enhanced glass morphism -->
    <div class="relative bg-dark-900/70 backdrop-blur-lg rounded-xl overflow-hidden border border-dark-800/50 group-hover:border-opacity-0 transition-all duration-300">
      <!-- Card header with gradient -->
      <div class="h-2 w-full bg-gradient-to-r from-primary-500 to-violet-500"></div>
      
      <div class="p-6 sm:p-8">
        <h2 class="text-xl font-bold mb-6 bg-gradient-to-r from-primary-400 to-violet-400 bg-clip-text text-transparent">
          {{ title }}
        </h2>
        
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
          <div class="flex-grow">
            <!-- Balance display with enhanced styling -->
            <div>
              <div class="text-sm text-gray-400 mb-1">{{ balanceLabel }}</div>
              <div class="flex items-baseline gap-2">
                <div v-if="loading" class="animate-pulse">
                  <div class="h-9 w-20 bg-dark-800 rounded"></div>
                </div>
                <div v-else class="text-3xl font-bold bg-gradient-to-r from-primary-300 to-violet-300 bg-clip-text text-transparent">
                  {{ credits.toLocaleString() }}
                </div>
                <div class="text-sm text-primary-400">credits</div>
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
              <!-- Default action button with modern styling -->
              <button class="relative group transform transition-all duration-300 hover:-translate-y-1 px-4 py-2 rounded-xl text-white backdrop-blur-sm border border-dark-800/50 hover:border-primary-500/50 overflow-hidden bg-dark-800/70">
                <span class="relative z-10 flex items-center justify-center text-sm font-medium">
                  <i class="fas fa-plus mr-2"></i>
                  Add Credits
                </span>
              </button>
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