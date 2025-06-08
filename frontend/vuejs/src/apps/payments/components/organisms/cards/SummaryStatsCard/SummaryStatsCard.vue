<template>
  <div class="summary-stats-card group relative transform transition-all duration-300 hover:-translate-y-1">
    <div class="absolute -inset-0.5 rounded-2xl opacity-30 group-hover:opacity-70 bg-gradient-to-r from-amber-500/50 to-orange-500/50 blur group-hover:blur-md transition-all duration-300"></div>
    <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
      <!-- Sleek gradient header -->
      <div class="h-1 w-full bg-gradient-to-r from-amber-400 via-orange-400 to-amber-400 opacity-80"></div>
      
      <!-- Subtle background effects -->
      <div class="absolute -top-32 -right-32 w-64 h-64 bg-gradient-to-br from-amber-400/4 to-orange-400/4 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"></div>
      
      <div class="relative z-10 p-6">
        <!-- Modern pill badge -->
        <div class="inline-flex items-center px-3 py-1 bg-gradient-to-r from-amber-500/15 to-orange-500/15 border border-amber-400/20 rounded-full mb-6 backdrop-blur-sm">
          <div class="w-1.5 h-1.5 bg-amber-400 rounded-full mr-2 animate-pulse"></div>
          <span class="text-amber-300 font-medium text-xs tracking-wide uppercase">Summary</span>
        </div>
        
        <h3 class="text-xl font-semibold text-white mb-4">Payment Summary</h3>
        
        <div class="flex flex-col gap-4">
          <!-- Total Credits Added -->
          <div class="flex justify-between items-center py-3 border-b border-white/10">
            <div class="flex items-center">
              <div class="w-8 h-8 bg-gradient-to-br from-emerald-500/20 to-green-500/20 rounded-xl flex items-center justify-center mr-3 border border-emerald-400/20">
                <i class="fas fa-arrow-up text-emerald-400 text-sm"></i>
              </div>
              <span class="text-gray-300">Total Credits Added</span>
            </div>
            <span class="text-white font-semibold">{{ Number(totalAdded).toFixed(3) }}</span>
          </div>
          
          <!-- Total Credits Spent -->
          <div class="flex justify-between items-center py-3 border-b border-white/10">
            <div class="flex items-center">
              <div class="w-8 h-8 bg-gradient-to-br from-red-500/20 to-rose-500/20 rounded-xl flex items-center justify-center mr-3 border border-red-400/20">
                <i class="fas fa-arrow-down text-red-400 text-sm"></i>
              </div>
              <span class="text-gray-300">Total Credits Spent</span>
            </div>
            <span class="text-white font-semibold">{{ Number(totalSpent).toFixed(3) }}</span>
          </div>
          
          <!-- Total Transactions -->
          <div class="flex justify-between items-center py-3">
            <div class="flex items-center">
              <div class="w-8 h-8 bg-gradient-to-br from-blue-500/20 to-indigo-500/20 rounded-xl flex items-center justify-center mr-3 border border-blue-400/20">
                <i class="fas fa-receipt text-blue-400 text-sm"></i>
              </div>
              <span class="text-gray-300">Total Transactions</span>
            </div>
            <span class="text-white font-semibold">{{ totalTransactions }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  totalSpent: number
  totalAdded: number
  totalTransactions: number
}>()
</script> 