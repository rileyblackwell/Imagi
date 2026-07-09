<!-- Hero Section - Clean Apple/Cursor-inspired design -->
<template>
  <section class="relative py-32 sm:py-40 md:py-48 px-6 sm:px-8 lg:px-12 bg-white dark:bg-[#0a0a0a] transition-colors duration-500 overflow-hidden">

    <!-- Ambient gradient orbs for depth -->
    <div class="absolute inset-0 pointer-events-none overflow-hidden">
      <div class="absolute -top-32 left-1/2 -translate-x-1/2 w-[760px] h-[520px] bg-gradient-radial from-blue-400/10 dark:from-blue-500/[0.12] via-transparent to-transparent rounded-full blur-3xl"></div>
      <div class="absolute top-1/3 -left-20 w-[420px] h-[420px] bg-gradient-radial from-violet-400/[0.07] dark:from-violet-500/[0.08] via-transparent to-transparent rounded-full blur-3xl animate-pulse-slow"></div>
      <div class="absolute top-1/4 -right-20 w-[420px] h-[420px] bg-gradient-radial from-cyan-400/[0.06] dark:from-cyan-500/[0.07] via-transparent to-transparent rounded-full blur-3xl animate-pulse-slow"></div>
    </div>

    <div class="relative max-w-4xl mx-auto text-center">

      <!-- Eyebrow badge -->
      <div class="reveal flex justify-center mb-8" style="animation-delay: 0ms">
        <span class="group inline-flex items-center gap-2 pl-2 pr-4 py-1.5 rounded-full border border-gray-200/80 dark:border-white/10 bg-white/70 dark:bg-white/[0.04] backdrop-blur-md text-xs font-medium text-gray-700 dark:text-white/70 shadow-sm transition-colors duration-300">
          <span class="inline-flex items-center justify-center px-2 py-0.5 rounded-full bg-gradient-to-r from-blue-500 to-violet-500 text-white text-[10px] font-semibold tracking-wide">NEW</span>
          <span>Build web apps with AI</span>
        </span>
      </div>

      <!-- Hero title -->
      <h1 class="reveal text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-semibold text-gray-900 dark:text-white mb-6 tracking-tight leading-[1.05] transition-colors duration-300" style="animation-delay: 80ms">
        Turn ideas into
        <span class="bg-gradient-to-r from-blue-600 via-violet-500 to-cyan-500 dark:from-blue-400 dark:via-violet-400 dark:to-cyan-300 bg-clip-text text-transparent">web apps</span>
      </h1>

      <!-- Subtitle -->
      <p class="reveal text-lg sm:text-xl text-gray-600 dark:text-white/70 tracking-wide font-medium mb-10 max-w-2xl mx-auto leading-relaxed transition-colors duration-300" style="animation-delay: 160ms">
        Imagi is a suite of AI tools that empowers non-technical developers to build web applications. Design visually, chat with AI, and launch to the web—fast, affordable, and approachable.
      </p>

      <!-- CTA buttons -->
      <div class="reveal flex flex-col sm:flex-row gap-4 justify-center mb-14" style="animation-delay: 240ms">
        <router-link
          :to="startBuildingRoute"
          class="btn-3d group relative inline-flex items-center justify-center gap-3 px-8 py-4 bg-gradient-to-b from-gray-800 via-gray-900 to-gray-950 dark:from-white dark:via-gray-50 dark:to-gray-100 text-white dark:text-gray-900 rounded-full font-medium text-lg transition-all duration-300 overflow-hidden border border-gray-700/50 dark:border-gray-300/50 hover:-translate-y-0.5"
        >
          <!-- Top edge highlight for 3D effect -->
          <span class="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/70 to-transparent"></span>
          <!-- Bottom edge shadow for depth -->
          <span class="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-blue-900/15 to-transparent"></span>
          <span class="relative">Start Building</span>
          <svg class="relative w-5 h-5 transition-transform duration-300 group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
          </svg>
        </router-link>
      </div>

      <!-- Value props - centered and minimal -->
      <div class="reveal flex flex-wrap items-center justify-center gap-3 text-xs transition-colors duration-300" style="animation-delay: 320ms">
        <span
          v-for="(prop, index) in valueProps"
          :key="index"
          class="flex items-center gap-2 px-3.5 py-2 rounded-full bg-white/70 dark:bg-white/[0.04] border border-gray-200/70 dark:border-white/10 backdrop-blur-md transition-all duration-300 whitespace-nowrap hover:border-gray-300 dark:hover:border-white/20"
        >
          <span class="w-4 h-4 rounded-full bg-emerald-100 dark:bg-emerald-500/15 flex items-center justify-center transition-all duration-300">
            <i class="fas fa-check text-[9px] text-emerald-600 dark:text-emerald-400"></i>
          </span>
          <span class="text-gray-700 dark:text-white/80 font-medium">{{ prop }}</span>
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
      'Prototype and validate ideas quickly',
      'No coding experience required',
      'Deploy to the web in minutes'
    ]

    return { startBuildingRoute, valueProps }
  }
})
</script>

<style scoped>
/* Staggered entrance */
.reveal {
  opacity: 0;
  animation: hero-reveal 0.7s cubic-bezier(0.22, 1, 0.36, 1) forwards;
}

@keyframes hero-reveal {
  0% {
    opacity: 0;
    transform: translateY(16px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (prefers-reduced-motion: reduce) {
  .reveal {
    opacity: 1;
    animation: none;
  }
}

/* 3D Printed Button Effect */
.btn-3d {
  transform: translateZ(0);
  box-shadow:
    /* Tight shadow for immediate depth */
    0 2px 3px -1px rgba(0, 0, 0, 0.4),
    /* Medium shadow for body lift */
    0 6px 12px -3px rgba(0, 0, 0, 0.35),
    /* Large diffuse shadow */
    0 16px 32px -8px rgba(0, 0, 0, 0.3),
    0 24px 48px -12px rgba(0, 0, 0, 0.2),
    /* Bottom edge thickness */
    0 3px 0 -1px rgba(0, 0, 0, 0.5),
    /* Inset highlights */
    inset 0 2px 4px 0 rgba(255, 255, 255, 0.2),
    inset 0 -4px 8px -2px rgba(0, 0, 0, 0.3);
}

.btn-3d:hover {
  box-shadow:
    0 4px 6px -1px rgba(0, 0, 0, 0.4),
    0 10px 20px -4px rgba(0, 0, 0, 0.38),
    0 22px 42px -10px rgba(0, 0, 0, 0.32),
    0 32px 60px -14px rgba(0, 0, 0, 0.24),
    0 3px 0 -1px rgba(0, 0, 0, 0.5),
    inset 0 2px 4px 0 rgba(255, 255, 255, 0.25),
    inset 0 -4px 8px -2px rgba(0, 0, 0, 0.3);
}

.dark .btn-3d {
  box-shadow:
    /* Tight shadow for immediate depth */
    0 2px 3px -1px rgba(0, 0, 0, 0.1),
    /* Medium shadow for body lift */
    0 6px 12px -3px rgba(0, 0, 0, 0.1),
    /* Large diffuse shadow */
    0 16px 32px -8px rgba(0, 0, 0, 0.1),
    0 24px 48px -12px rgba(0, 0, 0, 0.08),
    /* Bottom edge thickness */
    0 3px 0 -1px rgba(0, 0, 0, 0.15),
    /* Inset highlights */
    inset 0 3px 6px 0 rgba(255, 255, 255, 0.9),
    inset 0 -4px 8px -2px rgba(0, 0, 0, 0.08);
}

.dark .btn-3d:hover {
  box-shadow:
    0 4px 6px -1px rgba(0, 0, 0, 0.12),
    0 10px 20px -4px rgba(0, 0, 0, 0.12),
    0 22px 42px -10px rgba(0, 0, 0, 0.12),
    0 32px 60px -14px rgba(0, 0, 0, 0.1),
    0 3px 0 -1px rgba(0, 0, 0, 0.15),
    inset 0 3px 6px 0 rgba(255, 255, 255, 0.95),
    inset 0 -4px 8px -2px rgba(0, 0, 0, 0.08);
}
</style>
