<template>
  <PaymentLayout>
    <div class="container mx-auto px-4 py-12">
      <div class="max-w-2xl mx-auto">
        <div class="mb-8">
          <router-link 
            to="/payments/dashboard"
            class="inline-flex items-center text-gray-400 hover:text-white transition-colors"
          >
            <span class="mr-2">←</span>
            Back to Dashboard
          </router-link>
        </div>
        
        <div class="bg-dark-800 border border-gray-700 rounded-lg p-8">
          <h1 class="text-2xl font-bold text-white mb-2">Add Credits</h1>
          <p class="text-gray-400 mb-8">Purchase credits to use for AI generation</p>
          
          <div v-if="success" class="bg-green-500/10 border border-green-500/30 rounded-lg p-4 mb-8">
            <h3 class="text-green-400 font-medium mb-1">Payment Successful!</h3>
            <p class="text-gray-300">
              Your payment has been processed and credits have been added to your account.
            </p>
          </div>
          
          <div v-if="store.error" class="bg-red-500/10 border border-red-500/30 rounded-lg p-4 mb-8">
            <h3 class="text-red-400 font-medium mb-1">Payment Failed</h3>
            <p class="text-gray-300">{{ store.error }}</p>
          </div>
          
          <PaymentForm 
            :initialAmount="50"
            @payment-success="onPaymentSuccess" 
          />
          
          <div class="mt-8 text-center text-sm text-gray-500">
            <p>Need help? <a href="#" class="text-primary-400 hover:text-primary-300">Contact Support</a></p>
          </div>
        </div>
      </div>
    </div>
  </PaymentLayout>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import PaymentLayout from '../layouts/PaymentLayout.vue'
import PaymentForm from '../components/organisms/PaymentForm.vue'
import { usePaymentsStore } from '../store'

export default {
  name: 'AddCreditsView',
  components: {
    PaymentLayout,
    PaymentForm
  },
  setup() {
    const store = usePaymentsStore()
    const router = useRouter()
    const success = ref(false)
    
    const onPaymentSuccess = (paymentData) => {
      success.value = true
      
      // Redirect to dashboard after successful payment
      setTimeout(() => {
        router.push('/payments/dashboard')
      }, 3000)
    }
    
    return {
      store,
      success,
      onPaymentSuccess
    }
  }
}
</script> 