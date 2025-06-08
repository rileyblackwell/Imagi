<template>
  <PaymentLayout>
    <div class="checkout-view min-h-screen bg-dark-950 relative overflow-hidden">
      <!-- Enhanced Background Effects matching About page -->
      <div class="absolute inset-0 pointer-events-none">
        <!-- Enhanced Pattern Overlay -->
        <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.03]"></div>
        <div class="absolute inset-0 bg-noise opacity-[0.015]"></div>
        <div class="absolute inset-0 bg-gradient-to-br from-primary-950/10 via-dark-900 to-violet-950/10"></div>
        
        <!-- Enhanced Glowing Orbs Animation -->
        <div class="absolute -top-[10%] right-[15%] w-[800px] h-[800px] rounded-full bg-indigo-600/5 blur-[150px] animate-float"></div>
        <div class="absolute bottom-[5%] left-[20%] w-[600px] h-[600px] rounded-full bg-fuchsia-600/5 blur-[120px] animate-float-delay"></div>
        
        <!-- Animated Lines and Particles -->
        <div class="absolute left-0 right-0 top-1/3 h-px bg-gradient-to-r from-transparent via-indigo-500/20 to-transparent animate-pulse-slow"></div>
        <div class="absolute left-0 right-0 bottom-1/3 h-px bg-gradient-to-r from-transparent via-violet-500/20 to-transparent animate-pulse-slow delay-700"></div>
      </div>

      <!-- Enhanced Content Container -->
      <div class="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <!-- Modern Welcome Header Section -->
        <div class="mb-16 text-center">
          <div class="inline-flex items-center px-4 py-1.5 bg-gradient-to-r from-indigo-500/10 to-violet-500/10 rounded-full mb-3">
            <span class="text-indigo-400 font-semibold text-sm tracking-wider">CREDITS & PAYMENTS</span>
          </div>
          <h1 class="text-4xl sm:text-5xl font-bold text-white mb-4 leading-tight">
            <span>Upgrade Your </span>
            <span class="bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">Imagi Experience</span>
          </h1>
          <p class="text-xl text-gray-300 max-w-3xl mx-auto">
            Purchase credits to use AI models and unlock your creative potential.
          </p>
          
          <!-- Decorative line with gradient -->
          <div class="w-24 h-1 bg-gradient-to-r from-indigo-500 to-violet-500 rounded-full mx-auto mt-8"></div>
        </div>
        
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <!-- Left Column: Account & Status -->
          <div class="lg:col-span-1 flex flex-col gap-8">
            <!-- Current Balance Card -->
            <div class="animate-fade-in-up animation-delay-300">
              <AccountBalanceCard
                :credits="store.balance ?? 0"
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
              <div class="group relative transform transition-all duration-300 hover:-translate-y-1">
                <div class="absolute -inset-0.5 rounded-2xl opacity-70 bg-gradient-to-r from-emerald-500/50 to-green-500/50 blur-md"></div>
                <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden">
                  <!-- Sleek gradient header -->
                  <div class="h-1 w-full bg-gradient-to-r from-emerald-400 via-green-400 to-emerald-400 opacity-80"></div>
                  
                  <!-- Subtle background effects -->
                  <div class="absolute -top-32 -right-32 w-64 h-64 bg-gradient-to-br from-emerald-400/4 to-green-400/4 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"></div>
                  
                  <div class="relative z-10 p-6">
                    <div class="flex items-start gap-4">
                      <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-400/20 to-green-400/20 flex items-center justify-center border border-emerald-400/20 flex-shrink-0">
                        <i class="fas fa-check text-emerald-300 text-lg"></i>
                      </div>
                      <div class="flex-1">
                        <h3 class="text-xl font-semibold text-white mb-3 leading-tight">Payment Successful!</h3>
                        <p class="text-gray-300 leading-relaxed">Your payment has been processed and credits have been added to your account.</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div v-if="paymentError" class="animate-fade-in-up">
              <div class="group relative transform transition-all duration-300 hover:-translate-y-1">
                <div class="absolute -inset-0.5 rounded-2xl opacity-70 bg-gradient-to-r from-red-500/50 to-rose-500/50 blur-md"></div>
                <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden">
                  <!-- Sleek gradient header -->
                  <div class="h-1 w-full bg-gradient-to-r from-red-400 via-rose-400 to-red-400 opacity-80"></div>
                  
                  <!-- Subtle background effects -->
                  <div class="absolute -top-32 -left-32 w-64 h-64 bg-gradient-to-br from-red-400/4 to-rose-400/4 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"></div>
                  
                  <div class="relative z-10 p-6">
                    <div class="flex items-start gap-4">
                      <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-red-400/20 to-rose-400/20 flex items-center justify-center border border-red-400/20 flex-shrink-0">
                        <i class="fas fa-exclamation-triangle text-red-300 text-lg"></i>
                      </div>
                      <div class="flex-1">
                        <h3 class="text-xl font-semibold text-white mb-3 leading-tight">Payment Error</h3>
                        <p class="text-gray-300 leading-relaxed">{{ paymentError }}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Payment Form with enhanced styling -->
            <div class="animate-fade-in-up animation-delay-600">
              <div class="group relative transform transition-all duration-300 hover:-translate-y-1">
                <div class="absolute -inset-0.5 rounded-2xl opacity-30 group-hover:opacity-70 bg-gradient-to-r from-indigo-500/50 to-violet-500/50 blur group-hover:blur-md transition-all duration-300"></div>
                <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
                  <!-- Sleek gradient header -->
                  <div class="h-1 w-full bg-gradient-to-r from-indigo-400 via-violet-400 to-indigo-400 opacity-80"></div>
                  
                  <!-- Subtle background effects -->
                  <div class="absolute -top-32 -right-32 w-64 h-64 bg-gradient-to-br from-indigo-400/4 to-violet-400/4 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"></div>
                  
                  <div class="relative z-10 p-8">
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
              <div class="flex items-center justify-center gap-3 py-3 px-6 bg-gradient-to-r from-dark-900/40 to-dark-800/40 backdrop-blur-sm rounded-xl border border-white/10 w-fit mx-auto">
                <div class="w-8 h-8 rounded-full bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center">
                  <i class="fas fa-lock text-indigo-400"></i>
                </div>
                <span class="text-gray-300 text-sm">All payments are secure and encrypted</span>
              </div>
            </div>
            
            <!-- Enhanced Payment History Link -->
            <div class="animate-fade-in-up animation-delay-900 mt-8 text-center">
              <router-link to="/payments/history" class="group inline-block">
                <div class="relative transform transition-all duration-300 hover:-translate-y-1 hover:scale-105">
                  <div class="absolute -inset-0.5 rounded-xl opacity-30 group-hover:opacity-70 bg-gradient-to-r from-violet-500/50 to-indigo-500/50 blur group-hover:blur-md transition-all duration-300"></div>
                  <div class="relative flex items-center gap-3 px-6 py-3 bg-gradient-to-r from-dark-900/80 to-dark-800/80 backdrop-blur-sm rounded-xl border border-white/10 group-hover:border-white/20 transition-all duration-300">
                    <div class="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500/20 to-indigo-500/20 flex items-center justify-center border border-violet-400/20 group-hover:border-violet-400/40 transition-all duration-300">
                      <i class="fas fa-history text-violet-400 group-hover:text-violet-300 transition-colors"></i>
                    </div>
                    <div class="text-left">
                      <div class="text-white font-medium group-hover:text-violet-200 transition-colors">View Payment History</div>
                      <div class="text-gray-400 text-sm group-hover:text-gray-300 transition-colors">Track your transactions</div>
                    </div>
                    <div class="w-5 h-5 text-violet-400 group-hover:text-violet-300 group-hover:translate-x-1 transition-all duration-300">
                      <i class="fas fa-arrow-right"></i>
                    </div>
                  </div>
                </div>
              </router-link>
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
import ModelPricingSection from '../components/organisms/sections/ModelPricingSection/ModelPricingSection.vue'
import PaymentFormSection from '../components/organisms/forms/PaymentFormSection/PaymentFormSection.vue'

const store = usePaymentStore()
const { userCredits, lastUpdated, isLoading, error } = storeToRefs(store)

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
/* Completely remove any browser default styling for form inputs */
input, textarea {
  outline: none !important;
  box-shadow: none !important;
  -webkit-appearance: none !important;
  -moz-appearance: none !important;
  appearance: none !important;
}

input:focus, textarea:focus {
  outline: none !important;
  box-shadow: none !important;
}

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

.animation-delay-900 {
  animation-delay: 900ms;
}

/* Float animation for background orbs */
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

.animate-float {
  animation: float 15s ease-in-out infinite;
}

.animate-float-delay {
  animation: float 18s ease-in-out infinite reverse;
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

/* Add subtle animation for loading state */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.animate-pulse-slow {
  animation: pulse 3s ease-in-out infinite;
}

.delay-700 {
  animation-delay: 700ms;
}
</style> 