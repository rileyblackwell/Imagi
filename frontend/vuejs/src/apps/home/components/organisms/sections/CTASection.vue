<!-- CTA Section Component -->
<template>
  <section class="py-16 sm:py-24 md:py-36 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
    <!-- Decorative background elements -->
    <div class="absolute inset-0 pointer-events-none">
      <!-- Subtle pattern overlay -->
      <div class="absolute inset-0 bg-[url('/dot-pattern.svg')] opacity-[0.03]"></div>
      
      <!-- Glowing orbs - matching the style from other sections -->
      <div class="absolute -top-[10%] right-[15%] w-[300px] sm:w-[500px] md:w-[800px] h-[300px] sm:h-[500px] md:h-[800px] rounded-full bg-indigo-600/5 blur-[80px] sm:blur-[150px]"></div>
      <div class="absolute bottom-[5%] left-[20%] w-[200px] sm:w-[400px] md:w-[600px] h-[200px] sm:h-[400px] md:h-[600px] rounded-full bg-fuchsia-600/5 blur-[60px] sm:blur-[120px]"></div>
      
      <!-- Animated gradient line -->
      <div class="absolute left-0 right-0 top-1/2 h-px bg-gradient-to-r from-transparent via-indigo-500/20 to-transparent"></div>
    </div>
    
    <div class="max-w-5xl mx-auto relative z-10">
      <!-- Main CTA Card -->
      <div class="group relative rounded-2xl sm:rounded-3xl overflow-hidden bg-dark-900/40 backdrop-blur-sm border border-gray-800/60 transition-all duration-500 hover:shadow-[0_0_25px_-5px_rgba(99,102,241,0.5)] hover:-translate-y-2">
        <!-- Card top highlight -->
        <div class="absolute top-0 inset-x-0 h-px bg-gradient-to-r from-indigo-500/0 via-indigo-500/60 to-indigo-500/0 opacity-60"></div>
        
        <!-- Background gradient -->
        <div class="absolute inset-0 bg-gradient-to-br opacity-10 -z-10 transition-opacity duration-300 group-hover:opacity-20 from-indigo-900 to-violet-900"></div>
        
        <!-- Subtle decorative elements -->
        <div class="absolute inset-0">
          <div class="absolute inset-0 bg-[url('/dot-pattern.svg')] opacity-[0.03]"></div>
          <div class="absolute -bottom-20 -right-20 w-32 sm:w-40 h-32 sm:h-40 rounded-full opacity-10 blur-3xl transition-opacity duration-500 group-hover:opacity-20 bg-indigo-500"></div>
        </div>

        <!-- Content Container -->
        <div class="relative z-10 px-6 py-12 sm:px-8 sm:py-16 md:px-12 md:py-20">
          <div class="max-w-3xl mx-auto text-center">
            <!-- Section header design matching other sections -->
            <div class="inline-block px-3 sm:px-4 py-1 sm:py-1.5 bg-indigo-500/10 rounded-full mb-3 sm:mb-4">
              <span class="text-indigo-400 font-semibold text-xs sm:text-sm tracking-wider">GET STARTED TODAY</span>
            </div>
            
            <!-- Main Text with staggered animation -->
            <div class="animate-fade-in animation-delay-100">
              <h2 class="text-3xl sm:text-4xl md:text-5xl font-bold text-white mb-4 sm:mb-6 leading-tight">
                {{ title }}
                <span class="bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">
                  {{ highlightedText }}
                </span>
              </h2>
            </div>

            <div class="animate-fade-in animation-delay-200">
              <p class="text-base sm:text-lg md:text-xl text-gray-300 mb-6 sm:mb-10 max-w-2xl mx-auto leading-relaxed">
                {{ description }}
                <span class="font-semibold bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">
                  {{ highlightedStat }}
                </span>
                {{ descriptionSuffix }}
              </p>
              
              <!-- Decorative element matching other sections -->
              <div class="w-16 sm:w-24 h-1 bg-gradient-to-r from-indigo-500 to-violet-500 rounded-full mx-auto mt-4 sm:mt-6 mb-6 sm:mb-10"></div>
            </div>

            <!-- Action Buttons with staggered animation -->
            <div class="flex flex-col sm:flex-row items-center justify-center gap-4 sm:gap-5 animate-fade-in animation-delay-300">
              <!-- Start Building Button -->
              <HomeNavbarButton
                :to="{ name: isAuthenticated ? 'builder-dashboard' : 'login' }"
                class="group relative w-full sm:w-auto min-w-[160px] sm:min-w-[200px] !h-12 sm:!h-14 px-6 sm:px-8 rounded-xl bg-indigo-600 hover:bg-indigo-500 border border-indigo-500/40 hover:border-indigo-400/50 transition-all duration-300 transform hover:-translate-y-1 shadow-lg hover:shadow-indigo-500/20"
              >
                <span class="relative z-10 flex items-center justify-center text-base sm:text-lg font-medium text-white">
                  {{ primaryButtonText }}
                  <i class="fas fa-arrow-right ml-2 transform group-hover:translate-x-1 transition-transform"></i>
                </span>
                <div class="absolute inset-0 rounded-xl bg-gradient-to-r from-indigo-500 to-indigo-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300 blur-sm -z-10"></div>
              </HomeNavbarButton>

              <!-- Contact Sales Button -->
              <HomeNavbarButton
                :to="secondaryButtonTo"
                class="group relative w-full sm:w-auto min-w-[160px] sm:min-w-[200px] !h-12 sm:!h-14 px-6 sm:px-8 rounded-xl bg-dark-800/70 hover:bg-dark-800 border border-indigo-500/30 hover:border-indigo-500/50 transition-all duration-300 transform hover:-translate-y-1 shadow-lg shadow-indigo-900/20"
              >
                <span class="relative z-10 flex items-center justify-center text-base sm:text-lg font-medium text-white group-hover:text-white">
                  {{ secondaryButtonText }}
                  <i class="fas fa-arrow-up-right-from-square ml-2 transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform"></i>
                </span>
              </HomeNavbarButton>
            </div>
            
            <!-- Testimonial snippet with updated styling -->
            <div class="mt-12 max-w-md mx-auto animate-fade-in animation-delay-400 opacity-90 hover:opacity-100 transition-opacity duration-300">
              <div class="flex items-center justify-center">
                <div class="flex -space-x-2">
                  <div class="w-8 h-8 rounded-full bg-dark-800 border border-indigo-500/30 flex items-center justify-center text-xs text-indigo-400">
                    <i class="fas fa-user"></i>
                  </div>
                  <div class="w-8 h-8 rounded-full bg-dark-800 border border-indigo-500/30 flex items-center justify-center text-xs text-indigo-400">
                    <i class="fas fa-user"></i>
                  </div>
                </div>
                <div class="ml-4 text-left">
                  <p class="text-gray-300 text-sm">{{ testimonialQuote }}</p>
                  <p class="text-indigo-400 text-xs mt-1">— {{ testimonialAuthor }}</p>
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
      default: 'Start Building Free'
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

@keyframes float-particle-1 {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  25% { transform: translate(40px, 50px) rotate(45deg); }
  50% { transform: translate(80px, 0px) rotate(90deg); }
  75% { transform: translate(40px, -50px) rotate(45deg); }
}

@keyframes float-particle-2 {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  25% { transform: translate(-50px, 40px) rotate(-45deg); }
  50% { transform: translate(-70px, 0px) rotate(-90deg); }
  75% { transform: translate(-40px, -60px) rotate(-45deg); }
}

@keyframes float-particle-3 {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  33% { transform: translate(60px, -50px) rotate(60deg); }
  66% { transform: translate(-60px, -30px) rotate(-60deg); }
}

@keyframes float-particle-4 {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  33% { transform: translate(-40px, 60px) rotate(-45deg); }
  66% { transform: translate(50px, 40px) rotate(45deg); }
}

@keyframes float-particle-5 {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  25% { transform: translate(30px, 30px) rotate(30deg); }
  50% { transform: translate(0px, 60px) rotate(0deg); }
  75% { transform: translate(-30px, 30px) rotate(-30deg); }
}

/* Animation classes */
.animate-fade-in {
  animation: fade-in 0.7s ease-out forwards;
}

.animate-float-particle-1 {
  animation: float-particle-1 15s ease-in-out infinite;
}

.animate-float-particle-2 {
  animation: float-particle-2 18s ease-in-out infinite;
}

.animate-float-particle-3 {
  animation: float-particle-3 20s ease-in-out infinite;
}

.animate-float-particle-4 {
  animation: float-particle-4 22s ease-in-out infinite;
}

.animate-float-particle-5 {
  animation: float-particle-5 25s ease-in-out infinite;
}

/* Animation delays */
.animation-delay-100 {
  animation-delay: 100ms;
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

.animation-delay-500 {
  animation-delay: 500ms;
}

/* Removed lightning bolt animation as it's no longer needed */
</style> 