<template>
  <PaymentLayout>
    <div class="payment-history-view min-h-screen bg-dark-950 relative overflow-hidden">
      <!-- Enhanced Background Effects matching About page -->
      <div class="absolute inset-0 pointer-events-none">
        <!-- Enhanced Pattern Overlay -->
        <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.03]"></div>
        <div class="absolute inset-0 bg-noise opacity-[0.015]"></div>
        <div class="absolute inset-0 bg-gradient-to-br from-primary-950/10 via-dark-900 to-violet-950/10"></div>
        
        <!-- Enhanced Glowing Orbs Animation -->
        <div class="absolute -top-[10%] right-[15%] w-[800px] h-[800px] rounded-full bg-cyan-600/5 blur-[150px] animate-float"></div>
        <div class="absolute bottom-[5%] left-[20%] w-[600px] h-[600px] rounded-full bg-emerald-600/5 blur-[120px] animate-float-delay"></div>
        
        <!-- Animated Lines and Particles -->
        <div class="absolute left-0 right-0 top-1/3 h-px bg-gradient-to-r from-transparent via-cyan-500/20 to-transparent animate-pulse-slow"></div>
        <div class="absolute left-0 right-0 bottom-1/3 h-px bg-gradient-to-r from-transparent via-emerald-500/20 to-transparent animate-pulse-slow delay-700"></div>
      </div>

      <!-- Enhanced Content Container -->
      <div class="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <!-- Modern Welcome Header Section -->
        <div class="mb-16 text-center">
          <div class="inline-flex items-center px-4 py-1.5 bg-gradient-to-r from-cyan-500/10 to-emerald-500/10 rounded-full mb-3">
            <span class="text-cyan-400 font-semibold text-sm tracking-wider">PAYMENT HISTORY</span>
          </div>
          <h1 class="text-4xl sm:text-5xl font-bold text-white mb-4 leading-tight">
            <span>Your </span>
            <span class="bg-gradient-to-r from-cyan-400 to-emerald-400 bg-clip-text text-transparent">Transactions</span>
          </h1>
          <p class="text-xl text-gray-300 max-w-3xl mx-auto">
            Track your credit purchases and usage over time.
          </p>
          
          <!-- Decorative line with gradient -->
          <div class="w-24 h-1 bg-gradient-to-r from-cyan-500 to-emerald-500 rounded-full mx-auto mt-8"></div>
        </div>
        
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <!-- Left Column: Account & Status -->
          <div class="lg:col-span-1 flex flex-col gap-8">
            <!-- Current Balance Card -->
            <div class="animate-fade-in-up animation-delay-300">
              <AccountBalanceCard
                :credits="store.balance ?? 0"
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
              <div class="group relative transform transition-all duration-300 hover:-translate-y-1">
                <div class="absolute -inset-0.5 rounded-2xl opacity-30 group-hover:opacity-70 bg-gradient-to-r from-cyan-500/50 to-emerald-500/50 blur group-hover:blur-md transition-all duration-300"></div>
                <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
                  <!-- Sleek gradient header -->
                  <div class="h-1 w-full bg-gradient-to-r from-cyan-400 via-emerald-400 to-cyan-400 opacity-80"></div>
                  
                  <!-- Subtle background effects -->
                  <div class="absolute -top-32 -right-32 w-64 h-64 bg-gradient-to-br from-cyan-400/4 to-emerald-400/4 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"></div>
                  
                  <div class="relative z-10 p-6">
                    <!-- Modern pill badge -->
                    <div class="inline-flex items-center px-3 py-1 bg-gradient-to-r from-cyan-500/15 to-emerald-500/15 border border-cyan-400/20 rounded-full mb-6 backdrop-blur-sm">
                      <div class="w-1.5 h-1.5 bg-cyan-400 rounded-full mr-2 animate-pulse"></div>
                      <span class="text-cyan-300 font-medium text-xs tracking-wide uppercase">Balance Chart</span>
                    </div>
                    
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
              <div class="group relative transform transition-all duration-300 hover:-translate-y-1">
                <div class="absolute -inset-0.5 rounded-2xl opacity-30 group-hover:opacity-70 bg-gradient-to-r from-violet-500/50 to-indigo-500/50 blur group-hover:blur-md transition-all duration-300"></div>
                <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
                  <!-- Sleek gradient header -->
                  <div class="h-1 w-full bg-gradient-to-r from-violet-400 via-indigo-400 to-violet-400 opacity-80"></div>
                  
                  <!-- Subtle background effects -->
                  <div class="absolute -top-32 -left-32 w-64 h-64 bg-gradient-to-br from-violet-400/4 to-indigo-400/4 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"></div>
                  
                  <div class="relative z-10 p-6">
                    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
                      <!-- Modern pill badge -->
                      <div class="flex items-center gap-4">
                        <div class="inline-flex items-center px-3 py-1 bg-gradient-to-r from-violet-500/15 to-indigo-500/15 border border-violet-400/20 rounded-full backdrop-blur-sm">
                          <div class="w-1.5 h-1.5 bg-violet-400 rounded-full mr-2 animate-pulse"></div>
                          <span class="text-violet-300 font-medium text-xs tracking-wide uppercase">Transaction History</span>
                        </div>
                        <h3 class="text-xl font-semibold text-white">All Transactions</h3>
                      </div>
                      
                      <div class="flex gap-2">
                        <!-- Transaction Type Filter -->
                        <select 
                          v-model="transactionFilter" 
                          class="bg-dark-800/60 border border-white/20 rounded-lg text-gray-300 px-3 py-1.5 text-sm focus:ring-violet-500 focus:border-violet-500 backdrop-blur-sm"
                        >
                          <option value="all">All Transactions</option>
                          <option value="purchase">Purchases</option>
                          <option value="usage">Usage</option>
                        </select>
                        
                        <!-- Time Sort Order -->
                        <select 
                          v-model="sortOrder" 
                          class="bg-dark-800/60 border border-white/20 rounded-lg text-gray-300 px-3 py-1.5 text-sm focus:ring-violet-500 focus:border-violet-500 backdrop-blur-sm"
                        >
                          <option value="desc">Newest First</option>
                          <option value="asc">Oldest First</option>
                        </select>
                      </div>
                    </div>
                    
                    <!-- Transaction List with Loading State -->
                    <div v-if="isHistoryLoading" class="py-12 flex justify-center items-center">
                      <div class="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-violet-400 border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite]"></div>
                    </div>
                    
                    <div v-else-if="filteredTransactions.length === 0" class="py-12 text-center">
                      <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-violet-500/10 flex items-center justify-center">
                        <i class="fas fa-receipt text-violet-400 text-xl"></i>
                      </div>
                      <div class="text-gray-400 text-lg mb-2">No transactions found</div>
                      <div class="text-gray-500 text-sm">Try adjusting your filters or make your first purchase</div>
                    </div>
                    
                    <div v-else class="overflow-x-auto">
                      <table class="min-w-full divide-y divide-white/10">
                        <thead>
                          <tr>
                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Date</th>
                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Model</th>
                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Request Type</th>
                            <th class="px-4 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">Amount</th>
                            <th class="px-4 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">Status</th>
                          </tr>
                        </thead>
                        <tbody class="divide-y divide-white/10">
                          <tr v-for="transaction in filteredTransactions" :key="transaction.id" class="hover:bg-white/5 transition-colors">
                            <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-300">{{ formatDate(transaction.created_at) }}</td>
                            <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-300">{{ transaction.transaction_type || '—' }}</td>
                            <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-300">{{ transaction.transaction_type || '—' }}</td>
                            <td class="px-4 py-3 whitespace-nowrap text-sm text-right">
                              <span :class="getAmountClass(transaction.amount)">
                                {{ formatCredits(transaction.amount) }}
                              </span>
                            </td>
                            <td class="px-4 py-3 whitespace-nowrap text-sm text-right">
                              <span :class="['inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium', getStatusClass(transaction.status)]">
                                <span :class="['w-2 h-2 rounded-full mr-2', getStatusDotClass(transaction.status)]"></span>
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
    </div>
  </PaymentLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { usePaymentStore } from '../stores/payments'
import { storeToRefs } from 'pinia'
import PaymentLayout from '../layouts/PaymentLayout.vue'
import AccountBalanceCard from '../components/organisms/cards/AccountBalanceCard/AccountBalanceCard.vue'
import TimePeriodSelector from '../components/molecules/selectors/TimePeriodSelector/TimePeriodSelector.vue'
import SummaryStatsCard from '../components/organisms/cards/SummaryStatsCard/SummaryStatsCard.vue'
import BalanceChart from '../components/organisms/charts/BalanceChart/BalanceChart.vue'
import type { Transaction as BaseTransaction } from '../types/store'

type Transaction = BaseTransaction & {
  model?: string;
  request_type?: string;
};

const store = usePaymentStore()
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
  
  // Limit to 10 most recent transactions
  return filtered.slice(0, 10)
})

// Computed statistics
const roundOrShow = (value: number) => {
  return value >= 1000 ? Math.round(value / 1000) * 1000 : value
}

const totalSpent = computed(() => {
  return transactions.value
    .filter((t: Transaction) => t.amount < 0)
    .reduce((sum: number, t: Transaction) => sum + Math.abs(Number(t.amount)), 0)
})

const totalAdded = computed(() => {
  const sum = transactions.value
    .filter((t: Transaction) => t.amount > 0)
    .reduce((acc: number, t: Transaction) => acc + Number(t.amount), 0)
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
    // Initialize the payment system - loads balance and payment methods
    await store.initializePayments()
    
    // If balance is still null after initialization, try direct fetch
    if (store.balance === null) {
      await store.fetchBalance()
    }
    
    // Fetch transaction history
    await fetchHistoryData()
  } catch (error) {
    console.error('Failed to initialize payment history:', error)
  }
})

// Watch for filter changes to regenerate chart data
watch([selectedPeriod, transactionFilter], () => {
  fetchHistoryData()
})
</script>

<style scoped>
/* Completely remove any browser default styling for form inputs */
input, textarea, select {
  outline: none !important;
  box-shadow: none !important;
  -webkit-appearance: none !important;
  -moz-appearance: none !important;
  appearance: none !important;
}

input:focus, textarea:focus, select:focus {
  outline: none !important;
  box-shadow: none !important;
}

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

/* Float animation for background orbs */
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

.animate-float {
  animation: float 15s ease-in-out infinite;
}

.animate-float-delay {
  animation: float 18s ease-in-out infinite reverse;
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

/* Add subtle animation for loading state */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.animate-pulse-slow {
  animation: pulse 3s ease-in-out infinite;
}

.delay-700 {
  animation-delay: 700ms;
}
</style> 