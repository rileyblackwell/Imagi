<template>
  <PaymentLayout>
    <div class="checkout-view container mx-auto px-4 py-8">
      <h1 class="text-2xl font-bold mb-6">Checkout</h1>
      
      <!-- Current Balance Card -->
      <div class="bg-white shadow rounded-lg p-6 mb-8">
        <h2 class="text-xl font-semibold mb-4">Your Account</h2>
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-gray-600 font-medium">Current Balance</h3>
          <div class="text-2xl font-bold text-primary-600">{{ userCredits }} credits</div>
        </div>
        <div class="text-sm text-gray-500">
          <p>Last updated: {{ formatDate(lastUpdated || new Date()) }}</p>
        </div>
      </div>
      
      <!-- Payment Success Message -->
      <div v-if="success" class="bg-green-100 border border-green-300 text-green-700 rounded-lg p-4 mb-8">
        <h3 class="font-medium mb-1">Payment Successful!</h3>
        <p>Your payment has been processed and credits have been added to your account.</p>
      </div>
      
      <!-- Error Message -->
      <div v-if="error" class="bg-red-100 border border-red-300 text-red-700 rounded-lg p-4 mb-8">
        <h3 class="font-medium mb-1">Payment Failed</h3>
        <p>{{ error }}</p>
      </div>
      
      <!-- Credit Package Options -->
      <div class="bg-white shadow rounded-lg p-6 mb-8">
        <h2 class="text-xl font-semibold mb-4">Buy Credits</h2>
        <div class="mb-6">
          <h3 class="text-lg font-medium mb-4">Select a Package</h3>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div
              v-for="(pkg, index) in creditPackages"
              :key="index"
              class="border rounded-lg p-4 cursor-pointer transition-all duration-200"
              :class="{ 'border-primary-500 bg-primary-50': selectedPackage === pkg.credits }"
              @click="selectPackage(pkg.credits)"
            >
              <div class="text-xl font-bold mb-1">{{ pkg.credits }} credits</div>
              <div class="text-primary-600 font-medium mb-2">${{ pkg.price.toFixed(2) }}</div>
              <div class="text-sm text-gray-600">{{ pkg.description }}</div>
            </div>
          </div>
        </div>
        
        <!-- Payment Form -->
        <div class="mt-8">
          <h3 class="text-lg font-medium mb-4">Payment Details</h3>
          <form @submit.prevent="processPayment">
            <!-- Payment form fields would go here -->
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-600 mb-1">Card Information</label>
              <!-- Stripe Elements or similar payment form would go here -->
              <div class="mt-1 p-4 border rounded-md bg-gray-50 text-center text-gray-500">
                [Stripe Elements Placeholder]
              </div>
            </div>
            
            <button
              type="submit"
              class="w-full py-3 px-4 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-md shadow-sm transition-colors"
              :disabled="isLoading"
            >
              <span v-if="isLoading">Processing...</span>
              <span v-else>Pay ${{ selectedPackagePrice }}</span>
            </button>
          </form>
        </div>
      </div>
      
      <!-- Transaction History -->
      <div class="bg-white shadow rounded-lg p-6">
        <h2 class="text-xl font-semibold mb-4">Transaction History</h2>
        
        <!-- Loading state -->
        <div v-if="isLoading" class="flex justify-center py-8">
          <svg class="animate-spin h-8 w-8 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>
        
        <!-- Transactions list -->
        <div v-else-if="transactions.length > 0">
          <div class="hidden md:grid md:grid-cols-5 text-sm font-medium text-gray-500 mb-2 pb-2 border-b">
            <div>Date</div>
            <div>Description</div>
            <div>Type</div>
            <div>Status</div>
            <div class="text-right">Amount</div>
          </div>
          
          <div v-for="transaction in transactions" :key="transaction.id" class="py-3 border-b last:border-b-0">
            <div class="md:grid md:grid-cols-5 md:gap-4">
              <!-- Mobile view (stacked) -->
              <div class="md:hidden mb-2">
                <div class="flex justify-between">
                  <div class="font-medium">{{ formatDate(transaction.created_at) }}</div>
                  <div :class="getAmountClass(transaction.amount)" class="font-semibold">
                    {{ formatAmount(transaction.amount) }}
                  </div>
                </div>
                <div class="text-sm text-gray-600">{{ transaction.description }}</div>
                <div class="flex justify-between mt-1 text-sm">
                  <div class="capitalize">Payment</div>
                  <div :class="getStatusClass(transaction.status)" class="capitalize">
                    {{ transaction.status }}
                  </div>
                </div>
              </div>
              
              <!-- Desktop view (grid) -->
              <div class="hidden md:block">{{ formatDate(transaction.created_at) }}</div>
              <div class="hidden md:block">{{ transaction.description }}</div>
              <div class="hidden md:block capitalize">Payment</div>
              <div class="hidden md:block" :class="getStatusClass(transaction.status)">
                <span class="capitalize">{{ transaction.status }}</span>
              </div>
              <div class="hidden md:block text-right" :class="getAmountClass(transaction.amount)">
                {{ formatAmount(transaction.amount) }}
              </div>
            </div>
          </div>
        </div>
        
        <!-- Empty state -->
        <div v-else class="text-center py-8 text-gray-500">
          <div class="mb-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <p>No transactions yet</p>
        </div>
      </div>
    </div>
  </PaymentLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { usePaymentsStore } from '../store'
import { storeToRefs } from 'pinia'
import type { Transaction } from '../types'
import PaymentLayout from '../layouts/PaymentLayout.vue'

const store = usePaymentsStore()
const { transactions, userCredits, lastUpdated, isLoading, error } = storeToRefs(store)

// State
const success = ref(false)
const selectedPackage = ref(1000)

// Credit package options with non-optional description
const creditPackages = [
  {
    credits: 1000,
    price: 9.99,
    description: 'Basic package for small projects'
  },
  {
    credits: 5000,
    price: 39.99,
    description: 'Most popular option'
  },
  {
    credits: 10000,
    price: 69.99,
    description: 'Best value for power users'
  }
]

// Computed
const selectedPackagePrice = computed(() => {
  const pkg = creditPackages.find(p => p.credits === selectedPackage.value)
  return pkg ? pkg.price.toFixed(2) : '0.00'
})

// Methods
const selectPackage = (credits: number) => {
  selectedPackage.value = credits
}

const processPayment = async () => {
  // This would be implemented with actual payment processing
  // For now, just show success message
  success.value = true
  
  // Refresh data
  await store.fetchUserCredits()
  await store.fetchBalance()
  
  // Reset after 5 seconds
  setTimeout(() => {
    success.value = false
  }, 5000)
}

// Format date to readable format
const formatDate = (dateStr: string | Date) => {
  if (!dateStr) return ''
  const date = dateStr instanceof Date ? dateStr : new Date(dateStr)
  return date.toLocaleDateString(undefined, { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Format transaction type
const formatType = (type: string) => {
  if (!type) return ''
  return type.toLowerCase().replace('_', ' ')
}

// Format amount with sign and 2 decimal places
const formatAmount = (amount: number) => {
  if (amount === 0) return '$0.00'
  const sign = amount > 0 ? '+' : ''
  return `${sign}$${Math.abs(amount).toFixed(2)}`
}

// Get CSS class for amount display
const getAmountClass = (amount: number) => {
  if (amount > 0) return 'text-green-600'
  if (amount < 0) return 'text-red-600'
  return 'text-gray-600'
}

// Get CSS class for status display
const getStatusClass = (status: string) => {
  switch (status.toLowerCase()) {
    case 'completed':
      return 'text-green-600'
    case 'pending':
      return 'text-yellow-600'
    case 'failed':
      return 'text-red-600'
    default:
      return 'text-gray-600'
  }
}

// Load data on mount
onMounted(async () => {
  await store.fetchUserCredits()
  await store.fetchBalance()
})
</script>

<style scoped>
.checkout-view {
  max-width: 1024px;
}
</style> 