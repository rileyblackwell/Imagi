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
        <h2 class="text-2xl font-bold text-white">Add Funds</h2>
        <p class="text-gray-400 mt-2">Add credits to your account for AI model usage</p>
      </div>

      <!-- Main Content -->
      <div class="p-6">
        <!-- Current Balance -->
        <div class="mb-8">
          <h3 class="text-lg font-medium text-white mb-4">Current Balance</h3>
          <div class="bg-dark-900 rounded-lg p-4">
            <div class="flex justify-between items-center">
              <div>
                <p class="text-white font-medium">Available Credits</p>
                <p class="text-sm text-gray-400">Last updated: {{ lastUpdated }}</p>
              </div>
              <div class="text-2xl font-bold text-primary-400">
                ${{ currentBalance.toFixed(2) }}
              </div>
            </div>
          </div>
        </div>

        <!-- Payment Form -->
        <form id="payment-form" @submit.prevent="handleSubmit">
          <!-- Amount Input -->
          <div class="mb-6">
            <label for="amount" class="block text-sm font-medium text-gray-300 mb-2">
              Amount to Add ($)
            </label>
            <div class="relative">
              <span class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">$</span>
              <input
                type="number"
                id="amount"
                v-model="amount"
                min="5"
                max="1000"
                step="0.01"
                class="w-full pl-8 pr-4 py-3 bg-dark-900 border border-dark-700 rounded-lg text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="Enter amount"
                :disabled="isProcessing"
              >
            </div>
            <p class="mt-2 text-sm text-gray-400">Minimum: $5.00, Maximum: $1,000.00</p>
          </div>

          <!-- Order Summary -->
          <div v-if="isValidAmount" class="mb-6">
            <h3 class="text-lg font-medium text-white mb-4">Order Summary</h3>
            <div class="bg-dark-900 rounded-lg p-4">
              <div class="flex justify-between items-center mb-4">
                <div>
                  <p class="text-white font-medium">Add Funds</p>
                  <p class="text-sm text-gray-400">Credits for AI model usage</p>
                </div>
                <p class="text-xl font-bold text-primary-400">${{ amount }}</p>
              </div>
              <div class="border-t border-dark-700 pt-4">
                <div class="flex justify-between items-center">
                  <p class="text-gray-400">Total</p>
                  <p class="text-2xl font-bold text-primary-400">${{ amount }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Card Element -->
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

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="!isValidAmount || isProcessing || !stripe || !elements"
            class="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="isProcessing" class="mr-2">
              <i class="fas fa-spinner fa-spin"></i>
            </span>
            {{ isProcessing ? 'Processing Payment...' : 'Pay Now' }}
          </button>
        </form>

        <!-- Error Message -->
        <div v-if="error" class="mt-4 text-red-500 text-sm text-center">
          {{ error }}
        </div>

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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { loadStripe } from '@stripe/stripe-js'
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
    const stripe = ref(null)
    const elements = ref(null)
    const cardElement = ref(null)
    const amount = ref('')
    const isLoading = ref(false)
    const isProcessing = ref(false)
    const error = ref(null)
    const currentBalance = ref(0)
    const lastUpdated = ref(new Date().toLocaleString())
    const paymentService = new PaymentService()
    const toast = useToast()

    const isValidAmount = computed(() => {
      const value = parseFloat(amount.value)
      return !isNaN(value) && value >= 5 && value <= 1000
    })

    async function loadBalance() {
      try {
        isLoading.value = true
        const { balance } = await paymentService.getBalance()
        currentBalance.value = balance
        lastUpdated.value = new Date().toLocaleString()
      } catch (err) {
        console.error('Failed to load balance:', err)
        error.value = 'Failed to load current balance. Please refresh the page.'
        toast.error('Failed to load current balance')
      } finally {
        isLoading.value = false
      }
    }

    async function initializeStripe() {
      try {
        // Initialize Stripe
        if (!import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY) {
          throw new Error('Stripe publishable key is not configured')
        }

        stripe.value = await loadStripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY)
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

        // Create and mount the Card Element with specific style options
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
          hidePostalCode: true // Remove postal code field if not needed
        })

        // Mount the card element
        const container = document.getElementById('card-element')
        if (!container) {
          throw new Error('Card element container not found')
        }
        
        await cardElement.value.mount('#card-element')

        // Handle real-time validation errors
        cardElement.value.on('change', (event) => {
          const displayError = document.getElementById('card-errors')
          if (displayError) {
            if (event.error) {
              displayError.textContent = event.error.message
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

      } catch (err) {
        error.value = 'Failed to initialize payment form: ' + err.message
        console.error('Stripe initialization error:', err)
      }
    }

    async function handleSubmit() {
      if (!isValidAmount.value) {
        error.value = 'Please enter a valid amount between $5 and $1,000'
        return
      }

      try {
        isProcessing.value = true
        error.value = null
        const value = parseFloat(amount.value)

        // Create payment intent
        const { clientSecret } = await paymentService.createPaymentIntent({
          amount: value
        })

        if (!clientSecret) {
          throw new Error('Failed to initialize payment')
        }

        // Confirm the payment
        const { error: paymentError } = await stripe.value.confirmCardPayment(clientSecret, {
          payment_method: {
            card: cardElement.value,
            billing_details: {
              email: window.userEmail // Assuming you have the user's email available
            }
          }
        })

        if (paymentError) {
          throw paymentError
        }

        // Payment successful
        toast.success('Payment successful!')
        await loadBalance() // Refresh the balance after successful payment
        
        // Reset form
        amount.value = ''
        cardElement.value.clear()
        
        // Show success message
        toast.success('Your credits have been added successfully!')
      } catch (err) {
        error.value = err.message
        toast.error(err.message)
        console.error('Payment error:', err)
      } finally {
        isProcessing.value = false
      }
    }

    onMounted(() => {
      loadBalance()
      initializeStripe()
    })

    onUnmounted(() => {
      if (cardElement.value) {
        cardElement.value.unmount()
      }
    })

    return {
      amount,
      isLoading,
      isProcessing,
      error,
      currentBalance,
      lastUpdated,
      stripe,
      elements,
      isValidAmount,
      handleSubmit
    }
  }
}
</script>

<style scoped>
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

input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

input[type="number"] {
  -moz-appearance: textfield;
}
</style> 