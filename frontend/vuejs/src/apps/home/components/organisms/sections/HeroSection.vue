<!-- Hero Section - Clean Apple/Cursor-inspired design -->
<template>
  <section class="py-32 sm:py-40 md:py-48 px-6 sm:px-8 lg:px-12 bg-gray-50 dark:bg-[#0f0f0f] transition-colors duration-500">
    <div class="max-w-4xl mx-auto text-center">
      
      <!-- Hero title -->
      <h1 class="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-semibold text-gray-900 dark:text-white mb-6 tracking-tight leading-[1.1] transition-colors duration-300">
        Create web apps without writing code
      </h1>

      <!-- Subtitle -->
      <p class="text-xl sm:text-2xl text-gray-500 dark:text-white/60 mb-10 max-w-3xl mx-auto transition-colors duration-300">
        Imagi gives anyone the power to build professional web applications. Just describe what you want — our AI handles the rest.
      </p>

      <!-- CTA buttons -->
      <div class="flex flex-col sm:flex-row gap-4 justify-center mb-12">
        <router-link
          :to="{ name: isAuthenticated ? 'builder-dashboard' : 'login' }"
          class="inline-flex items-center justify-center gap-3 px-8 py-4 bg-gray-900 dark:bg-white text-white dark:text-gray-900 rounded-full font-medium text-lg transition-all duration-300 hover:scale-[1.02] hover:shadow-xl"
        >
          Start Building
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
          </svg>
        </router-link>
      </div>

      <!-- Value props - centered and minimal -->
      <div class="flex flex-wrap items-center justify-center gap-x-8 gap-y-3 text-sm text-gray-500 dark:text-white/50 transition-colors duration-300">
        <span class="flex items-center gap-2">
          <svg class="w-4 h-4 text-gray-400 dark:text-white/40" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
          </svg>
          No technical skills needed
        </span>
        <span class="flex items-center gap-2">
          <svg class="w-4 h-4 text-gray-400 dark:text-white/40" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
          </svg>
          Production-ready code
        </span>
        <span class="flex items-center gap-2">
          <svg class="w-4 h-4 text-gray-400 dark:text-white/40" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
          </svg>
          You own everything you create
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

