<!-- CTA Section Component -->
<template>
  <section class="py-16 sm:py-24 md:py-36 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
    <!-- Decorative background elements -->
    <div class="absolute inset-0 pointer-events-none">
      <!-- Subtle pattern overlay -->
      <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.03]"></div>
      
      <!-- Glowing orbs - matching the style from other sections -->
      <div class="absolute -top-[10%] right-[15%] w-[300px] sm:w-[500px] md:w-[800px] h-[300px] sm:h-[500px] md:h-[800px] rounded-full bg-primary-600/5 blur-[80px] sm:blur-[150px] animate-pulse-slow"></div>
      <div class="absolute bottom-[5%] left-[20%] w-[200px] sm:w-[400px] md:w-[600px] h-[200px] sm:h-[400px] md:h-[600px] rounded-full bg-violet-600/5 blur-[60px] sm:blur-[120px] animate-pulse-slow animation-delay-150"></div>
    </div>
    
    <div class="max-w-5xl mx-auto relative z-10">
      <!-- Main CTA Card with enhanced glass morphism -->
      <div class="group relative transform transition-all duration-300 hover:-translate-y-2">
        <!-- Enhanced glass morphism effect with stronger gradient glow -->
        <div class="absolute -inset-0.5 bg-gradient-to-r from-primary-500/70 to-violet-500/70 rounded-2xl opacity-70 group-hover:opacity-90 blur group-hover:blur-md transition-all duration-300"></div>
        
        <div class="relative bg-dark-900/70 backdrop-blur-xl rounded-xl overflow-hidden border border-primary-500/30 group-hover:border-primary-500/50 transition-all duration-300">
          <!-- Gradient header line -->
          <div class="h-3 w-full bg-gradient-to-r from-primary-500 to-violet-500"></div>
          
          <!-- Subtle decorative elements -->
          <div class="absolute inset-0 pointer-events-none">
            <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-10"></div>
          </div>

          <!-- Content Container -->
          <div class="relative z-10 px-6 py-12 sm:px-8 sm:py-16 md:px-12 md:py-20">
            <div class="max-w-3xl mx-auto text-center">
              <!-- Main Text with staggered animation -->
              <div class="animate-fade-in animation-delay-100">
                <h2 class="text-3xl sm:text-4xl md:text-5xl font-bold text-white mb-4 sm:mb-6 leading-tight">
                  {{ title }}
                  <span class="bg-gradient-to-r from-primary-300 to-violet-300 bg-clip-text text-transparent">
                    {{ highlightedText }}
                  </span>
                </h2>
              </div>

              <div class="animate-fade-in animation-delay-200">
                <p class="text-lg text-white/90 mb-8 max-w-2xl mx-auto leading-relaxed">
                  {{ description }}
                  <span class="font-semibold text-primary-200">{{ highlightedStat }}</span>
                  {{ descriptionSuffix }}
                </p>
              </div>

              <!-- Action Buttons with staggered animation -->
              <div class="flex flex-col sm:flex-row items-center justify-center gap-4 sm:gap-5 animate-fade-in animation-delay-300">
                <!-- Start Building Button -->
                <HomeNavbarButton
                  :to="{ name: isAuthenticated ? 'builder-dashboard' : 'login' }"
                  class="group relative w-full sm:w-auto min-w-[160px] sm:min-w-[200px] !h-12 sm:!h-14 px-6 sm:px-8 rounded-xl bg-white/10 hover:bg-white/20 border border-white/30 hover:border-white/50 transition-all duration-300 transform hover:-translate-y-1"
                >
                  <span class="relative z-10 flex items-center justify-center text-base sm:text-lg font-bold text-white">
                    {{ primaryButtonText }}
                    <i class="fas fa-arrow-right ml-2 transform group-hover:translate-x-1 transition-transform duration-300"></i>
                  </span>
                </HomeNavbarButton>

                <!-- Contact Sales Button -->
                <HomeNavbarButton
                  :to="secondaryButtonTo"
                  class="group relative w-full sm:w-auto min-w-[160px] sm:min-w-[200px] !h-12 sm:!h-14 px-6 sm:px-8 rounded-xl bg-dark-800/30 hover:bg-dark-800/50 border border-white/20 hover:border-white/30 backdrop-blur-sm transition-all duration-300 transform hover:-translate-y-1"
                >
                  <span class="relative z-10 flex items-center justify-center text-base sm:text-lg font-medium text-white/90 group-hover:text-white">
                    {{ secondaryButtonText }}
                    <i class="fas fa-arrow-up-right-from-square ml-2 transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform duration-300"></i>
                  </span>
                </HomeNavbarButton>
              </div>
              
              <!-- Enhanced testimonial with modernized styling -->
              <div class="mt-12 max-w-md mx-auto animate-fade-in animation-delay-400">
                <div class="group relative transform transition-all duration-300 hover:-translate-y-1">
                  <div class="absolute -inset-0.5 bg-gradient-to-r from-primary-500/30 to-violet-500/30 rounded-xl opacity-0 group-hover:opacity-70 blur group-hover:blur-sm transition-all duration-300"></div>
                  
                  <div class="relative px-4 py-3 bg-dark-900/50 backdrop-blur-sm rounded-xl border border-white/10 group-hover:border-primary-500/20 transition-all duration-300">
                    <div class="flex items-center">
                      <div class="flex -space-x-2">
                        <div class="w-8 h-8 rounded-full bg-dark-800 border border-primary-500/30 flex items-center justify-center text-xs text-primary-400">
                          <i class="fas fa-user"></i>
                        </div>
                        <div class="w-8 h-8 rounded-full bg-dark-800 border border-primary-500/30 flex items-center justify-center text-xs text-primary-400">
                          <i class="fas fa-user"></i>
                        </div>
                      </div>
                      <div class="ml-4 text-left">
                        <p class="text-white/90 text-sm">{{ testimonialQuote }}</p>
                        <p class="text-primary-400 text-xs mt-1">— {{ testimonialAuthor }}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
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
      default: 'Start Building'
    },
    secondaryButtonText: {
      type: String,
      default: 'Contact Sales'
    },
    secondaryButtonTo: {
      type: String,
      default: '/contact'
    },
    testimonialQuote: {
      type: String,
      default: 'This tool completely revolutionized how I build applications.'
    },
    testimonialAuthor: {
      type: String,
      default: 'Full-Stack Developer'
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

<style scoped>
/* Animation keyframes */
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pulse-slow {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 0.8; }
}

/* Animation classes */
.animate-fade-in {
  animation: fade-in 0.7s ease-out forwards;
}

.animate-pulse-slow {
  animation: pulse-slow 3s ease-in-out infinite;
}

/* Animation delays */
.animation-delay-100 {
  animation-delay: 100ms;
}

.animation-delay-150 {
  animation-delay: 150ms;
}

.animation-delay-200 {
  animation-delay: 200ms;
}

.animation-delay-300 {
  animation-delay: 300ms;
}

.animation-delay-400 {
  animation-delay: 400ms;
}
</style> 