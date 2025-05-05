<template>
  <div class="summary-stats-card relative group">
    <div class="absolute -inset-0.5 rounded-xl opacity-30 group-hover:opacity-70 bg-gradient-to-r from-primary-500/50 to-violet-500/50 blur group-hover:blur-md transition-all duration-300"></div>
    <div class="relative bg-dark-900/70 backdrop-blur-lg rounded-xl overflow-hidden border border-dark-800/50 group-hover:border-opacity-0 transition-all duration-300">
      <!-- Card header with gradient -->
      <div class="h-2 w-full bg-gradient-to-r from-primary-500 to-violet-500"></div>
      
      <div class="p-6">
        <h3 class="text-xl font-semibold text-white mb-4">Payment Summary</h3>
        
        <div class="flex flex-col gap-4">
          <!-- Total Credits Added -->
          <div class="flex justify-between items-center py-3 border-b border-dark-700">
            <div class="flex items-center">
              <div class="w-8 h-8 bg-green-500/10 rounded-full flex items-center justify-center mr-3">
                <i class="fas fa-arrow-up text-green-400 text-sm"></i>
              </div>
              <span class="text-gray-300">Total Credits Added</span>
            </div>
            <span class="text-white font-semibold">{{ totalAdded }}</span>
          </div>
          
          <!-- Total Credits Spent -->
          <div class="flex justify-between items-center py-3 border-b border-dark-700">
            <div class="flex items-center">
              <div class="w-8 h-8 bg-red-500/10 rounded-full flex items-center justify-center mr-3">
                <i class="fas fa-arrow-down text-red-400 text-sm"></i>
              </div>
              <span class="text-gray-300">Total Credits Spent</span>
            </div>
            <span class="text-white font-semibold">{{ totalSpent }}</span>
          </div>
          
          <!-- Total Transactions -->
          <div class="flex justify-between items-center py-3">
            <div class="flex items-center">
              <div class="w-8 h-8 bg-primary-500/10 rounded-full flex items-center justify-center mr-3">
                <i class="fas fa-exchange-alt text-primary-400 text-sm"></i>
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