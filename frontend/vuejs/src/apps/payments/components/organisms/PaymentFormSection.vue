<template>
  <div>
    <h2 class="text-xl font-bold mb-6 bg-gradient-to-r from-primary-400 to-violet-400 bg-clip-text text-transparent">
      {{ title }}
    </h2>
    
    <!-- Custom Amount Input -->
    <div class="mb-8">
      <h3 class="text-lg font-medium mb-4 text-white/90">{{ amountSectionTitle }}</h3>
      <div class="mb-4">
        <label class="block text-sm font-medium text-white/80 mb-2">{{ amountLabel }}</label>
        <div class="relative mt-1 rounded-xl shadow-sm">
          <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
            <span class="text-white/60 sm:text-sm">$</span>
          </div>
          <input
            v-model="amount"
            type="number"
            :min="minAmount"
            :step="step"
            class="block w-full rounded-xl border-white/20 bg-dark-800/60 py-3 pl-8 pr-12 text-white placeholder-white/40 backdrop-blur-sm focus:border-primary-500 focus:ring-primary-500 transition-all duration-300"
            :placeholder="placeholder"
          />
          <div class="absolute inset-y-0 right-0 flex items-center pr-3">
            <span class="text-white/60 sm:text-sm">USD</span>
          </div>
        </div>
        <p class="mt-2 text-sm text-white/60">{{ helpText }}</p>
      </div>
    </div>
    
    <!-- Payment Form -->
    <div>
      <h3 class="text-lg font-medium mb-6 bg-gradient-to-r from-primary-400 to-violet-400 bg-clip-text text-transparent">
        {{ paymentSectionTitle }}
      </h3>
      <form @submit.prevent="submitPayment">
        <!-- Stripe Elements -->
        <div class="mb-8">
          <!-- Credit Card Information -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-white/80 mb-2">{{ cardLabel }}</label>
            <div 
              id="card-element" 
              ref="cardElement"
              class="block w-full rounded-xl border border-white/20 bg-dark-800/60 py-3 px-4 text-white backdrop-blur-sm transition-all duration-300 focus-within:border-primary-500 focus-within:ring-1 focus-within:ring-primary-500 min-h-[45px]"
            ></div>
            <div id="card-errors" class="mt-2 text-sm text-red-400"></div>
          </div>
          
          <!-- Save Card Checkbox -->
          <div class="flex items-center">
            <input 
              type="checkbox" 
              id="save-card" 
              v-model="saveCard" 
              class="w-4 h-4 text-primary-500 bg-dark-900 border-white/20 rounded focus:ring-primary-500 focus:ring-offset-dark-900"
            />
            <label for="save-card" class="ml-2 text-sm text-white/80">
              {{ saveCardLabel }}
            </label>
          </div>
        </div>
        
        <!-- Order Summary -->
        <div class="mb-8 rounded-xl border border-white/10 bg-dark-800/40 backdrop-blur-sm overflow-hidden">
          <div class="p-4 border-b border-white/10 bg-gradient-to-r from-primary-900/40 to-violet-900/40">
            <h4 class="font-medium text-white">{{ summaryTitle }}</h4>
            <p class="text-sm text-white/60">{{ summarySubtitle }}</p>
          </div>
          <div class="p-4">
            <div class="flex justify-between py-2 border-b border-white/10">
              <span class="text-white/70">{{ amountSummaryLabel }}</span>
              <span class="font-medium text-white">${{ formattedAmount }}</span>
            </div>
            <div class="flex justify-between py-2">
              <span class="text-white/70">{{ totalLabel }}</span>
              <span class="font-medium text-white">${{ formattedAmount }}</span>
            </div>
          </div>
        </div>
        
        <!-- Submit Button with modern styling -->
        <div class="relative group transform transition-all duration-300 hover:-translate-y-1">
          <div class="absolute -inset-0.5 rounded-xl opacity-40 group-hover:opacity-70 bg-gradient-to-r from-primary-500/70 to-violet-500/70 blur group-hover:blur-md transition-all duration-300"></div>
          <button 
            type="submit"
            :disabled="!isValidAmount || isLoading || !cardComplete"
            class="relative w-full py-3 px-6 font-medium rounded-xl text-white backdrop-blur-sm border border-dark-800/50 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed overflow-hidden bg-dark-900/70"
          >
            <span v-if="isLoading" class="flex items-center justify-center">
              <span class="h-5 w-5 mr-2">
                <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </span>
              <span>Processing payment...</span>
            </span>
            <span v-else class="flex items-center justify-center">
              {{ buttonText }}
              <i class="fas fa-arrow-right ml-2 transform group-hover:translate-x-1 transition-transform duration-300"></i>
            </span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    default: 'Payment Details'
  },
  amountSectionTitle: {
    type: String,
    default: 'Amount'
  },
  amountLabel: {
    type: String,
    default: 'Credit Amount'
  },
  minAmount: {
    type: Number,
    default: 5
  },
  step: {
    type: Number,
    default: 1
  },
  placeholder: {
    type: String,
    default: 'Enter amount'
  },
  helpText: {
    type: String,
    default: 'Minimum amount is $5'
  },
  paymentSectionTitle: {
    type: String,
    default: 'Payment Method'
  },
  cardLabel: {
    type: String,
    default: 'Card Information'
  },
  saveCardLabel: {
    type: String,
    default: 'Save card for future payments'
  },
  summaryTitle: {
    type: String,
    default: 'Order Summary'
  },
  summarySubtitle: {
    type: String,
    default: 'Review your order details'
  },
  amountSummaryLabel: {
    type: String,
    default: 'Credits'
  },
  totalLabel: {
    type: String,
    default: 'Total'
  },
  isLoading: {
    type: Boolean,
    default: false
  },
  buttonText: {
    type: String,
    default: 'Complete Payment'
  },
  animate: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['submit', 'update:amount', 'payment-error'])

// State
const cardElement = ref<HTMLElement | null>(null)
const stripeElements = ref<any>(null)
const cardComplete = ref(false)
const amount = ref(props.minAmount)
const saveCard = ref(false)

// Computed
const isValidAmount = computed(() => {
  return amount.value >= props.minAmount
})

const formattedAmount = computed(() => {
  return amount.value.toFixed(2)
})

// Initialize Stripe
onMounted(() => {
  if (!window.Stripe) {
    emit('payment-error', 'Stripe.js failed to load. Please refresh the page.')
    return
  }
  
  try {
    const stripe = window.Stripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY)
    const elements = stripe.elements()
    stripeElements.value = elements
    
    // Create card element
    const card = elements.create('card', {
      style: {
        base: {
          color: '#FFFFFF',
          fontFamily: 'ui-sans-serif, system-ui, sans-serif',
          fontSmoothing: 'antialiased',
          fontSize: '16px',
          '::placeholder': {
            color: 'rgba(255, 255, 255, 0.4)'
          }
        },
        invalid: {
          color: '#F87171',
          iconColor: '#F87171'
        }
      }
    })
    
    // Mount card element
    card.mount('#card-element')
    
    // Handle real-time validation errors
    card.on('change', (event: any) => {
      const displayError = document.getElementById('card-errors')
      if (displayError) {
        if (event.error) {
          displayError.textContent = event.error.message
        } else {
          displayError.textContent = ''
        }
      }
      
      cardComplete.value = event.complete
    })
  } catch (err: any) {
    console.error('Error initializing Stripe:', err)
    emit('payment-error', err.message || 'Failed to initialize payment form')
  }
})

// Clean up on unmount
onUnmounted(() => {
  if (stripeElements.value) {
    // Cleanup if needed
  }
})

// Watch amount changes
watch(amount, (newValue) => {
  emit('update:amount', newValue)
})

// Submit payment
const submitPayment = async () => {
  if (!isValidAmount.value || props.isLoading || !cardComplete.value) {
    return
  }
  
  // Emit payment data
  emit('submit', {
    amount: amount.value,
    saveCard: saveCard.value
  })
}
</script>

<style scoped>
/* Component-specific styles */
</style> 