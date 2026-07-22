<template>
  <div class="payment-form">
    <div class="mb-8">
      <PaymentAmountSelector
        :value="amount"
        @input="updateAmount"
      />
    </div>

    <div class="payment-method mb-6">
      <h3 class="text-lg font-medium tracking-tight text-blue-950 dark:text-white mb-4 transition-colors duration-300">Payment Method</h3>

      <div
        ref="cardElement"
        class="p-4 bg-white dark:bg-white/[0.05] border border-blue-950/[0.12] dark:border-white/[0.14] rounded-xl mb-4 transition-colors duration-200"
      ></div>

      <div v-if="cardError" class="text-red-600 dark:text-red-400 text-sm mb-4">
        {{ cardError }}
      </div>
    </div>

    <div class="summary mb-6">
      <h3 class="text-lg font-medium tracking-tight text-blue-950 dark:text-white mb-4 transition-colors duration-300">Summary</h3>
      <div class="bg-white/85 dark:bg-white/[0.045] border border-blue-950/[0.08] dark:border-white/[0.1] backdrop-blur-sm rounded-2xl p-4 transition-colors duration-300">
        <div class="flex justify-between py-2 border-b border-blue-950/[0.08] dark:border-white/[0.1]">
          <span class="text-blue-950/60 dark:text-blue-100/55">Amount</span>
          <span class="tabular-nums text-blue-950 dark:text-white">${{ amount.toFixed(2) }}</span>
        </div>
        <div class="flex justify-between py-2">
          <span class="text-blue-950/60 dark:text-blue-100/55">Total</span>
          <span class="font-medium tabular-nums text-blue-950 dark:text-white">${{ amount.toFixed(2) }}</span>
        </div>
      </div>
    </div>

    <button
      @click="submitPayment"
      :disabled="loading || !cardComplete"
      class="w-full inline-flex items-center justify-center py-3 px-6 bg-blue-950 text-[#fdf9f2] hover:bg-blue-900 dark:bg-[#f3ede2] dark:text-blue-950 dark:hover:bg-white font-medium rounded-full transition-colors duration-200 shadow-[0_1px_2px_rgba(23,37,84,0.2),0_3px_8px_-2px_rgba(23,37,84,0.25)] dark:shadow-[0_1px_2px_rgba(0,0,0,0.4),0_3px_8px_-2px_rgba(0,0,0,0.45)] disabled:opacity-50 disabled:cursor-not-allowed focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0a0a0a]"
    >
      <span v-if="loading" class="flex items-center justify-center">
        <span class="mr-2">Processing</span>
        <span class="animate-spin">⟳</span>
      </span>
      <span v-else>Add Funds</span>
    </button>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import PaymentAmountSelector from '../molecules/PaymentAmountSelector.vue'
import { usePaymentStore } from '../../../../stores/payments'

export default {
  name: 'PaymentForm',
  components: {
    PaymentAmountSelector
  },
  props: {
    initialAmount: {
      type: Number,
      default: 50
    }
  },
  setup(props, { emit }) {
    const store = usePaymentStore()
    const amount = ref(props.initialAmount)
    const cardElement = ref(null)
    const stripe = ref(null)
    const card = ref(null)
    const cardComplete = ref(false)
    const cardError = ref('')
    const loading = ref(false)

    const updateAmount = (newAmount) => {
      amount.value = newAmount
    }

    onMounted(() => {
      // Initialize Stripe
      if (window.Stripe) {
        // Create Stripe instance with explicit API version
        const stripePublishableKey = import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY;
        stripe.value = window.Stripe(stripePublishableKey, {
          apiVersion: '2022-11-15'
        });
        
        // Create elements with minimal configuration
        const elements = stripe.value.elements();
        
        // Match the Stripe iframe text to the theme's ink color
        const isDarkMode = document.documentElement.classList.contains('dark');

        // Create card element with simple styling
        card.value = elements.create('card', {
          style: {
            base: {
              color: isDarkMode ? '#ffffff' : '#172554',
              fontFamily: '"Inter", sans-serif',
              fontSize: '16px',
              '::placeholder': {
                color: isDarkMode ? 'rgba(255, 255, 255, 0.4)' : 'rgba(23, 37, 84, 0.4)'
              }
            },
            invalid: {
              color: '#ef4444'
            }
          }
        });
        
        // Add HTTP warning only in development
        if (import.meta.env.DEV && window.location.protocol === 'http:') {
          console.warn('Stripe is running over HTTP. This is fine for development, but HTTPS is required for production.');
        }
        
        // Mount the card element
        card.value.mount(cardElement.value);
        
        // Listen for changes
        card.value.on('change', (event) => {
          cardComplete.value = event.complete;
          cardError.value = event.error ? event.error.message : '';
        });
      } else {
        console.error('Stripe.js not loaded');
        cardError.value = 'Payment system not available';
      }
    })

    const submitPayment = async () => {
      if (!cardComplete.value) return
      
      loading.value = true
      cardError.value = ''
      
      try {
        // Create payment method
        const { paymentMethod, error } = await stripe.value.createPaymentMethod({
          type: 'card',
          card: card.value
        })
        
        if (error) {
          throw new Error(error.message)
        }
        
        // Process payment with backend
        await store.processPayment({
          amount: amount.value,
          paymentMethodId: paymentMethod.id
        })
        
        // Emit success event
        emit('payment-success', {
          amount: amount.value
        })
      } catch (error) {
        cardError.value = error.message || 'Payment failed'
      } finally {
        loading.value = false
      }
    }

    return {
      amount,
      cardElement,
      cardComplete,
      cardError,
      loading,
      updateAmount,
      submitPayment
    }
  }
}
</script>

<style scoped>
.payment-form {
  max-width: 100%;
}
</style> 