<template>
  <div class="add-credits-container">
    <!-- Error message -->
    <div v-if="error" class="error-message bg-red-50/80 dark:bg-red-500/10 border border-red-200/70 dark:border-red-400/25 text-red-700 dark:text-red-300 p-3 rounded-xl mb-4 transition-colors duration-300">
      {{ error }}
    </div>

    <!-- Success message -->
    <div v-if="successMessage" class="success-message bg-emerald-50/80 dark:bg-emerald-400/[0.07] border border-emerald-200/70 dark:border-emerald-300/[0.18] text-emerald-700 dark:text-emerald-300 p-3 rounded-xl mb-4 transition-colors duration-300">
      {{ successMessage }}
    </div>

    <!-- Credit packages section -->
    <div v-if="packages.length > 0" class="mb-6">
      <h3 class="text-lg font-semibold tracking-tight text-blue-950 dark:text-white mb-3 transition-colors duration-300">Credit Packages</h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div
          v-for="pkg in packages"
          :key="pkg.id"
          @click="selectPackage(pkg)"
          class="border rounded-xl p-4 bg-white/85 dark:bg-white/[0.045] backdrop-blur-sm hover:border-blue-400/60 dark:hover:border-blue-300/40 cursor-pointer transition-colors"
          :class="selectedPackage?.id === pkg.id ? 'border-blue-500 bg-blue-50/80 dark:border-blue-300/60 dark:bg-blue-400/10' : 'border-blue-950/[0.1] dark:border-white/[0.12]'"
        >
          <div class="font-semibold text-lg text-blue-950 dark:text-white transition-colors duration-300">{{ pkg.name }}</div>
          <div class="text-blue-950/60 dark:text-blue-100/55 mb-2 transition-colors duration-300">{{ pkg.description || `${pkg.credits} credits` }}</div>
          <div class="text-xl font-semibold tabular-nums text-blue-700 dark:text-blue-300 transition-colors duration-300">${{ pkg.price.toFixed(2) }}</div>
        </div>
      </div>
    </div>

    <!-- Custom amount section -->
    <div class="mb-6">
      <h3 class="text-lg font-semibold tracking-tight text-blue-950 dark:text-white mb-3 transition-colors duration-300">Custom Amount</h3>
      <div class="flex items-center">
        <span class="text-blue-950/60 dark:text-blue-100/55 text-lg mr-2">$</span>
        <input
          v-model.number="customAmount"
          type="number"
          min="5"
          max="1000"
          step="1"
          placeholder="Enter amount"
          class="flex-1 p-2 border rounded-xl bg-white dark:bg-white/[0.05] text-blue-950 dark:text-white placeholder-blue-950/40 dark:placeholder-blue-100/30 transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:border-blue-500/50 dark:focus-visible:border-blue-300/50"
          :class="customAmountError ? 'border-red-500/50 dark:border-red-400/50' : 'border-blue-950/[0.12] dark:border-white/[0.14]'"
        />
      </div>
      <div v-if="customAmountError" class="text-red-600 dark:text-red-400 text-sm mt-1">
        {{ customAmountError }}
      </div>
      <div class="text-sm text-blue-950/60 dark:text-blue-100/55 mt-1 transition-colors duration-300">
        Minimum $5, Maximum $1,000
      </div>
    </div>

    <!-- Payment methods section -->
    <div class="mb-6">
      <h3 class="text-lg font-semibold tracking-tight text-blue-950 dark:text-white mb-3 transition-colors duration-300">Payment Method</h3>

      <!-- Select saved payment method -->
      <div v-if="paymentMethods.length > 0" class="mb-4">
        <div
          v-for="method in paymentMethods"
          :key="method.id"
          @click="selectedPaymentMethod = method"
          class="border rounded-xl p-3 mb-2 flex items-center bg-white/85 dark:bg-white/[0.045] backdrop-blur-sm hover:border-blue-400/60 dark:hover:border-blue-300/40 cursor-pointer transition-colors"
          :class="selectedPaymentMethod?.id === method.id ? 'border-blue-500 bg-blue-50/80 dark:border-blue-300/60 dark:bg-blue-400/10' : 'border-blue-950/[0.1] dark:border-white/[0.12]'"
        >
          <div class="flex-1">
            <div class="font-medium text-blue-950 dark:text-white transition-colors duration-300">{{ method.card_brand.charAt(0).toUpperCase() + method.card_brand.slice(1) }} •••• {{ method.last4 }}</div>
            <div class="text-sm text-blue-950/60 dark:text-blue-100/55 transition-colors duration-300">Expires {{ method.exp_month }}/{{ method.exp_year }}</div>
          </div>
          <div v-if="method.is_default" class="text-sm text-blue-700 dark:text-blue-300 font-medium transition-colors duration-300">Default</div>
        </div>
      </div>

      <!-- Add new card if no saved cards -->
      <div v-else>
        <p class="text-blue-950/65 dark:text-blue-100/65 mb-3 transition-colors duration-300">No saved payment methods. Please add a card to continue.</p>
      </div>

      <!-- Toggle add new card form -->
      <button
        @click="showAddCard = !showAddCard"
        class="text-blue-700 hover:text-blue-800 dark:text-blue-300 dark:hover:text-blue-200 text-sm font-medium flex items-center rounded transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0a0a0a]"
      >
        <span v-if="!showAddCard">+ Add a new card</span>
        <span v-else>Cancel</span>
      </button>

      <!-- Add card form -->
      <div v-if="showAddCard" class="mt-3">
        <add-credit-card @card-added="handleCardAdded" />
      </div>
    </div>

    <!-- Payment buttons -->
    <div class="flex flex-col space-y-3">
      <!-- Direct payment -->
      <button
        @click="processDirectPayment"
        :disabled="!canProceed || isLoading"
        class="inline-flex items-center justify-center bg-blue-950 text-[#fdf9f2] hover:bg-blue-900 dark:bg-[#f3ede2] dark:text-blue-950 dark:hover:bg-white font-medium py-2 px-4 rounded-full transition-colors duration-200 shadow-[0_1px_2px_rgba(23,37,84,0.2),0_3px_8px_-2px_rgba(23,37,84,0.25)] dark:shadow-[0_1px_2px_rgba(0,0,0,0.4),0_3px_8px_-2px_rgba(0,0,0,0.45)] disabled:opacity-50 disabled:cursor-not-allowed focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0a0a0a]"
      >
        <span v-if="isLoading">
          <svg class="animate-spin -ml-1 mr-2 h-4 w-4 inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Processing...
        </span>
        <span v-else>Pay Now</span>
      </button>

      <!-- Checkout option -->
      <button
        @click="processCheckout"
        :disabled="!amountValid || isLoading"
        class="inline-flex items-center justify-center border border-blue-950/[0.14] text-blue-950/80 hover:text-blue-950 hover:border-blue-950/30 hover:bg-blue-950/[0.03] dark:border-white/[0.16] dark:text-blue-100/80 dark:hover:text-white dark:hover:border-white/30 dark:hover:bg-white/[0.06] font-medium py-2 px-4 rounded-full transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0a0a0a]"
      >
        <span v-if="isCheckoutLoading">
          <svg class="animate-spin -ml-1 mr-2 h-4 w-4 inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Redirecting...
        </span>
        <span v-else>Pay with Stripe Checkout</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { usePaymentStore } from '@/apps/payments/stores'
import AddCreditCard from '../AddCreditCard/AddCreditCard.vue'
import type { PaymentMethod, CreditPackage, Transaction } from '@/apps/payments/types'

const store = usePaymentStore()

// State
const customAmount = ref<number | null>(null)
const selectedPackage = ref<CreditPackage | null>(null)
const selectedPaymentMethod = ref<PaymentMethod | null>(null)
const showAddCard = ref(false)
const error = ref('')
const successMessage = ref('')
const customAmountError = ref('')
const isLoading = ref(false)
const isCheckoutLoading = ref(false)

// Computed properties
const paymentMethods = computed(() => store.paymentMethods)
const packages = computed(() => store.packages)

const amountValid = computed(() => {
  if (selectedPackage.value) return true
  if (!customAmount.value) return false
  return customAmount.value >= 5 && customAmount.value <= 1000
})

const canProceed = computed(() => {
  return amountValid.value && selectedPaymentMethod.value !== null
})

const finalAmount = computed(() => {
  if (selectedPackage.value) return selectedPackage.value.price
  return customAmount.value || 0
})

// Load data on mount
onMounted(async () => {
  try {
    await store.fetchPaymentMethods()
    await store.fetchPackages()
    
    // Set default payment method if available
    if (store.defaultPaymentMethod) {
      selectedPaymentMethod.value = store.defaultPaymentMethod
    }
  } catch (err) {
    console.error('Error loading initial data:', err)
  }
})

// Select a package
const selectPackage = (pkg: CreditPackage) => {
  selectedPackage.value = pkg
  customAmount.value = null
  customAmountError.value = ''
}

// Handle card added event
const handleCardAdded = async (paymentMethod: any) => {
  successMessage.value = 'Card added successfully!'
  showAddCard.value = false
  
  // Refresh payment methods and select the new one
  await store.fetchPaymentMethods()
  
  // Find and select the newly added payment method
  const newMethod = store.paymentMethods.find(
    (pm: PaymentMethod) => pm.payment_method_id === paymentMethod.id
  )
  
  if (newMethod) {
    selectedPaymentMethod.value = newMethod
  }
}

// Validate amount
const validateAmount = () => {
  if (selectedPackage.value) {
    customAmountError.value = ''
    return true
  }
  
  if (!customAmount.value) {
    customAmountError.value = 'Please enter an amount or select a package'
    return false
  }
  
  if (customAmount.value < 5) {
    customAmountError.value = 'Minimum amount is $5'
    return false
  }
  
  if (customAmount.value > 1000) {
    customAmountError.value = 'Maximum amount is $1,000'
    return false
  }
  
  customAmountError.value = ''
  return true
}

// Process direct payment
const processDirectPayment = async () => {
  // Validate amount
  if (!validateAmount()) return
  
  // Validate payment method
  if (!selectedPaymentMethod.value) {
    error.value = 'Please select a payment method.'
    return
  }
  
  try {
    isLoading.value = true
    error.value = ''
    successMessage.value = ''
    
    const result = await store.processPayment({
      amount: finalAmount.value,
      paymentMethodId: selectedPaymentMethod.value.payment_method_id
    })
    
    if (result.requires_action) {
      // Get Stripe from window
      const stripe = (window as any).Stripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY)
      
      // Handle additional authentication if needed
      const { error: stripeError } = await stripe.handleCardAction(result.payment_intent_client_secret)
      
      if (stripeError) {
        error.value = stripeError.message || 'Your card was declined.'
        return
      }
      
      // Confirm the payment after handling the action
      await store.confirmPayment(result.payment_intent_id)
    }
    
    // Success
    successMessage.value = `Successfully added ${result.credits_added || finalAmount.value} credits to your account!`
    
    // Reset form
    customAmount.value = null
    selectedPackage.value = null
    
    // Refresh balance
    await store.fetchBalance()
    
  } catch (err: any) {
    console.error('Payment processing error:', err)
    error.value = err.message || 'Failed to process payment. Please try again.'
  } finally {
    isLoading.value = false
  }
}

// Process checkout
const processCheckout = async () => {
  // Validate amount
  if (!validateAmount()) return
  
  try {
    isCheckoutLoading.value = true
    error.value = ''
    successMessage.value = ''
    
    // Create checkout session
    const session = await store.createCheckoutSession(finalAmount.value)
    
    // Redirect to Stripe Checkout
    const stripe = (window as any).Stripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY)
    await stripe.redirectToCheckout({
      sessionId: session.session_id
    })
    
  } catch (err: any) {
    console.error('Checkout error:', err)
    error.value = err.message || 'Failed to initialize checkout. Please try again.'
  } finally {
    isCheckoutLoading.value = false
  }
}
</script>

<style scoped>
.add-credits-container {
  width: 100%;
}
</style> 