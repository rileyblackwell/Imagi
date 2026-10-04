<!--
  Hero — prompt first.

  The call to action is the product's own first step: a box to describe the
  business. While the visitor hasn't touched it, the placeholder types out an
  example and the row underneath shows what Imagi produces from that one
  description — the web app, plus the Sell, Market and Operate pieces that come
  with it. As soon as the visitor focuses or types, the demo stops and stays
  out of the way.

  No screenshot here on purpose: the real product shots sit lower on the page,
  next to the sections that explain them.
-->
<template>
  <section class="hero relative pt-28 sm:pt-32 md:pt-36 pb-20 md:pb-28">
    <div class="section-shell">

      <!-- Header: the section pattern, one size up -->
      <div class="md:flex md:items-end md:justify-between gap-12 lg:gap-16">
        <div class="hero-item max-w-[38rem]" style="animation-delay: 0ms">
          <p class="eyebrow">
            <span class="eyebrow__rule" aria-hidden="true"></span>
            <span>The all-in-one business platform</span>
          </p>

          <h1 class="display mt-7 text-[2.9rem] sm:text-[4rem] md:text-[4.6rem] hero-title">
            Build and <em class="hero-accent">run</em> your business
          </h1>
        </div>

        <p class="hero-item lede mt-7 md:mt-0 md:max-w-sm md:pb-4 text-lg" style="animation-delay: 90ms">
          Describe the business you want. Imagi's agent writes the web app, shows it
          running next to the conversation, and puts it online &mdash; then hands you the
          tools to market, sell and run it.
        </p>
      </div>

      <!-- The prompt -->
      <div class="hero-item hero-prompt mt-10 md:mt-12" style="animation-delay: 180ms">
        <IdeaPrompt
          input-id="hero-idea"
          :placeholder="placeholder"
          :suggestions="suggestions"
          restore
          @engage="stopDemo"
        />

        <div class="hero-meta">
          <span>Start for free. Upgrade anytime.</span>
          <button type="button" class="btn-quiet group" @click="scrollToWhy">
            <span>See how it works</span>
            <svg class="w-4 h-4 transition-transform duration-300 group-hover:translate-y-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
            </svg>
          </button>
        </div>
      </div>

      <!-- What one description turns into -->
      <div class="hero-item mt-14 md:mt-16" style="animation-delay: 270ms">
        <p class="outputs-label">
          <span>From one description</span>
          <span class="outputs-label__example">{{ current.name }}</span>
        </p>

        <ul class="rule-cols rule-cols--4 outputs" :key="index" aria-live="off">
          <li
            v-for="(item, i) in current.outputs"
            :key="item.kind"
            class="rule-col output"
            :class="{ 'output--shown': i < shown }"
          >
            <LineIcon :name="item.icon" class="rule-col__icon" />
            <span class="output__kind">{{ item.kind }}</span>
            <h3 class="rule-col__title output__title">{{ item.title }}</h3>
            <p class="output__body">{{ item.detail }}</p>
            <span class="output__status">
              <span class="output__dot" aria-hidden="true"></span>{{ item.status }}
            </span>
          </li>
        </ul>
      </div>

    </div>
  </section>
</template>

<script>
import { defineComponent, ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { LineIcon } from '@/shared/components'
import IdeaPrompt from '@/apps/home/components/molecules/IdeaPrompt.vue'

// Each example is one business described in a sentence, and the four pieces
// Imagi sets up from it. Kept to things the product actually does.
export const EXAMPLES = [
  {
    name: 'Ticker Insights',
    prompt: 'A stock tracker for everyday investors, with AI-written weekly summaries, sold as a monthly subscription',
    outputs: [
      { kind: 'Build', icon: 'launch', title: 'Web app', detail: 'Watchlist, live prices and a weekly AI brief.', status: 'Live on the web' },
      { kind: 'Sell', icon: 'sales', title: 'Pro plan', detail: 'A monthly subscription with Stripe checkout.', status: 'Checkout ready' },
      { kind: 'Market', icon: 'marketing', title: 'Launch email', detail: 'An announcement to everyone on the waitlist.', status: 'Drafted' },
      { kind: 'Operate', icon: 'finance', title: 'The books', detail: 'Subscription income and data costs, tracked.', status: 'Set up' }
    ]
  },
  {
    name: 'Paws & Suds',
    prompt: 'A booking site for my dog-grooming studio, with a deposit at checkout and reminder emails',
    outputs: [
      { kind: 'Build', icon: 'launch', title: 'Booking site', detail: 'Services, prices and an appointment calendar.', status: 'Live on the web' },
      { kind: 'Sell', icon: 'sales', title: 'Deposits', detail: 'A deposit taken with every booking.', status: 'Checkout ready' },
      { kind: 'Market', icon: 'marketing', title: 'Reminders', detail: 'An email the day before each appointment.', status: 'Scheduled' },
      { kind: 'Operate', icon: 'finance', title: 'Daily schedule', detail: 'Tasks per appointment, income logged.', status: 'Set up' }
    ]
  },
  {
    name: 'Ember & Brine',
    prompt: 'An online shop for small-batch hot sauce, with a monthly tasting box for subscribers',
    outputs: [
      { kind: 'Build', icon: 'launch', title: 'Storefront', detail: 'Product pages, a cart and customer accounts.', status: 'Live on the web' },
      { kind: 'Sell', icon: 'sales', title: 'Tasting box', detail: 'Single bottles plus a monthly subscription.', status: 'Checkout ready' },
      { kind: 'Market', icon: 'marketing', title: 'First campaign', detail: 'An email and ads for launch week.', status: 'Drafted' },
      { kind: 'Operate', icon: 'finance', title: 'Wholesale', detail: 'Invoices for shops that stock the sauce.', status: 'Set up' }
    ]
  }
]

const IDLE_PLACEHOLDER = 'Describe the business you want to start…'
const TYPE_MS = 32
const HOLD_MS = 5200
const REVEAL_MS = 380

export default defineComponent({
  name: 'HeroSection',
  components: { IdeaPrompt, LineIcon },
  setup() {
    const index = ref(0)
    const typed = ref(EXAMPLES[0].prompt)
    const shown = ref(4)
    const demoOn = ref(false)
    let timers = []

    const current = computed(() => EXAMPLES[index.value])
    // While the demo runs, the placeholder is the example being typed. Once the
    // visitor engages, it goes back to a plain instruction.
    const placeholder = computed(() => (demoOn.value ? typed.value : IDLE_PLACEHOLDER))

    const suggestions = [
      { label: 'Online store', text: 'An online store that sells ' },
      { label: 'Local service', text: 'A booking site for my ' },
      { label: 'Subscription app', text: 'A subscription app that helps ' }
    ]

    const later = (fn, ms) => timers.push(setTimeout(fn, ms))
    const clearTimers = () => {
      timers.forEach(clearTimeout)
      timers = []
    }

    const play = (i) => {
      if (!demoOn.value) return
      index.value = i
      shown.value = 0
      const full = EXAMPLES[i].prompt
      let n = 0
      const tick = () => {
        if (!demoOn.value) return
        n += 1
        typed.value = full.slice(0, n)
        if (n < full.length) {
          later(tick, TYPE_MS)
          return
        }
        // Prompt finished: the four pieces land one after another, then hold.
        for (let k = 1; k <= 4; k++) later(() => { if (demoOn.value) shown.value = k }, REVEAL_MS * k)
        later(() => play((i + 1) % EXAMPLES.length), REVEAL_MS * 4 + HOLD_MS)
      }
      typed.value = full.slice(0, 1)
      n = 1
      later(tick, TYPE_MS)
    }

    const stopDemo = () => {
      if (!demoOn.value) {
        shown.value = 4
        return
      }
      demoOn.value = false
      clearTimers()
      shown.value = 4
    }

    onMounted(() => {
      // Reduced motion: no typing, no cycling — the first example sits still.
      const reduce = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
      if (reduce) return
      demoOn.value = true
      later(() => play(0), 900)
    })

    onBeforeUnmount(clearTimers)

    const scrollToWhy = () => {
      const reduceMotion = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
      document
        .getElementById('why-imagi')
        ?.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'start' })
    }

    return { index, current, shown, placeholder, suggestions, stopDemo, scrollToWhy }
  }
})
</script>

<style scoped>
/* Staggered entrance on load */
.hero-item {
  animation: hero-rise 0.85s var(--app-ease) both;
}

@keyframes hero-rise {
  from {
    opacity: 0;
    transform: translateY(18px);
  }
  to {
    opacity: 1;
    transform: none;
  }
}

.hero-title {
  letter-spacing: -0.03em;
  line-height: 1;
}

/* The one word set in the display italic, in the accent — "run" is the half
   of the promise most site builders leave out. */
.hero-accent {
  font-style: italic;
  font-weight: 500;
  color: var(--accent);
  font-variation-settings: 'SOFT' 100, 'WONK' 1;
}

/* A low warm glow behind the prompt, so the one interactive thing on the
   first screen sits slightly forward of the paper. */
.hero-prompt {
  position: relative;
  max-width: 52rem;
}

.hero-prompt::before {
  content: '';
  position: absolute;
  inset: -3rem -4rem -2rem -4rem;
  z-index: -1;
  background: radial-gradient(60% 70% at 40% 50%, var(--accent-soft), transparent 70%);
  filter: blur(8px);
  pointer-events: none;
}

.hero-meta {
  margin-top: 1.1rem;
  padding-left: 0.4rem;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem 1.75rem;
  font-size: 0.875rem;
  color: var(--ink-40);
}

.outputs-label {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 0.25rem 0.9rem;
  padding-bottom: 1.25rem;
  margin-bottom: 1.75rem;
  border-bottom: 1px solid var(--rule);
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: var(--ink-55);
}

.outputs-label__example {
  font-family: var(--font-display);
  font-size: 0.95rem;
  font-style: italic;
  font-weight: 500;
  letter-spacing: 0;
  text-transform: none;
  color: var(--ink);
}

.outputs {
  list-style: none;
  padding: 0;
  margin: 0;
}

.output {
  opacity: 0.3;
  transform: translateY(6px);
  transition: opacity 0.5s var(--app-ease), transform 0.5s var(--app-ease);
}

.output--shown {
  opacity: 1;
  transform: none;
}

.output__kind {
  margin-top: 1rem;
  font-size: 0.66rem;
  font-weight: 600;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--ink-40);
}

.output__title {
  margin-top: 0.35rem;
}

.output__body {
  margin-top: 0.4rem;
  margin-bottom: 1rem;
  font-size: 0.9rem;
  line-height: 1.55;
  color: var(--ink-55);
}

.output__status {
  margin-top: auto;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: var(--ink-70);
}

.output__dot {
  width: 0.4rem;
  height: 0.4rem;
  border-radius: 999px;
  background: #16a34a;
  box-shadow: 0 0 0 3px rgba(22, 163, 74, 0.14);
}

@media (prefers-reduced-motion: reduce) {
  .hero-item {
    animation: none;
  }

  .output {
    transition: none;
  }
}
</style>
