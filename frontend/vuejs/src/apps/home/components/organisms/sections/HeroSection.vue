<!--
  Hero — the page's opening statement.

  Copy only. The build workspace screenshot used to sit here, but it belongs
  with step 01 ("Build your web app"), which is what it actually illustrates —
  so the hero is now a plain statement and the product appears where the page
  starts explaining it.

  Built from the same parts as every section below it: the eyebrow and the
  headline-left / supporting-copy-right header, differing only in scale.
-->
<template>
  <section class="relative pt-32 sm:pt-40 md:pt-44 pb-20 md:pb-28">
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

    </div>
  </section>
</template>

<script>
import { defineComponent, computed } from 'vue'
import { useAuthStore } from '@/shared/stores/auth'

export default defineComponent({
  name: 'HeroSection',
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

</style>
