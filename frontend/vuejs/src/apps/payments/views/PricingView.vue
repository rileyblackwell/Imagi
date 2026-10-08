<!--
  Pricing — on the Spotlight stage.

  A lit opener, then the three plans as cards standing in the light (the
  recommended one edged with the same glowing gradient as the home page's
  prompt bar), then how usage is measured. Light and dark come from
  shared/styles/spotlight.css; the editorial wrapper keeps the shared button
  and checklist markup, re-lit by its bridge.
-->
<template>
  <PaymentLayout>
    <div class="editorial pricing-page relative min-h-screen">

      <!-- Opener -->
      <section class="sl-opener pricing-opener">
        <div class="sl-spot" aria-hidden="true"></div>
        <div class="sl-dots" aria-hidden="true"></div>
        <div class="sl-wrap sl-opener__inner">
          <p class="sl-eyebrow sl-pill pricing-rise">
            <span class="sl-pip" aria-hidden="true"></span>
            <span>Pricing</span>
          </p>
          <h1 class="sl-display sl-h1 pricing-title pricing-rise">Choose your plan</h1>
          <p class="sl-lede pricing-rise">
            Start free, then upgrade as you grow. Every plan gives you an amount of AI usage
            per week, on a rolling window — no session limits, nothing to top up.
          </p>

          <!-- Subscribers manage billing (card, invoices, cancelling) in Stripe's portal -->
          <p v-if="currentPlanKey" class="pricing-current pricing-rise">
            You're on the {{ currentPlanName }} plan.
            <button type="button" class="link-inline" :disabled="portalLoading" @click="openPortal">
              {{ portalLoading ? 'Opening…' : 'Manage billing' }}
            </button>
          </p>
        </div>
      </section>

      <div class="sl-wrap pricing-body">
        <!-- Confirm a plan switch: it charges or credits the card on file -->
        <div
          v-if="pendingSwitch"
          class="pricing-note pricing-note--confirm"
          role="alertdialog"
          aria-labelledby="switch-title"
        >
          <p id="switch-title" class="pricing-note__title">
            Switch to {{ pendingSwitch.label }} for ${{ pendingSwitch.price }}/month?
          </p>
          <p class="pricing-note__body">
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
        <p v-if="notice" class="pricing-note pricing-note--ok" role="status">
          {{ notice }}
        </p>

        <!-- Error -->
        <p v-if="error" class="pricing-note pricing-note--error" role="alert">
          {{ error }}
        </p>

        <!-- Plans -->
        <div class="tiers">
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
        <p class="pricing-stripe">
          <i class="fas fa-lock" aria-hidden="true"></i>
          Payments are processed by Stripe. Secure and encrypted.
        </p>
      </div>

      <!-- How usage is metered -->
      <section class="sl-sec pricing-usage">
        <div class="sl-divider" aria-hidden="true"></div>
        <div class="sl-wrap pricing-usage__inner">
          <div class="pricing-usage__head">
            <p class="sl-eyebrow"><span class="sl-grad-text">01</span><span>Usage</span></p>
            <h2 class="sl-display pricing-usage__title">How usage is measured</h2>
          </div>
          <p class="sl-lede pricing-usage__lede">
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
.sl-opener.pricing-opener {
  padding-bottom: clamp(36px, 5vw, 56px);
}

.sl-opener .pricing-title {
  font-size: clamp(44px, 7.4vw, 96px);
}

.pricing-current {
  margin: 4px 0 0;
  padding: 7px 14px;
  border: 1px solid var(--sl-line);
  border-radius: 999px;
  background: var(--sl-pill-bg);
  color: var(--sl-muted);
  font-size: 14px;
}

.link-inline {
  margin-left: 0.25rem;
  color: var(--sl-text);
  font-weight: 600;
  text-decoration: underline;
  text-decoration-color: var(--sl-coral);
  text-underline-offset: 3px;
}

.link-inline:disabled {
  opacity: 0.6;
}

.pricing-body {
  padding-bottom: clamp(72px, 9vw, 120px);
}

/* Notices above the plans: a quiet card with a lit left edge */
.pricing-note {
  max-width: 44rem;
  margin: 0 auto 1.5rem;
  padding: 1rem 1.25rem;
  border: 1px solid var(--sl-line);
  border-left: 3px solid var(--sl-coral);
  border-radius: 14px;
  background: var(--sl-card-bg);
  box-shadow: var(--sl-card-shadow);
  color: var(--sl-muted);
  font-size: 15px;
  line-height: 1.6;
}

.pricing-note--ok {
  border-left-color: var(--sl-ok);
}

.pricing-note--error {
  border-left-color: var(--sl-bad);
}

.pricing-note__title {
  margin: 0;
  color: var(--sl-text);
  font-family: var(--sl-font-display);
  font-size: 19px;
  font-weight: 700;
  letter-spacing: -0.015em;
}

.pricing-note__body {
  margin: 0.4rem 0 0;
}

.tiers {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 18px;
  margin-top: clamp(16px, 3vw, 32px);
}

@media (min-width: 900px) {
  .tiers {
    grid-template-columns: repeat(3, minmax(0, 1fr));
    align-items: stretch;
  }
}

.pricing-stripe {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin: 28px 0 0;
  color: var(--sl-faint);
  font-size: 13.5px;
}

.pricing-stripe i {
  font-size: 11px;
}

.sl-sec.pricing-usage {
  padding-top: 0;
}

.pricing-usage__inner {
  display: grid;
  gap: 20px;
  padding-top: clamp(64px, 8vw, 110px);
}

@media (min-width: 900px) {
  .pricing-usage__inner {
    grid-template-columns: minmax(0, 0.9fr) minmax(0, 1.1fr);
    gap: 64px;
    align-items: start;
  }
}

.pricing-usage__head {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.pricing-usage__title {
  font-size: clamp(34px, 4.4vw, 54px);
  line-height: 1.02;
  letter-spacing: -0.03em;
}

.pricing-usage__lede {
  padding-top: 6px;
}

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
