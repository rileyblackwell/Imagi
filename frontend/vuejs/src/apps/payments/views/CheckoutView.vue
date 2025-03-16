<template>
  <PaymentLayout>
    <div class="checkout-view max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 relative">
      <!-- Animated background elements -->
      <div class="absolute -z-10 inset-0 pointer-events-none overflow-hidden">
        <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.03]"></div>
        <div class="absolute top-[20%] right-[10%] w-[400px] sm:w-[600px] h-[400px] sm:h-[600px] rounded-full bg-primary-600/5 blur-[120px] animate-pulse-slow"></div>
        <div class="absolute bottom-[10%] left-[10%] w-[350px] sm:w-[500px] h-[350px] sm:h-[500px] rounded-full bg-violet-600/5 blur-[100px] animate-pulse-slow animation-delay-150"></div>
      </div>
    
      <!-- Page Header with modern styling -->
      <div class="mb-16 text-center">
        <div class="inline-block px-4 py-1.5 bg-primary-500/10 rounded-full mb-3">
          <span class="text-primary-400 font-semibold text-sm tracking-wider">CREDITS & PAYMENTS</span>
        </div>
        <h1 class="text-4xl sm:text-5xl font-bold text-white mb-4 leading-tight">
          <span>Upgrade Your </span>
          <span class="bg-gradient-to-r from-primary-400 to-violet-400 bg-clip-text text-transparent">Imagi Experience</span>
        </h1>
        <p class="text-xl text-gray-300 max-w-3xl mx-auto">
          Purchase credits to use AI models and unlock your creative potential.
        </p>
        
        <!-- Decorative line with gradient -->
        <div class="w-24 h-1 bg-gradient-to-r from-primary-500 to-violet-500 rounded-full mx-auto mt-8"></div>
      </div>
      
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Left Column: Account & Status -->
        <div class="lg:col-span-1 flex flex-col gap-8">
          <!-- Current Balance Card -->
          <div class="animate-fade-in-up animation-delay-300">
            <AccountBalanceCard
              :credits="userCredits"
              :loading="isLoading"
              :last-updated="lastUpdated || undefined"
            />
          </div>
          
          <!-- AI Model Pricing Information -->
          <div class="animate-fade-in-up animation-delay-450">
            <ModelPricingSection :animate="false" />
          </div>
        </div>
        
        <!-- Right Column: Payment Form -->
        <div class="lg:col-span-2 flex flex-col gap-8">
          <!-- Status Messages with enhanced styling -->
          <div v-if="success" class="animate-fade-in-up">
            <div class="relative group">
              <div class="absolute -inset-0.5 rounded-xl opacity-70 bg-gradient-to-r from-green-500/50 to-emerald-500/50 blur-md"></div>
              <div class="relative bg-dark-900/70 backdrop-blur-lg rounded-xl overflow-hidden border border-dark-800/50 p-6">
                <div class="flex items-start gap-4">
                  <div class="w-10 h-10 bg-green-500/20 rounded-full flex-shrink-0 flex items-center justify-center">
                    <i class="fas fa-check text-green-400"></i>
                  </div>
                  <div>
                    <h3 class="text-xl font-semibold text-white mb-1">Payment Successful!</h3>
                    <p class="text-gray-300">Your payment has been processed and credits have been added to your account.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div v-if="paymentError" class="animate-fade-in-up">
            <div class="relative group">
              <div class="absolute -inset-0.5 rounded-xl opacity-70 bg-gradient-to-r from-red-500/50 to-rose-500/50 blur-md"></div>
              <div class="relative bg-dark-900/70 backdrop-blur-lg rounded-xl overflow-hidden border border-dark-800/50 p-6">
                <div class="flex items-start gap-4">
                  <div class="w-10 h-10 bg-red-500/20 rounded-full flex-shrink-0 flex items-center justify-center">
                    <i class="fas fa-exclamation-triangle text-red-400"></i>
                  </div>
                  <div>
                    <h3 class="text-xl font-semibold text-white mb-1">Payment Error</h3>
                    <p class="text-gray-300">{{ paymentError }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Payment Form with enhanced styling -->
          <div class="animate-fade-in-up animation-delay-600">
            <div class="relative group">
              <div class="absolute -inset-0.5 rounded-xl opacity-30 group-hover:opacity-70 bg-gradient-to-r from-primary-500/50 to-violet-500/50 blur group-hover:blur-md transition-all duration-300"></div>
              <div class="relative bg-dark-900/70 backdrop-blur-lg rounded-xl overflow-hidden border border-dark-800/50 group-hover:border-opacity-0 transition-all duration-300">
                <!-- Card header with gradient -->
                <div class="h-2 w-full bg-gradient-to-r from-primary-500 to-violet-500"></div>
                
                <div class="p-8">
                  <PaymentFormSection
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
          </div>
          
          <!-- Secure Payment Badge with enhanced styling -->
          <div class="animate-fade-in-up animation-delay-750">
            <div class="flex items-center justify-center gap-3 py-3 px-6 bg-dark-900/40 backdrop-blur-sm rounded-xl border border-dark-800/60 w-fit mx-auto">
              <div class="w-8 h-8 rounded-full bg-primary-500/10 border border-primary-500/20 flex items-center justify-center">
                <i class="fas fa-lock text-primary-400"></i>
              </div>
              <span class="text-gray-300 text-sm">All payments are secure and encrypted</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </PaymentLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { usePaymentsStore } from '../store'
import { storeToRefs } from 'pinia'
import PaymentLayout from '../layouts/PaymentLayout.vue'
import StatusMessage from '../components/molecules/StatusMessage.vue'
import AccountBalanceCard from '../components/organisms/AccountBalanceCard.vue'
import ModelPricingSection from '../components/organisms/ModelPricingSection.vue'
import PaymentFormSection from '../components/organisms/PaymentFormSection.vue'

const store = usePaymentsStore()
const { userCredits, lastUpdated, isLoading, error } = storeToRefs(store)

// State
const success = ref(false)
const customAmount = ref<number | null>(null)
const paymentError = ref('')
const processingPayment = ref(false)

// Initialize payment data when component mounts
onMounted(async () => {
  try {
    // Initialize the payment system with auto-refresh
    await store.initializePayments();
    
    // Set default amount
    customAmount.value = 5;
  } catch (err: any) {
    console.error('Failed to initialize payment data:', err);
    paymentError.value = 'Failed to load account data. Please refresh the page.';
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

const processPayment = async (paymentData: any) => {
  if (!isValidAmount.value) return

  try {
    // Clear any previous errors
    paymentError.value = ''
    
    // Set local loading state
    processingPayment.value = true
    
    console.log('Processing payment with data:', paymentData)
    
    // Actually call the backend API to process the payment
    const response = await store.processPayment({
      amount: paymentData.amount,
      paymentMethodId: paymentData.paymentMethodId
    });
    
    // Handle successful payment
    success.value = true
    
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

@keyframes pulse-slow {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 0.8; }
}

.animate-pulse-slow {
  animation: pulse-slow 3s ease-in-out infinite;
}
</style> 