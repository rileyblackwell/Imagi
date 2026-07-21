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
      <label class="block text-sm font-medium text-blue-950/80 dark:text-blue-100/80 mb-2 transition-colors duration-300">
        Card Information
      </label>
      <div
        id="card-element"
        class="bg-white dark:bg-white/[0.05] rounded-xl p-4 min-h-[40px] border border-blue-950/[0.12] dark:border-white/[0.14] transition-colors duration-200"
      ></div>
      <div id="card-errors" class="mt-2 text-sm text-red-600 dark:text-red-400"></div>
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

        // Match the Stripe iframe to the warm-porcelain theme (ink navy / dark)
        const isDarkMode = document.documentElement.classList.contains('dark')

        // Create Elements instance with proper styling
        elements.value = stripe.value.elements({
          appearance: {
            theme: isDarkMode ? 'night' : 'stripe',
            variables: {
              colorPrimary: isDarkMode ? '#93c5fd' : '#1d4ed8',
              colorBackground: isDarkMode ? '#16161a' : '#ffffff',
              colorText: isDarkMode ? '#ffffff' : '#172554',
              colorDanger: isDarkMode ? '#f87171' : '#dc2626',
              fontFamily: 'system-ui, sans-serif',
              borderRadius: '12px',
            },
            rules: {
              '.Input': {
                border: isDarkMode ? '1px solid rgba(255, 255, 255, 0.14)' : '1px solid rgba(23, 37, 84, 0.12)',
                boxShadow: 'none',
              },
              '.Input:focus': {
                border: isDarkMode ? '1px solid rgba(147, 197, 253, 0.5)' : '1px solid rgba(59, 130, 246, 0.5)',
              },
              '.Label': {
                color: isDarkMode ? '#ffffff' : '#172554',
              }
            }
          },
          loader: 'auto'
        })

        // Create and mount the Card Element
        cardElement.value = elements.value.create('card', {
          style: {
            base: {
              color: isDarkMode ? '#ffffff' : '#172554',
              fontFamily: 'system-ui, sans-serif',
              fontSize: '16px',
              '::placeholder': {
                color: isDarkMode ? 'rgba(255, 255, 255, 0.4)' : 'rgba(23, 37, 84, 0.4)',
              },
              backgroundColor: 'transparent',
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
            el.classList.add('ring-2', 'ring-blue-500/40', 'dark:ring-blue-300/50', 'border-blue-500/50', 'dark:border-blue-300/50')
          }
        })

        cardElement.value.on('blur', () => {
          const el = document.getElementById('card-element')
          if (el) {
            el.classList.remove('ring-2', 'ring-blue-500/40', 'dark:ring-blue-300/50', 'border-blue-500/50', 'dark:border-blue-300/50')
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