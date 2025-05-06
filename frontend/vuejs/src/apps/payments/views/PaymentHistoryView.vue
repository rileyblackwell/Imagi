<template>
  <PaymentLayout>
    <div class="payment-history-view max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 relative">
      <!-- Animated background elements -->
      <div class="absolute -z-10 inset-0 pointer-events-none overflow-hidden">
        <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.03]"></div>
        <div class="absolute top-[20%] right-[10%] w-[400px] sm:w-[600px] h-[400px] sm:h-[600px] rounded-full bg-primary-600/5 blur-[120px] animate-pulse-slow"></div>
        <div class="absolute bottom-[10%] left-[10%] w-[350px] sm:w-[500px] h-[350px] sm:h-[500px] rounded-full bg-violet-600/5 blur-[100px] animate-pulse-slow animation-delay-150"></div>
      </div>
    
      <!-- Page Header with modern styling -->
      <div class="mb-16 text-center">
        <div class="inline-block px-4 py-1.5 bg-primary-500/10 rounded-full mb-3">
          <span class="text-primary-400 font-semibold text-sm tracking-wider">PAYMENT HISTORY</span>
        </div>
        <h1 class="text-4xl sm:text-5xl font-bold text-white mb-4 leading-tight">
          <span>Your </span>
          <span class="bg-gradient-to-r from-primary-400 to-violet-400 bg-clip-text text-transparent">Transactions</span>
        </h1>
        <p class="text-xl text-gray-300 max-w-3xl mx-auto">
          Track your credit purchases and usage over time.
        </p>
        
        <!-- Decorative line with gradient -->
        <div class="w-24 h-1 bg-gradient-to-r from-primary-500 to-violet-500 rounded-full mx-auto mt-8"></div>
      </div>
      
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Left Column: Account & Status -->
        <div class="lg:col-span-1 flex flex-col gap-8">
          <!-- Current Balance Card -->
          <div class="animate-fade-in-up animation-delay-300">
            <AccountBalanceCard
              :credits="userCredits"
              :loading="isLoading"
              :last-updated="lastUpdated || undefined"
            />
          </div>
          
          <!-- Period Selection Card -->
          <div class="animate-fade-in-up animation-delay-450">
            <TimePeriodSelector 
              v-model="selectedPeriod" 
              @period-changed="fetchHistoryData"
            />
          </div>
          
          <!-- Summary Stats Card -->
          <div class="animate-fade-in-up animation-delay-600">
            <SummaryStatsCard 
              :total-spent="totalSpent"
              :total-added="totalAdded"
              :total-transactions="transactions.length"
            />
          </div>
        </div>
        
        <!-- Right Column: Charts and Transaction History -->
        <div class="lg:col-span-2 flex flex-col gap-8">
          <!-- Balance Over Time Chart -->
          <div class="animate-fade-in-up animation-delay-300">
            <div class="relative group">
              <div class="absolute -inset-0.5 rounded-xl opacity-30 group-hover:opacity-70 bg-gradient-to-r from-primary-500/50 to-violet-500/50 blur group-hover:blur-md transition-all duration-300"></div>
              <div class="relative bg-dark-900/70 backdrop-blur-lg rounded-xl overflow-hidden border border-dark-800/50 group-hover:border-opacity-0 transition-all duration-300">
                <!-- Card header with gradient -->
                <div class="h-2 w-full bg-gradient-to-r from-primary-500 to-violet-500"></div>
                
                <div class="p-6">
                  <h3 class="text-xl font-semibold text-white mb-4">Balance Over Time</h3>
                  <div class="h-64">
                    <BalanceChart 
                      :chart-data="balanceChartData" 
                      :loading="isHistoryLoading"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Transaction History Table -->
          <div class="animate-fade-in-up animation-delay-450">
            <div class="relative group">
              <div class="absolute -inset-0.5 rounded-xl opacity-30 group-hover:opacity-70 bg-gradient-to-r from-primary-500/50 to-violet-500/50 blur group-hover:blur-md transition-all duration-300"></div>
              <div class="relative bg-dark-900/70 backdrop-blur-lg rounded-xl overflow-hidden border border-dark-800/50 group-hover:border-opacity-0 transition-all duration-300">
                <!-- Card header with gradient -->
                <div class="h-2 w-full bg-gradient-to-r from-primary-500 to-violet-500"></div>
                
                <div class="p-6">
                  <div class="flex justify-between items-center mb-6">
                    <h3 class="text-xl font-semibold text-white">Transaction History</h3>
                    
                    <div class="flex gap-2">
                      <!-- Transaction Type Filter -->
                      <select 
                        v-model="transactionFilter" 
                        class="bg-dark-800 border border-dark-700 rounded-md text-gray-300 px-3 py-1.5 text-sm focus:ring-primary-500 focus:border-primary-500"
                      >
                        <option value="all">All Transactions</option>
                        <option value="purchase">Purchases</option>
                        <option value="usage">Usage</option>
                      </select>
                      
                      <!-- Time Sort Order -->
                      <select 
                        v-model="sortOrder" 
                        class="bg-dark-800 border border-dark-700 rounded-md text-gray-300 px-3 py-1.5 text-sm focus:ring-primary-500 focus:border-primary-500"
                      >
                        <option value="desc">Newest First</option>
                        <option value="asc">Oldest First</option>
                      </select>
                    </div>
                  </div>
                  
                  <!-- Transaction List with Loading State -->
                  <div v-if="isHistoryLoading" class="py-12 flex justify-center items-center">
                    <div class="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-primary-400 border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite]"></div>
                  </div>
                  
                  <div v-else-if="filteredTransactions.length === 0" class="py-12 text-center">
                    <div class="text-gray-400">No transactions found</div>
                  </div>
                  
                  <div v-else class="overflow-x-auto">
                    <table class="min-w-full divide-y divide-dark-700">
                      <thead>
                        <tr>
                          <th class="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Date</th>
                          <th class="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Description</th>
                          <th class="px-4 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">Amount</th>
                          <th class="px-4 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">Status</th>
                        </tr>
                      </thead>
                      <tbody class="divide-y divide-dark-700">
                        <tr v-for="transaction in filteredTransactions" :key="transaction.id" class="hover:bg-dark-800/40 transition-colors">
                          <td class="px-4 py-3 text-sm text-gray-300">
                            {{ formatDate(transaction.created_at) }}
                          </td>
                          <td class="px-4 py-3 text-sm text-gray-300">
                            {{ transaction.description }}
                          </td>
                          <td class="px-4 py-3 text-sm text-right" :class="getAmountClass(transaction.amount)">
                            {{ formatCredits(transaction.amount) }}
                          </td>
                          <td class="px-4 py-3 text-sm text-right">
                            <span :class="getStatusClass(transaction.status)" class="px-2 py-1 rounded-full text-xs inline-flex items-center">
                              <span class="w-1.5 h-1.5 rounded-full mr-1" :class="getStatusDotClass(transaction.status)"></span>
                              {{ transaction.status }}
                            </span>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </PaymentLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { usePaymentsStore } from '../store'
import { storeToRefs } from 'pinia'
import PaymentLayout from '../layouts/PaymentLayout.vue'
import AccountBalanceCard from '../components/organisms/AccountBalanceCard.vue'
import TimePeriodSelector from '../components/molecules/TimePeriodSelector.vue'
import SummaryStatsCard from '../components/organisms/SummaryStatsCard.vue'
import BalanceChart from '../components/organisms/BalanceChart.vue'
import type { Transaction } from '../types'

const store = usePaymentsStore()
const { userCredits, lastUpdated, isLoading, isHistoryLoading, transactions } = storeToRefs(store)

// State for filtering and time periods
const selectedPeriod = ref('month')
const transactionFilter = ref('all')
const sortOrder = ref('desc')
const balanceChartData = ref({
  labels: [] as string[],
  datasets: [{
    label: 'Account Balance',
    data: [] as number[],
    borderColor: '#8B5CF6',
    backgroundColor: 'rgba(139, 92, 246, 0.1)',
    fill: true,
    tension: 0.4
  }]
})

// Computed properties for filtered data
const filteredTransactions = computed(() => {
  let filtered = [...transactions.value]
  
  // Apply transaction type filter
  if (transactionFilter.value !== 'all') {
    filtered = filtered.filter(t => {
      if (transactionFilter.value === 'purchase') {
        return t.amount > 0
      } else {
        return t.amount < 0
      }
    })
  }
  
  // Apply sort order
  filtered.sort((a, b) => {
    const dateA = new Date(a.created_at).getTime()
    const dateB = new Date(b.created_at).getTime()
    return sortOrder.value === 'desc' ? dateB - dateA : dateA - dateB
  })
  
  return filtered
})

// Computed statistics
const roundOrShow = (value: number) => {
  return value >= 1000 ? Math.round(value / 1000) * 1000 : value
}

const totalSpent = computed(() => {
  return transactions.value
    .filter(t => t.amount < 0)
    .reduce((sum, t) => sum + Math.abs(Number(t.amount)), 0)
})

const totalAdded = computed(() => {
  const sum = transactions.value
    .filter(t => t.amount > 0)
    .reduce((acc, t) => acc + Number(t.amount), 0)
  return roundOrShow(sum)
})

// Methods
const fetchHistoryData = async () => {
  try {
    await store.fetchTransactions()
    generateChartData()
  } catch (error) {
    console.error('Error fetching transaction data:', error)
  }
}

const generateChartData = () => {
  // Sort transactions by date (oldest first for chart data)
  const sortedTransactions = [...transactions.value].sort((a, b) => {
    return new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
  })
  
  // Generate cumulative balance over time
  let runningBalance = 0
  const balanceData: number[] = []
  const dateLabels: string[] = []
  
  sortedTransactions.forEach(transaction => {
    runningBalance += transaction.amount
    balanceData.push(runningBalance)
    dateLabels.push(formatDate(transaction.created_at))
  })
  
  // Update chart data
  balanceChartData.value = {
    labels: dateLabels,
    datasets: [{
      label: 'Account Balance',
      data: balanceData,
      borderColor: '#8B5CF6',
      backgroundColor: 'rgba(139, 92, 246, 0.1)',
      fill: true,
      tension: 0.4
    }]
  }
}

// Utility functions for formatting
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  })
}

const formatCredits = (amount: number) => {
  return amount > 0 
    ? `+${amount} credits` 
    : `${amount} credits`
}

const getAmountClass = (amount: number) => {
  return amount > 0 
    ? 'text-green-400' 
    : 'text-red-400'
}

const getStatusClass = (status: string) => {
  switch (status.toLowerCase()) {
    case 'completed':
      return 'bg-green-500/20 text-green-400'
    case 'pending':
      return 'bg-yellow-500/20 text-yellow-400'
    case 'failed':
      return 'bg-red-500/20 text-red-400'
    default:
      return 'bg-gray-500/20 text-gray-400'
  }
}

const getStatusDotClass = (status: string) => {
  switch (status.toLowerCase()) {
    case 'completed':
      return 'bg-green-400'
    case 'pending':
      return 'bg-yellow-400'
    case 'failed':
      return 'bg-red-400'
    default:
      return 'bg-gray-400'
  }
}

// Lifecycle hooks
onMounted(async () => {
  try {
    // Initialize the payment system
    await store.initializePayments()
    
    // Fetch transaction history
    await fetchHistoryData()
  } catch (err: any) {
    console.error('Failed to initialize payment history:', err)
  }
})

// Watch for filter changes to regenerate chart data
watch([selectedPeriod, transactionFilter], () => {
  fetchHistoryData()
})
</script>

<style scoped>
/* Animation delays */
.animation-delay-150 {
  animation-delay: 150ms;
}

.animation-delay-300 {
  animation-delay: 300ms;
}

.animation-delay-450 {
  animation-delay: 450ms;
}

.animation-delay-600 {
  animation-delay: 600ms;
}

.animation-delay-750 {
  animation-delay: 750ms;
}

@keyframes fade-in-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in-up {
  animation: fade-in-up 0.7s ease-out forwards;
}

@keyframes pulse-slow {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 0.8; }
}

.animate-pulse-slow {
  animation: pulse-slow 3s ease-in-out infinite;
}
</style> 