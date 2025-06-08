<template>
  <div class="time-period-selector group relative transform transition-all duration-300 hover:-translate-y-1">
    <div class="absolute -inset-0.5 rounded-2xl opacity-30 group-hover:opacity-70 bg-gradient-to-r from-cyan-500/50 to-emerald-500/50 blur group-hover:blur-md transition-all duration-300"></div>
    <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
      <!-- Sleek gradient header -->
      <div class="h-1 w-full bg-gradient-to-r from-cyan-400 via-emerald-400 to-cyan-400 opacity-80"></div>
      
      <!-- Subtle background effects -->
      <div class="absolute -top-32 -left-32 w-64 h-64 bg-gradient-to-br from-cyan-400/4 to-emerald-400/4 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"></div>
      
      <div class="relative z-10 p-6">
        <!-- Modern pill badge -->
        <div class="inline-flex items-center px-3 py-1 bg-gradient-to-r from-cyan-500/15 to-emerald-500/15 border border-cyan-400/20 rounded-full mb-6 backdrop-blur-sm">
          <div class="w-1.5 h-1.5 bg-cyan-400 rounded-full mr-2 animate-pulse"></div>
          <span class="text-cyan-300 font-medium text-xs tracking-wide uppercase">Time Period</span>
        </div>
        
        <h3 class="text-xl font-semibold text-white mb-4">Filter Time Period</h3>
        
        <div class="grid grid-cols-2 gap-2">
          <button 
            @click="selectPeriod('week')" 
            :class="[
              'px-4 py-2 rounded-lg font-medium text-sm transition-all duration-200',
              modelValue === 'week' 
                ? 'bg-gradient-to-r from-cyan-500 to-emerald-500 text-white shadow-lg shadow-cyan-500/25' 
                : 'bg-white/5 text-gray-300 hover:bg-white/10 border border-white/10 hover:border-cyan-400/30'
            ]"
          >
            Last Week
          </button>
          
          <button 
            @click="selectPeriod('month')" 
            :class="[
              'px-4 py-2 rounded-lg font-medium text-sm transition-all duration-200',
              modelValue === 'month' 
                ? 'bg-gradient-to-r from-cyan-500 to-emerald-500 text-white shadow-lg shadow-cyan-500/25' 
                : 'bg-white/5 text-gray-300 hover:bg-white/10 border border-white/10 hover:border-cyan-400/30'
            ]"
          >
            Last Month
          </button>
          
          <button 
            @click="selectPeriod('quarter')" 
            :class="[
              'px-4 py-2 rounded-lg font-medium text-sm transition-all duration-200',
              modelValue === 'quarter' 
                ? 'bg-gradient-to-r from-cyan-500 to-emerald-500 text-white shadow-lg shadow-cyan-500/25' 
                : 'bg-white/5 text-gray-300 hover:bg-white/10 border border-white/10 hover:border-cyan-400/30'
            ]"
          >
            Last 3 Months
          </button>
          
          <button 
            @click="selectPeriod('year')" 
            :class="[
              'px-4 py-2 rounded-lg font-medium text-sm transition-all duration-200',
              modelValue === 'year' 
                ? 'bg-gradient-to-r from-cyan-500 to-emerald-500 text-white shadow-lg shadow-cyan-500/25' 
                : 'bg-white/5 text-gray-300 hover:bg-white/10 border border-white/10 hover:border-cyan-400/30'
            ]"
          >
            Last Year
          </button>
          
          <button 
            @click="selectPeriod('all')" 
            :class="[
              'px-4 py-2 rounded-lg font-medium text-sm transition-all duration-200 col-span-2',
              modelValue === 'all' 
                ? 'bg-gradient-to-r from-cyan-500 to-emerald-500 text-white shadow-lg shadow-cyan-500/25' 
                : 'bg-white/5 text-gray-300 hover:bg-white/10 border border-white/10 hover:border-cyan-400/30'
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