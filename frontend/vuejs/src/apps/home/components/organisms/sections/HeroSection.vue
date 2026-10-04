<!--
  Hero — prompt first.

  The call to action is the product's own first step: a box to describe the
  business. While the visitor hasn't touched it, the placeholder types out an
  example. As soon as the visitor focuses or types, the demo stops and stays
  out of the way.

  No screenshot here on purpose: the real product shots sit lower on the page,
  next to the sections that explain them.
-->
<template>
  <section class="hero relative pt-28 sm:pt-32 md:pt-36 pb-10 md:pb-14">
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

    </div>
  </section>
</template>

<script>
import { defineComponent, ref, computed, onMounted, onBeforeUnmount } from 'vue'
import IdeaPrompt from '@/apps/home/components/molecules/IdeaPrompt.vue'

// Businesses the placeholder types out while the box is untouched.
export const EXAMPLES = [
  'A stock tracker for everyday investors, with AI-written weekly summaries, sold as a monthly subscription',
  'A booking site for my dog-grooming studio, with a deposit at checkout and reminder emails',
  'An online shop for small-batch hot sauce, with a monthly tasting box for subscribers'
]

const IDLE_PLACEHOLDER = 'Describe the business you want to start…'
const TYPE_MS = 32
const HOLD_MS = 5200

export default defineComponent({
  name: 'HeroSection',
  components: { IdeaPrompt },
  setup() {
    const typed = ref(EXAMPLES[0])
    const demoOn = ref(false)
    let timers = []

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
      const full = EXAMPLES[i]
      let n = 0
      const tick = () => {
        if (!demoOn.value) return
        n += 1
        typed.value = full.slice(0, n)
        if (n < full.length) {
          later(tick, TYPE_MS)
          return
        }
        // Hold the finished example, then type the next one.
        later(() => play((i + 1) % EXAMPLES.length), HOLD_MS)
      }
      typed.value = full.slice(0, 1)
      n = 1
      later(tick, TYPE_MS)
    }

    const stopDemo = () => {
      demoOn.value = false
      clearTimers()
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

    return { placeholder, suggestions, stopDemo, scrollToWhy }
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

@media (prefers-reduced-motion: reduce) {
  .hero-item {
    animation: none;
  }
}
</style>
