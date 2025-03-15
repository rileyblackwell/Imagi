<template>
  <PaymentLayout>
    <div class="checkout-view container mx-auto px-4 py-16">
      <!-- Page Header -->
      <PageHeader 
        title-prefix="Upgrade Your" 
        highlighted-title="Imagi Experience" 
        subtitle="Purchase credits to use AI models and unlock your creative potential."
        :animate="true"
      />
      
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
          <!-- Status Messages -->
          <StatusMessage 
            v-if="success" 
            type="success"
            title="Payment Successful!"
            message="Your payment has been processed and credits have been added to your account."
          />
          
          <StatusMessage 
            v-if="paymentError" 
            type="error"
            title="Payment Error"
            :message="paymentError"
          />
          
          <!-- Payment Form -->
          <div class="animate-fade-in-up animation-delay-600">
            <PaymentFormSection
              :is-loading="processingPayment"
              :animate="false"
              :button-text="`Pay $${formattedAmount}`"
              @submit="processPayment"
              @update:amount="updateAmount"
              @payment-error="handlePaymentError"
            />
          </div>
          
          <!-- Secure Payment Badge -->
          <div class="flex items-center justify-center gap-2 text-white/60 text-sm animate-fade-in-up animation-delay-750">
            <i class="fas fa-lock"></i>
            <span>All payments are secure and encrypted</span>
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
import PageHeader from '../components/molecules/PageHeader.vue'
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
    // Here you would typically call your backend API to process the Stripe payment
    // For now we'll just simulate a successful payment

    console.log('Processing payment with data:', paymentData)
    
    // Set local loading state
    processingPayment.value = true
    
    // Simulate backend API call delay
    await new Promise(resolve => setTimeout(resolve, 1500))

    // Check for simulated payment error (for testing)
    if (paymentData.amount > 500) {
      throw new Error('Payment amount exceeds maximum allowed.')
    }
    
    // Process successful payment
    success.value = true
    paymentError.value = ''
    
    // Refresh user credits
    await store.fetchUserCredits()
    
    // Reset success message after delay
    setTimeout(() => {
      success.value = false
    }, 5000)
  } catch (err: any) {
    paymentError.value = err.message || 'Payment processing failed'
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
</style> 