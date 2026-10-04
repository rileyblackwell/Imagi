<!--
  Hero — the page's opening statement.

  Built from the same parts as every section below it: the eyebrow and the
  headline-left / supporting-copy-right header, differing only in scale.

  Below the copy sits the project hub, the one screenshot that shows the
  headline's whole claim at once: a business with Build, Sell, Market and
  Operate in one place. Copy alone left the first screen half empty, so this
  puts the product in view before the visitor scrolls. It stands on a soft warm
  wash — the accent at very low strength — so the dark shot sits on the paper
  rather than being dropped onto it. The build workspace stays with step 01,
  which is what it illustrates.
-->
<template>
  <section class="hero relative pt-28 sm:pt-36 md:pt-40 pb-6 md:pb-10">
    <div class="section-shell">

      <!-- Header: the section pattern, one size up -->
      <div class="md:flex md:items-end md:justify-between gap-12 lg:gap-16">
        <div class="hero-item max-w-[36rem]" style="animation-delay: 0ms">
          <p class="eyebrow">
            <span class="eyebrow__rule" aria-hidden="true"></span>
            <span>The all-in-one business platform</span>
          </p>

          <h1 class="display mt-7 text-[2.75rem] sm:text-6xl md:text-[3.9rem]">
            Build and <em class="hero-accent">run</em> your business
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

      <!-- The product, in view on the first screen -->
      <div class="hero-item hero-stage mt-16 md:mt-20" style="animation-delay: 270ms">
        <ProductShot
          src="/product/project-hub.webp"
          alt="The project hub for Ticker Insights, showing its four workspaces: Build, Sell, Market and Operate."
          :width="2400"
          :height="1752"
          label="imagi — project hub"
          caption="One project, four workspaces. Build makes the product; Sell, Market and Operate run the business around it."
          eager
        />
      </div>

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

/* The one word set in the display italic, in the accent — "run" is the half
   of the promise most site builders leave out. */
.hero-accent {
  font-style: italic;
  font-weight: 500;
  color: var(--accent);
  font-variation-settings: 'SOFT' 100, 'WONK' 1;
}

/* The wash below reaches past the shell on narrow screens; clip it here
   rather than letting it widen the page. */
.hero {
  overflow-x: clip;
}

/* A warm wash behind the shot: wider than the frame and fading out at every
   edge, so there is no box — just light on the paper. */
.hero-stage {
  position: relative;
}

.hero-stage::before {
  content: '';
  position: absolute;
  inset: -4rem -6rem -2rem;
  z-index: -1;
  background:
    radial-gradient(ellipse 60% 55% at 50% 36%, color-mix(in srgb, var(--accent) 16%, transparent), transparent 70%),
    radial-gradient(ellipse 80% 60% at 50% 55%, rgba(19, 26, 44, 0.05), transparent 72%);
  filter: blur(8px);
  pointer-events: none;
}

.dark .hero-stage::before {
  background:
    radial-gradient(ellipse 55% 50% at 50% 38%, var(--accent-soft), transparent 70%);
}

</style>
