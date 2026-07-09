<!-- CTA Section - Clean Apple/Cursor-inspired design -->
<template>
  <section class="relative py-24 sm:py-32 px-6 sm:px-8 lg:px-12 bg-orange-50 dark:bg-orange-700 border-t border-orange-200/60 dark:border-orange-500/[0.12] transition-colors duration-500 overflow-hidden">

    <div class="relative max-w-4xl mx-auto text-center">

      <!-- Content -->
      <h2 class="text-4xl sm:text-5xl md:text-6xl font-semibold text-blue-950 dark:text-white mb-6 tracking-tight text-balance transition-colors duration-300">
        {{ title }}
      </h2>

      <p class="text-xl text-blue-950/70 dark:text-orange-50 leading-relaxed text-pretty mb-10 max-w-2xl mx-auto transition-colors duration-300">
        {{ description }}
      </p>
      
      <!-- Buttons with 3D printed styling -->
      <div class="flex flex-col sm:flex-row gap-4 justify-center">
        <router-link
          :to="getAuthenticatedRedirect"
          class="btn-3d btn-accent group relative inline-flex items-center justify-center gap-3 px-8 py-4 text-blue-950 rounded-full font-medium text-lg overflow-hidden border border-white/60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0a0a0a]"
        >
          <!-- Top edge highlight for 3D effect -->
          <span class="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/70 to-transparent"></span>
          <!-- Bottom edge shadow for depth -->
          <span class="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-blue-900/15 to-transparent"></span>
          <span class="relative">{{ primaryButtonText }}</span>
          <svg class="relative w-5 h-5 transition-transform duration-300 group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
          </svg>
        </router-link>
        
        <router-link 
          v-if="showSecondaryButton"
          :to="secondaryButtonTo"
          class="group relative inline-flex items-center justify-center gap-2 px-8 py-4 bg-transparent text-orange-700 dark:text-orange-300 rounded-full font-medium text-lg overflow-hidden border-2 border-orange-500/60 dark:border-orange-400/50 hover:bg-orange-50 dark:hover:bg-orange-500/10 transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-orange-500/40 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0a0a0a]"
        >
          <span class="relative">{{ secondaryButtonText }}</span>
        </router-link>
      </div>
    </div>
  </section>
</template>

<script>
import { defineComponent, computed } from 'vue'
import { useAuthStore } from '@/shared/stores/auth'

export default defineComponent({
  name: 'CTASection',
  props: {
    title: {
      type: String,
      default: 'Ready to build?'
    },
    description: {
      type: String,
      default: 'Transform your ideas into production-ready web applications. Start building for free today.'
    },
    primaryButtonText: {
      type: String,
      default: 'Get Started'
    },
    primaryButtonTo: {
      type: [String, Object],
      default: '/products/imagi/projects'
    },
    showSecondaryButton: {
      type: Boolean,
      default: false
    },
    secondaryButtonText: {
      type: String,
      default: 'Learn More'
    },
    secondaryButtonTo: {
      type: [String, Object],
      default: '/docs'
    }
  },
  setup(props) {
    const authStore = useAuthStore()
    const isAuthenticated = computed(() => authStore.isAuthenticated)
    
    const getAuthenticatedRedirect = computed(() => {
      return isAuthenticated.value 
        ? (typeof props.primaryButtonTo === 'string' ? props.primaryButtonTo : '/products/imagi/projects')
        : '/auth/signin'
    })
    
    return {
      isAuthenticated,
      getAuthenticatedRedirect
    }
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
</style>
