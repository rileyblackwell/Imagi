<template>
  <div class="checkout-container">
    <div class="max-w-3xl mx-auto px-4 py-8">
      <base-card>
        <template #header>
          <h2 class="text-2xl font-bold text-white">Add Credits</h2>
          <p class="text-gray-400 mt-2">Power your AI development with Imagi credits</p>
        </template>
        
        <div class="space-y-6">
          <!-- Amount Selection -->
          <div class="amount-selection">
            <label class="block text-sm font-medium text-gray-300 mb-2">
              Amount to Add
            </label>
            <div class="relative">
              <span class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">$</span>
              <input
                v-model="amount"
                type="number"
                min="10"
                max="100"
                step="0.01"
                class="w-full pl-8 pr-4 py-2 bg-dark-800 border border-dark-700 rounded-md text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                @input="handleAmountChange"
              />
            </div>
            <p v-if="amountError" class="mt-2 text-red-500 text-sm">{{ amountError }}</p>
          </div>

          <!-- Credits Preview -->
          <div class="credits-preview bg-dark-800 p-4 rounded-md border border-dark-700">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm text-gray-400">You'll receive</p>
                <p class="text-xl font-bold text-white">{{ creditsToReceive }} credits</p>
              </div>
              <div class="text-right">
                <p class="text-sm text-gray-400">Current Balance</p>
                <p class="text-xl font-bold text-primary-500">${{ currentBalance }}</p>
              </div>
            </div>
          </div>

          <!-- Stripe Payment Element -->
          <div class="payment-element-container">
            <div id="payment-element"></div>
          </div>

          <div v-if="errorMessage" class="text-red-500 text-sm mt-2">
            {{ errorMessage }}
          </div>

          <!-- Submit Button -->
          <button
            @click="handleSubmit"
            :disabled="isLoading || !isAmountValid"
            class="w-full py-3 px-4 border border-transparent rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            <span v-if="isLoading" class="mr-2">
              <i class="fas fa-spinner fa-spin"></i>
            </span>
            <span>{{ isLoading ? 'Processing...' : 'Complete Purchase' }}</span>
          </button>
        </div>
      </base-card>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import BaseCard from '@/shared/components/BaseCard.vue'
import PaymentService from '../services/payment.service'
import config from '@/shared/config'

export default {
  name: 'Checkout',
  components: {
    BaseCard
  },
  setup() {
    const router = useRouter()
    const paymentService = new PaymentService()
    const amount = ref(20)
    const amountError = ref('')
    const errorMessage = ref('')
    const isLoading = ref(false)
    const currentBalance = ref(0)
    const stripe = ref(null)
    const elements = ref(null)

    const creditsToReceive = computed(() => {
      return Math.floor(amount.value * config.payments.creditsPerDollar)
    })

    const isAmountValid = computed(() => {
      return amount.value >= 10 && amount.value <= 100 && !amountError.value
    })

    const handleAmountChange = () => {
      amountError.value = ''
      if (amount.value < 10) {
        amountError.value = 'Minimum amount is $10.00'
      } else if (amount.value > 100) {
        amountError.value = 'Maximum amount is $100.00'
      }
      // Reinitialize payment element with new amount
      if (isAmountValid.value) {
        initializePaymentElement()
      }
    }

    const initializePaymentElement = async () => {
      try {
        isLoading.value = true
        errorMessage.value = ''

        // Create payment intent
        const { clientSecret } = await paymentService.createPaymentIntent(amount.value)

        if (!elements.value) {
          elements.value = stripe.value.elements({
            clientSecret,
            appearance: {
              theme: 'night',
              variables: {
                colorPrimary: '#00ffc6',
                colorBackground: '#1a1b23',
                colorText: '#ffffff',
                colorDanger: '#ff4d4d',
                fontFamily: 'system-ui, sans-serif',
              }
            }
          })

          const paymentElement = elements.value.create('payment')
          paymentElement.mount('#payment-element')
        } else {
          await elements.value.fetchUpdates()
        }
      } catch (error) {
        errorMessage.value = error.message || 'Failed to initialize payment'
      } finally {
        isLoading.value = false
      }
    }

    const handleSubmit = async () => {
      if (!stripe.value || !elements.value) {
        return
      }

      try {
        isLoading.value = true
        errorMessage.value = ''

        const { error } = await stripe.value.confirmPayment({
          elements: elements.value,
          confirmParams: {
            return_url: `${window.location.origin}/payments/success/`,
            payment_method_data: {
              billing_details: {
                amount: amount.value
              }
            }
          }
        })

        if (error) {
          errorMessage.value = error.message
        }
      } catch (error) {
        errorMessage.value = 'Payment failed. Please try again.'
      } finally {
        isLoading.value = false
      }
    }

    const fetchBalance = async () => {
      try {
        const { balance } = await paymentService.getBalance()
        currentBalance.value = balance
      } catch (error) {
        console.error('Failed to fetch balance:', error)
      }
    }

    onMounted(async () => {
      // Initialize Stripe
      if (!window.Stripe) {
        errorMessage.value = 'Failed to load Stripe. Please refresh the page.'
        return
      }

      stripe.value = window.Stripe(config.payments.stripePublishableKey)
      if (!stripe.value) {
        errorMessage.value = 'Invalid Stripe configuration. Please contact support.'
        return
      }

      await Promise.all([
        initializePaymentElement(),
        fetchBalance()
      ])
    })

    return {
      amount,
      amountError,
      errorMessage,
      isLoading,
      currentBalance,
      creditsToReceive,
      isAmountValid,
      handleAmountChange,
      handleSubmit
    }
  }
}
</script>

<style scoped>
.payment-element-container {
  min-height: 300px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 20px;
}
</style> 