<template>
  <base-layout>
    <template #hero>
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center">
          <h1 class="text-4xl font-extrabold text-white sm:text-5xl md:text-6xl">
            <span class="block">AI Credits</span>
            <span class="block text-primary-400">Power Your Development</span>
          </h1>
          <p class="mt-3 max-w-md mx-auto text-base text-gray-300 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
            Purchase credits to use our AI services for building your web applications.
          </p>
        </div>
      </div>
    </template>

    <template #default>
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <!-- Credit Packages -->
        <div class="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
          <!-- Starter Package -->
          <div class="bg-dark-800 rounded-lg shadow-xl overflow-hidden border border-dark-700 hover:border-primary-500/20 transition-all duration-300">
            <div class="p-6">
              <h3 class="text-lg font-semibold text-white">Starter Package</h3>
              <div class="mt-4">
                <p class="text-3xl font-bold text-white">
                  $10
                </p>
                <p class="text-sm text-gray-400">100 credits</p>
              </div>
              <ul class="mt-6 space-y-4">
                <li class="flex items-center text-gray-300">
                  <i class="fas fa-check text-primary-400 mr-2"></i>
                  Build simple web applications
                </li>
                <li class="flex items-center text-gray-300">
                  <i class="fas fa-check text-primary-400 mr-2"></i>
                  Basic AI assistance
                </li>
                <li class="flex items-center text-gray-300">
                  <i class="fas fa-check text-primary-400 mr-2"></i>
                  30-day validity
                </li>
              </ul>
              <button
                @click="purchaseCredits('starter')"
                class="mt-8 w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                Purchase Now
              </button>
            </div>
          </div>

          <!-- Pro Package -->
          <div class="bg-dark-800 rounded-lg shadow-xl overflow-hidden border border-primary-500/20 hover:border-primary-500/40 transition-all duration-300">
            <div class="p-6">
              <div class="absolute top-0 right-0 -mt-1 -mr-1 px-3 py-1 bg-primary-500 text-white text-xs font-medium rounded-bl">
                Popular
              </div>
              <h3 class="text-lg font-semibold text-white">Pro Package</h3>
              <div class="mt-4">
                <p class="text-3xl font-bold text-white">
                  $25
                </p>
                <p class="text-sm text-gray-400">300 credits</p>
              </div>
              <ul class="mt-6 space-y-4">
                <li class="flex items-center text-gray-300">
                  <i class="fas fa-check text-primary-400 mr-2"></i>
                  Build complex applications
                </li>
                <li class="flex items-center text-gray-300">
                  <i class="fas fa-check text-primary-400 mr-2"></i>
                  Advanced AI features
                </li>
                <li class="flex items-center text-gray-300">
                  <i class="fas fa-check text-primary-400 mr-2"></i>
                  60-day validity
                </li>
                <li class="flex items-center text-gray-300">
                  <i class="fas fa-check text-primary-400 mr-2"></i>
                  Priority support
                </li>
              </ul>
              <button
                @click="purchaseCredits('pro')"
                class="mt-8 w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                Purchase Now
              </button>
            </div>
          </div>

          <!-- Enterprise Package -->
          <div class="bg-dark-800 rounded-lg shadow-xl overflow-hidden border border-dark-700 hover:border-primary-500/20 transition-all duration-300">
            <div class="p-6">
              <h3 class="text-lg font-semibold text-white">Enterprise Package</h3>
              <div class="mt-4">
                <p class="text-3xl font-bold text-white">
                  $50
                </p>
                <p class="text-sm text-gray-400">1000 credits</p>
              </div>
              <ul class="mt-6 space-y-4">
                <li class="flex items-center text-gray-300">
                  <i class="fas fa-check text-primary-400 mr-2"></i>
                  Unlimited application complexity
                </li>
                <li class="flex items-center text-gray-300">
                  <i class="fas fa-check text-primary-400 mr-2"></i>
                  Premium AI features
                </li>
                <li class="flex items-center text-gray-300">
                  <i class="fas fa-check text-primary-400 mr-2"></i>
                  90-day validity
                </li>
                <li class="flex items-center text-gray-300">
                  <i class="fas fa-check text-primary-400 mr-2"></i>
                  24/7 priority support
                </li>
                <li class="flex items-center text-gray-300">
                  <i class="fas fa-check text-primary-400 mr-2"></i>
                  Custom solutions
                </li>
              </ul>
              <button
                @click="purchaseCredits('enterprise')"
                class="mt-8 w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                Purchase Now
              </button>
            </div>
          </div>
        </div>

        <!-- Current Credits -->
        <div class="mt-12 bg-dark-800 rounded-lg shadow-xl p-6 border border-dark-700">
          <h3 class="text-lg font-semibold text-white mb-4">Your Credits</h3>
          <div class="flex items-center justify-between">
            <div>
              <p class="text-3xl font-bold text-white">{{ credits }}</p>
              <p class="text-sm text-gray-400">Available credits</p>
            </div>
            <div class="text-right">
              <p class="text-sm text-gray-300">Last purchase: {{ lastPurchaseDate }}</p>
              <p class="text-sm text-gray-400">Valid until: {{ validUntil }}</p>
            </div>
          </div>
        </div>
      </div>
    </template>
  </base-layout>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import BaseLayout from '@/shared/layouts/BaseLayout.vue'
import PaymentService from '../services/payment.service'

export default {
  name: 'Credits',
  components: {
    BaseLayout
  },
  setup() {
    const router = useRouter()
    const credits = ref(0)
    const lastPurchaseDate = ref('Never')
    const validUntil = ref('N/A')
    const isLoading = ref(false)
    const error = ref(null)

    async function purchaseCredits(package_type) {
      try {
        isLoading.value = true
        error.value = null
        
        // Create payment intent for the selected package
        const { clientSecret } = await PaymentService.createPaymentIntent({
          package_type,
          return_url: `${window.location.origin}/payments/success`
        })

        // Redirect to checkout with the client secret
        router.push({
          name: 'checkout',
          query: { 
            package: package_type,
            client_secret: clientSecret
          }
        })
      } catch (err) {
        console.error('Failed to purchase credits:', err)
        error.value = err.message || 'Failed to purchase credits. Please try again.'
      } finally {
        isLoading.value = false
      }
    }

    async function fetchUserCredits() {
      try {
        const { balance, last_purchase, valid_until } = await PaymentService.getBalance()
        credits.value = balance
        lastPurchaseDate.value = last_purchase || 'Never'
        validUntil.value = valid_until || 'N/A'
      } catch (err) {
        console.error('Failed to fetch user credits:', err)
      }
    }

    onMounted(() => {
      fetchUserCredits()
    })

    return {
      credits,
      lastPurchaseDate,
      validUntil,
      purchaseCredits,
      isLoading,
      error
    }
  }
}
</script> 