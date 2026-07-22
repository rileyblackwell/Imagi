<template>
  <div class="add-card-form">
    <div v-if="error" class="error-message bg-red-50/80 dark:bg-red-500/10 border border-red-200/70 dark:border-red-400/25 text-red-700 dark:text-red-300 p-3 rounded-xl mb-4 transition-colors duration-300">
      {{ error }}
    </div>

    <div class="mb-4">
      <div ref="cardElement" class="card-element p-3 border border-blue-950/[0.12] dark:border-white/[0.14] rounded-xl"></div>
      <div v-if="cardError" class="text-red-600 dark:text-red-400 text-sm mt-1">{{ cardError }}</div>
    </div>

    <button
      @click="handleSubmit"
      :disabled="isLoading || !stripe"
      class="w-full inline-flex items-center justify-center py-2 px-4 rounded-full bg-blue-950 text-[#fdf9f2] hover:bg-blue-900 dark:bg-[#f3ede2] dark:text-blue-950 dark:hover:bg-white font-medium transition-colors duration-200 shadow-[0_1px_2px_rgba(23,37,84,0.2),0_3px_8px_-2px_rgba(23,37,84,0.25)] dark:shadow-[0_1px_2px_rgba(0,0,0,0.4),0_3px_8px_-2px_rgba(0,0,0,0.45)] disabled:opacity-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0a0a0a]"
    >
      <span v-if="isLoading">
        <svg class="animate-spin -ml-1 mr-2 h-4 w-4 inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        Processing...
      </span>
      <span v-else>Add Card</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { usePaymentStore } from '@/apps/payments/stores'

const store = usePaymentStore()

// Element references
const cardElement = ref<HTMLElement | null>(null)
const stripe = ref<any>(null)
const elements = ref<any>(null)
const cardError = ref('')
const error = ref('')
const isLoading = ref(false)

// Setup Stripe on component mount
onMounted(async () => {
  if (!window.Stripe) {
    error.value = 'Stripe.js not loaded. Please refresh the page.'
    return
  }
  
  try {
    // Initialize Stripe with your publishable key
    stripe.value = window.Stripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY)
    
    // Create Elements instance
    elements.value = stripe.value.elements()
    
    // Create and mount the Card Element
    const card = elements.value.create('card', {
      style: {
        base: {
          fontSize: '16px',
          color: '#32325d',
          fontFamily: '-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif',
          '::placeholder': {
            color: '#a0aec0',
          },
        },
        invalid: {
          color: '#e53e3e',
          iconColor: '#e53e3e',
        },
      },
    })
    
    if (cardElement.value) {
      card.mount(cardElement.value)
      
      // Listen for card input changes
      card.on('change', (event: any) => {
        cardError.value = event.error ? event.error.message : ''
      })
    }
  } catch (err: any) {
    console.error('Stripe initialization error:', err)
    error.value = 'Failed to initialize payment form. Please refresh and try again.'
  }
})

// Clean up on unmount
onUnmounted(() => {
  if (elements.value) {
    const card = elements.value.getElement('card')
    if (card) {
      card.unmount()
      card.destroy()
    }
  }
})

// Handle form submission
const handleSubmit = async () => {
  if (!stripe.value || !elements.value) {
    error.value = 'Stripe has not been initialized yet.'
    return
  }
  
  const card = elements.value.getElement('card')
  if (!card) {
    error.value = 'Card element not found.'
    return
  }
  
  try {
    isLoading.value = true
    error.value = ''
    
    // Create a payment method
    const result = await stripe.value.createPaymentMethod({
      type: 'card',
      card,
    })
    
    if (result.error) {
      error.value = result.error.message || 'Failed to process card. Please try again.'
      return
    }
    
    // Ensure user has a Stripe customer on the backend
    await store.setupCustomer()
    
    // Attach the payment method to the customer
    await store.attachPaymentMethod(result.paymentMethod.id)
    
    // Emit event to notify parent component
    emit('cardAdded', result.paymentMethod)
    
  } catch (err: any) {
    console.error('Payment method creation error:', err)
    error.value = err.message || 'Failed to add card. Please try again.'
  } finally {
    isLoading.value = false
  }
}

// Define emit events
const emit = defineEmits<{
  (e: 'cardAdded', paymentMethod: any): void
}>()
</script>

<style scoped>
/* Kept white in both themes: the Stripe element renders dark slate text (#32325d) */
.card-element {
  background-color: white;
  min-height: 40px;
  display: flex;
  align-items: center;
}
</style> 