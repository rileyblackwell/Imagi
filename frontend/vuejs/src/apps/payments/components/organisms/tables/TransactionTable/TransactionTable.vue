<template>
  <div>
    <!-- Filters -->
    <div class="mb-6 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div class="flex items-center">
        <span class="text-blue-950/60 dark:text-blue-100/55 mr-2 transition-colors duration-300">Filter:</span>
        <select
          v-model="filter"
          class="bg-white dark:bg-white/[0.05] border border-blue-950/[0.12] dark:border-white/[0.14] text-blue-950 dark:text-white rounded-lg px-3 py-2 transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:border-blue-500/50 dark:focus-visible:border-blue-300/50"
        >
          <option value="all">All Transactions</option>
          <option value="completed">Completed</option>
          <option value="pending">Pending</option>
          <option value="failed">Failed</option>
        </select>
      </div>
      <div class="flex items-center">
        <span class="text-blue-950/60 dark:text-blue-100/55 mr-2 transition-colors duration-300">Sort:</span>
        <select
          v-model="sort"
          class="bg-white dark:bg-white/[0.05] border border-blue-950/[0.12] dark:border-white/[0.14] text-blue-950 dark:text-white rounded-lg px-3 py-2 transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:border-blue-500/50 dark:focus-visible:border-blue-300/50"
        >
          <option value="date-desc">Newest First</option>
          <option value="date-asc">Oldest First</option>
          <option value="amount-desc">Amount (High to Low)</option>
          <option value="amount-asc">Amount (Low to High)</option>
        </select>
      </div>
    </div>

    <!-- Table -->
    <div class="overflow-x-auto rounded-2xl border border-blue-950/[0.08] dark:border-white/[0.1] transition-colors duration-300">
      <table class="min-w-full divide-y divide-blue-950/[0.08] dark:divide-white/[0.1]">
        <thead class="bg-blue-50/60 dark:bg-white/[0.04]">
          <tr>
            <th scope="col" class="px-6 py-3 text-left text-xs font-semibold text-blue-950/60 dark:text-blue-100/55 uppercase tracking-[0.16em]">
              Date
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-semibold text-blue-950/60 dark:text-blue-100/55 uppercase tracking-[0.16em]">
              Description
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-semibold text-blue-950/60 dark:text-blue-100/55 uppercase tracking-[0.16em]">
              Amount
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-semibold text-blue-950/60 dark:text-blue-100/55 uppercase tracking-[0.16em]">
              Status
            </th>
          </tr>
        </thead>
        <tbody class="bg-white/85 dark:bg-white/[0.02] divide-y divide-blue-950/[0.08] dark:divide-white/[0.1]">
          <tr v-for="transaction in paginatedTransactions" :key="transaction.id" class="hover:bg-blue-50/50 dark:hover:bg-white/[0.04] transition-colors duration-200">
            <td class="px-6 py-4 whitespace-nowrap text-sm text-blue-950/80 dark:text-blue-100/75">
              {{ formatDate(transaction.created_at) }}
            </td>
            <td class="px-6 py-4 text-sm text-blue-950/80 dark:text-blue-100/75">
              {{ transaction.description }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium tabular-nums" :class="getAmountClass(transaction.amount)">
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
            <td colspan="4" class="px-6 py-8 text-center text-blue-950/60 dark:text-blue-100/55">
              No transactions found matching your filters.
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div class="mt-6 flex justify-between items-center">
      <div class="text-sm text-blue-950/60 dark:text-blue-100/55 transition-colors duration-300">
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
      return amount >= 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400'
    }

    const getStatusClass = (status: string) => {
      const statusLower = status.toLowerCase()
      if (statusLower === 'completed' || statusLower === 'succeeded') {
        return 'bg-emerald-100 text-emerald-800 dark:bg-emerald-400/10 dark:text-emerald-300'
      } else if (statusLower === 'pending' || statusLower === 'processing') {
        return 'bg-amber-100 text-amber-800 dark:bg-amber-400/10 dark:text-amber-300'
      } else {
        return 'bg-red-100 text-red-800 dark:bg-red-400/10 dark:text-red-300'
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