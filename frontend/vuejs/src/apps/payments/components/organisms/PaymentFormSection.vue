<template>
  <PaymentCard contentClass="p-8" :class="animate ? 'animate-fade-in-up animation-delay-600' : ''">
    <h2 class="text-xl font-semibold mb-4 bg-gradient-to-r from-primary-300 to-primary-500 bg-clip-text text-transparent">
      {{ title }}
    </h2>
    
    <!-- Custom Amount Input -->
    <div class="mb-8">
      <h3 class="text-lg font-medium mb-4 text-white/90">{{ amountSectionTitle }}</h3>
      <div class="mb-4">
        <label class="block text-sm font-medium text-white/80 mb-2">{{ amountLabel }}</label>
        <div class="relative mt-1 rounded-md shadow-sm">
          <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
            <span class="text-white/60 sm:text-sm">$</span>
          </div>
          <input
            v-model="amount"
            type="number"
            :min="minAmount"
            :step="step"
            class="block w-full rounded-xl border-white/20 bg-dark-800/50 py-3 pl-8 pr-12 text-white placeholder-white/40 backdrop-blur-sm focus:border-primary-500 focus:ring-primary-500 transition-all duration-300"
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
      <h3 class="text-lg font-medium mb-6 bg-gradient-to-r from-primary-300 to-primary-500 bg-clip-text text-transparent">
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
              class="block w-full rounded-xl border border-white/20 bg-dark-800/50 py-3 px-4 text-white backdrop-blur-sm transition-all duration-300 focus-within:border-primary-500 focus-within:ring-1 focus-within:ring-primary-500 min-h-[45px]"
            ></div>
            <div id="card-errors" class="mt-2 text-sm text-red-400"></div>
          </div>
          
          <!-- Additional Payment Fields -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-white/80 mb-2">Name on Card</label>
              <input
                v-model="cardholderName"
                type="text"
                class="block w-full rounded-xl border-white/20 bg-dark-800/50 py-3 px-4 text-white placeholder-white/40 backdrop-blur-sm focus:border-primary-500 focus:ring-primary-500 transition-all duration-300"
                placeholder="John Smith"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-white/80 mb-2">Email</label>
              <input
                v-model="email"
                type="email"
                class="block w-full rounded-xl border-white/20 bg-dark-800/50 py-3 px-4 text-white placeholder-white/40 backdrop-blur-sm focus:border-primary-500 focus:ring-primary-500 transition-all duration-300"
                placeholder="you@example.com"
              />
            </div>
          </div>
        </div>
        
        <!-- Submission Button -->
        <button
          type="submit"
          class="group relative w-full py-4 px-6 bg-primary-600 hover:bg-primary-500 text-white font-medium rounded-xl border border-primary-500/40 hover:border-primary-400/50 shadow-lg shadow-primary-600/30 transition-all duration-300 transform hover:-translate-y-1 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:translate-y-0"
          :disabled="isLoading || !isValidAmount || !stripe || !elements || !cardElement || !isStripeReady"
        >
          <span class="relative z-10">
            <span v-if="isLoading" class="flex items-center justify-center">
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ loadingText }}
            </span>
            <span v-else>{{ buttonText }}</span>
          </span>
          <div class="absolute inset-0 rounded-xl bg-gradient-to-r from-primary-500 to-primary-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300 blur-sm -z-10"></div>
        </button>
        
        <!-- Payment Card Icons -->
        <div class="mt-4 flex justify-center gap-2">
          <img src="@/assets/images/visa.svg" alt="Visa" class="h-6 opacity-60">
          <img src="@/assets/images/mastercard.svg" alt="Mastercard" class="h-6 opacity-60">
          <img src="@/assets/images/amex.svg" alt="American Express" class="h-6 opacity-60">
        </div>
      </form>
    </div>
  </PaymentCard>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import PaymentCard from '../atoms/Card.vue';
import { loadStripe } from '@stripe/stripe-js';
import type { Stripe, StripeElements, StripeCardElement } from '@stripe/stripe-js';

const props = defineProps({
  title: {
    type: String,
    default: 'Buy Credits'
  },
  amountSectionTitle: {
    type: String,
    default: 'Enter Amount'
  },
  amountLabel: {
    type: String,
    default: 'Amount to Add ($USD)'
  },
  paymentSectionTitle: {
    type: String,
    default: 'Payment Details'
  },
  cardLabel: {
    type: String,
    default: 'Card Information'
  },
  buttonText: {
    type: String,
    default: 'Pay'
  },
  loadingText: {
    type: String,
    default: 'Processing...'
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
    default: 'Minimum amount: $5'
  },
  stripePublicKey: {
    type: String,
    default: 'pk_test_51MmOZjDEzYnWl3gYjUCK9hFdnx8ayRW9M46FG1cBnXP0nh0obUYyKF6ub5mZsMZJmQfnoJ5pLzfwsVRgGSAhp9jB00bvJjsRqV'
  },
  isLoading: {
    type: Boolean,
    default: false
  },
  animate: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['submit', 'update:amount', 'payment-error']);

// Payment form state
const amount = ref<string | number>('');
const cardholderName = ref('');
const email = ref('');

// Stripe related state
const stripe = ref<Stripe | null>(null);
const elements = ref<StripeElements | null>(null);
const cardElement = ref<StripeCardElement | null>(null);
const isStripeReady = ref(false);
const cardErrors = ref('');

watch(amount, (newAmount) => {
  emit('update:amount', newAmount);
});

const isValidAmount = computed(() => {
  const numAmount = typeof amount.value === 'string' ? parseFloat(amount.value) : amount.value;
  return !isNaN(numAmount) && numAmount >= props.minAmount;
});

const formattedAmount = computed(() => {
  const numAmount = typeof amount.value === 'string' ? parseFloat(amount.value) : amount.value;
  return isNaN(numAmount) ? '0.00' : numAmount.toFixed(2);
});

// Initialize Stripe
const initializeStripe = async () => {
  try {
    stripe.value = await loadStripe(props.stripePublicKey);
    
    if (!stripe.value) {
      throw new Error('Failed to load Stripe');
    }
    
    elements.value = stripe.value.elements({
      appearance: {
        theme: 'night',
        variables: {
          colorPrimary: '#3b82f6',
          colorBackground: 'rgba(22, 26, 34, 0.95)',
          colorText: '#ffffff',
          colorDanger: '#ef4444',
          fontFamily: 'system-ui, sans-serif',
          borderRadius: '0.75rem',
          fontSizeBase: '16px'
        },
        rules: {
          '.Input': {
            border: '1px solid rgba(255, 255, 255, 0.2)',
            boxShadow: 'none',
            padding: '12px',
          },
          '.Input:focus': {
            border: '1px solid rgba(59, 130, 246, 0.8)',
            boxShadow: '0 0 0 1px rgba(59, 130, 246, 0.4)',
          }
        }
      }
    });
    
    cardElement.value = elements.value.create('card', {
      hidePostalCode: true,
      style: {
        base: {
          color: '#ffffff',
          fontFamily: 'system-ui, sans-serif',
          fontSize: '16px',
          '::placeholder': {
            color: 'rgba(255, 255, 255, 0.4)',
          },
          iconColor: 'rgba(255, 255, 255, 0.6)'
        },
        invalid: {
          color: '#ef4444',
          iconColor: '#ef4444'
        }
      }
    });
    
    // Mount card element
    cardElement.value.mount('#card-element');
    
    // Handle real-time validation errors
    cardElement.value.on('change', (event) => {
      const displayError = document.getElementById('card-errors');
      if (displayError) {
        if (event.error) {
          cardErrors.value = event.error.message;
          displayError.textContent = event.error.message;
        } else {
          cardErrors.value = '';
          displayError.textContent = '';
        }
      }
    });
    
    isStripeReady.value = true;
  } catch (error: any) {
    console.error('Stripe initialization error:', error);
    emit('payment-error', error.message);
  }
};

const submitPayment = async () => {
  if (!isValidAmount.value || !stripe.value || !elements.value || !cardElement.value) {
    return;
  }
  
  try {
    // Get payment details
    const { paymentMethod, error } = await stripe.value.createPaymentMethod({
      type: 'card',
      card: cardElement.value,
      billing_details: {
        name: cardholderName.value,
        email: email.value
      }
    });
    
    if (error) {
      cardErrors.value = error.message || 'Payment failed';
      emit('payment-error', error.message);
      return;
    }
    
    // Payment method created successfully
    emit('submit', {
      amount: parseFloat(formattedAmount.value),
      paymentMethodId: paymentMethod.id,
      email: email.value,
      name: cardholderName.value
    });
    
  } catch (error: any) {
    cardErrors.value = error.message || 'Payment processing failed';
    emit('payment-error', error.message);
  }
};

onMounted(() => {
  initializeStripe();
});

onUnmounted(() => {
  if (cardElement.value) {
    cardElement.value.unmount();
  }
});
</script>

<style scoped>
/* Animation delays */
.animation-delay-600 {
  animation-delay: 600ms;
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

/* Custom styling for card elements */
:deep(.StripeElement) {
  width: 100%;
}

:deep(.StripeElement--focus) {
  border-color: rgba(59, 130, 246, 0.8);
  box-shadow: 0 0 0 1px rgba(59, 130, 246, 0.4);
}

:deep(.StripeElement--invalid) {
  border-color: rgba(239, 68, 68, 0.8);
}
</style> 