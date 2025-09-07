<!-- Hero Section Component -->
<template>
  <section class="relative min-h-[80vh] sm:min-h-[85vh] md:min-h-[90vh] flex items-center justify-center overflow-hidden pt-32 pb-16 sm:pb-20 md:pb-24">
    <!-- Enhanced Background Effects -->
    <div class="absolute inset-0">
      <!-- Base gradient background -->
      <div class="absolute inset-0 bg-gradient-to-br from-dark-950 via-dark-900 to-dark-950"></div>
      
      <!-- Animated glow effects -->
      <div class="absolute top-40 left-1/2 -translate-x-1/2 w-[90%] max-w-[900px] h-[500px] bg-gradient-to-r from-primary-500/10 to-violet-500/10 rounded-full blur-[120px] opacity-70 animate-pulse-slower"></div>
      
      <!-- Subtle grid pattern -->
      <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.03]"></div>
    </div>

    <!-- Content -->
    <div class="relative w-full max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
      <div class="flex flex-col lg:flex-row items-center gap-8 sm:gap-12 lg:gap-20">
        <!-- Left side - Main content -->
        <div class="flex-1 text-center lg:text-left pt-6 sm:pt-0">
          <!-- Modern pill badge -->
          <div class="mb-6 inline-block animate-fade-in-up">
            <div class="inline-flex items-center px-4 py-1.5 bg-gradient-to-r from-indigo-500/10 to-violet-500/10 rounded-full border border-indigo-400/20 backdrop-blur-sm">
              <div class="w-1.5 h-1.5 bg-indigo-400 rounded-full mr-2 animate-pulse"></div>
              <span class="text-indigo-300 font-medium text-sm tracking-wide uppercase">AI-Powered Web Development</span>
            </div>
          </div>

          <!-- Enhanced title with animation - responsive sizes -->
          <h1 class="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight mb-6 sm:mb-8 animate-fade-in-up animation-delay-150">
            <span class="text-white block mb-2">{{ titleLine1 }}</span>
            <span class="text-white block mb-2">{{ titleLine2 }}</span>
            <span class="inline-block bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent font-bold text-4xl sm:text-5xl md:text-6xl lg:text-7xl tracking-tighter mt-2 mb-8 py-1">
              {{ highlightedTitle }}
            </span>
          </h1>

          <!-- Enhanced description with animation -->
          <p class="text-lg sm:text-xl text-gray-300 mb-8 sm:mb-10 max-w-2xl mx-auto lg:mx-0 animate-fade-in-up animation-delay-300 leading-relaxed">
            {{ description }}
          </p>

          <!-- Enhanced buttons with animation -->
          <div class="flex flex-col sm:flex-row items-center gap-4 sm:gap-5 justify-center lg:justify-start animate-fade-in-up animation-delay-450">
            <!-- Primary button with enhanced styling -->
            <HomeNavbarButton
              :to="{ name: isAuthenticated ? 'builder-dashboard' : 'login' }"
              class="group relative w-full sm:w-auto !h-12 sm:!h-14 px-8 rounded-xl bg-gradient-to-r from-indigo-500 to-violet-500 hover:from-indigo-400 hover:to-violet-400 transition-all duration-300 transform hover:-translate-y-1 shadow-lg shadow-indigo-500/25"
            >
              <span class="relative z-10 flex items-center justify-center text-lg font-medium text-white">
                {{ primaryButtonText }}
                <i class="fas fa-arrow-right ml-3 transform group-hover:translate-x-1 transition-transform duration-300"></i>
              </span>
            </HomeNavbarButton>

            <!-- Secondary button with glass morphism -->
            <a 
              :href="secondaryButtonHref" 
              class="group relative flex items-center gap-3 text-gray-300 hover:text-white transition-all duration-300 px-8 py-3 sm:py-4 rounded-xl border border-white/10 hover:border-violet-400/30 bg-white/5 hover:bg-white/8 backdrop-blur-sm transform hover:-translate-y-1"
            >
              <div class="w-8 h-8 rounded-full bg-white/5 group-hover:bg-violet-400/20 flex items-center justify-center transition-all duration-300 border border-white/10">
                <i class="fas fa-play text-xs text-violet-400"></i>
              </div>
              <span class="font-medium text-lg">{{ secondaryButtonText }}</span>
            </a>
          </div>
        </div>

        <!-- Right side - Interactive Demo with glass morphism -->
        <div class="flex-1 w-full max-w-xl mx-auto lg:mx-0 mt-10 lg:mt-0 animate-fade-in-up animation-delay-300">
          <div class="group relative transform transition-all duration-300 hover:-translate-y-2">
            <!-- Modern glassmorphism container -->
            <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden">
              <!-- Sleek gradient header -->
              <div class="h-1 w-full bg-gradient-to-r from-indigo-400 via-violet-400 to-indigo-400 opacity-80"></div>
              
              <!-- Subtle background effects -->
              <div class="absolute -top-32 -right-32 w-64 h-64 bg-gradient-to-br from-indigo-400/4 to-violet-400/4 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"></div>
              
              <!-- Terminal component with enhanced styling -->
              <div class="relative z-10">
                <AnimatedTerminal />
              </div>
            </div>
            
            <!-- Enhanced decorative elements -->
            <div class="absolute -z-10 -bottom-6 -right-6 w-20 sm:w-28 h-20 sm:h-28 bg-indigo-500/15 rounded-full blur-xl animate-pulse-slow"></div>
            <div class="absolute -z-10 -top-6 -left-6 w-28 sm:w-36 h-28 sm:h-36 bg-violet-500/15 rounded-full blur-xl animate-pulse-slow animation-delay-150"></div>
          </div>
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

export default defineComponent({
  name: 'HeroSection',
  components: {
    GradientText,
    HomeNavbarButton,
    AnimatedTerminal
  },
  props: {
    titleLine1: {
      type: String,
      default: 'Build Full-Stack'
    },
    titleLine2: {
      type: String,
      default: 'Web Apps Without'
    },
    highlightedTitle: {
      type: String,
      default: 'Writing Code'
    },
    description: {
      type: String,
      default: 'Perfect for non-technical users! Create professional web applications with Vue.js frontends and Django backends in minutes. Just describe what you want in plain English - no programming experience needed.'
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

@keyframes pulse-slow {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 0.8; }
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

.animate-pulse-slow {
  animation: pulse-slow 3s ease-in-out infinite;
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

.text-shadow-sm {
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

/* Remove animation for the highlighted title */
.no-animation {
  animation: none !important;
  background-size: 100% auto !important;
}

/* Purple border glow style */
.purple-glow-border {
  box-shadow: 0 0 10px -3px rgba(139, 92, 246, 0.5);
}
</style> 