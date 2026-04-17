<template>
  <PaymentLayout>
    <div class="pricing-view min-h-screen bg-white dark:bg-[#0a0a0a] relative overflow-hidden transition-colors duration-500">
      <!-- Minimal Background Effects -->
      <div class="fixed inset-0 pointer-events-none -z-10">
        <div class="absolute inset-0 bg-gradient-to-b from-gray-50/50 via-white to-white dark:from-[#0a0a0a] dark:via-[#0a0a0a] dark:to-[#0a0a0a] transition-colors duration-500"></div>
        <div class="absolute inset-0 opacity-[0.015] dark:opacity-[0.02]"
             style="background-image: linear-gradient(rgba(128,128,128,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(128,128,128,0.1) 1px, transparent 1px); background-size: 64px 64px;"></div>
        <div class="absolute top-1/2 left-1/2 w-[800px] h-[400px] bg-gradient-radial from-gray-200/30 dark:from-white/[0.02] via-transparent to-transparent rounded-full blur-3xl transform -translate-x-1/2 -translate-y-1/2"></div>
      </div>

      <!-- Content Container -->
      <div class="relative z-10 max-w-6xl mx-auto px-6 sm:px-8 lg:px-12 pt-24 pb-24 md:pt-32 md:pb-32">
        <!-- Header Section -->
        <div class="mb-16 md:mb-20 text-center">
          <p class="text-sm font-medium text-gray-500 dark:text-white/50 uppercase tracking-widest mb-4 transition-colors duration-300">
            Pricing
          </p>
          <h1 class="text-4xl sm:text-5xl md:text-6xl font-semibold text-gray-900 dark:text-white mb-6 tracking-tight transition-colors duration-300">
            Choose your plan
          </h1>
          <p class="text-xl text-gray-500 dark:text-white/60 max-w-3xl mx-auto transition-colors duration-300">
            Simple, transparent pricing for every team. Start building today with the plan that fits your needs.
          </p>
        </div>

        <!-- Error Message -->
        <div v-if="error" class="mb-8 max-w-2xl mx-auto">
          <div class="rounded-2xl bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800/30 p-4 transition-colors duration-300">
            <div class="flex items-center gap-3">
              <svg class="w-5 h-5 text-red-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
              </svg>
              <p class="text-sm text-red-700 dark:text-red-300">{{ error }}</p>
            </div>
          </div>
        </div>

        <!-- Subscription Tier Cards -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8 mb-16 md:mb-20">
          <SubscriptionTierCard
            v-for="tier in tiers"
            :key="tier.lookupKey"
            :name="tier.name"
            :price="tier.price"
            :features="tier.features"
            :deployments="tier.deployments"
            :api-usage="tier.apiUsage"
            :is-popular="tier.isPopular"
            :loading="loadingTier === tier.lookupKey"
            @subscribe="handleSubscribe(tier)"
          />
        </div>

        <!-- On-Demand Section -->
        <div class="mb-16">
          <div class="text-center mb-8">
            <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-2 transition-colors duration-300">
              Need extra usage?
            </h2>
            <p class="text-gray-500 dark:text-white/60 transition-colors duration-300">
              Purchase additional credits on demand, anytime.
            </p>
          </div>
          <div class="max-w-3xl mx-auto">
            <OnDemandCard
              :loading="loadingOnDemand"
              @purchase="handleOnDemandPurchase"
            />
          </div>
        </div>

        <!-- Secure Payment Badge -->
        <div class="text-center">
          <div class="inline-flex items-center gap-3 py-3 px-6 bg-white/50 dark:bg-white/[0.03] backdrop-blur-sm rounded-full border border-gray-200/50 dark:border-white/[0.06] transition-colors duration-300">
            <div class="w-8 h-8 rounded-full bg-gray-100 dark:bg-white/[0.05] flex items-center justify-center">
              <i class="fas fa-lock text-gray-600 dark:text-gray-400"></i>
            </div>
            <span class="text-gray-600 dark:text-gray-400 text-sm">Powered by Stripe. Secure and encrypted.</span>
          </div>
        </div>
      </div>
    </div>
  </PaymentLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/shared/stores/auth'
import PaymentLayout from '../layouts/PaymentLayout.vue'
import PaymentService from '../services/payment_service'
import SubscriptionTierCard from '../components/molecules/cards/SubscriptionTierCard/SubscriptionTierCard.vue'
import OnDemandCard from '../components/molecules/cards/OnDemandCard/OnDemandCard.vue'

const router = useRouter()
const authStore = useAuthStore()
const paymentService = new PaymentService()

const loadingTier = ref<string | null>(null)
const loadingOnDemand = ref(false)
const error = ref('')

const tiers = [
  {
    name: 'Hobby',
    price: 10,
    lookupKey: 'hobby_monthly',
    deployments: '1 project deployment',
    apiUsage: '$10 of API usage per month',
    features: [
      '1 project deployment',
      '$10 API usage/month',
      'Community support',
      'Basic analytics',
    ],
    isPopular: false,
  },
  {
    name: 'Pro',
    price: 50,
    lookupKey: 'pro_monthly',
    deployments: '5 project deployments',
    apiUsage: '$50 of API usage per month',
    features: [
      '5 project deployments',
      '$50 API usage/month',
      'Priority support',
      'Advanced analytics',
    ],
    isPopular: true,
  },
  {
    name: 'Max',
    price: 100,
    lookupKey: 'max_monthly',
    deployments: 'Unlimited project deployments',
    apiUsage: '$100 of API usage per month',
    features: [
      'Unlimited deployments',
      '$100 API usage/month',
      'Dedicated support',
      'Full analytics suite',
    ],
    isPopular: false,
  },
]

interface Tier {
  name: string
  price: number
  lookupKey: string
  deployments: string
  apiUsage: string
  features: string[]
  isPopular: boolean
}

const handleSubscribe = async (tier: Tier) => {
  error.value = ''

  // Check authentication
  if (!authStore.isAuthenticated) {
    router.push({ path: '/auth/signin', query: { redirect: '/payments/pricing' } })
    return
  }

  try {
    loadingTier.value = tier.lookupKey

    const response = await paymentService.createCheckoutSession({
      lookup_key: tier.lookupKey,
      success_url: window.location.origin + '/payments/success',
      cancel_url: window.location.origin + '/payments/cancel',
    })

    if (response.checkout_url) {
      window.location.href = response.checkout_url
    }
  } catch (err: any) {
    error.value = err.message || 'Failed to create checkout session. Please try again.'
  } finally {
    loadingTier.value = null
  }
}

const handleOnDemandPurchase = async (amount: number) => {
  error.value = ''

  if (!authStore.isAuthenticated) {
    router.push({ path: '/auth/signin', query: { redirect: '/payments/pricing' } })
    return
  }

  try {
    loadingOnDemand.value = true

    const response = await paymentService.createCheckoutSession({
      amount,
      success_url: window.location.origin + '/payments/success',
      cancel_url: window.location.origin + '/payments/cancel',
    })

    if (response.checkout_url) {
      window.location.href = response.checkout_url
    }
  } catch (err: any) {
    error.value = err.message || 'Failed to create checkout session. Please try again.'
  } finally {
    loadingOnDemand.value = false
  }
}
</script>

<style scoped>
/* Minimal, clean styling matching home page */
</style>
