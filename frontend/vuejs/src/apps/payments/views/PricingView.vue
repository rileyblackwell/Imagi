<template>
  <PaymentLayout>
    <div class="editorial relative min-h-screen font-body">
      <div class="grain-overlay absolute inset-0 z-[1] pointer-events-none" aria-hidden="true"></div>

      <div class="relative z-10 section-shell pt-32 sm:pt-40 md:pt-44 pb-20 md:pb-28">

        <!-- Header -->
        <div class="md:flex md:items-end md:justify-between gap-12 lg:gap-16">
          <div class="max-w-[36rem]">
            <p class="eyebrow">
              <span class="eyebrow__rule" aria-hidden="true"></span>
              <span>Pricing</span>
            </p>
            <h1 class="display mt-7 text-[2.75rem] sm:text-6xl md:text-[3.9rem]">
              Choose your plan
            </h1>
          </div>
          <p class="lede mt-7 md:mt-0 md:max-w-sm md:pb-3 text-lg">
            Start free, then upgrade as you grow. Every plan includes a monthly amount of AI
            usage, delivered through a rolling 5-hour session and a weekly window.
          </p>
        </div>

        <!-- Error -->
        <p v-if="error" class="mt-10 pl-4 text-sm" style="border-left: 2px solid var(--accent); color: var(--ink-70)">
          {{ error }}
        </p>

        <!-- Plans -->
        <div class="tiers mt-14 md:mt-16">
          <SubscriptionTierCard
            v-for="tier in tiers"
            :key="tier.name"
            :name="tier.name"
            :price="tier.price"
            :lookup-key="tier.lookupKey"
            :cta="tier.cta"
            :features="tier.features"
            :session-limit="tier.sessionLimit"
            :weekly-limit="tier.weeklyLimit"
            :options="tier.options"
            :is-popular="tier.isPopular"
            :loading="isTierLoading(tier)"
            @subscribe="(lookupKey) => handleSubscribe(tier, lookupKey)"
          />
        </div>

        <!-- How usage is metered -->
        <div class="mt-20 md:mt-24">
          <div class="section-rule mb-14 md:mb-16" aria-hidden="true"></div>
          <div class="md:flex md:items-start md:justify-between gap-12 lg:gap-16">
            <h2 class="display max-w-md text-3xl sm:text-4xl">
              How usage is measured
            </h2>
            <p class="lede mt-5 md:mt-0 md:max-w-md">
              Your allowance is spent as you build, priced by the model you pick and how hard
              you ask it to think. Lighter models and lower reasoning effort go further; the
              flagship model at high effort goes fastest. The usage meter in the builder shows
              what's left at any time.
            </p>
          </div>

          <p class="mt-12 pt-5 text-sm" style="border-top: 1px solid var(--rule); color: var(--ink-40)">
            Payments are processed by Stripe. Secure and encrypted.
          </p>
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

const router = useRouter()
const authStore = useAuthStore()
const paymentService = new PaymentService()

const loadingTier = ref<string | null>(null)
const error = ref('')

// The monthly figure in `features` is the headline we sell; the sessionLimit
// and weeklyLimit lines are how it is actually delivered, and those two must
// mirror the backend plan registry (Payments' services/plans.py) — the
// backend knows only those windows and is what enforces them. The weekly
// figures are set generously against the monthly headline rather than
// dividing it thinly, so four weeks add up to more than the monthly number.
// `price` is the Stripe subscription price, separate from the allowance.
const tiers: Tier[] = [
  {
    name: 'Free',
    price: 0,
    lookupKey: null,
    cta: 'Start for free',
    sessionLimit: '$5 of usage every 5 hours',
    weeklyLimit: '$25 of usage per week',
    features: [
      'Access to the core AI builder',
      '$50 of AI usage per month',
      '1 active project',
      'Community support',
    ],
    isPopular: false,
  },
  {
    name: 'Pro',
    price: 20,
    lookupKey: 'pro_monthly',
    cta: 'Get started',
    sessionLimit: '$20 of usage every 5 hours',
    weeklyLimit: '$100 of usage per week',
    features: [
      'Everything in Free',
      '$200 of AI usage per month',
      'Unlimited projects',
      'Priority support',
    ],
    isPopular: true,
  },
  {
    name: 'Max',
    cta: 'Get started',
    isPopular: false,
    // A single Max plan with selectable usage options, mirroring Claude's Max
    // tier. "5×"/"20×" are literal multiples of Pro's allowance.
    options: [
      {
        label: '5× usage',
        price: 100,
        lookupKey: 'max_5x_monthly',
        sessionLimit: '$100 of usage every 5 hours',
        weeklyLimit: '$500 of usage per week',
        features: [
          'Everything in Pro',
          '$1,000 of AI usage per month',
          '5× more usage than Pro',
          'Early access to new features',
        ],
      },
      {
        label: '20× usage',
        price: 200,
        lookupKey: 'max_20x_monthly',
        sessionLimit: '$400 of usage every 5 hours',
        weeklyLimit: '$2,000 of usage per week',
        features: [
          'Everything in Pro',
          '$4,000 of AI usage per month',
          '20× more usage than Pro',
          'Priority access at peak times',
        ],
      },
    ],
  },
]

interface TierOption {
  label: string
  price: number
  lookupKey: string
  sessionLimit: string
  weeklyLimit: string
  features: string[]
}

interface Tier {
  name: string
  cta: string
  isPopular: boolean
  // Single-option tiers set these directly; multi-option tiers use `options` instead.
  price?: number
  lookupKey?: string | null
  sessionLimit?: string
  weeklyLimit?: string
  features?: string[]
  options?: TierOption[]
}

// A Max-style tier is "loading" while any of its options is checking out.
const isTierLoading = (tier: Tier) => {
  if (tier.options) return tier.options.some((o) => o.lookupKey === loadingTier.value)
  return loadingTier.value === (tier.lookupKey ?? tier.name)
}

const handleSubscribe = async (tier: Tier, lookupKey: string | null) => {
  error.value = ''

  // Free plan has no checkout — send new users to sign up, existing users into the app.
  if (!lookupKey) {
    router.push(authStore.isAuthenticated ? { path: '/' } : { path: '/auth/register' })
    return
  }

  // Check authentication
  if (!authStore.isAuthenticated) {
    router.push({ path: '/auth/signin', query: { redirect: '/payments/pricing' } })
    return
  }

  try {
    loadingTier.value = lookupKey

    const response = await paymentService.createCheckoutSession({
      lookup_key: lookupKey,
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
</script>

<style scoped>
.tiers {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2.5rem;
}

@media (min-width: 768px) {
  .tiers {
    grid-template-columns: repeat(3, 1fr);
    gap: 0;
    align-items: stretch;
  }
}
</style>
