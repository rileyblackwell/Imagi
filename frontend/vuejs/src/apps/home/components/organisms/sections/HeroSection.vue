<!-- Hero Section - Clean Apple/Cursor-inspired design -->
<template>
  <section class="relative py-32 sm:py-40 md:py-48 px-6 sm:px-8 lg:px-12 bg-orange-50 dark:bg-[#16120e] transition-colors duration-500 overflow-hidden">

    <div class="relative max-w-4xl mx-auto text-center">

      <!-- Hero title -->
      <h1 class="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-semibold mb-6 tracking-[-0.025em] leading-[1.08] text-balance text-blue-950 dark:text-white">
        Build and run your business
      </h1>

      <!-- Subtitle -->
      <p class="text-lg sm:text-xl text-blue-950/70 dark:text-blue-100/70 leading-relaxed text-pretty mb-10 max-w-3xl mx-auto transition-colors duration-300">
        Imagi is the all-in-one platform to launch and grow a business. Build your web application with AI tools, then run everything—marketing, sales, and finance—in one place. Fast, affordable, and approachable.
      </p>

      <!-- CTA buttons -->
      <div class="flex flex-col sm:flex-row gap-4 justify-center mb-12">
        <router-link
          :to="startBuildingRoute"
          class="btn-3d btn-accent group relative inline-flex items-center justify-center gap-3 px-8 py-4 text-blue-950 rounded-full font-medium text-lg overflow-hidden border border-white/60 dark:border-white/30 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#16120e]"
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
      <div class="flex flex-wrap items-center justify-center gap-3 text-xs transition-colors duration-300">
        <span
          v-for="(prop, index) in valueProps"
          :key="index"
          class="value-pill flex items-center gap-2 px-3.5 py-2 rounded-full bg-white dark:bg-white/[0.07] border border-gray-200/90 dark:border-white/[0.14] transition-all duration-300 whitespace-nowrap"
        >
          <span class="w-4 h-4 rounded-full bg-orange-100 dark:bg-orange-400/[0.16] ring-1 ring-orange-200/80 dark:ring-orange-400/30 flex items-center justify-center transition-all duration-300">
            <i class="fas fa-check text-[9px] text-orange-600 dark:text-orange-300"></i>
          </span>
          <span class="text-gray-800 dark:text-blue-100/85 font-medium">{{ prop }}</span>
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

    return { startBuildingRoute, valueProps }
  }
})
</script>

<style scoped>
/* Soft 3D button effect - tight, layered, crisp. Blue-tinted shadows to suit the light baby-blue fill. */
.btn-3d {
  transform: translateY(0) translateZ(0);
  transition: transform 0.3s ease, box-shadow 0.3s ease, background 0.3s ease;
  box-shadow:
    0 1px 2px rgba(30, 58, 138, 0.14),
    0 4px 10px -2px rgba(30, 58, 138, 0.16),
    0 10px 20px -6px rgba(30, 58, 138, 0.18),
    inset 0 1px 1px 0 rgba(255, 255, 255, 0.75),
    inset 0 -2px 4px -1px rgba(30, 58, 138, 0.12);
}

.btn-3d:active {
  transform: translateY(0) translateZ(0);
  transition-duration: 0.1s;
}

/* Soft baby-blue gradient fill */
.btn-accent {
  background: linear-gradient(155deg, #dbeeff 0%, #b7ddf7 55%, #9ecdf3 100%);
}

.dark .btn-accent {
  background: linear-gradient(155deg, #dbeeff 0%, #b7ddf7 55%, #9ecdf3 100%);
}

/* On dark, ground the light button with deep neutral shadows; keep the inner sheen */
.dark .btn-3d {
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.5),
    0 4px 10px -2px rgba(0, 0, 0, 0.45),
    0 10px 20px -6px rgba(0, 0, 0, 0.5),
    inset 0 1px 1px 0 rgba(255, 255, 255, 0.75),
    inset 0 -2px 4px -1px rgba(30, 58, 138, 0.18);
}

/* Hairline-edged pills with a whisper of depth */
.value-pill {
  box-shadow:
    0 1px 2px rgba(15, 23, 42, 0.05),
    0 2px 6px -2px rgba(15, 23, 42, 0.06);
}

.dark .value-pill {
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.4),
    0 2px 6px -2px rgba(0, 0, 0, 0.35);
}
</style>
