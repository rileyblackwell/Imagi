<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
    <!-- Hero Section -->
    <div class="text-center mb-12">
      <h1 class="text-4xl font-extrabold text-white sm:text-5xl md:text-6xl">
        <span class="block">Add Funds</span>
        <span class="block text-primary-400">Power Your Development</span>
      </h1>
      <p class="mt-3 max-w-md mx-auto text-base text-gray-300 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
        Add funds to your account to use our AI services for building your web applications.
      </p>
    </div>

    <!-- Current Balance -->
    <div class="mb-12 bg-dark-800 rounded-lg shadow-xl p-6 border border-dark-700 max-w-xl mx-auto">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-lg font-semibold text-white mb-2">Your Balance</h3>
          <p class="text-3xl font-bold text-primary-400">${{ currentBalance }}</p>
        </div>
        <div class="text-right">
          <p class="text-sm text-gray-400">Last updated</p>
          <p class="text-sm text-gray-300">{{ lastUpdated }}</p>
        </div>
      </div>
    </div>

    <!-- Add Funds Form -->
    <div class="max-w-xl mx-auto bg-dark-800 rounded-lg shadow-xl overflow-hidden border border-dark-700">
      <div class="p-6">
        <h3 class="text-lg font-semibold text-white mb-6">Add Funds</h3>
        
        <div class="space-y-6">
          <!-- Amount Input -->
          <div>
            <label for="amount" class="block text-sm font-medium text-gray-300 mb-2">
              Enter Amount ($)
            </label>
            <div class="relative">
              <span class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">$</span>
              <input
                type="number"
                id="amount"
                v-model="amount"
                min="5"
                max="1000"
                step="0.01"
                class="w-full pl-8 pr-4 py-3 bg-dark-900 border border-dark-700 rounded-lg text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="Enter amount"
              >
            </div>
            <p class="mt-2 text-sm text-gray-400">Minimum: $5.00, Maximum: $1,000.00</p>
          </div>

          <!-- Error Message -->
          <div v-if="error" class="text-red-500 text-sm">
            {{ error }}
          </div>

          <!-- Submit Button -->
          <button
            @click="addFunds"
            :disabled="!isValidAmount || isLoading"
            class="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="isLoading" class="mr-2">
              <i class="fas fa-spinner fa-spin"></i>
            </span>
            {{ isLoading ? 'Processing...' : 'Add Funds' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import PaymentService from '../services/payment.service'
import { usePaymentStore } from '../store/payments'

export default {
  name: 'AddFunds',
  setup() {
    const router = useRouter()
    const paymentStore = usePaymentStore()
    const currentBalance = ref(0)
    const lastUpdated = ref(new Date().toLocaleString())
    const isLoading = ref(false)
    const error = ref(null)
    const amount = ref('')
    const paymentService = new PaymentService()

    const isValidAmount = computed(() => {
      const value = parseFloat(amount.value)
      return value >= 5 && value <= 1000
    })

    async function loadData() {
      try {
        const balanceData = await paymentService.getBalance()
        currentBalance.value = balanceData.balance
        lastUpdated.value = new Date().toLocaleString()
      } catch (err) {
        error.value = 'Failed to load balance. Please try again.'
        console.error('Error loading data:', err)
      }
    }

    async function addFunds() {
      try {
        isLoading.value = true
        error.value = null

        const value = parseFloat(amount.value)
        if (!value || value < 5 || value > 1000) {
          error.value = 'Please enter a valid amount between $5.00 and $1,000.00'
          return
        }

        // Navigate to checkout with the amount
        router.push({
          name: 'checkout',
          query: { 
            amount: value.toFixed(2)
          }
        })
      } catch (err) {
        error.value = err.message || 'Failed to process request'
        console.error('Add funds error:', err)
      } finally {
        isLoading.value = false
      }
    }

    onMounted(() => {
      loadData()
    })

    return {
      currentBalance,
      lastUpdated,
      isLoading,
      error,
      amount,
      isValidAmount,
      addFunds
    }
  }
}
</script>

<style scoped>
.credit-package {
  transition: all 0.3s ease;
}

.credit-package:hover {
  transform: translateY(-5px);
}

.popular-badge {
  background: linear-gradient(135deg, #00ffc6, #00a2ff);
}
</style> 