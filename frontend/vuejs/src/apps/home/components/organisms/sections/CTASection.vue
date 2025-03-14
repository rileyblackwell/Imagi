<!-- CTA Section Component -->
<template>
  <section class="py-12 px-4 sm:px-6 lg:px-8 relative">
    <div class="max-w-4xl mx-auto relative">
      <!-- Main CTA Card -->
      <div class="group relative rounded-2xl overflow-hidden bg-gradient-to-b from-dark-800/80 to-dark-900/80 backdrop-blur-xl border border-dark-700/40 hover:border-primary-500/30 transition-all duration-300 shadow-[0_4px_20px_-2px_rgba(0,0,0,0.3)] hover:shadow-xl">
        <!-- Card top highlight -->
        <div class="absolute top-0 inset-x-0 h-px bg-gradient-to-r from-primary-500/0 via-primary-500/40 to-primary-500/0"></div>
        
        <!-- Subtle gradient background -->
        <div class="absolute inset-0 bg-gradient-to-br from-primary-600/10 via-violet-600/5 to-purple-600/10"></div>
        
        <!-- Card inner glow -->
        <div class="absolute inset-0 bg-gradient-to-br from-primary-500/5 to-violet-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
        
        <!-- Subtle decorative elements -->
        <div class="absolute inset-0">
          <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-5"></div>
          <div class="absolute top-0 right-0 w-80 h-80 bg-primary-500/5 rounded-full blur-[120px] opacity-30"></div>
          <div class="absolute bottom-0 left-0 w-60 h-60 bg-violet-500/5 rounded-full blur-[100px] opacity-20"></div>
        </div>

        <!-- Content Container -->
        <div class="relative z-10 px-6 py-10 md:px-10">
          <div class="max-w-2xl mx-auto text-center">
            <!-- Main Text -->
            <h2 class="text-3xl md:text-4xl font-bold text-white mb-4 leading-tight">
              {{ title }}
              <span class="bg-gradient-to-r from-primary-300 to-violet-300 bg-clip-text text-transparent">
                {{ highlightedText }}
              </span>
            </h2>

            <p class="text-lg text-white/80 mb-6 max-w-xl mx-auto">
              {{ description }}
              <span class="font-medium text-primary-300">{{ highlightedStat }}</span>
              {{ descriptionSuffix }}
            </p>

            <!-- Action Buttons -->
            <div class="flex flex-col sm:flex-row items-center justify-center gap-4">
              <!-- Start Building Button -->
              <HomeNavbarButton
                :to="{ name: isAuthenticated ? 'builder-dashboard' : 'login' }"
                class="group relative w-full sm:w-auto min-w-[180px] !h-11 px-5 rounded-xl bg-primary-500/80 hover:bg-primary-500/90 border border-primary-500/30 hover:border-primary-400/70 transition-all duration-300 transform hover:-translate-y-1 shadow-md"
              >
                <span class="relative z-10 flex items-center justify-center text-base font-medium text-white">
                  {{ primaryButtonText }}
                  <i class="fas fa-arrow-right ml-2 transform group-hover:translate-x-1 transition-transform"></i>
                </span>
              </HomeNavbarButton>

              <!-- Contact Sales Button -->
              <HomeNavbarButton
                :to="secondaryButtonTo"
                class="group relative w-full sm:w-auto min-w-[180px] !h-11 px-5 rounded-xl bg-dark-700/50 hover:bg-dark-700/80 border border-dark-700/70 hover:border-primary-500/30 transition-all duration-300 transform hover:-translate-y-1 shadow-sm"
              >
                <span class="relative z-10 flex items-center justify-center text-base font-medium text-white">
                  {{ secondaryButtonText }}
                  <i class="fas fa-arrow-up-right-from-square ml-2 transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform"></i>
                </span>
              </HomeNavbarButton>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { defineComponent, computed } from 'vue'
import { useAuthStore } from '@/shared/stores/auth'
import { HomeNavbarButton } from '@/apps/home/components/atoms/buttons'

export default defineComponent({
  name: 'CTASection',
  components: {
    HomeNavbarButton
  },
  props: {
    title: {
      type: String,
      default: 'Ready to Transform Your'
    },
    highlightedText: {
      type: String,
      default: 'Development Process?'
    },
    description: {
      type: String,
      default: 'Join thousands of developers building amazing applications'
    },
    highlightedStat: {
      type: String,
      default: '10x faster'
    },
    descriptionSuffix: {
      type: String,
      default: 'with AI.'
    },
    primaryButtonText: {
      type: String,
      default: 'Start Building Free'
    },
    secondaryButtonText: {
      type: String,
      default: 'Contact Sales'
    },
    secondaryButtonTo: {
      type: String,
      default: '/contact'
    }
  },
  setup() {
    const authStore = useAuthStore()
    
    return {
      isAuthenticated: computed(() => authStore.isAuthenticated)
    }
  }
})
</script> 