<template>
  <div class="payment-form">
    <div class="mb-8">
      <PaymentAmountSelector
        :value="amount"
        @input="updateAmount"
      />
    </div>

    <div class="payment-method mb-6">
      <h3 class="text-lg font-medium text-white mb-4">Payment Method</h3>
      
      <div 
        ref="cardElement" 
        class="p-4 bg-dark-800 border border-gray-700 rounded-lg mb-4"
      ></div>
      
      <div v-if="cardError" class="text-red-500 text-sm mb-4">
        {{ cardError }}
      </div>
    </div>

    <div class="summary mb-6">
      <h3 class="text-lg font-medium text-white mb-4">Summary</h3>
      <div class="bg-dark-800 border border-gray-700 rounded-lg p-4">
        <div class="flex justify-between py-2 border-b border-gray-700">
          <span class="text-gray-400">Amount</span>
          <span class="text-white">${{ amount.toFixed(2) }}</span>
        </div>
        <div class="flex justify-between py-2">
          <span class="text-gray-400">Total</span>
          <span class="font-medium text-white">${{ amount.toFixed(2) }}</span>
        </div>
      </div>
    </div>

    <button 
      @click="submitPayment"
      :disabled="loading || !cardComplete"
      class="w-full py-3 px-6 bg-primary-500 text-white font-medium rounded-lg transition-all duration-200 hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed"
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
import { usePaymentsStore } from '../../stores'

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
    const store = usePaymentsStore()
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
        
        // Create card element with simple styling
        card.value = elements.create('card', {
          style: {
            base: {
              color: '#fff',
              fontFamily: '"Inter", sans-serif',
              fontSize: '16px',
              '::placeholder': {
                color: '#6b7280'
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