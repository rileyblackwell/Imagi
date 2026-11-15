<!--
  Pricing — on the Spotlight stage.

  A lit opener, then the one plan, Free, as a card standing in the light (edged
  with the same glowing gradient as the home page's prompt bar), then how
  usage is measured. Imagi sells nothing: the paid plans and their Stripe
  checkout were removed. Light and dark come from shared/styles/spotlight.css;
  the editorial wrapper keeps the shared button and checklist markup, re-lit by
  its bridge.
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
            Imagi is free
          </h1>
          <p class="sl-lede pricing-rise">
            One plan, open to everyone, with as many projects as you need. Every account
            gets $20 of AI usage a week. No card, nothing to top up.
          </p>
        </div>
      </section>

      <div class="sl-wrap pb-[clamp(72px,9vw,120px)]">
        <!-- The one plan: a single card, centred at a card's width -->
        <div class="tiers mx-auto mt-[clamp(16px,3vw,32px)] grid max-w-[26rem] grid-cols-1">
          <SubscriptionTierCard
            :name="freePlan.name"
            :price="0"
            :cta="freePlan.cta"
            :weekly-limit="freePlan.weeklyLimit"
            :features="freePlan.features"
            :is-popular="true"
            :flag="freePlan.flag"
            @start="startBuilding"
          />
        </div>
      </div>

      <!-- How usage is metered -->
      <section class="sl-sec !pt-0">
        <div class="sl-divider" aria-hidden="true"></div>
        <div class="sl-wrap grid gap-5 pt-[clamp(64px,8vw,110px)] min-[900px]:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)] min-[900px]:[align-items:start] min-[900px]:gap-16">
          <div class="flex flex-col gap-4">
            <p class="sl-eyebrow"><span class="sl-grad-text">01</span><span>Usage</span></p>
            <h2 class="sl-display text-[clamp(34px,4.4vw,54px)] leading-[1.02] tracking-[-0.03em]">
              How usage is measured
            </h2>
          </div>
          <p class="sl-lede pt-1.5">
            Your $20 a week is spent as you build, priced by the model you pick and how hard
            you ask it to think, across Claude and OpenAI models alike. It's a rolling 7 days:
            usage frees up as each run turns a week old. Lighter models and lower reasoning
            effort go further. The Usage panel in the builder shows how much of the week
            you've used.
          </p>
        </div>
      </section>
    </div>
  </PaymentLayout>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/shared/stores/auth'
import PaymentLayout from '../layouts/PaymentLayout.vue'
import SubscriptionTierCard from '../components/molecules/cards/SubscriptionTierCard/SubscriptionTierCard.vue'

const router = useRouter()
const authStore = useAuthStore()

// Mirrors the backend's only plan (Payments' services/plans.py): $20 a week of
// metered usage on a rolling window, and no project limit.
const freePlan = {
  name: 'Free',
  cta: 'Start building',
  weeklyLimit: '$20 of usage per week',
  features: [
    'The full AI builder',
    'Unlimited projects',
    'Sell, Market and Operate (beta)',
  ],
  flag: 'Open to everyone',
}

// Nothing to buy: new visitors sign up, signed-in users go into the app.
function startBuilding() {
  router.push(authStore.isAuthenticated ? { path: '/' } : { path: '/auth/register' })
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
