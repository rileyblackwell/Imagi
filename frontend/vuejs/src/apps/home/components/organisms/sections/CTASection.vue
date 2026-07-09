<!-- CTA Section - Clean Apple/Cursor-inspired design -->
<template>
  <section class="relative py-24 sm:py-32 px-6 sm:px-8 lg:px-12 bg-white dark:bg-[#0a0a0a] transition-colors duration-500 overflow-hidden">

    <div class="relative max-w-5xl mx-auto">

      <!-- Elegant gradient-bordered panel -->
      <div class="relative rounded-3xl p-px bg-gradient-to-br from-gray-200 via-gray-100 to-gray-200 dark:from-white/15 dark:via-white/[0.04] dark:to-white/15 overflow-hidden">
        <div class="relative rounded-[calc(1.5rem-1px)] bg-gray-50 dark:bg-[#0d0d0d] px-8 py-16 sm:px-12 sm:py-20 text-center overflow-hidden">

          <!-- Ambient glow inside the panel -->
          <div class="absolute inset-0 pointer-events-none">
            <div class="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-gradient-radial from-blue-400/10 dark:from-blue-500/[0.12] via-transparent to-transparent rounded-full blur-3xl"></div>
            <div class="absolute bottom-0 right-1/4 w-[400px] h-[300px] bg-gradient-radial from-violet-400/[0.07] dark:from-violet-500/[0.08] via-transparent to-transparent rounded-full blur-3xl"></div>
          </div>

          <!-- Content -->
          <h2 class="relative text-4xl sm:text-5xl md:text-6xl font-semibold text-gray-900 dark:text-white mb-6 tracking-tight transition-colors duration-300">
            {{ title }}
          </h2>

          <p class="relative text-xl text-gray-600 dark:text-white/70 mb-10 max-w-2xl mx-auto transition-colors duration-300">
            {{ description }}
          </p>

          <!-- Buttons with 3D printed styling -->
          <div class="relative flex flex-col sm:flex-row gap-4 justify-center">
            <router-link
              :to="getAuthenticatedRedirect"
              class="btn-3d group relative inline-flex items-center justify-center gap-3 px-8 py-4 bg-gradient-to-b from-gray-800 via-gray-900 to-gray-950 dark:from-white dark:via-gray-50 dark:to-gray-100 text-white dark:text-gray-900 rounded-full font-medium text-lg transition-all duration-300 overflow-hidden border border-gray-700/50 dark:border-gray-300/50 hover:-translate-y-0.5"
            >
              <!-- Top edge highlight for 3D effect -->
              <span class="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/30 to-transparent dark:via-white/60"></span>
              <!-- Bottom edge shadow for depth -->
              <span class="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-black/30 to-transparent dark:via-black/10"></span>
              <span class="relative">{{ primaryButtonText }}</span>
              <svg class="relative w-5 h-5 transition-transform duration-300 group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </router-link>

            <router-link
              v-if="showSecondaryButton"
              :to="secondaryButtonTo"
              class="group relative inline-flex items-center justify-center gap-2 px-8 py-4 rounded-full font-medium text-lg text-gray-900 dark:text-white border border-gray-300 dark:border-white/15 bg-white/60 dark:bg-white/[0.04] backdrop-blur-md transition-all duration-300 hover:-translate-y-0.5 hover:border-gray-400 dark:hover:border-white/25"
            >
              <span class="relative">{{ secondaryButtonText }}</span>
            </router-link>
          </div>
        </div>
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
