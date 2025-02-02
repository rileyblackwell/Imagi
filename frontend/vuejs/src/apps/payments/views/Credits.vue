<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="bg-dark-800 rounded-lg shadow-xl overflow-hidden border border-dark-700">
      <!-- Header -->
      <div class="p-6 border-b border-dark-700">
        <h2 class="text-2xl font-bold text-white">Add Credits</h2>
        <p class="text-gray-400 mt-2">Purchase credits to use Imagi's AI models</p>
      </div>

      <!-- Main Content -->
      <div class="p-6">
        <!-- Current Balance -->
        <div class="mb-8">
          <h3 class="text-lg font-medium text-white mb-4">Current Balance</h3>
          <div class="bg-dark-900 rounded-lg p-4">
            <div class="flex justify-between items-center">
              <div>
                <p class="text-white font-medium">Available Credits</p>
                <p class="text-sm text-gray-400">Last updated: {{ lastUpdated }}</p>
              </div>
              <div class="text-2xl font-bold text-primary-400">
                ${{ currentBalance.toFixed(2) }}
              </div>
            </div>
          </div>
        </div>

        <!-- Add Funds Form -->
        <div class="max-w-xl mx-auto">
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

            <!-- Quick Select Amounts -->
            <div class="grid grid-cols-3 gap-4">
              <button
                v-for="quickAmount in quickAmounts"
                :key="quickAmount"
                @click="amount = quickAmount"
                :class="[
                  'px-4 py-2 rounded-lg text-sm font-medium',
                  amount === quickAmount
                    ? 'bg-primary-600 text-white'
                    : 'bg-dark-900 text-gray-300 hover:bg-dark-700'
                ]"
              >
                ${{ quickAmount }}
              </button>
            </div>

            <!-- Submit Button -->
            <button
              @click="addFunds"
              :disabled="!isValidAmount || isLoading"
              class="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span v-if="isLoading" class="mr-2">
                <i class="fas fa-spinner fa-spin"></i>
              </span>
              {{ isLoading ? 'Processing...' : 'Continue to Payment' }}
            </button>

            <!-- Error Message -->
            <div v-if="error" class="text-red-500 text-sm text-center">
              {{ error }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import PaymentService from '../services/payment_service'
import { useToast } from '../composables/useToast'

export default {
  name: 'Credits',
  setup() {
    const router = useRouter()
    const paymentService = new PaymentService()
    const toast = useToast()

    const amount = ref('')
    const isLoading = ref(false)
    const error = ref(null)
    const currentBalance = ref(0)
    const lastUpdated = ref(new Date().toLocaleString())

    const quickAmounts = [10, 25, 50, 100, 250, 500]

    const isValidAmount = computed(() => {
      const value = parseFloat(amount.value)
      return !isNaN(value) && value >= 5 && value <= 1000
    })

    async function loadData() {
      try {
        const { balance } = await paymentService.getBalance()
        currentBalance.value = balance
        lastUpdated.value = new Date().toLocaleString()
      } catch (err) {
        console.error('Failed to load balance:', err)
        toast.error('Failed to load current balance')
      }
    }

    async function addFunds() {
      if (!isValidAmount.value) {
        error.value = 'Please enter a valid amount between $5 and $1,000'
        return
      }

      try {
        isLoading.value = true
        error.value = null
        const value = parseFloat(amount.value)

        // Store the amount and navigate to checkout
        localStorage.setItem('payment_amount', value.toString())
        router.push({
          name: 'payments-checkout',
          query: { 
            amount: value.toFixed(2)
          }
        })
      } catch (err) {
        error.value = err.message || 'Failed to process request'
        toast.error('Failed to process request')
        console.error('Add funds error:', err)
      } finally {
        isLoading.value = false
      }
    }

    onMounted(() => {
      loadData()
    })

    return {
      amount,
      isLoading,
      error,
      currentBalance,
      lastUpdated,
      quickAmounts,
      isValidAmount,
      addFunds
    }
  }
}
</script>

<style scoped>
input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

input[type="number"] {
  -moz-appearance: textfield;
}
</style> 