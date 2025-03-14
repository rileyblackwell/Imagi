<template>
  <PaymentLayout>
    <div class="container mx-auto px-4 py-12">
      <div class="max-w-4xl mx-auto">
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-12">
          <div>
            <h1 class="text-3xl font-bold text-white mb-2">Credits Dashboard</h1>
            <p class="text-gray-400">Manage your Imagi credits and payment history</p>
          </div>
          
          <router-link 
            to="/payments/add-credits" 
            class="mt-4 md:mt-0 px-6 py-2 bg-primary-500 text-white font-medium rounded-lg hover:bg-primary-600 transition-colors"
          >
            Add Credits
          </router-link>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
          <div class="bg-dark-800 border border-gray-700 rounded-lg p-6">
            <h2 class="text-xl font-semibold text-white mb-4">Current Balance</h2>
            <BalanceDisplay 
              :balance="store.balance"
              :loading="store.isLoading"
              label="Available Credits"
            />
          </div>
          
          <div class="bg-dark-800 border border-gray-700 rounded-lg p-6">
            <h2 class="text-xl font-semibold text-white mb-4">Usage Stats</h2>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <div class="text-sm text-gray-400 mb-1">Projects Created</div>
                <div class="font-semibold text-2xl text-white">12</div>
              </div>
              <div>
                <div class="text-sm text-gray-400 mb-1">Credits Used</div>
                <div class="font-semibold text-2xl text-white">320</div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="bg-dark-800 border border-gray-700 rounded-lg p-6">
          <h2 class="text-xl font-semibold text-white mb-6">Recent Transactions</h2>
          
          <div v-if="store.isHistoryLoading" class="text-center py-12">
            <div class="animate-spin text-2xl text-primary-500 mb-2">⟳</div>
            <p class="text-gray-400">Loading transaction history...</p>
          </div>
          
          <div v-else-if="store.paymentHistory.length === 0" class="text-center py-12">
            <p class="text-gray-400">No transactions yet.</p>
          </div>
          
          <div v-else class="overflow-x-auto">
            <table class="w-full min-w-full">
              <thead>
                <tr class="border-b border-gray-700">
                  <th class="py-3 px-4 text-left text-sm font-medium text-gray-400">Date</th>
                  <th class="py-3 px-4 text-left text-sm font-medium text-gray-400">Description</th>
                  <th class="py-3 px-4 text-right text-sm font-medium text-gray-400">Amount</th>
                  <th class="py-3 px-4 text-right text-sm font-medium text-gray-400">Status</th>
                </tr>
              </thead>
              <tbody>
                <tr 
                  v-for="transaction in store.paymentHistory" 
                  :key="transaction.id"
                  class="border-b border-gray-700"
                >
                  <td class="py-3 px-4 text-sm text-white">
                    {{ new Date(transaction.created_at).toLocaleDateString() }}
                  </td>
                  <td class="py-3 px-4 text-sm text-white">
                    {{ transaction.description }}
                  </td>
                  <td class="py-3 px-4 text-sm text-white text-right">
                    ${{ transaction.amount.toFixed(2) }}
                  </td>
                  <td class="py-3 px-4 text-right">
                    <span 
                      class="inline-block px-2 py-1 text-xs rounded-full"
                      :class="{
                        'bg-green-500/20 text-green-400': transaction.status === 'completed',
                        'bg-yellow-500/20 text-yellow-400': transaction.status === 'pending',
                        'bg-red-500/20 text-red-400': transaction.status === 'failed'
                      }"
                    >
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
  </PaymentLayout>
</template>

<script>
import { onMounted } from 'vue'
import PaymentLayout from '../layouts/PaymentLayout.vue'
import BalanceDisplay from '../components/atoms/BalanceDisplay.vue'
import { usePaymentsStore } from '../store'

export default {
  name: 'DashboardView',
  components: {
    PaymentLayout,
    BalanceDisplay
  },
  setup() {
    const store = usePaymentsStore()
    
    onMounted(() => {
      // Fetch user's balance and payment history
      store.fetchBalance()
      store.fetchPaymentHistory()
    })
    
    return {
      store
    }
  }
}
</script> 