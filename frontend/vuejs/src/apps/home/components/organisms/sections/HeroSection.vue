<!-- Hero Section - warm porcelain editorial design -->
<template>
  <section class="relative pt-36 pb-28 sm:pt-44 sm:pb-36 md:pt-52 md:pb-44 px-6 sm:px-8 lg:px-12 transition-colors duration-500">

    <!-- Atmosphere: soft apricot + baby-blue washes over the porcelain canvas -->
    <div class="absolute inset-0 pointer-events-none" aria-hidden="true">
      <div class="hero-glow-warm absolute -top-40 left-1/2 -translate-x-1/3 w-[900px] h-[560px]"></div>
      <div class="hero-glow-cool absolute -top-24 -left-40 w-[700px] h-[520px]"></div>
      <!-- Hairline halo ring behind the headline -->
      <div class="hero-ring absolute left-1/2 top-[46%] -translate-x-1/2 -translate-y-1/2 w-[54rem] h-[54rem] rounded-full"></div>
    </div>

    <div class="relative max-w-4xl mx-auto text-center">

      <!-- Editorial kicker: tracked small caps flanked by fading hairline rules -->
      <div class="hero-item flex items-center justify-center gap-4 mb-8" style="animation-delay: 0ms">
        <span aria-hidden="true" class="hidden sm:block h-px w-12 md:w-16 bg-gradient-to-l from-blue-950/25 to-transparent dark:from-white/25"></span>
        <span class="flex items-center gap-3">
          <span aria-hidden="true" class="w-1 h-1 rotate-45 bg-orange-500/80 dark:bg-orange-400/80"></span>
          <span class="text-[10px] sm:text-[11px] font-semibold uppercase tracking-[0.25em] sm:tracking-[0.3em] leading-none text-blue-950/70 dark:text-blue-100/55 whitespace-nowrap">The all-in-one business platform</span>
          <span aria-hidden="true" class="w-1 h-1 rotate-45 bg-orange-500/80 dark:bg-orange-400/80"></span>
        </span>
        <span aria-hidden="true" class="hidden sm:block h-px w-12 md:w-16 bg-gradient-to-r from-blue-950/25 to-transparent dark:from-white/25"></span>
      </div>

      <!-- Hero title -->
      <h1 class="hero-item font-display font-semibold text-[2.9rem] sm:text-6xl md:text-7xl lg:text-[5.4rem] mb-7 tracking-[-0.02em] leading-[1.04] text-balance text-blue-950 dark:text-white" style="animation-delay: 90ms">
        Build and run
        <br class="hidden sm:block" />
        <em class="hero-accent not-italic">your business</em>
      </h1>

      <!-- Subtitle -->
      <p class="hero-item text-lg sm:text-xl text-blue-950/65 dark:text-blue-100/65 leading-relaxed text-pretty mb-11 max-w-2xl mx-auto transition-colors duration-300" style="animation-delay: 180ms">
        Imagi is the all-in-one platform to launch and grow a business. Build your web application with AI, then run everything&mdash;marketing, sales, and finance&mdash;in one place.
      </p>

      <!-- CTA buttons -->
      <div class="hero-item flex flex-col sm:flex-row items-center gap-4 justify-center mb-14" style="animation-delay: 270ms">
        <router-link
          :to="startBuildingRoute"
          class="group inline-flex items-center justify-center gap-3 px-8 py-4 rounded-full font-medium text-lg bg-blue-950 text-[#fdf9f2] hover:bg-blue-900 dark:bg-[#f3ede2] dark:text-blue-950 dark:hover:bg-white transition-all duration-200 hover:-translate-y-0.5 active:translate-y-0 shadow-[0_1px_2px_rgba(23,37,84,0.25),0_8px_20px_-6px_rgba(23,37,84,0.35),inset_0_1px_0_rgba(255,255,255,0.12)] hover:shadow-[0_2px_3px_rgba(23,37,84,0.22),0_14px_28px_-8px_rgba(23,37,84,0.4),inset_0_1px_0_rgba(255,255,255,0.12)] dark:shadow-[0_1px_2px_rgba(0,0,0,0.5),0_10px_24px_-8px_rgba(0,0,0,0.55)] dark:hover:shadow-[0_2px_3px_rgba(0,0,0,0.5),0_14px_30px_-8px_rgba(0,0,0,0.6)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0c0c0e]"
        >
          <span>Start Building</span>
          <svg class="w-5 h-5 transition-transform duration-300 group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
          </svg>
        </router-link>

        <button
          type="button"
          @click="scrollToWhy"
          class="group inline-flex items-center gap-2.5 px-6 py-4 rounded-full font-medium text-lg text-blue-950/75 dark:text-blue-100/75 hover:text-blue-950 dark:hover:text-white transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0c0c0e]"
        >
          <span class="border-b border-blue-950/20 dark:border-blue-100/25 group-hover:border-blue-950/50 dark:group-hover:border-blue-100/60 transition-colors duration-200 pb-0.5">See how it works</span>
          <svg class="w-4 h-4 transition-transform duration-300 group-hover:translate-y-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
          </svg>
        </button>
      </div>

      <!-- Value props - centered and minimal -->
      <div class="hero-item flex flex-wrap items-center justify-center gap-3 text-xs transition-colors duration-300" style="animation-delay: 360ms">
        <span
          v-for="(prop, index) in valueProps"
          :key="index"
          class="value-pill flex items-center gap-2 px-3.5 py-2 rounded-full bg-white/85 dark:bg-white/[0.07] border border-blue-950/[0.08] dark:border-white/[0.14] transition-all duration-300 whitespace-nowrap"
        >
          <span class="w-4 h-4 rounded-full bg-orange-100 dark:bg-orange-400/[0.16] ring-1 ring-orange-200/80 dark:ring-orange-400/30 flex items-center justify-center transition-all duration-300">
            <i class="fas fa-check text-[9px] text-orange-600 dark:text-orange-300"></i>
          </span>
          <span class="text-blue-950/80 dark:text-blue-100/85 font-medium">{{ prop }}</span>
        </span>
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

    const startBuildingRoute = computed(() => {
      return authStore.isAuthenticated
        ? { name: 'projects' }
        : { name: 'login' }
    })

    const valueProps = [
      'Build your web app with AI',
      'Run marketing, sales & finance',
      'No coding experience required'
    ]

    const scrollToWhy = () => {
      const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
      document.getElementById('why-imagi')?.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'start' })
    }

    return { startBuildingRoute, valueProps, scrollToWhy }
  }
})
</script>

<style scoped>
/* Staggered entrance: each .hero-item rises in sequence on page load */
.hero-item {
  animation: hero-rise 0.9s cubic-bezier(0.22, 1, 0.36, 1) both;
}

@keyframes hero-rise {
  from {
    opacity: 0;
    transform: translateY(22px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (prefers-reduced-motion: reduce) {
  .hero-item {
    animation: none;
  }
}

/* Atmosphere washes */
.hero-glow-warm {
  background: radial-gradient(closest-side, rgba(251, 146, 60, 0.16), rgba(251, 146, 60, 0.05) 55%, transparent 75%);
  filter: blur(40px);
}

.hero-glow-cool {
  background: radial-gradient(closest-side, rgba(158, 205, 243, 0.28), rgba(158, 205, 243, 0.08) 55%, transparent 75%);
  filter: blur(44px);
}

.dark .hero-glow-warm {
  background: radial-gradient(closest-side, rgba(251, 146, 60, 0.09), rgba(251, 146, 60, 0.025) 55%, transparent 75%);
}

.dark .hero-glow-cool {
  background: radial-gradient(closest-side, rgba(96, 165, 250, 0.11), rgba(96, 165, 250, 0.03) 55%, transparent 75%);
}

/* Hairline halo ring for quiet depth behind the headline */
.hero-ring {
  border: 1px solid rgba(23, 37, 84, 0.05);
  mask-image: linear-gradient(180deg, rgba(0, 0, 0, 0.9), transparent 70%);
  -webkit-mask-image: linear-gradient(180deg, rgba(0, 0, 0, 0.9), transparent 70%);
}

.dark .hero-ring {
  border-color: rgba(255, 255, 255, 0.06);
}

/* Italic serif accent with a warm gradient ink */
.hero-accent {
  font-style: italic;
  font-variation-settings: 'SOFT' 30, 'WONK' 1;
  background: linear-gradient(115deg, #c2410c 5%, #ea580c 55%, #b45309 95%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent;
  padding-right: 0.06em; /* keep the italic terminal from clipping */
}

.dark .hero-accent {
  background: linear-gradient(115deg, #fb923c 5%, #fcd34d 60%, #f59e0b 95%);
  -webkit-background-clip: text;
  background-clip: text;
}

/* Hairline-edged pills with a whisper of depth */
.value-pill {
  box-shadow:
    0 1px 2px rgba(15, 23, 42, 0.05),
    0 2px 6px -2px rgba(15, 23, 42, 0.06);
}

.value-pill:hover {
  transform: translateY(-2px);
  border-color: rgba(234, 88, 12, 0.28);
  box-shadow:
    0 2px 4px rgba(15, 23, 42, 0.06),
    0 6px 14px -4px rgba(15, 23, 42, 0.1);
}

.dark .value-pill {
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.4),
    0 2px 6px -2px rgba(0, 0, 0, 0.35);
}

.dark .value-pill:hover {
  border-color: rgba(251, 146, 60, 0.35);
  box-shadow:
    0 2px 4px rgba(0, 0, 0, 0.45),
    0 6px 14px -4px rgba(0, 0, 0, 0.4);
}
</style>
