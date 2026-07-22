<template>
  <div>
    <!-- Two-column layout for credit amount and payment method -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
      <!-- Credit Amount Section (narrower, 1 column) -->
      <div>
        <!-- Clean section title -->
        <div class="mb-6 text-center md:text-left">
          <span class="text-xs font-semibold uppercase tracking-[0.16em] text-blue-700 dark:text-blue-300/70 transition-colors duration-300">{{ title }}</span>
        </div>

        <!-- Custom Amount Input -->
        <div>
          <div class="mb-4">
            <div class="relative mt-1 rounded-xl shadow-sm">
              <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                <span class="text-blue-950/60 dark:text-blue-100/55 sm:text-sm">$</span>
              </div>
              <input
                v-model.number="amount"
                type="number"
                :min="minAmount"
                :max="maxAmount"
                :step="step"
                class="block w-full rounded-xl border border-blue-950/[0.12] dark:border-white/[0.14] bg-white dark:bg-white/[0.05] py-3 pl-8 pr-28 text-blue-950 dark:text-white placeholder-blue-950/40 dark:placeholder-blue-100/30 transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:border-blue-500/50 dark:focus-visible:border-blue-300/50"
              />
              <div class="absolute inset-y-0 right-12 flex flex-col justify-center py-1 gap-0.5">
                <button
                  type="button"
                  @click="incrementAmount"
                  class="flex items-center justify-center px-1 rounded text-blue-950/50 hover:text-blue-950 dark:text-blue-100/50 dark:hover:text-white transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50"
                  tabindex="-1"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4">
                    <path fill-rule="evenodd" d="M10 17a.75.75 0 01-.75-.75V5.612L5.29 9.77a.75.75 0 01-1.08-1.04l5.25-5.5a.75.75 0 011.08 0l5.25 5.5a.75.75 0 11-1.08 1.04l-3.96-4.158V16.25A.75.75 0 0110 17z" clip-rule="evenodd" />
                  </svg>
                </button>
                <button
                  type="button"
                  @click="decrementAmount"
                  class="flex items-center justify-center px-1 rounded text-blue-950/50 hover:text-blue-950 dark:text-blue-100/50 dark:hover:text-white transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50"
                  tabindex="-1"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4">
                    <path fill-rule="evenodd" d="M10 3a.75.75 0 01.75.75v10.638l3.96-4.158a.75.75 0 111.08 1.04l-5.25 5.5a.75.75 0 01-1.08 0l-5.25-5.5a.75.75 0 111.08-1.04l3.96 4.158V3.75A.75.75 0 0110 3z" clip-rule="evenodd" />
                  </svg>
                </button>
              </div>
              <div class="absolute inset-y-0 right-0 flex items-center pr-3">
                <span class="text-blue-950/60 dark:text-blue-100/55 sm:text-sm">USD</span>
              </div>
            </div>
            <p class="mt-2 text-sm text-blue-950/60 dark:text-blue-100/55 transition-colors duration-300">{{ helpText }}</p>
          </div>
        </div>
      </div>

      <!-- Payment Method Section (wider, 2 columns) -->
      <div class="md:col-span-2">
        <!-- Clean section title -->
        <div class="mb-6 text-center md:text-left">
          <span class="text-xs font-semibold uppercase tracking-[0.16em] text-blue-700 dark:text-blue-300/70 transition-colors duration-300">{{ paymentSectionTitle }}</span>
        </div>
        
        <!-- Payment Form -->
        <form @submit.prevent="submitPayment">
          <!-- Stripe Elements -->
          <div class="mb-8">
            <!-- Credit Card Information -->
            <div class="mb-4">
              <div
                id="card-element"
                ref="cardElement"
                class="block w-full rounded-xl border border-blue-950/[0.12] dark:border-white/[0.14] bg-white dark:bg-white/[0.05] py-3 px-4 text-blue-950 dark:text-white transition-all duration-300 focus-within:border-blue-500/50 dark:focus-within:border-blue-300/50 focus-within:ring-2 focus-within:ring-blue-500/40 dark:focus-within:ring-blue-300/50 min-h-[45px]"
              ></div>
              <div id="card-errors" class="mt-2 text-sm text-red-600 dark:text-red-400"></div>
            </div>
          </div>

          <!-- Order Summary -->
          <div class="mb-8 rounded-xl border border-blue-950/[0.08] dark:border-white/[0.1] bg-white/70 dark:bg-white/[0.03] overflow-hidden transition-colors duration-300">
            <div class="p-4 border-b border-blue-950/[0.08] dark:border-white/[0.1] bg-white/85 dark:bg-white/[0.045]">
              <h4 class="font-semibold tracking-tight text-blue-950 dark:text-white transition-colors duration-300">{{ summaryTitle }}</h4>
              <p class="text-sm text-blue-950/60 dark:text-blue-100/55 transition-colors duration-300">{{ summarySubtitle }}</p>
            </div>
            <div class="p-4">
              <div class="flex justify-between py-2 border-b border-blue-950/[0.08] dark:border-white/[0.1]">
                <span class="text-blue-950/60 dark:text-blue-100/55">{{ amountSummaryLabel }}</span>
                <span class="font-medium tabular-nums text-blue-950 dark:text-white">${{ formattedAmount }}</span>
              </div>
              <div class="flex justify-between py-2">
                <span class="text-blue-950/60 dark:text-blue-100/55">{{ totalLabel }}</span>
                <span class="font-semibold tabular-nums text-blue-950 dark:text-white">${{ formattedAmount }}</span>
              </div>
            </div>
          </div>

          <!-- Submit Button with navy ink pill styling -->
          <button
            type="submit"
            :disabled="!isValidAmount || isLoading || !cardComplete"
            class="group relative w-full inline-flex items-center justify-center gap-3 px-8 py-4 rounded-full font-medium text-lg bg-blue-950 text-[#fdf9f2] hover:bg-blue-900 dark:bg-[#f3ede2] dark:text-blue-950 dark:hover:bg-white transition-all duration-200 hover:-translate-y-0.5 active:translate-y-0 shadow-[0_1px_2px_rgba(23,37,84,0.25),0_8px_20px_-6px_rgba(23,37,84,0.35),inset_0_1px_0_rgba(255,255,255,0.12)] hover:shadow-[0_2px_3px_rgba(23,37,84,0.22),0_14px_28px_-8px_rgba(23,37,84,0.4),inset_0_1px_0_rgba(255,255,255,0.12)] dark:shadow-[0_1px_2px_rgba(0,0,0,0.5),0_10px_24px_-8px_rgba(0,0,0,0.55)] dark:hover:shadow-[0_2px_3px_rgba(0,0,0,0.5),0_14px_30px_-8px_rgba(0,0,0,0.6)] disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:translate-y-0 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0a0a0a]"
          >
            <span v-if="isLoading" class="relative flex items-center justify-center gap-2">
              <svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>Processing payment...</span>
            </span>
            <span v-else class="relative flex items-center gap-2">
              {{ buttonText }}
              <svg class="w-5 h-5 transition-transform duration-300 group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </span>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    default: 'Credit Amount'
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
    // Verify the card element exists in the DOM
    const cardElementDiv = document.getElementById('card-element');
    if (!cardElementDiv) {
      console.error('Card element not found in DOM');
      setTimeout(() => initializeStripe(), 500);
      return;
    }
    
    // Get Stripe instance with explicit API version
    if (!window.Stripe) {
      console.error('Stripe.js not loaded');
      emit('payment-error', 'Stripe.js failed to load. Please refresh the page.');
      return;
    }
    const stripePublishableKey = import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY;
    const stripe = window.Stripe(stripePublishableKey, {
      apiVersion: '2022-11-15'
    });
    
    // Store the stripe instance
    stripeInstance.value = stripe;
    
    // Create elements instance with minimal configuration
    const elements = stripe.elements();
    stripeElements.value = elements;
    
    // Detect if dark mode is active
    const isDarkMode = document.documentElement.classList.contains('dark');
    
    // Create card element with adaptive colors
    const card = elements.create('card', {
      style: {
        base: {
          color: isDarkMode ? '#FFFFFF' : '#172554',
          fontFamily: 'ui-sans-serif, system-ui, sans-serif',
          fontSize: '16px',
          '::placeholder': {
            color: isDarkMode ? 'rgba(255, 255, 255, 0.4)' : 'rgba(23, 37, 84, 0.4)'
          }
        },
        invalid: {
          color: '#EF4444'
        }
      }
    });
    
    // Add HTTP warning only in development
    if (import.meta.env.DEV && window.location.protocol === 'http:') {
      console.warn('Stripe is running over HTTP. This is fine for development, but HTTPS is required for production.');
    }
    
    // Mount card element and handle potential errors
    try {
      card.mount('#card-element');
      console.log('Stripe card element mounted successfully');
    } catch (mountError: any) {
      console.error('Error mounting Stripe card element:', mountError);
      emit('payment-error', 'Failed to load payment form');
      return;
    }
    
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
      paymentMethodId: result.paymentMethod.id
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

// Clear form - resets amount and clears card element
const clearForm = () => {
  // Reset amount to minimum
  amount.value = props.minAmount;
  
  // Clear the Stripe card element
  if (stripeElements.value) {
    const cardElement = stripeElements.value.getElement('card');
    if (cardElement) {
      cardElement.clear();
      cardComplete.value = false;
    }
  }
  
  // Clear any error messages
  const errorElement = document.getElementById('card-errors');
  if (errorElement) {
    errorElement.textContent = '';
  }
}

// Expose clearForm method to parent component
defineExpose({
  clearForm
})
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

/* Respect users who prefer reduced motion */
@media (prefers-reduced-motion: reduce) {
  button[type="submit"],
  button[type="submit"]:hover,
  button[type="submit"]:active {
    transform: none;
  }
}

/* Ensure Stripe element container is properly displayed */
#card-element {
  display: block;
  width: 100%;
}

/* Ensure Stripe iframe renders properly within the grid */
#card-element iframe {
  display: block;
  width: 100%;
}
</style> 