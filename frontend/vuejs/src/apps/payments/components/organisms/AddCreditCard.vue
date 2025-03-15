<template>
  <div class="add-card-form">
    <div v-if="error" class="error-message bg-red-50 text-red-600 p-3 rounded mb-4">
      {{ error }}
    </div>
    
    <div class="mb-4">
      <div ref="cardElement" class="card-element p-3 border rounded"></div>
      <div v-if="cardError" class="text-red-500 text-sm mt-1">{{ cardError }}</div>
    </div>
    
    <button 
      @click="handleSubmit" 
      :disabled="isLoading || !stripe" 
      class="w-full py-2 px-4 rounded bg-indigo-600 text-white font-medium hover:bg-indigo-700 disabled:opacity-50"
    >
      <span v-if="isLoading">
        <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
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
import { usePaymentStore } from '../../stores/payments'

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
.card-element {
  background-color: white;
  min-height: 40px;
  display: flex;
  align-items: center;
}
</style> 