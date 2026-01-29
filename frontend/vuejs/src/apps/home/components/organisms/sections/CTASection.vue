<!-- CTA Section - Clean Apple/Cursor-inspired design -->
<template>
  <section class="relative py-24 sm:py-32 px-6 sm:px-8 lg:px-12 bg-gray-50 dark:bg-[#0f0f0f] transition-colors duration-500 overflow-hidden">
    
    <div class="relative max-w-4xl mx-auto text-center">
      
      <!-- Content -->
      <h2 class="text-4xl sm:text-5xl md:text-6xl font-semibold text-gray-900 dark:text-white mb-6 tracking-tight transition-colors duration-300">
        {{ title }}
      </h2>
      
      <p class="text-xl text-gray-500 dark:text-white/60 mb-10 max-w-2xl mx-auto transition-colors duration-300">
        {{ description }}
      </p>
      
      <!-- Buttons with enhanced styling -->
      <div class="flex flex-col sm:flex-row gap-4 justify-center">
        <router-link 
          :to="getAuthenticatedRedirect"
          class="group relative inline-flex items-center justify-center gap-3 px-8 py-4 bg-gray-900 dark:bg-white text-white dark:text-gray-900 rounded-full font-medium text-lg transition-all duration-300 hover:scale-[1.02] hover:shadow-2xl overflow-hidden"
        >
          <!-- Subtle shine effect on hover -->
          <span class="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent translate-x-[-200%] group-hover:translate-x-[200%] transition-transform duration-700 ease-out"></span>
          <span class="relative">{{ primaryButtonText }}</span>
          <svg class="relative w-5 h-5 transition-transform duration-300 group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
          </svg>
        </router-link>
        
        <router-link 
          v-if="showSecondaryButton"
          :to="secondaryButtonTo"
          class="group inline-flex items-center justify-center gap-2 px-8 py-4 bg-white/80 dark:bg-white/5 backdrop-blur-sm text-gray-700 dark:text-white/80 border border-gray-200/80 dark:border-white/10 rounded-full font-medium text-lg transition-all duration-300 hover:border-gray-300 dark:hover:border-white/20 hover:shadow-lg hover:shadow-gray-200/30 dark:hover:shadow-none"
        >
          {{ secondaryButtonText }}
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
      default: '/products/oasis/builder/dashboard'
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
        ? (typeof props.primaryButtonTo === 'string' ? props.primaryButtonTo : '/products/oasis/builder/dashboard')
        : '/auth/login'
    })
    
    return {
      isAuthenticated,
      getAuthenticatedRedirect
    }
  }
})
</script>
