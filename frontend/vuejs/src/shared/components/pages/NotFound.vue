<!-- 404 page - warm porcelain editorial design -->
<template>
  <div class="not-found-page relative min-h-screen overflow-hidden font-body flex items-center justify-center px-6 sm:px-8 transition-colors duration-500">

    <!-- Grain texture over the canvas -->
    <div class="grain-overlay absolute inset-0 z-[1] pointer-events-none" aria-hidden="true"></div>

    <!-- Atmosphere: one soft apricot wash behind the folio -->
    <div class="absolute inset-0 pointer-events-none" aria-hidden="true">
      <div class="nf-glow-warm absolute left-1/2 top-[42%] -translate-x-1/2 -translate-y-1/2 w-[700px] h-[440px]"></div>
    </div>

    <div class="relative z-10 max-w-xl mx-auto text-center py-24">

      <!-- Folio number: giant serif with the warm gradient ink -->
      <h1 class="nf-item font-display font-semibold text-[6rem] sm:text-[8rem] leading-none tracking-[-0.02em] mb-4" style="animation-delay: 0ms">
        <em class="nf-accent">404</em>
      </h1>

      <!-- Editorial kicker: tracked small caps flanked by fading hairline rules -->
      <div class="nf-item flex items-center justify-center gap-4 mb-8" style="animation-delay: 90ms">
        <span aria-hidden="true" class="hidden sm:block h-px w-10 md:w-14 bg-gradient-to-l from-blue-950/25 to-transparent dark:from-white/25"></span>
        <h2 class="flex items-center gap-3">
          <span aria-hidden="true" class="w-1 h-1 rotate-45 bg-orange-500/80 dark:bg-orange-400/80"></span>
          <span class="text-[10px] sm:text-[11px] font-semibold uppercase tracking-[0.25em] leading-none text-blue-950/70 dark:text-blue-100/55 whitespace-nowrap">Page Not Found</span>
          <span aria-hidden="true" class="w-1 h-1 rotate-45 bg-orange-500/80 dark:bg-orange-400/80"></span>
        </h2>
        <span aria-hidden="true" class="hidden sm:block h-px w-10 md:w-14 bg-gradient-to-r from-blue-950/25 to-transparent dark:from-white/25"></span>
      </div>

      <p class="nf-item text-lg text-blue-950/65 dark:text-blue-100/65 leading-relaxed text-pretty mb-10 transition-colors duration-300" style="animation-delay: 180ms">
        The page you're looking for doesn't exist or has been moved.
      </p>

      <!-- Navy ink pill home button -->
      <div class="nf-item" style="animation-delay: 270ms">
        <router-link
          to="/"
          class="group inline-flex items-center justify-center gap-3 px-8 py-4 rounded-full font-medium text-lg bg-blue-950 text-[#fdf9f2] hover:bg-blue-900 dark:bg-[#f3ede2] dark:text-blue-950 dark:hover:bg-white transition-all duration-200 hover:-translate-y-0.5 active:translate-y-0 shadow-[0_1px_2px_rgba(23,37,84,0.25),0_8px_20px_-6px_rgba(23,37,84,0.35),inset_0_1px_0_rgba(255,255,255,0.12)] hover:shadow-[0_2px_3px_rgba(23,37,84,0.22),0_14px_28px_-8px_rgba(23,37,84,0.4),inset_0_1px_0_rgba(255,255,255,0.12)] dark:shadow-[0_1px_2px_rgba(0,0,0,0.5),0_10px_24px_-8px_rgba(0,0,0,0.55)] dark:hover:shadow-[0_2px_3px_rgba(0,0,0,0.5),0_14px_30px_-8px_rgba(0,0,0,0.6)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0c0c0e]"
        >
          <span>Return Home</span>
          <svg class="w-5 h-5 transition-transform duration-300 group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
          </svg>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineOptions({
  name: 'NotFound'
})
</script>

<style scoped>
/* Short-page porcelain canvas: starts porcelain, ends on the footer white */
.not-found-page {
  background: linear-gradient(180deg, #fdf9f2 0%, #faf7f1 55%, #ffffff 100%);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
}

:root.dark .not-found-page,
.dark .not-found-page {
  background: linear-gradient(180deg, #0c0c0e 0%, #0a0b0f 55%, #0a0a0a 100%);
}

/* Fine film grain over the canvas */
.grain-overlay {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160' viewBox='0 0 160 160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='160' height='160' filter='url(%23n)' opacity='0.5'/%3E%3C/svg%3E");
  background-size: 160px 160px;
  opacity: 0.035;
  mix-blend-mode: multiply;
}

:root.dark .grain-overlay,
.dark .grain-overlay {
  opacity: 0.05;
  mix-blend-mode: overlay;
}

/* Soft warm wash behind the folio number */
.nf-glow-warm {
  background: radial-gradient(closest-side, rgba(251, 146, 60, 0.13), rgba(251, 146, 60, 0.04) 55%, transparent 75%);
  filter: blur(44px);
}

.dark .nf-glow-warm {
  background: radial-gradient(closest-side, rgba(251, 146, 60, 0.07), rgba(251, 146, 60, 0.02) 55%, transparent 75%);
}

/* Italic serif folio number with the warm gradient ink */
.nf-accent {
  font-style: italic;
  font-variation-settings: 'SOFT' 30, 'WONK' 1;
  background: linear-gradient(115deg, #c2410c 5%, #ea580c 55%, #b45309 95%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent;
  padding-right: 0.06em; /* keep the italic terminal from clipping */
}

.dark .nf-accent {
  background: linear-gradient(115deg, #fb923c 5%, #fcd34d 60%, #f59e0b 95%);
  -webkit-background-clip: text;
  background-clip: text;
}

/* Staggered entrance: each .nf-item rises in sequence on page load */
.nf-item {
  animation: nf-rise 0.9s cubic-bezier(0.22, 1, 0.36, 1) both;
}

@keyframes nf-rise {
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
  .nf-item {
    animation: none;
  }
}
</style>

<!-- Unscoped: brand-tinted text selection on the 404 page -->
<style>
.not-found-page ::selection {
  background: rgba(158, 205, 243, 0.55);
  color: #172554;
}

.dark .not-found-page ::selection {
  background: rgba(96, 165, 250, 0.4);
  color: #eff6ff;
}
</style>
