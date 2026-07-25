<template>
  <PaymentLayout>
    <div class="pricing-view relative min-h-screen overflow-hidden transition-colors duration-500">
      <!-- Atmosphere: soft apricot + baby-blue washes over the porcelain canvas -->
      <div class="absolute inset-0 pointer-events-none" aria-hidden="true">
        <div class="pricing-glow-warm absolute -top-32 left-1/2 -translate-x-1/2 w-[860px] h-[520px]"></div>
        <div class="pricing-glow-cool absolute top-64 -left-48 w-[640px] h-[480px]"></div>
      </div>

      <!-- Content Container -->
      <div class="relative z-10 max-w-6xl mx-auto px-6 sm:px-8 lg:px-12 pt-24 pb-24 md:pt-32 md:pb-32">
        <!-- Header Section -->
        <div class="mb-16 md:mb-20 text-center">
          <!-- Editorial kicker: tracked small caps flanked by fading hairline rules -->
          <div class="pricing-rise flex items-center justify-center gap-4 mb-8" style="animation-delay: 0ms">
            <span aria-hidden="true" class="hidden sm:block h-px w-12 md:w-16 bg-gradient-to-l from-blue-950/25 to-transparent dark:from-white/25"></span>
            <span class="flex items-center gap-3">
              <span aria-hidden="true" class="w-1 h-1 rotate-45 bg-orange-500/80 dark:bg-orange-400/80"></span>
              <span class="text-[10px] sm:text-[11px] font-semibold uppercase tracking-[0.25em] sm:tracking-[0.3em] leading-none text-blue-950/70 dark:text-blue-100/55 whitespace-nowrap">Pricing</span>
              <span aria-hidden="true" class="w-1 h-1 rotate-45 bg-orange-500/80 dark:bg-orange-400/80"></span>
            </span>
            <span aria-hidden="true" class="hidden sm:block h-px w-12 md:w-16 bg-gradient-to-r from-blue-950/25 to-transparent dark:from-white/25"></span>
          </div>
          <h1 class="pricing-rise font-display font-semibold text-4xl sm:text-5xl md:text-6xl mb-6 tracking-[-0.02em] leading-[1.05] text-balance text-blue-950 dark:text-white transition-colors duration-300" style="animation-delay: 90ms">
            Choose your <em class="pricing-accent not-italic">plan</em>
          </h1>
          <p class="pricing-rise text-xl text-blue-950/65 dark:text-blue-100/65 leading-relaxed text-pretty max-w-3xl mx-auto transition-colors duration-300" style="animation-delay: 180ms">
            Start free, then upgrade as you grow. Every plan includes a monthly amount of AI usage, metered as you build and delivered through a rolling 5-hour session and weekly window.
          </p>
        </div>

        <!-- Error Message -->
        <div v-if="error" class="mb-8 max-w-2xl mx-auto">
          <div class="rounded-2xl bg-red-50/80 dark:bg-red-500/10 border border-red-200/70 dark:border-red-400/25 p-4 transition-colors duration-300">
            <div class="flex items-center gap-3">
              <svg class="w-5 h-5 text-red-500 dark:text-red-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
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
        <div class="mb-16">
          <!-- Hairline divider -->
          <div class="section-divider mb-12 md:mb-16" aria-hidden="true"></div>
          <div class="text-center mb-8 max-w-2xl mx-auto">
            <h2 class="font-display text-2xl sm:text-3xl font-semibold text-blue-950 dark:text-white tracking-[-0.015em] leading-[1.08] mb-2 transition-colors duration-300">
              How usage is measured
            </h2>
            <p class="text-blue-950/65 dark:text-blue-100/65 leading-relaxed transition-colors duration-300">
              Your allowance is spent as you build, priced by the model you pick and how
              hard you ask it to think. Lighter models and lower reasoning effort go
              further; the flagship model at high effort goes fastest. You can watch
              what's left at any time from the usage meter in the builder.
            </p>
          </div>
        </div>

        <!-- Secure Payment Badge -->
        <div class="text-center">
          <div class="inline-flex items-center gap-3 py-3 px-6 bg-white/85 dark:bg-white/[0.07] backdrop-blur-sm rounded-full border border-blue-950/[0.08] dark:border-white/[0.14] transition-colors duration-300">
            <div class="w-8 h-8 rounded-full bg-orange-100 dark:bg-orange-400/[0.16] ring-1 ring-orange-200/80 dark:ring-orange-400/30 flex items-center justify-center">
              <i class="fas fa-lock text-xs text-orange-600 dark:text-orange-300"></i>
            </div>
            <span class="text-blue-950/70 dark:text-blue-100/55 text-sm">Powered by Stripe. Secure and encrypted.</span>
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
    sessionLimit: '$0.50 of usage every 5 hours',
    weeklyLimit: '$2.50 of usage per week',
    features: [
      'Access to the core AI builder',
      '$5 of AI usage per month',
      '1 active project',
      'Community support',
    ],
    isPopular: false,
  },
  {
    name: 'Pro',
    price: 20,
    lookupKey: 'pro_monthly',
    cta: 'Get Started',
    sessionLimit: '$2 of usage every 5 hours',
    weeklyLimit: '$10 of usage per week',
    features: [
      'Everything in Free',
      '$20 of AI usage per month',
      'Unlimited projects',
      'Priority support',
    ],
    isPopular: true,
  },
  {
    name: 'Max',
    cta: 'Get Started',
    isPopular: false,
    // A single Max plan with selectable usage options, mirroring Claude's Max
    // tier. "5×"/"20×" are literal multiples of Pro's allowance.
    options: [
      {
        label: '5× usage',
        price: 100,
        lookupKey: 'max_5x_monthly',
        sessionLimit: '$10 of usage every 5 hours',
        weeklyLimit: '$50 of usage per week',
        features: [
          'Everything in Pro',
          '$100 of AI usage per month',
          '5× more usage than Pro',
          'Early access to new features',
        ],
      },
      {
        label: '20× usage',
        price: 200,
        lookupKey: 'max_20x_monthly',
        sessionLimit: '$40 of usage every 5 hours',
        weeklyLimit: '$200 of usage per week',
        features: [
          'Everything in Pro',
          '$400 of AI usage per month',
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
/* Staggered entrance: header items rise in sequence on page load */
.pricing-rise {
  animation: pricing-rise 0.9s cubic-bezier(0.22, 1, 0.36, 1) both;
}

@keyframes pricing-rise {
  from {
    opacity: 0;
    transform: translateY(22px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (prefers-reduced-motion: reduce) {
  .pricing-rise {
    animation: none;
  }
}

/* Atmosphere washes */
.pricing-glow-warm {
  background: radial-gradient(closest-side, rgba(251, 146, 60, 0.16), rgba(251, 146, 60, 0.05) 55%, transparent 75%);
  filter: blur(40px);
}

.pricing-glow-cool {
  background: radial-gradient(closest-side, rgba(158, 205, 243, 0.28), rgba(158, 205, 243, 0.08) 55%, transparent 75%);
  filter: blur(44px);
}

.dark .pricing-glow-warm {
  background: radial-gradient(closest-side, rgba(251, 146, 60, 0.09), rgba(251, 146, 60, 0.025) 55%, transparent 75%);
}

.dark .pricing-glow-cool {
  background: radial-gradient(closest-side, rgba(96, 165, 250, 0.11), rgba(96, 165, 250, 0.03) 55%, transparent 75%);
}

/* Italic serif accent with the warm gradient ink */
.pricing-accent {
  font-style: italic;
  font-variation-settings: 'SOFT' 30, 'WONK' 1;
  background: linear-gradient(115deg, #c2410c 5%, #ea580c 55%, #b45309 95%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent;
  padding-right: 0.06em;
}

.dark .pricing-accent {
  background: linear-gradient(115deg, #fb923c 5%, #fcd34d 60%, #f59e0b 95%);
  -webkit-background-clip: text;
  background-clip: text;
}

/* Hairline gradient divider that fades at the edges */
.section-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(23, 37, 84, 0.12), transparent);
}

.dark .section-divider {
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
}
</style>
