<template>
  <div class="max-w-3xl mx-auto px-4 py-8">
    <div class="bg-dark-800 rounded-lg shadow-xl overflow-hidden border border-dark-700">
      <div class="p-6">
        <div v-if="isLoading" class="flex justify-center">
          <div class="spinner"></div>
        </div>
        
        <div v-else-if="status === 'complete'" class="text-center">
          <div class="mb-6">
            <i class="fas fa-check-circle text-6xl text-primary-400"></i>
          </div>
          <h2 class="text-2xl font-bold text-white mb-4">Payment Successful!</h2>
          <p class="text-gray-400 mb-6">
            Thank you for your purchase. Your credits have been added to your account.
            <br>
            A confirmation email has been sent to {{ customerEmail }}.
          </p>
          <router-link 
            to="/dashboard" 
            class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            Go to Dashboard
          </router-link>
        </div>

        <div v-else-if="error" class="text-center">
          <div class="mb-6">
            <i class="fas fa-exclamation-circle text-6xl text-red-500"></i>
          </div>
          <h2 class="text-2xl font-bold text-white mb-4">Payment Failed</h2>
          <p class="text-red-400 mb-6">{{ error }}</p>
          <router-link 
            to="/payments/credits" 
            class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            Try Again
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import PaymentService from '../services/payment_service'
import { useToast } from '../composables/useToast'

export default {
  name: 'Return',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const paymentService = new PaymentService()
    const toast = useToast()

    const status = ref(null)
    const customerEmail = ref('')
    const error = ref(null)
    const isLoading = ref(true)

    onMounted(async () => {
      try {
        const sessionId = route.query.session_id
        if (!sessionId) {
          throw new Error('No session ID provided')
        }

        const response = await paymentService.getSessionStatus(sessionId)
        status.value = response.status
        customerEmail.value = response.customer_email

        if (status.value === 'open') {
          router.push('/payments/checkout')
        }
      } catch (err) {
        error.value = err.message
        toast.error(err.message)
        console.error('Return page error:', err)
      } finally {
        isLoading.value = false
      }
    })

    return {
      status,
      customerEmail,
      error,
      isLoading
    }
  }
}
</script>

<style scoped>
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