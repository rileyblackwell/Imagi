<template>
  <PaymentLayout>
    <div class="checkout-view min-h-screen bg-white dark:bg-[#0a0a0a] relative overflow-hidden transition-colors duration-500">
      <!-- Minimal background with subtle texture - matching home page -->
      <div class="fixed inset-0 pointer-events-none -z-10">
        <!-- Subtle gradient - very minimal -->
        <div class="absolute inset-0 bg-gradient-to-b from-gray-50/50 via-white to-white dark:from-[#0a0a0a] dark:via-[#0a0a0a] dark:to-[#0a0a0a] transition-colors duration-500"></div>
        
        <!-- Very subtle grid pattern for texture -->
        <div class="absolute inset-0 opacity-[0.015] dark:opacity-[0.02]" 
             style="background-image: linear-gradient(rgba(128,128,128,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(128,128,128,0.1) 1px, transparent 1px); background-size: 64px 64px;"></div>
      </div>

      <!-- Content Container -->
      <div class="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-16">
        <!-- Clean Header Section - matching home page style -->
        <div class="mb-16 text-center">
          <h1 class="text-4xl sm:text-5xl md:text-6xl font-semibold text-gray-900 dark:text-white mb-6 tracking-tight leading-[1.1] transition-colors duration-300">
            Purchase Credits
          </h1>
          <p class="text-xl sm:text-2xl text-gray-500 dark:text-white/60 max-w-3xl mx-auto transition-colors duration-300">
            Add credits to your account to use AI models and build your applications.
          </p>
          <div class="mt-6">
            <router-link 
              to="/payments/pricing" 
              class="inline-flex items-center gap-2 text-gray-500 dark:text-white transition-colors duration-200"
            >
              <i class="fas fa-info-circle text-sm"></i>
              <span class="text-sm font-medium">View model pricing details</span>
            </router-link>
          </div>
        </div>
        
        <!-- Single unified checkout container -->
        <div class="max-w-2xl mx-auto">
          <!-- Status Messages with clean styling -->
          <div v-if="success" class="animate-fade-in-up mb-6">
            <div class="rounded-2xl bg-emerald-50 dark:bg-emerald-900/10 border border-emerald-200 dark:border-emerald-800/30 p-6 transition-colors duration-300">
              <div class="flex items-start gap-4">
                <div class="w-10 h-10 rounded-full bg-emerald-100 dark:bg-emerald-900/20 flex items-center justify-center flex-shrink-0">
                  <i class="fas fa-check text-emerald-600 dark:text-emerald-400"></i>
                </div>
                <div class="flex-1">
                  <h3 class="text-lg font-semibold text-emerald-900 dark:text-emerald-100 mb-2">Payment Successful!</h3>
                  <p class="text-emerald-700 dark:text-emerald-300/80">Your payment has been processed and credits have been added to your account.</p>
                </div>
              </div>
            </div>
          </div>
          
          <div v-if="paymentError" class="animate-fade-in-up mb-6">
            <div class="rounded-2xl bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800/30 p-6 transition-colors duration-300">
              <div class="flex items-start gap-4">
                <div class="w-10 h-10 rounded-full bg-red-100 dark:bg-red-900/20 flex items-center justify-center flex-shrink-0">
                  <i class="fas fa-exclamation-triangle text-red-600 dark:text-red-400"></i>
                </div>
                <div class="flex-1">
                  <h3 class="text-lg font-semibold text-red-900 dark:text-red-100 mb-2">Payment Error</h3>
                  <p class="text-red-700 dark:text-red-300/80">{{ paymentError }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Unified checkout card with balance and payment details -->
          <div class="animate-fade-in-up animation-delay-300">
            <div class="rounded-2xl bg-white/50 dark:bg-white/[0.03] border border-gray-200 dark:border-white/[0.08] backdrop-blur-sm transition-all duration-300 hover:border-gray-300 dark:hover:border-white/[0.12] hover:shadow-lg overflow-hidden">
              <!-- Current Balance Section -->
              <div class="p-8 border-b border-gray-200 dark:border-white/[0.08] text-center">
                <div class="mb-2">
                  <span class="text-sm font-medium text-gray-600 dark:text-gray-400 uppercase tracking-wide">Current Balance</span>
                </div>
                <div class="flex items-baseline gap-2 justify-center">
                  <div v-if="isLoading" class="animate-pulse">
                    <div class="h-9 w-20 bg-gray-200 dark:bg-white/10 rounded-lg"></div>
                  </div>
                  <div v-else class="text-3xl sm:text-4xl font-semibold text-gray-900 dark:text-white">
                    ${{ (store.balance ?? 0).toLocaleString() }}
                  </div>
                  <div class="text-sm text-gray-500 dark:text-gray-400">USD</div>
                </div>
              </div>

              <!-- Payment Details Section -->
              <div class="p-8">
                <PaymentFormSection
                  ref="paymentFormRef"
                  :is-loading="processingPayment"
                  :animate="false"
                  :button-text="`Pay $${formattedAmount}`"
                  @submit="processPayment"
                  @update:amount="updateAmount"
                  @payment-error="handlePaymentError"
                />
              </div>
            </div>
          </div>

          <!-- Secure Payment Badge with clean styling -->
          <div class="animate-fade-in-up animation-delay-600 mt-6">
            <div class="flex items-center justify-center gap-3 py-3 px-6 bg-white/50 dark:bg-white/[0.03] backdrop-blur-sm rounded-full border border-gray-200/50 dark:border-white/[0.06] w-fit mx-auto transition-colors duration-300">
              <div class="w-8 h-8 rounded-full bg-gray-100 dark:bg-white/[0.05] flex items-center justify-center">
                <i class="fas fa-lock text-gray-600 dark:text-gray-400"></i>
              </div>
              <span class="text-gray-600 dark:text-gray-400 text-sm">All payments are secure and encrypted</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </PaymentLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { usePaymentStore } from '../stores/payments'
import { storeToRefs } from 'pinia'
import PaymentLayout from '../layouts/PaymentLayout.vue'
import StatusMessage from '../components/molecules/messages/StatusMessage/StatusMessage.vue'
import AccountBalanceCard from '../components/organisms/cards/AccountBalanceCard/AccountBalanceCard.vue'
import PaymentFormSection from '../components/organisms/forms/PaymentFormSection/PaymentFormSection.vue'

const store = usePaymentStore()
const { userCredits, lastUpdated, isLoading, error } = storeToRefs(store)

// Refs
const paymentFormRef = ref<{ clearForm: () => void } | null>(null)

// State
const success = ref(false)
const customAmount = ref<number | null>(null)
const paymentError = ref('')
const processingPayment = ref(false)

// Initialize payment data when component mounts
onMounted(async () => {
  try {
    // Initialize payment store
    await store.initializePayments()
    
    // If balance is still null after initialization, try direct fetch
    if (store.balance === null) {
      await store.fetchBalance()
    }
    
    // Set default amount
    customAmount.value = 5;
  } catch (error) {
    console.error('Failed to initialize checkout view:', error)
  }
})

// Computed
const isValidAmount = computed(() => {
  return customAmount.value !== null && customAmount.value >= 5
})

const formattedAmount = computed(() => {
  return customAmount.value ? customAmount.value.toFixed(2) : '0.00'
})

// Methods
const updateAmount = (amount: string | number) => {
  customAmount.value = typeof amount === 'string' ? parseFloat(amount) : amount
}

const handlePaymentError = (errorMessage: string) => {
  paymentError.value = errorMessage
}

const formatDateTime = (date: Date | string) => {
  if (!date) return '';
  
  const dateObj = date instanceof Date ? date : new Date(date);
  return dateObj.toLocaleString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

const processPayment = async (paymentData: any) => {
  if (!isValidAmount.value) return

  try {
    // Clear any previous errors
    paymentError.value = ''
    
    // Set local loading state
    processingPayment.value = true
    
    // Actually call the backend API to process the payment
    const response = await store.processPayment({
      amount: paymentData.amount,
      paymentMethodId: paymentData.paymentMethodId
    });
    
    // Handle successful payment
    success.value = true
    
    // Clear the payment form (amount and card information)
    if (paymentFormRef.value?.clearForm) {
      paymentFormRef.value.clearForm()
    }
    
    // Refresh user credits immediately
    await store.fetchUserCredits()
    
    // Success message will be cleared after 5 seconds
    setTimeout(() => {
      success.value = false
    }, 5000)
  } catch (err: any) {
    console.error('Payment error:', err)
    paymentError.value = err.response?.data?.error || err.message || 'Payment processing failed'
  } finally {
    processingPayment.value = false
  }
}
</script>

<style scoped>
/* Clean scrollbar - matching home page */
:deep(::-webkit-scrollbar) {
  width: 8px;
}

:deep(::-webkit-scrollbar-track) {
  background: transparent;
}

:deep(::-webkit-scrollbar-thumb) {
  background: rgba(0, 0, 0, 0.12);
  border-radius: 4px;
  transition: background 0.2s ease;
}

:deep(::-webkit-scrollbar-thumb:hover) {
  background: rgba(0, 0, 0, 0.2);
}

:root.dark :deep(::-webkit-scrollbar-thumb) {
  background: rgba(255, 255, 255, 0.12);
}

:root.dark :deep(::-webkit-scrollbar-thumb:hover) {
  background: rgba(255, 255, 255, 0.2);
}

/* Animation delays */
.animation-delay-300 {
  animation-delay: 300ms;
}

.animation-delay-600 {
  animation-delay: 600ms;
}

.animation-delay-750 {
  animation-delay: 750ms;
}

/* Simple fade-in-up animation */
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
  animation: fade-in-up 0.6s ease-out forwards;
}

/* Smooth scroll behavior */
:deep(html) {
  scroll-behavior: smooth;
}
</style> 