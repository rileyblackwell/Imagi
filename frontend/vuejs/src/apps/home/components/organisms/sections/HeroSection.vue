<!-- Hero Section - Clean Apple/Cursor-inspired design -->
<template>
  <section class="relative py-32 sm:py-40 md:py-48 px-6 sm:px-8 lg:px-12 bg-gray-50 dark:bg-[#0f0f0f] transition-colors duration-500 overflow-hidden">
    
    <div class="relative max-w-4xl mx-auto text-center">
      
      <!-- Hero title -->
      <h1 class="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-semibold text-gray-900 dark:text-white mb-6 tracking-tight leading-[1.1] transition-colors duration-300">
        Turn ideas into web apps
      </h1>

      <!-- Subtitle -->
      <p class="text-xl sm:text-2xl text-gray-500 dark:text-white/60 mb-10 max-w-3xl mx-auto transition-colors duration-300">
        Imagi is a suite of AI tools that empowers non-technical developers to build web applications. Design visually, chat with AI, and launch to the web—fast, affordable, and approachable.
      </p>

      <!-- CTA buttons -->
      <div class="flex flex-col sm:flex-row gap-4 justify-center mb-12">
        <router-link
          :to="{ name: isAuthenticated ? 'builder-dashboard' : 'login' }"
          class="group relative inline-flex items-center justify-center gap-3 px-8 py-4 bg-gray-900 dark:bg-white text-white dark:text-gray-900 rounded-full font-medium text-lg transition-all duration-300 hover:scale-[1.02] hover:shadow-2xl overflow-hidden"
        >
          <!-- Subtle shine effect on hover -->
          <span class="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent translate-x-[-200%] group-hover:translate-x-[200%] transition-transform duration-700 ease-out"></span>
          <span class="relative">Start Building</span>
          <svg class="relative w-5 h-5 transition-transform duration-300 group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
          </svg>
        </router-link>
      </div>

      <!-- Value props - centered and minimal with enhanced styling -->
      <div class="flex flex-wrap items-center justify-center gap-x-8 gap-y-3 text-sm text-gray-500 dark:text-white/50 transition-colors duration-300">
        <span class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/50 dark:bg-white/[0.03] backdrop-blur-sm border border-gray-200/50 dark:border-white/[0.06] transition-all duration-300">
          <svg class="w-4 h-4 text-emerald-500 dark:text-emerald-400/80" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
          </svg>
          Prototype and validate ideas quickly
        </span>
        <span class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/50 dark:bg-white/[0.03] backdrop-blur-sm border border-gray-200/50 dark:border-white/[0.06] transition-all duration-300">
          <svg class="w-4 h-4 text-emerald-500 dark:text-emerald-400/80" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
          </svg>
          Deploy to the web in minutes
        </span>
        <span class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/50 dark:bg-white/[0.03] backdrop-blur-sm border border-gray-200/50 dark:border-white/[0.06] transition-all duration-300">
          <svg class="w-4 h-4 text-emerald-500 dark:text-emerald-400/80" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
          </svg>
          No coding experience required
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

