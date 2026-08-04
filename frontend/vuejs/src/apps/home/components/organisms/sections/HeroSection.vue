<!--
  Hero — copy block, then the product.

  Built from the same parts as every section below it: the eyebrow, the
  headline-left / supporting-copy-right header, and a closing hairline. It
  differs only in scale, which is what makes it read as the top of one page
  rather than a differently-designed lid on it.

  Deliberately no coloured word in the headline and no drop-shadowed pill —
  both fought the flat ink-and-hairline language of the rest of the page.
-->
<template>
  <section class="relative pt-32 sm:pt-40 md:pt-44 pb-10 md:pb-14">
    <div class="section-shell">

      <!-- Header: the section pattern, one size up -->
      <div class="md:flex md:items-end md:justify-between gap-12 lg:gap-16">
        <div class="hero-item max-w-[36rem]" style="animation-delay: 0ms">
          <p class="eyebrow">
            <span class="eyebrow__rule" aria-hidden="true"></span>
            <span>The all-in-one business platform</span>
          </p>

          <h1 class="display mt-7 text-[2.75rem] sm:text-6xl md:text-[3.9rem]">
            Build and run your business
          </h1>
        </div>

        <p class="hero-item lede mt-7 md:mt-0 md:max-w-sm md:pb-3 text-lg" style="animation-delay: 90ms">
          Describe the business you want. Imagi's agent writes the web app, shows it
          running next to the conversation, and puts it online &mdash; then hands you the
          tools to market, sell and run it.
        </p>
      </div>

      <div class="hero-item mt-11 flex flex-col sm:flex-row sm:items-center gap-4 sm:gap-7" style="animation-delay: 180ms">
        <router-link :to="startBuildingRoute" class="btn-primary group">
          <span>Start building</span>
          <svg class="w-4 h-4 transition-transform duration-300 group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
          </svg>
        </router-link>

        <button type="button" class="btn-quiet group" @click="scrollToWhy">
          <span>See how it works</span>
          <svg class="w-4 h-4 transition-transform duration-300 group-hover:translate-y-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
          </svg>
        </button>
      </div>

      <!-- Closing hairline: hands the eye down to the product, and starts the
           rule-per-section rhythm the rest of the page keeps up. -->
      <div class="hero-item section-rule mt-14 md:mt-16" style="animation-delay: 260ms" aria-hidden="true"></div>
    </div>

    <!-- Product shot: breaks out past the text measure, the one wide moment -->
    <div class="hero-item hero-stage mt-14 md:mt-16" style="animation-delay: 320ms">
      <div class="hero-stage__inner">
        <ProductShot
          src="/product/build-workspace.webp"
          alt="The Imagi build workspace: a conversation with the agent on the left, and on the right the live stock-tracking app it wrote — a portfolio snapshot with AAPL and TSLA prices and AI-written summaries."
          :width="2400"
          :height="1500"
          label="imagi — build workspace"
          eager
        />
      </div>
      <p class="hero-stage__caption section-shell">
        A real project mid-conversation: &ldquo;Ticker Insights&rdquo;, a stock tracker with
        AI-written summaries, built from a description and running live beside the chat.
      </p>
    </div>
  </section>
</template>

<script>
import { defineComponent, computed } from 'vue'
import { useAuthStore } from '@/shared/stores/auth'
import { ProductShot } from '@/apps/home/components/atoms'

export default defineComponent({
  name: 'HeroSection',
  components: { ProductShot },
  setup() {
    const authStore = useAuthStore()

    const startBuildingRoute = computed(() =>
      authStore.isAuthenticated ? { name: 'projects' } : { name: 'login' }
    )

    const scrollToWhy = () => {
      const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
      document
        .getElementById('why-imagi')
        ?.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'start' })
    }

    return { startBuildingRoute, scrollToWhy }
  }
})
</script>

<style scoped>
/* Staggered entrance on load */
.hero-item {
  animation: hero-rise 0.85s cubic-bezier(0.22, 1, 0.36, 1) both;
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

/* The shot sits in a wider measure than the copy — up to 80rem against the
   copy's 68rem — so it reads as a stage the page opens onto. */
.hero-stage__inner {
  max-width: 80rem;
  margin: 0 auto;
  padding: 0 1.5rem;
}

@media (min-width: 640px) {
  .hero-stage__inner {
    padding: 0 2rem;
  }
}

.hero-stage__caption {
  margin-top: 1.25rem;
  max-width: 34rem;
  font-size: 0.85rem;
  line-height: 1.6;
  color: var(--ink-40);
  text-wrap: pretty;
}
</style>
