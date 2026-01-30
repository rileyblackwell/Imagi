<!-- Hero Section - Clean Apple/Cursor-inspired design -->
<template>
  <section class="relative py-32 sm:py-40 md:py-48 px-6 sm:px-8 lg:px-12 bg-white dark:bg-[#0a0a0a] transition-colors duration-500 overflow-hidden">
    
    <div class="relative max-w-4xl mx-auto text-center">
      
      <!-- Hero title -->
      <h1 class="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-semibold text-gray-900 dark:text-white mb-6 tracking-tight leading-[1.1] transition-colors duration-300">
        Turn ideas into web apps
      </h1>

      <!-- Subtitle -->
      <p class="text-lg sm:text-xl text-gray-700 dark:text-white/80 tracking-wide font-medium mb-10 max-w-3xl mx-auto transition-colors duration-300">
        Imagi is a suite of AI tools that empowers non-technical developers to build web applications. Design visually, chat with AI, and launch to the web—fast, affordable, and approachable.
      </p>

      <!-- CTA buttons -->
      <div class="flex flex-col sm:flex-row gap-4 justify-center mb-12">
        <router-link
          :to="{ name: isAuthenticated ? 'projects' : 'login' }"
          class="btn-3d group relative inline-flex items-center justify-center gap-3 px-8 py-4 bg-gradient-to-b from-gray-800 via-gray-900 to-gray-950 dark:from-white dark:via-gray-50 dark:to-gray-100 text-white dark:text-gray-900 rounded-full font-medium text-lg transition-all duration-300 overflow-hidden border border-gray-700/50 dark:border-gray-300/50"
        >
          <!-- Top edge highlight for 3D effect -->
          <span class="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/30 to-transparent dark:via-white/60"></span>
          <!-- Bottom edge shadow for depth -->
          <span class="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-black/30 to-transparent dark:via-black/10"></span>
          <span class="relative">Start Building</span>
          <svg class="relative w-5 h-5 transition-transform duration-300 group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
          </svg>
        </router-link>
      </div>

      <!-- Value props - centered and minimal -->
      <div class="flex flex-nowrap items-center justify-center gap-x-3 text-xs transition-colors duration-300">
        <span class="flex items-center gap-2 px-3.5 py-2 rounded-full bg-gray-100 dark:bg-white transition-all duration-300 hover:shadow-xl whitespace-nowrap">
          <div class="w-4 h-4 rounded-full bg-emerald-100 dark:bg-emerald-100 flex items-center justify-center transition-all duration-300">
            <i class="fas fa-check text-[9px] text-emerald-600 dark:text-emerald-600"></i>
          </div>
          <span class="text-gray-900 dark:text-gray-900 font-medium">Prototype and validate ideas quickly</span>
        </span>
        <span class="flex items-center gap-2 px-3.5 py-2 rounded-full bg-gray-100 dark:bg-white transition-all duration-300 hover:shadow-xl whitespace-nowrap">
          <div class="w-4 h-4 rounded-full bg-emerald-100 dark:bg-emerald-100 flex items-center justify-center transition-all duration-300">
            <i class="fas fa-check text-[9px] text-emerald-600 dark:text-emerald-600"></i>
          </div>
          <span class="text-gray-900 dark:text-gray-900 font-medium">No coding experience required</span>
        </span>
        <span class="flex items-center gap-2 px-3.5 py-2 rounded-full bg-gray-100 dark:bg-white transition-all duration-300 hover:shadow-xl whitespace-nowrap">
          <div class="w-4 h-4 rounded-full bg-emerald-100 dark:bg-emerald-100 flex items-center justify-center transition-all duration-300">
            <i class="fas fa-check text-[9px] text-emerald-600 dark:text-emerald-600"></i>
          </div>
          <span class="text-gray-900 dark:text-gray-900 font-medium">Deploy to the web in minutes</span>
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
    
    return {
      isAuthenticated: computed(() => authStore.isAuthenticated)
    }
  }
})
</script>

<style scoped>
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
</style>
