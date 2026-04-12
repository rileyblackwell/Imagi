<template>
  <div>
    <div class="mb-6">
      <PaymentInput
        v-model="amount"
        id="amount"
        type="number"
        label="Amount to Add ($)"
        prefix="$"
        min="5"
        max="1000"
        step="0.01"
        placeholder="Enter amount"
        :disabled="isProcessing"
        :error="amountError"
        helpText="Minimum: $5.00, Maximum: $1,000.00"
      />
    </div>

    <div v-if="isValidAmount" class="mb-6">
      <OrderSummary :amount="Number(amount)" :title="summaryTitle" :subtitle="summarySubtitle" />
    </div>

    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-300 mb-2">
        Card Information
      </label>
      <div 
        id="card-element" 
        class="bg-dark-900 rounded-lg p-4 min-h-[40px] border border-dark-700"
      ></div>
      <div id="card-errors" class="mt-2 text-sm text-red-500"></div>
    </div>

    <PaymentButton
      type="submit"
      :disabled="!isValidAmount || isProcessing || !isStripeReady"
      :loading="isProcessing"
      :full-width="true"
    >
      {{ isProcessing ? 'Processing Payment...' : 'Pay Now' }}
    </PaymentButton>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { loadStripe } from '@stripe/stripe-js'
import PaymentInput from '../atoms/Input.vue'
import PaymentButton from '../atoms/Button.vue'
import OrderSummary from './OrderSummary.vue'

export default defineComponent({
  name: 'PaymentForm',
  components: {
    PaymentInput,
    PaymentButton,
    OrderSummary
  },
  props: {
    isProcessing: {
      type: Boolean,
      default: false
    },
    summaryTitle: {
      type: String,
      default: 'Add Funds'
    },
    summarySubtitle: {
      type: String,
      default: 'Credits for AI model usage'
    }
  },
  emits: ['update:amount', 'submit', 'stripe-ready', 'stripe-error'],
  setup(props, { emit }) {
    const amount = ref('')
    const amountError = ref('')
    const stripe = ref<any>(null)
    const elements = ref<any>(null)
    const cardElement = ref<any>(null)
    const isStripeReady = ref(false)

    const isValidAmount = computed(() => {
      const value = parseFloat(amount.value)
      return !isNaN(value) && value >= 5 && value <= 1000
    })

    watch(amount, (newValue) => {
      emit('update:amount', newValue)
      // Validate amount
      if (newValue && !isValidAmount.value) {
        amountError.value = 'Please enter a valid amount between $5 and $1,000'
      } else {
        amountError.value = ''
      }
    })

    const initializeStripe = async () => {
      try {
        // Initialize Stripe
        const stripeKey = import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY
        if (!stripeKey) {
          throw new Error('Stripe publishable key is not configured')
        }

        stripe.value = await loadStripe(stripeKey)
        if (!stripe.value) {
          throw new Error('Failed to load Stripe')
        }

        // Create Elements instance with proper styling
        elements.value = stripe.value.elements({
          appearance: {
            theme: 'night',
            variables: {
              colorPrimary: '#00ffc6',
              colorBackground: '#1a1b23',
              colorText: '#ffffff',
              colorDanger: '#ff4d4d',
              fontFamily: 'system-ui, sans-serif',
              borderRadius: '8px',
            },
            rules: {
              '.Input': {
                border: '1px solid #2d2d3b',
                boxShadow: 'none',
              },
              '.Input:focus': {
                border: '1px solid #00ffc6',
              },
              '.Label': {
                color: '#ffffff',
              }
            }
          },
          loader: 'auto'
        })

        // Create and mount the Card Element
        cardElement.value = elements.value.create('card', {
          style: {
            base: {
              color: '#ffffff',
              fontFamily: 'system-ui, sans-serif',
              fontSize: '16px',
              '::placeholder': {
                color: '#6b7280',
              },
              backgroundColor: '#1a1b23',
            },
          },
          hidePostalCode: true
        })

        // Mount the card element
        const container = document.getElementById('card-element')
        if (!container) {
          throw new Error('Card element container not found')
        }
        
        await cardElement.value.mount('#card-element')

        // Handle real-time validation errors
        cardElement.value.on('change', (event: any) => {
          const displayError = document.getElementById('card-errors')
          if (displayError) {
            if (event.error) {
              displayError.textContent = event.error.message
              emit('stripe-error', event.error.message)
            } else {
              displayError.textContent = ''
            }
          }
        })

        // Add focus/blur handlers for better UX
        cardElement.value.on('focus', () => {
          const el = document.getElementById('card-element')
          if (el) {
            el.classList.add('ring-2', 'ring-primary-500', 'border-primary-500')
          }
        })

        cardElement.value.on('blur', () => {
          const el = document.getElementById('card-element')
          if (el) {
            el.classList.remove('ring-2', 'ring-primary-500', 'border-primary-500')
          }
        })

        isStripeReady.value = true
        emit('stripe-ready', { stripe: stripe.value, elements: elements.value, cardElement: cardElement.value })
      } catch (err: any) {
        emit('stripe-error', err.message)
        console.error('Stripe initialization error:', err)
      }
    }

    onMounted(() => {
      initializeStripe()
    })

    onUnmounted(() => {
      if (cardElement.value) {
        cardElement.value.unmount()
      }
    })

    return {
      amount,
      amountError,
      stripe,
      elements,
      cardElement,
      isValidAmount,
      isStripeReady
    }
  }
})
</script> 