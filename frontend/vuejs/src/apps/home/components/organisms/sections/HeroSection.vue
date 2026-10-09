<!--
  Hero — prompt first, under the spotlight.

  The call to action is the product's own first step: a box to describe the
  business, lit from above like a command bar on a stage. While the visitor
  hasn't touched it, the placeholder types out an example. As soon as the
  visitor focuses or types, the demo stops and stays out of the way.

  No screenshot here on purpose: the real product shots sit lower on the page,
  next to the sections that explain them.
-->
<template>
  <section class="hero sl-opener">
    <div class="sl-spot" aria-hidden="true"></div>
    <div class="sl-dots" aria-hidden="true"></div>

    <div class="sl-wrap sl-opener__inner">
      <p class="hero-item sl-eyebrow sl-pill" style="animation-delay: 0ms">
        <span class="sl-pip" aria-hidden="true"></span>
        <span>The all-in-one business platform</span>
      </p>

      <h1 class="hero-item sl-display sl-h1 hero-title" style="animation-delay: 60ms">
        Build and <em class="hero-accent sl-run">run</em> your business
      </h1>

      <p class="hero-item sl-lede hero-lede" style="animation-delay: 120ms">
        Turn an idea into an app, and the app into a business. Describe it in your own
        words and Imagi&rsquo;s agent builds it and puts it online, with the tools to
        market, sell and run it waiting in the same place.
      </p>

      <div class="hero-item hero-prompt" style="animation-delay: 180ms">
        <IdeaPrompt
          input-id="hero-idea"
          :placeholder="placeholder"
          :suggestions="suggestions"
          restore
          @engage="stopDemo"
        />
      </div>

      <div class="hero-item hero-meta" style="animation-delay: 240ms">
        <span>Start for free. Upgrade anytime.</span>
        <span class="hero-meta__sep" aria-hidden="true"></span>
        <button type="button" class="hero-meta__link" @click="scrollToHowItWorks">
          <span>See how it works</span>
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
          </svg>
        </button>
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

    const scrollToHowItWorks = () => {
      const reduceMotion = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
      document
        .getElementById('how-it-works')
        ?.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'start' })
    }

    return { placeholder, suggestions, stopDemo, scrollToHowItWorks }
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

.hero .hero-title {
  max-width: 11ch;
  margin-top: 6px;
}

.hero-prompt {
  width: 100%;
  max-width: 760px;
  margin-top: 18px;
  text-align: left;
}

.hero-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 10px 22px;
  margin-top: 6px;
  font-size: 15px;
  color: var(--sl-muted);
}

.hero-meta__sep {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--sl-faint);
}

.hero-meta__link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 0 0 2px;
  border: 0;
  border-bottom: 1px solid var(--sl-line-strong);
  background: none;
  color: var(--sl-text);
  font: inherit;
  font-weight: 600;
  cursor: pointer;
  transition: border-color 0.2s ease;
}

.hero-meta__link:hover {
  border-bottom-color: var(--sl-focus);
}

.hero-meta__link svg {
  transition: transform 0.3s ease;
}

.hero-meta__link:hover svg {
  transform: translateY(2px);
}

@media (max-width: 560px) {
  .hero-meta {
    flex-direction: column;
    gap: 12px;
  }

  .hero-meta__sep {
    display: none;
  }
}

@media (prefers-reduced-motion: reduce) {
  .hero-item {
    animation: none;
  }
}
</style>
