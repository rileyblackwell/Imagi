<template>
  <div class="max-w-3xl mx-auto px-4 py-8">
    <PaymentToast />
    <div class="bg-dark-800 rounded-lg shadow-xl overflow-hidden border border-dark-700 relative">
      <!-- Loading Overlay -->
      <div v-if="isLoading" class="loading-overlay">
        <div class="spinner"></div>
      </div>

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
                <p class="text-sm text-gray-400">Credits for AI model usage</p>
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
            <!-- Error Message -->
            <div v-if="error" class="error-message mt-2">
              {{ error }}
            </div>
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

        <!-- Additional Information -->
        <div class="mt-6 text-center">
          <p class="text-sm text-gray-400">
            By proceeding with the payment, you agree to our 
            <a href="/terms" class="text-primary-400 hover:text-primary-300">Terms of Service</a>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import PaymentService from '../services/payment_service'
import { useToast } from '../composables/useToast'
import PaymentToast from '../components/ui/Toast.vue'

export default {
  name: 'Checkout',
  components: {
    PaymentToast
  },
  setup() {
    const router = useRouter()
    const route = useRoute()
    const stripe = ref(null)
    const elements = ref(null)
    const paymentElement = ref(null)
    const isLoading = ref(false)
    const error = ref(null)
    const amount = ref(0)
    const paymentService = new PaymentService()
    const toast = useToast()

    // Wait for Stripe.js to load
    const waitForStripe = () => {
      return new Promise((resolve) => {
        if (window.Stripe) {
          resolve(window.Stripe)
        } else {
          const checkStripe = setInterval(() => {
            if (window.Stripe) {
              clearInterval(checkStripe)
              resolve(window.Stripe)
            }
          }, 100)
        }
      })
    }

    // Initialize Stripe and load amount details
    async function initialize() {
      try {
        isLoading.value = true
        error.value = null

        // Get amount from route query or localStorage
        const customAmount = route.query.amount || localStorage.getItem('payment_amount')

        if (!customAmount) {
          // Redirect to credits page if no amount specified
          router.push({ name: 'payments-credits' })
          return
        }

        // Handle amount
        const parsedAmount = parseFloat(customAmount)
        if (isNaN(parsedAmount) || parsedAmount < 5 || parsedAmount > 1000) {
          throw new Error('Invalid amount specified. Please enter an amount between $5 and $1,000.')
        }
        amount.value = parsedAmount
        
        // Store amount in localStorage in case of page refresh
        localStorage.setItem('payment_amount', parsedAmount.toString())

        // Create payment intent
        const paymentIntent = await paymentService.createPaymentIntent({
          amount: amount.value
        })

        if (!paymentIntent || !paymentIntent.clientSecret) {
          throw new Error('Failed to create payment session')
        }

        // Wait for Stripe to be available
        const Stripe = await waitForStripe()
        stripe.value = Stripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY)

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

        // Wait for the payment element container to be available
        await new Promise(resolve => setTimeout(resolve, 100))

        // Create and mount the Payment Element
        try {
          if (paymentElement.value) {
            paymentElement.value.unmount()
          }
          paymentElement.value = elements.value.create('payment')
          const container = document.getElementById('payment-element')
          if (!container) {
            throw new Error('Payment element container not found')
          }
          await paymentElement.value.mount('#payment-element')
        } catch (mountError) {
          console.error('Error mounting payment element:', mountError)
          throw new Error('Failed to load payment form. Please refresh the page.')
        }

        // Handle automatic redirect after successful payment
        if (paymentIntent.status === 'succeeded') {
          // Clear stored amount
          localStorage.removeItem('payment_amount')
          router.push({
            name: 'payments-success',
            query: { 
              payment_intent: paymentIntent.id,
              amount: amount.value
            }
          })
        }

      } catch (err) {
        error.value = err.message
        toast.error(err.message)
        console.error('Initialization error:', err)
        
        // Only redirect if it's an amount error
        if (err.message.includes('amount')) {
          setTimeout(() => {
            router.push({ name: 'payments-credits' })
          }, 3000)
        }
      } finally {
        isLoading.value = false
      }
    }

    // Handle form submission
    async function handleSubmit() {
      if (!stripe.value || !elements.value) {
        toast.error('Payment form not ready. Please wait or refresh the page.')
        return
      }

      try {
        isLoading.value = true
        error.value = null

        // Create a new customer or get existing customer
        await paymentService.setupCustomer()

        const { error: submitError } = await stripe.value.confirmPayment({
          elements: elements.value,
          confirmParams: {
            return_url: `${window.location.origin}/payments/success`,
            payment_method_data: {
              billing_details: {
                email: window.userEmail // Assuming you have the user's email available
              }
            }
          }
        })

        if (submitError) {
          throw submitError
        }
      } catch (err) {
        error.value = err.message
        toast.error('Payment failed: ' + err.message)
        console.error('Payment error:', err)
      } finally {
        isLoading.value = false
      }
    }

    // Clean up on component unmount
    onUnmounted(() => {
      if (paymentElement.value) {
        try {
          paymentElement.value.unmount()
        } catch (err) {
          console.error('Error unmounting payment element:', err)
        }
      }
      // Clear stored amount on unmount
      localStorage.removeItem('payment_amount')
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

.error-message {
  color: #ff4d4d;
  font-size: 0.875rem;
  margin-top: 0.5rem;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
}

.spinner {
  border: 3px solid rgba(0, 255, 198, 0.1);
  border-radius: 50%;
  border-top: 3px solid #00ffc6;
  width: 24px;
  height: 24px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style> 