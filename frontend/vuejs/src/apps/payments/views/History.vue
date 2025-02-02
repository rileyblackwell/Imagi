<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="bg-dark-800 rounded-lg shadow-xl overflow-hidden border border-dark-700">
      <!-- Header -->
      <div class="p-6 border-b border-dark-700">
        <h2 class="text-2xl font-bold text-white">Payment History</h2>
        <p class="text-gray-400 mt-2">View your past transactions and credit usage</p>
      </div>

      <!-- Main Content -->
      <div class="p-6">
        <!-- Loading State -->
        <div v-if="isLoading" class="flex justify-center items-center py-12">
          <div class="spinner"></div>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="text-center py-12">
          <p class="text-red-500">{{ error }}</p>
          <button 
            @click="loadTransactions" 
            class="mt-4 text-primary-400 hover:text-primary-300"
          >
            Try Again
          </button>
        </div>

        <!-- Empty State -->
        <div 
          v-else-if="!transactions.length" 
          class="text-center py-12"
        >
          <p class="text-gray-400">No transactions found</p>
          <router-link 
            :to="{ name: 'payments-credits' }" 
            class="mt-4 inline-block text-primary-400 hover:text-primary-300"
          >
            Add Credits
          </router-link>
        </div>

        <!-- Transactions List -->
        <div v-else class="space-y-4">
          <div 
            v-for="transaction in transactions" 
            :key="transaction.id"
            class="bg-dark-900 rounded-lg p-4"
          >
            <div class="flex justify-between items-start">
              <!-- Transaction Details -->
              <div>
                <p class="text-white font-medium">
                  {{ transaction.type === 'credit' ? 'Added Credits' : 'Used Credits' }}
                </p>
                <p class="text-sm text-gray-400">
                  {{ new Date(transaction.created_at).toLocaleDateString() }}
                </p>
                <p class="text-sm text-gray-400 mt-1">
                  {{ transaction.description }}
                </p>
              </div>

              <!-- Amount -->
              <div :class="[
                'text-lg font-bold',
                transaction.type === 'credit' ? 'text-green-400' : 'text-red-400'
              ]">
                {{ transaction.type === 'credit' ? '+' : '-' }}${{ transaction.amount.toFixed(2) }}
              </div>
            </div>

            <!-- Status Badge -->
            <div class="mt-4 flex items-center">
              <span 
                :class="[
                  'px-2 py-1 text-xs rounded-full',
                  transaction.status === 'completed' ? 'bg-green-900 text-green-400' : 
                  transaction.status === 'pending' ? 'bg-yellow-900 text-yellow-400' :
                  'bg-red-900 text-red-400'
                ]"
              >
                {{ transaction.status.charAt(0).toUpperCase() + transaction.status.slice(1) }}
              </span>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <div v-if="transactions.length" class="mt-6 flex justify-between items-center">
          <button
            :disabled="currentPage === 1"
            @click="loadPreviousPage"
            class="text-gray-400 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          <span class="text-gray-400">Page {{ currentPage }}</span>
          <button
            :disabled="!hasMorePages"
            @click="loadNextPage"
            class="text-gray-400 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import PaymentService from '../services/payment_service'
import { useToast } from '../composables/useToast'

export default {
  name: 'PaymentHistory',
  setup() {
    const paymentService = new PaymentService()
    const toast = useToast()
    const transactions = ref([])
    const isLoading = ref(false)
    const error = ref(null)
    const currentPage = ref(1)
    const hasMorePages = ref(false)

    async function loadTransactions(page = 1) {
      try {
        isLoading.value = true
        error.value = null
        const response = await paymentService.getTransactionHistory()
        transactions.value = response.transactions || []
        hasMorePages.value = response.has_more || false
        currentPage.value = page
      } catch (err) {
        error.value = 'Failed to load transactions'
        toast.error('Failed to load transactions')
        console.error('Transaction loading error:', err)
      } finally {
        isLoading.value = false
      }
    }

    function loadNextPage() {
      if (hasMorePages.value) {
        loadTransactions(currentPage.value + 1)
      }
    }

    function loadPreviousPage() {
      if (currentPage.value > 1) {
        loadTransactions(currentPage.value - 1)
      }
    }

    onMounted(() => {
      loadTransactions()
    })

    return {
      transactions,
      isLoading,
      error,
      currentPage,
      hasMorePages,
      loadTransactions,
      loadNextPage,
      loadPreviousPage
    }
  }
}
</script>

<style scoped>
.spinner {
  border: 3px solid rgba(0, 255, 198, 0.1);
  border-radius: 50%;
  border-top: 3px solid #00ffc6;
  width: 24px;
  height: 24px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style> 