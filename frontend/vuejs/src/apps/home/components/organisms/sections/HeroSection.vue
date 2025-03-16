<!-- Hero Section Component -->
<template>
  <section class="relative min-h-[80vh] sm:min-h-[85vh] md:min-h-[90vh] flex items-center justify-center overflow-hidden py-12 sm:py-16 md:py-24 mt-20 sm:mt-16 md:mt-0">
    <!-- Enhanced Background Effects -->
    <div class="absolute inset-0">
      <!-- Base gradient background -->
      <div class="absolute inset-0 bg-gradient-to-br from-dark-950 via-dark-900 to-dark-950"></div>
      
      <!-- Animated glow effects -->
      <div class="absolute top-20 left-1/2 -translate-x-1/2 w-[90%] max-w-[900px] h-[500px] bg-gradient-to-r from-primary-500/10 to-violet-500/10 rounded-full blur-[120px] opacity-70 animate-pulse-slower"></div>
      
      <!-- Subtle grid pattern -->
      <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.03]"></div>
      
      <!-- Removing decorative dot elements as requested -->
    </div>

    <!-- Content -->
    <div class="relative w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex flex-col lg:flex-row items-center gap-8 sm:gap-12 lg:gap-20">
        <!-- Left side - Main content -->
        <div class="flex-1 text-center lg:text-left pt-6 sm:pt-0">
          <!-- Enhanced badge with animation -->
          <div class="mb-4 sm:mb-6 inline-block animate-fade-in-up">
            <HeroBadge text="AI-Powered Web Development" class="shadow-glow-sm" />
          </div>

          <!-- Enhanced title with animation - responsive sizes -->
          <h1 class="text-2xl sm:text-3xl md:text-4xl lg:text-6xl font-bold tracking-tight mb-4 sm:mb-8 animate-fade-in-up animation-delay-150">
            <span class="text-white block mb-2">{{ titleLine1 }}</span>
            <span class="text-white block mb-2">{{ titleLine2 }}</span>
            <GradientText variant="primary" class="font-bold block text-3xl sm:text-4xl md:text-5xl lg:text-7xl tracking-tighter mt-2">
              {{ highlightedTitle }}
            </GradientText>
          </h1>

          <!-- Enhanced description with animation -->
          <p class="text-base sm:text-lg md:text-xl text-gray-300 mb-6 sm:mb-10 max-w-2xl mx-auto lg:mx-0 animate-fade-in-up animation-delay-300 leading-relaxed">
            {{ description }}
          </p>

          <!-- Enhanced buttons with animation -->
          <div class="flex flex-col sm:flex-row items-center gap-4 sm:gap-5 justify-center lg:justify-start animate-fade-in-up animation-delay-450">
            <!-- Primary button -->
            <HomeNavbarButton
              :to="{ name: isAuthenticated ? 'builder-dashboard' : 'login' }"
              class="group relative w-full sm:w-auto !h-12 sm:!h-14 px-6 sm:px-8 rounded-xl bg-primary-600 hover:bg-primary-500 border border-primary-500/40 hover:border-primary-400/70 transition-all duration-300 transform hover:-translate-y-1 shadow-lg hover:shadow-primary-600/20"
            >
              <span class="relative z-10 flex items-center justify-center text-base sm:text-lg font-medium text-white">
                {{ primaryButtonText }}
                <i class="fas fa-arrow-right ml-2 sm:ml-3 transform group-hover:translate-x-1 transition-transform duration-300"></i>
              </span>
              <div class="absolute inset-0 rounded-xl bg-gradient-to-r from-primary-500 to-primary-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300 blur-sm -z-10"></div>
            </HomeNavbarButton>

            <!-- Secondary button -->
            <a 
              :href="secondaryButtonHref" 
              class="group flex items-center gap-2 sm:gap-3 text-gray-300 hover:text-white transition-all duration-300 px-6 sm:px-8 py-3 sm:py-4 rounded-xl border border-gray-700/30 hover:border-primary-500/30 bg-dark-800/50 hover:bg-dark-700/50 backdrop-blur-sm transform hover:-translate-y-1"
            >
              <div class="w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-dark-700/80 group-hover:bg-primary-500/20 flex items-center justify-center transition-all duration-300">
                <i class="fas fa-play text-xs text-primary-400"></i>
              </div>
              <span class="font-medium text-base sm:text-lg">{{ secondaryButtonText }}</span>
            </a>
          </div>
          
          <!-- Removing social proof section as requested -->
        </div>

        <!-- Right side - Interactive Demo -->
        <div class="flex-1 w-full max-w-xl mx-auto lg:mx-0 mt-10 lg:mt-0 animate-fade-in-up animation-delay-300">
          <div class="relative">
            <!-- Glow effect behind terminal -->
            <div class="absolute -inset-0.5 bg-gradient-to-r from-primary-500/20 to-violet-500/20 rounded-xl blur-md"></div>
            
            <!-- Terminal component -->
            <div class="relative rounded-xl overflow-hidden border border-dark-700/50 shadow-2xl">
              <AnimatedTerminal />
            </div>
            
            <!-- Decorative elements -->
            <div class="absolute -z-10 -bottom-6 -right-6 w-16 sm:w-24 h-16 sm:h-24 bg-primary-500/10 rounded-full blur-xl"></div>
            <div class="absolute -z-10 -top-6 -left-6 w-24 sm:w-32 h-24 sm:h-32 bg-violet-500/10 rounded-full blur-xl"></div>
          </div>
        </div>
      </div>
      
      <!-- Removing scroll indicator as requested -->
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

<style scoped>
/* Animation keyframes */
@keyframes fade-in-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes ping-slow {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  75%, 100% {
    transform: scale(2.5);
    opacity: 0;
  }
}

@keyframes pulse-slower {
  0%, 100% {
    opacity: 0.5;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.05);
  }
}

@keyframes bounce-slow {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(10px);
  }
}

/* Animation classes */
.animate-fade-in-up {
  animation: fade-in-up 0.7s ease-out forwards;
}

.animate-ping-slow {
  animation: ping-slow 3s cubic-bezier(0, 0, 0.2, 1) infinite;
}

.animate-pulse-slower {
  animation: pulse-slower 6s ease-in-out infinite;
}

.animate-bounce-slow {
  animation: bounce-slow 2s ease-in-out infinite;
}

/* Animation delays */
.animation-delay-150 {
  animation-delay: 150ms;
}

.animation-delay-300 {
  animation-delay: 300ms;
}

.animation-delay-450 {
  animation-delay: 450ms;
}

.animation-delay-600 {
  animation-delay: 600ms;
}

.animation-delay-750 {
  animation-delay: 750ms;
}

/* Shadow effects */
.shadow-glow-sm {
  box-shadow: 0 0 12px 2px rgba(59, 130, 246, 0.15);
}
</style> 