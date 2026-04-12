<template>
  <div>
    <!-- Filters -->
    <div class="mb-6 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div class="flex items-center">
        <span class="text-gray-400 mr-2">Filter:</span>
        <select 
          v-model="filter" 
          class="bg-dark-900 border border-dark-700 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        >
          <option value="all">All Transactions</option>
          <option value="completed">Completed</option>
          <option value="pending">Pending</option>
          <option value="failed">Failed</option>
        </select>
      </div>
      <div class="flex items-center">
        <span class="text-gray-400 mr-2">Sort:</span>
        <select 
          v-model="sort" 
          class="bg-dark-900 border border-dark-700 text-white rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        >
          <option value="date-desc">Newest First</option>
          <option value="date-asc">Oldest First</option>
          <option value="amount-desc">Amount (High to Low)</option>
          <option value="amount-asc">Amount (Low to High)</option>
        </select>
      </div>
    </div>

    <!-- Table -->
    <div class="overflow-x-auto">
      <table class="min-w-full divide-y divide-dark-700">
        <thead class="bg-dark-900">
          <tr>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
              Date
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
              Description
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
              Amount
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
              Status
            </th>
          </tr>
        </thead>
        <tbody class="bg-dark-800 divide-y divide-dark-700">
          <tr v-for="transaction in paginatedTransactions" :key="transaction.id" class="hover:bg-dark-700">
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
              {{ formatDate(transaction.created_at) }}
            </td>
            <td class="px-6 py-4 text-sm text-gray-300">
              {{ transaction.description }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium" :class="getAmountClass(transaction.amount)">
              {{ formatAmount(transaction.amount) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
              <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full" :class="getStatusClass(transaction.status)">
                {{ transaction.status }}
              </span>
            </td>
          </tr>

          <!-- Empty State -->
          <tr v-if="paginatedTransactions.length === 0">
            <td colspan="4" class="px-6 py-8 text-center text-gray-400">
              No transactions found matching your filters.
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div class="mt-6 flex justify-between items-center">
      <div class="text-sm text-gray-400">
        Showing {{ paginatedTransactions.length }} of {{ filteredTransactions.length }} transactions
      </div>
      <div class="flex space-x-2">
        <PaymentButton
          variant="secondary"
          @click="prevPage"
          :disabled="currentPage === 1"
          custom-class="!py-1 !px-3 text-sm"
        >
          Previous
        </PaymentButton>
        <PaymentButton
          variant="secondary"
          @click="nextPage"
          :disabled="currentPage >= totalPages"
          custom-class="!py-1 !px-3 text-sm"
        >
          Next
        </PaymentButton>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, watch } from 'vue'
import type { PropType } from 'vue'
import type { Transaction } from '@/apps/payments/types'
import PaymentButton from '../../../atoms/buttons/Button/Button.vue'

export default defineComponent({
  name: 'TransactionTable',
  components: {
    PaymentButton
  },
  props: {
    transactions: {
      type: Array as PropType<Transaction[]>,
      required: true
    },
    perPage: {
      type: Number,
      default: 10
    }
  },
  setup(props) {
    const filter = ref('all')
    const sort = ref('date-desc')
    const currentPage = ref(1)

    // Reset current page when filters change
    watch([filter, sort], () => {
      currentPage.value = 1
    })

    const filteredTransactions = computed(() => {
      let result = [...props.transactions]
      
      // Apply filter
      if (filter.value !== 'all') {
        result = result.filter(t => t.status.toLowerCase() === filter.value)
      }
      
      // Apply sort
      switch (sort.value) {
        case 'date-desc':
          result.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
          break
        case 'date-asc':
          result.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
          break
        case 'amount-desc':
          result.sort((a, b) => b.amount - a.amount)
          break
        case 'amount-asc':
          result.sort((a, b) => a.amount - b.amount)
          break
      }
      
      return result
    })

    const totalPages = computed(() => Math.ceil(filteredTransactions.value.length / props.perPage))
    
    const paginatedTransactions = computed(() => {
      const start = (currentPage.value - 1) * props.perPage
      const end = start + props.perPage
      return filteredTransactions.value.slice(start, end)
    })

    const prevPage = () => {
      if (currentPage.value > 1) {
        currentPage.value--
      }
    }

    const nextPage = () => {
      if (currentPage.value < totalPages.value) {
        currentPage.value++
      }
    }

    const formatDate = (dateString: string) => {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const formatAmount = (amount: number) => {
      return `$${amount.toFixed(2)}`
    }

    const getAmountClass = (amount: number) => {
      return amount >= 0 ? 'text-green-500' : 'text-red-500'
    }

    const getStatusClass = (status: string) => {
      const statusLower = status.toLowerCase()
      if (statusLower === 'completed' || statusLower === 'succeeded') {
        return 'bg-green-100 text-green-800'
      } else if (statusLower === 'pending' || statusLower === 'processing') {
        return 'bg-yellow-100 text-yellow-800'
      } else {
        return 'bg-red-100 text-red-800'
      }
    }

    return {
      filter,
      sort,
      currentPage,
      filteredTransactions,
      paginatedTransactions,
      totalPages,
      prevPage,
      nextPage,
      formatDate,
      formatAmount,
      getAmountClass,
      getStatusClass
    }
  }
})
</script> 