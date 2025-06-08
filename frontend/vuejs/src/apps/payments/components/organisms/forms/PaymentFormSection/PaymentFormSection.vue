<template>
  <div>
    <!-- Modern pill badge -->
    <div class="inline-flex items-center px-3 py-1 bg-gradient-to-r from-indigo-500/15 to-violet-500/15 border border-indigo-400/20 rounded-full mb-6 backdrop-blur-sm">
      <div class="w-1.5 h-1.5 bg-indigo-400 rounded-full mr-2 animate-pulse"></div>
      <span class="text-indigo-300 font-medium text-xs tracking-wide uppercase">{{ title }}</span>
    </div>
    
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
            v-model.number="amount"
            type="number"
            :min="minAmount"
            :max="maxAmount"
            :step="step"
            class="block w-full rounded-xl border-white/20 bg-white/5 py-3 pl-8 pr-12 text-white placeholder-white/40 backdrop-blur-sm focus:border-indigo-500 focus:ring-indigo-500 transition-all duration-300"
            :placeholder="placeholder"
          />
          <div class="absolute inset-y-0 right-0 flex items-center pr-3">
            <span class="text-white/60 sm:text-sm">USD</span>
          </div>
          <div class="absolute inset-y-0 right-12 flex flex-col h-full">
            <button 
              type="button" 
              @click="incrementAmount"
              class="flex-1 px-1 text-white/60 hover:text-indigo-400 transition-colors duration-200 flex items-center justify-center"
              tabindex="-1"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4">
                <path fill-rule="evenodd" d="M10 17a.75.75 0 01-.75-.75V5.612L5.29 9.77a.75.75 0 01-1.08-1.04l5.25-5.5a.75.75 0 011.08 0l5.25 5.5a.75.75 0 11-1.08 1.04l-3.96-4.158V16.25A.75.75 0 0110 17z" clip-rule="evenodd" />
              </svg>
            </button>
            <button 
              type="button" 
              @click="decrementAmount"
              class="flex-1 px-1 text-white/60 hover:text-indigo-400 transition-colors duration-200 flex items-center justify-center"
              tabindex="-1"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4">
                <path fill-rule="evenodd" d="M10 3a.75.75 0 01.75.75v10.638l3.96-4.158a.75.75 0 111.08 1.04l-5.25 5.5a.75.75 0 01-1.08 0l-5.25-5.5a.75.75 0 111.08-1.04l3.96 4.158V3.75A.75.75 0 0110 3z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
        <p class="mt-2 text-sm text-white/60">{{ helpText }}</p>
      </div>
    </div>
    
    <!-- Payment Form -->
    <div>
      <h3 class="text-lg font-medium mb-6 bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">
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
              class="block w-full rounded-xl border border-white/20 bg-white/5 py-3 px-4 text-white backdrop-blur-sm transition-all duration-300 focus-within:border-indigo-500 focus-within:ring-1 focus-within:ring-indigo-500 min-h-[45px]"
            ></div>
            <div id="card-errors" class="mt-2 text-sm text-red-400"></div>
          </div>
          
          <!-- Save Card Checkbox -->
          <div class="flex items-center">
            <input 
              type="checkbox" 
              id="save-card" 
              v-model="saveCard" 
              class="w-4 h-4 text-indigo-500 bg-dark-900 border-white/20 rounded focus:ring-indigo-500 focus:ring-offset-dark-900"
            />
            <label for="save-card" class="ml-2 text-sm text-white/80">
              {{ saveCardLabel }}
            </label>
          </div>
        </div>
        
        <!-- Order Summary -->
        <div class="mb-8 rounded-xl border border-white/10 bg-white/5 backdrop-blur-sm overflow-hidden">
          <div class="p-4 border-b border-white/10 bg-gradient-to-r from-indigo-900/40 to-violet-900/40">
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
          <div class="absolute -inset-0.5 rounded-xl opacity-40 group-hover:opacity-70 bg-gradient-to-r from-indigo-500/70 to-violet-500/70 blur group-hover:blur-md transition-all duration-300"></div>
          <button 
            type="submit"
            :disabled="!isValidAmount || isLoading || !cardComplete"
            class="relative w-full py-3 px-6 font-medium rounded-xl text-white backdrop-blur-sm border border-white/10 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed overflow-hidden bg-gradient-to-r from-indigo-500 to-violet-500 hover:from-indigo-400 hover:to-violet-400 shadow-lg shadow-indigo-500/25 hover:shadow-indigo-500/40"
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
  maxAmount: {
    type: Number,
    default: 100
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
    default: 'Amount range: $5 - $100'
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
const stripeInstance = ref<any>(null)
const cardComplete = ref(false)
const amount = ref<number>(props.minAmount)
const saveCard = ref(false)

// Computed
const isValidAmount = computed(() => {
  return amount.value && amount.value >= props.minAmount && amount.value <= props.maxAmount
})

const formattedAmount = computed(() => {
  const numAmount = typeof amount.value === 'string' ? parseFloat(amount.value) : amount.value;
  return numAmount ? numAmount.toFixed(2) : '0.00';
})

// Initialize Stripe
onMounted(async () => {
  // Wait a bit to ensure Stripe has time to load from layout
  setTimeout(async () => {
    if (!window.Stripe) {
      console.error('Stripe.js not loaded yet. Attempting to retry...')
      // Wait another moment and try again
      setTimeout(() => {
        if (!window.Stripe) {
          emit('payment-error', 'Stripe.js failed to load. Please refresh the page.')
          return
        } else {
          initializeStripe()
        }
      }, 1500)
      return
    }
    
    initializeStripe()
  }, 500)
})

// Function to initialize Stripe elements
const initializeStripe = () => {
  try {
    // Get Stripe instance with explicit API version
    const stripePublishableKey = import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY;
    const stripe = window.Stripe(stripePublishableKey, {
      apiVersion: '2022-11-15'
    });
    
    // Store the stripe instance
    stripeInstance.value = stripe;
    
    // Create elements instance with minimal configuration
    const elements = stripe.elements();
    stripeElements.value = elements;
    
    // Create card element with limited options to avoid __shared_params__ warning
    const card = elements.create('card', {
      style: {
        base: {
          color: '#FFFFFF',
          fontFamily: 'ui-sans-serif, system-ui, sans-serif',
          fontSize: '16px',
          '::placeholder': {
            color: 'rgba(255, 255, 255, 0.4)'
          }
        },
        invalid: {
          color: '#F87171'
        }
      }
    });
    
    // Add HTTP warning only in development
    if (import.meta.env.DEV && window.location.protocol === 'http:') {
      console.warn('Stripe is running over HTTP. This is fine for development, but HTTPS is required for production.');
    }
    
    // Mount card element
    card.mount('#card-element');
    
    // Handle validation events
    card.on('change', (event: any) => {
      const displayError = document.getElementById('card-errors');
      if (displayError) {
        displayError.textContent = event.error ? event.error.message : '';
      }
      cardComplete.value = event.complete;
    });
  } catch (err: any) {
    console.error('Error initializing Stripe:', err);
    emit('payment-error', err.message || 'Failed to initialize payment form');
  }
}

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
  
  try {
    // Use the same Stripe instance that was created in initializeStripe
    if (!stripeInstance.value) {
      throw new Error('Stripe has not been initialized properly');
    }
    
    // Create a payment method with the card element
    const result = await stripeInstance.value.createPaymentMethod({
      type: 'card',
      card: stripeElements.value.getElement('card'),
    });
    
    if (result.error) {
      // Show error to your customer
      const errorElement = document.getElementById('card-errors');
      if (errorElement) {
        errorElement.textContent = result.error.message || 'An unexpected error occurred';
      }
      emit('payment-error', result.error.message || 'Payment failed');
      return;
    }
    
    // Emit payment data with payment method ID
    emit('submit', {
      amount: amount.value,
      paymentMethodId: result.paymentMethod.id,
      saveCard: saveCard.value
    });
  } catch (err: any) {
    console.error('Payment submission error:', err);
    emit('payment-error', err.message || 'Payment submission failed');
  }
}

// Increment amount
const incrementAmount = () => {
  if (amount.value < props.maxAmount) {
    amount.value += props.step;
  }
}

// Decrement amount
const decrementAmount = () => {
  if (amount.value > props.minAmount) {
    amount.value -= props.step;
  }
}
</script>

<style scoped>
/* Component-specific styles */
/* Hide default number input arrows */
input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

input[type="number"] {
  -moz-appearance: textfield;
}

/* Custom button hover effects */
button:hover svg {
  transform: scale(1.2);
  transition: transform 0.2s ease;
}
</style> 