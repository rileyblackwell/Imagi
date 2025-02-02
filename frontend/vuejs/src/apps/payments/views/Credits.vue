<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
    <!-- Hero Section -->
    <div class="text-center mb-12">
      <h1 class="text-4xl font-extrabold text-white sm:text-5xl md:text-6xl">
        <span class="block">AI Credits</span>
        <span class="block text-primary-400">Power Your Development</span>
      </h1>
      <p class="mt-3 max-w-md mx-auto text-base text-gray-300 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
        Purchase credits to use our AI services for building your web applications.
      </p>
    </div>

    <!-- Current Balance -->
    <div class="mb-12 bg-dark-800 rounded-lg shadow-xl p-6 border border-dark-700 max-w-xl mx-auto">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-lg font-semibold text-white mb-2">Your Balance</h3>
          <p class="text-3xl font-bold text-primary-400">${{ currentBalance }}</p>
        </div>
        <div class="text-right">
          <p class="text-sm text-gray-400">Last updated</p>
          <p class="text-sm text-gray-300">{{ lastUpdated }}</p>
        </div>
      </div>
    </div>

    <!-- Credit Packages -->
    <div class="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
      <div v-for="pkg in packages" :key="pkg.id" 
           class="bg-dark-800 rounded-lg shadow-xl overflow-hidden border"
           :class="[pkg.popular ? 'border-primary-500/20' : 'border-dark-700']">
        <div class="p-6 relative">
          <!-- Popular Badge -->
          <div v-if="pkg.popular" 
               class="absolute top-0 right-0 -mt-1 -mr-1 px-3 py-1 bg-primary-500 text-white text-xs font-medium rounded-bl">
            Popular
          </div>

          <h3 class="text-lg font-semibold text-white">{{ pkg.name }}</h3>
          <div class="mt-4">
            <p class="text-3xl font-bold text-white">
              ${{ pkg.amount }}
            </p>
            <p class="text-sm text-gray-400">{{ pkg.credits }} credits</p>
          </div>

          <!-- Features -->
          <ul class="mt-6 space-y-4">
            <li v-for="feature in pkg.features" :key="feature" 
                class="flex items-center text-gray-300">
              <i class="fas fa-check text-primary-400 mr-2"></i>
              {{ feature }}
            </li>
          </ul>

          <!-- Purchase Button -->
          <button
            @click="purchaseCredits(pkg.id)"
            :disabled="isLoading"
            class="mt-8 w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="isLoading && selectedPackage === pkg.id" class="mr-2">
              <i class="fas fa-spinner fa-spin"></i>
            </span>
            {{ isLoading && selectedPackage === pkg.id ? 'Processing...' : 'Purchase Now' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="mt-8 text-center">
      <p class="text-red-500">{{ error }}</p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import PaymentService from '../services/payment.service'
import { usePaymentStore } from '../store/payments'

export default {
  name: 'Credits',
  setup() {
    const router = useRouter()
    const paymentStore = usePaymentStore()
    const packages = ref([])
    const currentBalance = ref(0)
    const lastUpdated = ref(new Date().toLocaleString())
    const isLoading = ref(false)
    const error = ref(null)
    const selectedPackage = ref(null)
    const paymentService = new PaymentService()

    async function loadData() {
      try {
        const [packagesData, balanceData] = await Promise.all([
          paymentService.getCreditPackages().catch(() => paymentService.getMockPackages()),
          paymentService.getBalance().catch(() => ({ balance: 0 }))
        ])
        packages.value = packagesData
        currentBalance.value = balanceData.balance
        lastUpdated.value = new Date().toLocaleString()
      } catch (err) {
        error.value = 'Failed to load credit packages. Please try again.'
        console.error('Error loading data:', err)
        // Fallback to mock data if API fails
        packages.value = await paymentService.getMockPackages()
      }
    }

    async function purchaseCredits(packageId) {
      try {
        isLoading.value = true
        selectedPackage.value = packageId
        error.value = null

        // Navigate to checkout with the package ID
        router.push({
          name: 'checkout',
          query: { 
            package: packageId
          }
        })
      } catch (err) {
        error.value = err.message || 'Failed to initiate purchase. Please try again.'
        console.error('Purchase error:', err)
      } finally {
        isLoading.value = false
        selectedPackage.value = null
      }
    }

    onMounted(() => {
      loadData()
    })

    return {
      packages,
      currentBalance,
      lastUpdated,
      isLoading,
      error,
      selectedPackage,
      purchaseCredits
    }
  }
}
</script>

<style scoped>
.credit-package {
  transition: all 0.3s ease;
}

.credit-package:hover {
  transform: translateY(-5px);
}

.popular-badge {
  background: linear-gradient(135deg, #00ffc6, #00a2ff);
}
</style> 