<!-- Hero Section Component -->
<template>
  <section class="relative min-h-[90vh] md:min-h-[80vh] flex items-center justify-center overflow-hidden py-24 md:py-20 mt-16 sm:mt-0">
    <!-- Enhanced Background Effects -->
    <div class="absolute inset-0 bg-dark-950">
      <div class="absolute inset-0 bg-gradient-to-br from-primary-500/10 via-dark-950 to-violet-500/10"></div>
      <div class="absolute top-20 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-gradient-to-r from-primary-500/10 to-violet-500/10 rounded-full blur-[120px] opacity-70"></div>
      <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.02]"></div>
    </div>

    <!-- Content -->
    <div class="relative w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex flex-col lg:flex-row items-center gap-8 lg:gap-16">
        <!-- Left side - Main content -->
        <div class="flex-1 text-center lg:text-left">
          <HeroBadge text="AI-Powered Web Development" />

          <h1 class="text-3xl sm:text-4xl lg:text-6xl font-bold tracking-tight mb-6">
            <span class="text-white block mb-1">{{ titleLine1 }}</span>
            <span class="text-white block mb-1">{{ titleLine2 }}</span>
            <GradientText variant="primary" class="font-bold block text-4xl sm:text-5xl lg:text-7xl">
              {{ highlightedTitle }}
            </GradientText>
          </h1>

          <p class="text-lg sm:text-xl text-gray-300 mb-8 max-w-xl">
            {{ description }}
          </p>

          <!-- Buttons -->
          <div class="flex flex-col sm:flex-row items-center gap-4 justify-center lg:justify-start">
            <HomeNavbarButton
              :to="{ name: isAuthenticated ? 'builder-dashboard' : 'login' }"
              class="group relative w-full sm:w-auto !h-12 px-8 rounded-xl border border-primary-500/30 hover:border-primary-500/50 bg-dark-900/80 hover:bg-dark-800/80 backdrop-blur-sm transition-all duration-300 transform hover:-translate-y-1"
            >
              <span class="relative z-10 flex items-center justify-center text-base font-medium text-white group-hover:text-white/90">
                {{ primaryButtonText }}
                <i class="fas fa-arrow-right ml-2 transform group-hover:translate-x-1 transition-transform duration-300"></i>
              </span>
            </HomeNavbarButton>

            <a 
              :href="secondaryButtonHref" 
              class="group flex items-center gap-3 text-gray-300 hover:text-white transition-all duration-300 px-6 py-3 rounded-xl border border-dark-700 hover:border-primary-500/30 bg-dark-900/50 hover:bg-dark-800/80 backdrop-blur-sm"
            >
              <div class="w-7 h-7 rounded-full bg-dark-700 group-hover:bg-primary-500/20 flex items-center justify-center transition-all duration-300">
                <i class="fas fa-play text-xs text-primary-400"></i>
              </div>
              <span class="font-medium">{{ secondaryButtonText }}</span>
            </a>
          </div>
        </div>

        <!-- Right side - Interactive Demo -->
        <div class="flex-1">
          <AnimatedTerminal />
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { defineComponent, computed } from 'vue'
import { useAuthStore } from '@/shared/stores/auth'
import { GradientText } from '@/apps/home/components/atoms'
import { HomeNavbarButton } from '@/apps/home/components/atoms/buttons'
import { AnimatedTerminal } from '@/apps/home/components/molecules/demo'
import HeroBadge from '@/apps/home/components/atoms/badges/HeroBadge.vue'

export default defineComponent({
  name: 'HeroSection',
  components: {
    GradientText,
    HomeNavbarButton,
    AnimatedTerminal,
    HeroBadge
  },
  props: {
    titleLine1: {
      type: String,
      default: 'Transform Your'
    },
    titleLine2: {
      type: String,
      default: 'Ideas Into'
    },
    highlightedTitle: {
      type: String,
      default: 'Web Applications'
    },
    description: {
      type: String,
      default: 'Create professional web applications using natural language. Describe your vision, and watch as AI brings it to life.'
    },
    primaryButtonText: {
      type: String,
      default: 'Start Building'
    },
    secondaryButtonText: {
      type: String,
      default: 'How It Works'
    },
    secondaryButtonHref: {
      type: String,
      default: '#how-it-works'
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