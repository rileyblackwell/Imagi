<!--
  Pricing — on the Spotlight stage.

  A lit opener, then the plans as cards standing in the light (the
  recommended one edged with the same glowing gradient as the home page's
  prompt bar), then how usage is measured. While PAID_PLANS_ENABLED is off,
  the page holds the one open Free plan, centred. Light and dark come from
  shared/styles/spotlight.css; the editorial wrapper keeps the shared button
  and checklist markup, re-lit by its bridge.
-->
<template>
  <PaymentLayout>
    <div class="editorial pricing-page relative min-h-screen">

      <!-- Opener -->
      <section class="sl-opener !pb-[clamp(36px,5vw,56px)]">
        <div class="sl-spot" aria-hidden="true"></div>
        <div class="sl-dots" aria-hidden="true"></div>
        <div class="sl-wrap sl-opener__inner">
          <p class="sl-eyebrow sl-pill pricing-rise">
            <span class="sl-pip" aria-hidden="true"></span>
            <span>Pricing</span>
          </p>
          <h1 class="sl-display sl-h1 pricing-rise !text-[clamp(44px,7.4vw,96px)]">
            {{ PAID_PLANS_ENABLED ? 'Choose your plan' : 'Imagi is free' }}
          </h1>
          <p v-if="PAID_PLANS_ENABLED" class="sl-lede pricing-rise">
            Start free, then upgrade as you grow. Every plan gives you an amount of AI usage
            per week, on a rolling window — no session limits, nothing to top up.
          </p>
          <p v-else class="sl-lede pricing-rise">
            One plan, open to everyone. Build as much as you like, with as many projects as
            you need. No card, nothing to top up.
          </p>

          <!-- Subscribers manage billing (card, invoices, cancelling) in Stripe's portal -->
          <p
            v-if="currentPlanKey"
            class="pricing-rise mt-1 rounded-[999px] border border-sl-line bg-[var(--sl-pill-bg)] px-3.5 py-[7px] text-[14px] text-sl-muted"
          >
            You're on the {{ currentPlanName }} plan.
            <button
              type="button"
              class="ml-1 font-semibold text-sl-text underline decoration-sl-coral underline-offset-[3px] disabled:opacity-60"
              :disabled="portalLoading"
              @click="openPortal"
            >
              {{ portalLoading ? 'Opening…' : 'Manage billing' }}
            </button>
          </p>
        </div>
      </section>

      <div class="sl-wrap pb-[clamp(72px,9vw,120px)]">
        <!-- Confirm a plan switch: it charges or credits the card on file -->
        <div
          v-if="pendingSwitch"
          :class="pricingNote"
          class="border-l-sl-coral"
          role="alertdialog"
          aria-labelledby="switch-title"
        >
          <p id="switch-title" class="m-0 font-sl-display text-[19px] font-bold tracking-[-0.015em] text-sl-text">
            Switch to {{ pendingSwitch.label }} for ${{ pendingSwitch.price }}/month?
          </p>
          <p class="mt-[0.4rem]">
            The change is prorated on your current subscription:
            {{ pendingSwitch.upgrade
              ? 'the difference for the rest of this billing period is charged to your card now'
              : 'the unused part of your current plan is credited toward your next invoices' }},
            and your new weekly allowance applies right away.
          </p>
          <div class="mt-5 flex flex-wrap gap-3">
            <button type="button" class="btn-primary" :disabled="!!loadingTier" @click="confirmSwitch">
              {{ loadingTier ? 'Switching…' : 'Confirm switch' }}
            </button>
            <button type="button" class="btn-outline" :disabled="!!loadingTier" @click="pendingSwitch = null">
              Cancel
            </button>
          </div>
        </div>

        <!-- Success -->
        <p v-if="notice" :class="pricingNote" class="border-l-sl-ok" role="status">
          {{ notice }}
        </p>

        <!-- Error -->
        <p v-if="error" :class="pricingNote" class="border-l-sl-bad" role="alert">
          {{ error }}
        </p>

        <!-- Plans -->
        <!-- One open plan: a single card, centred at a card's width -->
        <div
          class="tiers mt-[clamp(16px,3vw,32px)] grid grid-cols-1 gap-[18px] min-[900px]:items-stretch"
          :class="tiers.length === 1 ? 'mx-auto max-w-[26rem]' : 'min-[900px]:grid-cols-3'"
        >
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
            :flag="tier.flag"
            :current-plan-key="currentPlanKey"
            :loading="isTierLoading(tier)"
            @subscribe="(lookupKey) => handleSubscribe(tier, lookupKey)"
          />
        </div>
        <p
          v-if="PAID_PLANS_ENABLED"
          class="pricing-stripe mt-7 flex items-center justify-center gap-2 text-[13.5px] text-sl-faint"
        >
          <i class="fas fa-lock text-[11px]" aria-hidden="true"></i>
          Payments are processed by Stripe. Secure and encrypted.
        </p>
      </div>

      <!-- How usage is metered -->
      <section class="sl-sec !pt-0">
        <div class="sl-divider" aria-hidden="true"></div>
        <div class="sl-wrap grid gap-5 pt-[clamp(64px,8vw,110px)] min-[900px]:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)] min-[900px]:[align-items:start] min-[900px]:gap-16">
          <div class="flex flex-col gap-4">
            <p class="sl-eyebrow"><span class="sl-grad-text">01</span><span>Usage</span></p>
            <h2 class="sl-display text-[clamp(34px,4.4vw,54px)] leading-[1.02] tracking-[-0.03em]">
              {{ PAID_PLANS_ENABLED ? 'How usage is measured' : 'One safeguard' }}
            </h2>
          </div>
          <p v-if="!PAID_PLANS_ENABLED" class="sl-lede pt-1.5">
            There's no weekly limit. The one check is per run: a single run that reaches
            $10 of AI work stops and asks you before it carries on, so a request that goes
            in circles never runs away. The Usage panel in the builder shows your plan.
          </p>
          <p v-else class="sl-lede pt-1.5">
            Your allowance is spent as you build, priced by the model you pick and how hard
            you ask it to think. Lighter models and lower reasoning effort go further; the
            flagship model at high effort goes fastest. The Usage panel in the builder shows
            how much of the week's allowance you've used at any time.
          </p>
        </div>
      </section>
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

// Notices above the plans: a quiet card with a lit left edge (each notice adds
// its own edge colour).
const pricingNote =
  'mx-auto mb-6 max-w-[44rem] rounded-[14px] border border-l-[3px] border-sl-line bg-sl-card-bg px-5 py-4 text-[15px] leading-[1.6] text-sl-muted shadow-sl-card'

const loadingTier = ref<string | null>(null)
const portalLoading = ref(false)
const error = ref('')
const notice = ref('')

// Paid plans are off for now: Imagi is free and the page shows the one open
// Free plan. Turning this on brings back Pro and Max (and their Stripe
// checkout, still in test mode) as they were; pair it with
// FREE_TIER_UNLIMITED=0 on the server so Free's limits return too.
const PAID_PLANS_ENABLED = false

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
// The project limit and early access mirror the registry's
// max_active_projects (Free holds one) and early_access (both Max tiers).
// The Free plan while it's the only one: no weekly limit, no project limit
// (the server's FREE_TIER_UNLIMITED).
const openFreeTier: Tier = {
  name: 'Free',
  price: 0,
  lookupKey: null,
  cta: 'Start building',
  weeklyLimit: 'Unlimited usage',
  features: [
    'The full AI builder',
    'Unlimited projects',
    'Sell, Market and Operate (beta)',
  ],
  isPopular: true,
  flag: 'Open to everyone',
}

const paidPlanTiers: Tier[] = [
  {
    name: 'Free',
    price: 0,
    lookupKey: null,
    cta: 'Start for free',
    weeklyLimit: '$3 of usage per week',
    features: [
      'Access to the core AI builder',
      '1 project',
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
          'Early access to new features',
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

const tiers: Tier[] = PAID_PLANS_ENABLED ? paidPlanTiers : [openFreeTier]

interface Tier {
  name: string
  cta: string
  isPopular: boolean
  flag?: string
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
/* The opener's staggered rise: keyframes stay in CSS (scoped names are hashed). */
.pricing-rise {
  animation: pricing-rise 0.8s cubic-bezier(0.22, 1, 0.36, 1) both;
}

.pricing-rise:nth-child(2) { animation-delay: 60ms; }
.pricing-rise:nth-child(3) { animation-delay: 120ms; }
.pricing-rise:nth-child(4) { animation-delay: 180ms; }

@keyframes pricing-rise {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: none; }
}

@media (prefers-reduced-motion: reduce) {
  .pricing-rise { animation: none; }
}
</style>
