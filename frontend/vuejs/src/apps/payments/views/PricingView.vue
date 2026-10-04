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
            Start free, then upgrade as you grow. Every plan gives you an amount of AI usage
            per week, on a rolling window — no session limits, nothing to top up.
          </p>
        </div>

        <!-- Subscribers manage billing (card, invoices, cancelling) in Stripe's portal -->
        <p v-if="currentPlanKey" class="mt-10 text-sm" style="color: var(--ink-55)">
          You're on the {{ currentPlanName }} plan.
          <button type="button" class="link-inline" :disabled="portalLoading" @click="openPortal">
            {{ portalLoading ? 'Opening…' : 'Manage billing' }}
          </button>
        </p>

        <!-- Confirm a plan switch: it charges or credits the card on file -->
        <div
          v-if="pendingSwitch"
          class="mt-10 pl-4"
          style="border-left: 2px solid var(--accent)"
          role="alertdialog"
          aria-labelledby="switch-title"
        >
          <p id="switch-title" class="text-base font-medium" style="color: var(--ink)">
            Switch to {{ pendingSwitch.label }} for ${{ pendingSwitch.price }}/month?
          </p>
          <p class="mt-1 text-sm" style="color: var(--ink-70)">
            The change is prorated on your current subscription:
            {{ pendingSwitch.upgrade
              ? 'the difference for the rest of this billing period is charged to your card now'
              : 'the unused part of your current plan is credited toward your next invoices' }},
            and your new weekly allowance applies right away.
          </p>
          <div class="mt-4 flex gap-3">
            <button type="button" class="btn-primary" :disabled="!!loadingTier" @click="confirmSwitch">
              {{ loadingTier ? 'Switching…' : 'Confirm switch' }}
            </button>
            <button type="button" class="btn-outline" :disabled="!!loadingTier" @click="pendingSwitch = null">
              Cancel
            </button>
          </div>
        </div>

        <!-- Success -->
        <p v-if="notice" class="mt-10 pl-4 text-sm" role="status" style="border-left: 2px solid var(--accent); color: var(--ink-70)">
          {{ notice }}
        </p>

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
            :weekly-limit="tier.weeklyLimit"
            :options="tier.options"
            :is-popular="tier.isPopular"
            :current-plan-key="currentPlanKey"
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
              flagship model at high effort goes fastest. The Usage panel in the builder shows
              how much of the week's allowance you've used at any time.
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
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/shared/stores/auth'
import { useUsageStore } from '@/shared/stores/usage'
import PaymentLayout from '../layouts/PaymentLayout.vue'
import PaymentService from '../services/payment_service'
import SubscriptionTierCard from '../components/molecules/cards/SubscriptionTierCard/SubscriptionTierCard.vue'

const router = useRouter()
const authStore = useAuthStore()
const paymentService = new PaymentService()

const usageStore = useUsageStore()

const loadingTier = ref<string | null>(null)
const portalLoading = ref(false)
const error = ref('')
const notice = ref('')

// The Stripe lookup key of each paid plan, keyed by the backend plan id
// (services/plans.py LOOKUP_KEY_TO_PLAN, inverted). Free has no price.
const PLAN_LOOKUP_KEYS: Record<string, string | null> = {
  free: null,
  pro: 'pro_monthly',
  max_5x: 'max_5x_monthly',
  max_10x: 'max_10x_monthly',
}

// The signed-in user's plan as a lookup key: null = Free, undefined = not
// known (signed out, not loaded, or a plan this page doesn't list). A
// subscriber must switch plans rather than check out again — a second
// checkout would start a second subscription and bill them twice.
const currentPlanKey = computed<string | null | undefined>(() => {
  const id = usageStore.plan?.id
  if (!authStore.isAuthenticated || !id) return undefined
  return id in PLAN_LOOKUP_KEYS ? PLAN_LOOKUP_KEYS[id] : undefined
})
const currentPlanName = computed(() => usageStore.plan?.name ?? '')

onMounted(() => {
  if (authStore.isAuthenticated) void usageStore.fetchUsage()
})

interface PendingSwitch {
  lookupKey: string
  label: string
  price: number
  upgrade: boolean
}
const pendingSwitch = ref<PendingSwitch | null>(null)

// weeklyLimit is the one allowance figure we publish, and it must mirror the
// backend plan registry (Payments' services/plans.py) — that weekly window is
// the only thing the meter enforces. Deliberately no monthly usage number in
// `features`: nothing enforces one, and carrying a second figure was the
// confusion that removing the 5-hour session window was meant to end.
// `price` is the Stripe subscription price, separate from the allowance.
const tiers: Tier[] = [
  {
    name: 'Free',
    price: 0,
    lookupKey: null,
    cta: 'Start for free',
    weeklyLimit: '$3 of usage per week',
    features: [
      'Access to the core AI builder',
      '1 active project',
      'Community support',
    ],
    isPopular: false,
  },
  {
    name: 'Pro',
    price: 25,
    lookupKey: 'pro_monthly',
    cta: 'Get started',
    weeklyLimit: '$10 of usage per week',
    features: [
      'Everything in Free',
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
    // tier. "5×"/"10×" are literal multiples of Pro's weekly allowance.
    options: [
      {
        label: '5× usage',
        price: 100,
        lookupKey: 'max_5x_monthly',
        weeklyLimit: '$50 of usage per week',
        features: [
          'Everything in Pro',
          '5× more usage than Pro',
          'Early access to new features',
        ],
      },
      {
        label: '10× usage',
        price: 200,
        lookupKey: 'max_10x_monthly',
        weeklyLimit: '$100 of usage per week',
        features: [
          'Everything in Pro',
          '10× more usage than Pro',
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
  weeklyLimit?: string
  features?: string[]
  options?: TierOption[]
}

// A Max-style tier is "loading" while any of its options is checking out.
const isTierLoading = (tier: Tier) => {
  if (tier.options) return tier.options.some((o) => o.lookupKey === loadingTier.value)
  return loadingTier.value === (tier.lookupKey ?? tier.name)
}

/** A paid plan's display name and monthly price, by lookup key. */
function describePlan(lookupKey: string): { label: string; price: number } | null {
  for (const tier of tiers) {
    if (tier.lookupKey === lookupKey) return { label: tier.name, price: tier.price ?? 0 }
    const option = tier.options?.find(o => o.lookupKey === lookupKey)
    if (option) return { label: `${tier.name} (${option.label})`, price: option.price }
  }
  return null
}

async function openPortal() {
  error.value = ''
  portalLoading.value = true
  try {
    const { url } = await paymentService.createPortalSession(window.location.href)
    window.location.href = url
  } catch (err: any) {
    error.value = err.message || 'Could not open the billing portal. Please try again.'
  } finally {
    portalLoading.value = false
  }
}

async function confirmSwitch() {
  const target = pendingSwitch.value
  if (!target) return
  error.value = ''
  loadingTier.value = target.lookupKey
  try {
    await paymentService.changePlan(target.lookupKey)
    pendingSwitch.value = null
    notice.value = `You're now on ${target.label}. Your new weekly allowance applies right away.`
  } catch (err: any) {
    error.value = err.message || 'Could not change your plan. Please try again.'
  } finally {
    loadingTier.value = null
    // Whatever happened, show the plan Stripe actually has.
    void usageStore.fetchUsage()
  }
}

const handleSubscribe = async (tier: Tier, lookupKey: string | null) => {
  error.value = ''
  notice.value = ''

  // A subscriber changes the subscription they have: Free means cancelling
  // (the billing portal), another paid plan is a prorated switch.
  if (currentPlanKey.value) {
    if (!lookupKey) {
      await openPortal()
      return
    }
    const plan = describePlan(lookupKey)
    const current = describePlan(currentPlanKey.value)
    if (!plan) return
    pendingSwitch.value = {
      lookupKey,
      ...plan,
      upgrade: !current || plan.price > current.price,
    }
    return
  }

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
    // Refused because they already subscribe (e.g. from another tab): load
    // their plan so the buttons turn into plan switches.
    void usageStore.fetchUsage()
  } finally {
    loadingTier.value = null
  }
}
</script>

<style scoped>
.link-inline {
  margin-left: 0.25rem;
  color: var(--accent);
  font-weight: 500;
  text-decoration: underline;
  text-underline-offset: 3px;
}

.link-inline:disabled {
  opacity: 0.6;
}

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
