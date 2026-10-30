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
  <section class="sl-opener">
    <div class="sl-spot" aria-hidden="true"></div>
    <div class="sl-dots" aria-hidden="true"></div>

    <div class="sl-wrap sl-opener__inner">
      <p class="hero-item sl-eyebrow sl-pill" style="animation-delay: 0ms">
        <span class="sl-pip" aria-hidden="true"></span>
        <span>The all-in-one business platform</span>
      </p>

      <!-- mt is important: .sl-display zeroes the margin -->
      <h1 class="hero-item sl-display sl-h1 max-w-[11ch] !mt-[6px]" style="animation-delay: 60ms">
        Build and <em class="hero-accent sl-run">run</em> your business
      </h1>

      <p class="hero-item sl-lede hero-lede" style="animation-delay: 120ms">
        Go from idea to app to business. Describe what you want, and Imagi builds it
        while you watch.
      </p>

      <div class="hero-item mt-[18px] w-full max-w-[760px] text-left" style="animation-delay: 180ms">
        <IdeaPrompt
          input-id="hero-idea"
          :placeholder="placeholder"
          :suggestions="suggestions"
          restore
          @engage="stopDemo"
        />
      </div>

      <div
        class="hero-item mt-[6px] flex flex-wrap items-center justify-center gap-x-[22px] gap-y-[10px] text-[15px]
          text-sl-muted max-[560px]:flex-col max-[560px]:gap-3"
        style="animation-delay: 240ms"
      >
        <span>Free to use. No card needed.</span>
        <span class="h-1 w-1 rounded-[50%] bg-sl-faint max-[560px]:hidden" aria-hidden="true"></span>
        <button
          type="button"
          class="group inline-flex cursor-pointer items-center gap-[6px] border-0 border-b px-0 pb-[2px] pt-0
            font-semibold text-sl-text transition-[border-color] duration-200 ease-[ease]
            [border-color:currentColor_currentColor_var(--sl-line-strong)] [border-style:none_none_solid]
            hover:border-b-sl-focus"
          @click="scrollToHowItWorks"
        >
          <span>See how it works</span>
          <svg
            class="w-4 h-4 transition-transform duration-300 ease-[ease] group-hover:translate-y-[2px]"
            fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
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
/* Staggered entrance on load. Stays CSS: a scoped @keyframes name is hashed,
   so a utility can't reference it. */
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

@media (prefers-reduced-motion: reduce) {
  .hero-item {
    animation: none;
  }
}
</style>
