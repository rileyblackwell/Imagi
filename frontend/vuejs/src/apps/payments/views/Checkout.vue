<template>
  <div class="max-w-3xl mx-auto px-4 py-8">
    <div class="bg-dark-800 rounded-lg shadow-xl overflow-hidden border border-dark-700">
      <!-- Header -->
      <div class="p-6 border-b border-dark-700">
        <h2 class="text-2xl font-bold text-white">Complete Purchase</h2>
        <p class="text-gray-400 mt-2">Secure payment powered by Stripe</p>
      </div>

      <!-- Main Content -->
      <div class="p-6">
        <!-- Order Summary -->
        <div class="mb-8">
          <h3 class="text-lg font-medium text-white mb-4">Order Summary</h3>
          <div class="bg-dark-900 rounded-lg p-4">
            <div class="flex justify-between items-center mb-4">
              <div>
                <p class="text-white font-medium">Add Funds</p>
              </div>
              <p class="text-xl font-bold text-white">${{ amount }}</p>
            </div>
            <div class="border-t border-dark-700 pt-4">
              <div class="flex justify-between items-center">
                <p class="text-gray-400">Total</p>
                <p class="text-2xl font-bold text-primary-400">${{ amount }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Payment Form -->
        <form id="payment-form" @submit.prevent="handleSubmit">
          <!-- Stripe Elements Container -->
          <div class="mb-6">
            <label class="block text-sm font-medium text-gray-300 mb-2">
              Card Details
            </label>
            <div 
              id="payment-element" 
              class="bg-dark-900 rounded-lg p-4 min-h-[200px] border border-dark-700"
            ></div>
          </div>

          <!-- Error Message -->
          <div v-if="error" class="mb-6">
            <p class="text-red-500 text-sm">{{ error }}</p>
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="isLoading || !stripe || !elements"
            class="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="isLoading" class="mr-2">
              <i class="fas fa-spinner fa-spin"></i>
            </span>
            {{ isLoading ? 'Processing...' : 'Pay Now' }}
          </button>
        </form>

        <!-- Security Badge -->
        <div class="mt-6 flex items-center justify-center text-gray-400 text-sm">
          <i class="fas fa-lock mr-2"></i>
          <span>Payments are secure and encrypted</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import PaymentService from '../services/payment_service'

export default {
  name: 'Checkout',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const stripe = ref(null)
    const elements = ref(null)
    const isLoading = ref(false)
    const error = ref(null)
    const amount = ref(0)
    const paymentService = new PaymentService()

    // Initialize Stripe and load amount details
    async function initialize() {
      try {
        isLoading.value = true
        error.value = null

        // Get amount from route query
        const customAmount = route.query.amount

        if (!customAmount) {
          throw new Error('No amount specified')
        }

        // Handle amount
        const parsedAmount = parseFloat(customAmount)
        if (isNaN(parsedAmount) || parsedAmount < 5 || parsedAmount > 1000) {
          throw new Error('Invalid amount specified')
        }
        amount.value = parsedAmount

        // Create payment intent
        const paymentIntent = await paymentService.createPaymentIntent({
          amount: amount.value
        })

        if (!paymentIntent || !paymentIntent.clientSecret) {
          throw new Error('Failed to create payment session')
        }

        // Initialize Stripe
        if (!window.Stripe) {
          throw new Error('Stripe.js not loaded')
        }

        stripe.value = window.Stripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY)

        // Create Elements instance with proper styling
        elements.value = stripe.value.elements({
          clientSecret: paymentIntent.clientSecret,
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
            },
          },
        })

        // Create and mount the Payment Element
        const paymentElement = elements.value.create('payment')
        paymentElement.mount('#payment-element')

      } catch (err) {
        error.value = err.message
        console.error('Initialization error:', err)
        
        // Redirect back to add funds page if there's an error
        router.push({ name: 'add-funds' })
      } finally {
        isLoading.value = false
      }
    }

    // Handle form submission
    async function handleSubmit() {
      if (!stripe.value || !elements.value) {
        return
      }

      try {
        isLoading.value = true
        error.value = null

        const { error: submitError } = await stripe.value.confirmPayment({
          elements: elements.value,
          confirmParams: {
            return_url: `${window.location.origin}/payments/success`
          }
        })

        if (submitError) {
          throw submitError
        }
      } catch (err) {
        error.value = err.message
        console.error('Payment error:', err)
      } finally {
        isLoading.value = false
      }
    }

    // Clean up on component unmount
    onUnmounted(() => {
      if (elements.value) {
        elements.value.unmount()
      }
    })

    onMounted(() => {
      initialize()
    })

    return {
      stripe,
      elements,
      isLoading,
      error,
      amount,
      handleSubmit
    }
  }
}
</script>

<style scoped>
#payment-element {
  min-height: 200px;
}

#payment-element iframe {
  background: transparent;
}
</style> 