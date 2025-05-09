<template>
  <div class="time-period-selector relative group">
    <div class="absolute -inset-0.5 rounded-xl opacity-30 group-hover:opacity-70 bg-gradient-to-r from-primary-500/50 to-violet-500/50 blur group-hover:blur-md transition-all duration-300"></div>
    <div class="relative bg-dark-900/70 backdrop-blur-lg rounded-xl overflow-hidden border border-dark-800/50 group-hover:border-opacity-0 transition-all duration-300">
      <!-- Card header with gradient -->
      <div class="h-2 w-full bg-gradient-to-r from-primary-500 to-violet-500"></div>
      
      <div class="p-6">
        <h3 class="text-xl font-semibold text-white mb-4">Filter Time Period</h3>
        
        <div class="grid grid-cols-2 gap-2">
          <button 
            @click="selectPeriod('week')" 
            :class="[
              'px-4 py-2 rounded-lg font-medium text-sm transition-all',
              modelValue === 'week' 
                ? 'bg-primary-500 text-white' 
                : 'bg-dark-800 text-gray-300 hover:bg-dark-700'
            ]"
          >
            Last Week
          </button>
          
          <button 
            @click="selectPeriod('month')" 
            :class="[
              'px-4 py-2 rounded-lg font-medium text-sm transition-all',
              modelValue === 'month' 
                ? 'bg-primary-500 text-white' 
                : 'bg-dark-800 text-gray-300 hover:bg-dark-700'
            ]"
          >
            Last Month
          </button>
          
          <button 
            @click="selectPeriod('quarter')" 
            :class="[
              'px-4 py-2 rounded-lg font-medium text-sm transition-all',
              modelValue === 'quarter' 
                ? 'bg-primary-500 text-white' 
                : 'bg-dark-800 text-gray-300 hover:bg-dark-700'
            ]"
          >
            Last 3 Months
          </button>
          
          <button 
            @click="selectPeriod('year')" 
            :class="[
              'px-4 py-2 rounded-lg font-medium text-sm transition-all',
              modelValue === 'year' 
                ? 'bg-primary-500 text-white' 
                : 'bg-dark-800 text-gray-300 hover:bg-dark-700'
            ]"
          >
            Last Year
          </button>
          
          <button 
            @click="selectPeriod('all')" 
            :class="[
              'px-4 py-2 rounded-lg font-medium text-sm transition-all col-span-2',
              modelValue === 'all' 
                ? 'bg-primary-500 text-white' 
                : 'bg-dark-800 text-gray-300 hover:bg-dark-700'
            ]"
          >
            All Time
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  modelValue: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'period-changed', value: string): void
}>()

const selectPeriod = (period: string) => {
  emit('update:modelValue', period)
  emit('period-changed', period)
}
</script> 