<!-- Hero Section Component - Ultra Premium Design -->
<template>
  <section class="relative min-h-[92vh] flex items-center justify-center overflow-hidden pt-28 pb-20 sm:pt-32 sm:pb-24 md:pt-36 md:pb-28">
    <!-- Local background effects -->
    <div class="absolute inset-0 pointer-events-none">
      <!-- Multi-layered spotlight effect - enhanced -->
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[180%] h-[100%] bg-[radial-gradient(ellipse_at_center,rgba(124,58,237,0.10)_0%,transparent_50%)]"></div>
      <div class="absolute top-[25%] left-1/2 -translate-x-1/2 w-[120%] h-[70%] bg-[radial-gradient(ellipse_at_center,rgba(217,70,239,0.06)_0%,transparent_45%)]"></div>
    </div>

    <!-- Content -->
    <div class="relative w-full max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
      <div class="flex flex-col lg:flex-row items-center gap-16 lg:gap-24">
        <!-- Left side - Main content -->
        <div class="flex-1 text-center lg:text-left">
          <!-- Premium animated badge - refined -->
          <div class="mb-8 inline-block animate-fade-in">
            <div class="group relative inline-flex items-center gap-3 px-5 py-2.5 rounded-full cursor-default overflow-hidden">
              <!-- Badge background with gradient border -->
              <div class="absolute inset-0 bg-gradient-to-r from-violet-500/25 via-fuchsia-500/25 to-violet-500/25 rounded-full"></div>
              <div class="absolute inset-[1px] bg-[#08081a]/95 rounded-full backdrop-blur-xl"></div>
              <!-- Shimmer effect -->
              <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-700">
                <div class="absolute inset-0 -translate-x-full group-hover:translate-x-full transition-transform duration-1000 bg-gradient-to-r from-transparent via-white/[0.08] to-transparent"></div>
              </div>
              <!-- Badge content -->
              <span class="relative flex h-2 w-2">
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-violet-400 opacity-50"></span>
                <span class="relative inline-flex rounded-full h-2 w-2 bg-gradient-to-br from-violet-400 to-fuchsia-400"></span>
              </span>
              <span class="relative text-sm font-medium text-white/90 tracking-wide">AI-Powered No-Code Builder</span>
            </div>
          </div>

          <!-- Hero title with staggered animation and refined typography -->
          <h1 class="text-4xl sm:text-5xl md:text-6xl lg:text-[3.5rem] xl:text-[4.25rem] font-bold tracking-[-0.025em] mb-7 leading-[1.05]">
            <span class="block text-white animate-fade-in-up" style="animation-delay: 100ms">{{ titleLine1 }}</span>
            <span class="block text-white animate-fade-in-up" style="animation-delay: 200ms">{{ titleLine2 }}</span>
            <span class="block mt-3 animate-fade-in-up" style="animation-delay: 300ms">
              <span class="relative inline-block">
                <span class="bg-gradient-to-r from-violet-400 via-fuchsia-400 to-violet-400 bg-clip-text text-transparent bg-[length:200%_auto] animate-gradient-x">
                  {{ highlightedTitle }}
                </span>
                <!-- Animated underline accent - refined -->
                <span class="absolute -bottom-2 left-0 right-0 h-[3px] bg-gradient-to-r from-transparent via-violet-500/50 to-transparent animate-pulse-subtle rounded-full"></span>
              </span>
            </span>
          </h1>

          <!-- Description with refined styling -->
          <p class="text-lg sm:text-xl text-white/75 mb-9 max-w-xl mx-auto lg:mx-0 leading-relaxed animate-fade-in-up font-light" style="animation-delay: 400ms">
            {{ description }}
          </p>

          <!-- CTA buttons - premium design with enhanced styling -->
          <div class="flex flex-col sm:flex-row items-center gap-5 justify-center lg:justify-start animate-fade-in-up" style="animation-delay: 500ms">
            <!-- Primary button with glass morphism and glow -->
            <HomeNavbarButton
              :to="{ name: isAuthenticated ? 'builder-dashboard' : 'login' }"
              class="group relative w-full sm:w-auto overflow-hidden"
            >
              <!-- Outer glow - enhanced -->
              <div class="absolute -inset-1.5 bg-gradient-to-r from-violet-600 via-fuchsia-600 to-violet-600 rounded-2xl blur-xl opacity-40 group-hover:opacity-70 transition-all duration-500"></div>
              
              <!-- Button background -->
              <div class="absolute inset-0 bg-gradient-to-r from-violet-600 via-fuchsia-600 to-violet-600 bg-[length:200%_100%] rounded-xl transition-all duration-700 group-hover:bg-[length:150%_100%]"></div>
              
              <!-- Inner highlight - refined -->
              <div class="absolute inset-[1px] bg-gradient-to-b from-white/[0.18] to-transparent rounded-xl opacity-90"></div>
              
              <!-- Shimmer effect on hover -->
              <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
                <div class="absolute inset-0 -translate-x-full group-hover:translate-x-full transition-transform duration-1000 ease-out bg-gradient-to-r from-transparent via-white/25 to-transparent skew-x-12"></div>
              </div>
              
              <!-- Button content -->
              <span class="relative flex items-center justify-center gap-3 px-9 py-4 rounded-xl text-white font-semibold text-base transition-all duration-300 group-hover:scale-[1.02]">
                <span class="flex items-center justify-center w-6 h-6 rounded-lg bg-white/20 group-hover:bg-white/30 transition-all duration-500 group-hover:rotate-[-12deg] group-hover:scale-110">
                  <i class="fas fa-rocket text-sm"></i>
                </span>
                <span class="tracking-wide">{{ primaryButtonText }}</span>
                <i class="fas fa-arrow-right text-sm opacity-0 -ml-2 group-hover:opacity-100 group-hover:ml-0.5 transition-all duration-300"></i>
              </span>
            </HomeNavbarButton>

            <!-- Secondary button - refined glass style -->
            <a 
              :href="secondaryButtonHref" 
              class="group flex items-center gap-3 px-5 py-3 text-white/80 hover:text-white transition-all duration-300"
            >
              <span class="relative flex items-center justify-center w-10 h-10 rounded-full overflow-hidden">
                <div class="absolute inset-0 bg-gradient-to-br from-white/[0.10] to-white/[0.03] backdrop-blur-sm"></div>
                <div class="absolute inset-[1px] rounded-full border border-white/[0.12] group-hover:border-white/[0.20] transition-colors duration-300"></div>
                <i class="fas fa-play text-xs text-violet-400 relative ml-0.5 group-hover:scale-110 transition-transform duration-300"></i>
              </span>
              <span class="font-medium text-sm tracking-wide">{{ secondaryButtonText }}</span>
            </a>
          </div>

          <!-- Trust indicators - refined with better visual hierarchy -->
          <div class="mt-12 pt-8 border-t border-white/[0.06] animate-fade-in-up" style="animation-delay: 600ms">
            <div class="flex flex-col sm:flex-row items-center gap-6 sm:gap-10 justify-center lg:justify-start">
              <div class="group flex items-center gap-2.5 text-white/65 hover:text-white/85 transition-colors duration-300 cursor-default">
                <div class="flex items-center justify-center w-8 h-8 rounded-lg bg-amber-500/10 group-hover:bg-amber-500/15 transition-all duration-300 border border-amber-500/20 group-hover:border-amber-500/30">
                  <i class="fas fa-bolt text-amber-400 text-xs"></i>
                </div>
                <span class="text-sm font-medium">Build in minutes</span>
              </div>
              <div class="group flex items-center gap-2.5 text-white/65 hover:text-white/85 transition-colors duration-300 cursor-default">
                <div class="flex items-center justify-center w-8 h-8 rounded-lg bg-emerald-500/10 group-hover:bg-emerald-500/15 transition-all duration-300 border border-emerald-500/20 group-hover:border-emerald-500/30">
                  <i class="fas fa-layer-group text-emerald-400 text-xs"></i>
                </div>
                <span class="text-sm font-medium">No code required</span>
              </div>
              <div class="group flex items-center gap-2.5 text-white/65 hover:text-white/85 transition-colors duration-300 cursor-default">
                <div class="flex items-center justify-center w-8 h-8 rounded-lg bg-violet-500/10 group-hover:bg-violet-500/15 transition-all duration-300 border border-violet-500/20 group-hover:border-violet-500/30">
                  <i class="fas fa-globe text-violet-400 text-xs"></i>
                </div>
                <span class="text-sm font-medium">Publish coming soon</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Right side - Interactive Demo with premium styling -->
        <div class="flex-1 w-full max-w-xl mx-auto lg:mx-0 animate-fade-in-up" style="animation-delay: 400ms">
          <div class="group relative">
            <!-- Multi-layer glow effect behind terminal - enhanced -->
            <div class="absolute -inset-8 bg-gradient-to-r from-violet-600/20 via-fuchsia-600/25 to-violet-600/20 rounded-[2.5rem] blur-3xl opacity-45 group-hover:opacity-60 transition-opacity duration-700"></div>
            <div class="absolute -inset-4 bg-gradient-to-br from-violet-500/12 to-fuchsia-500/12 rounded-3xl blur-2xl opacity-55 group-hover:opacity-75 transition-opacity duration-500"></div>
            
            <!-- Terminal container with refined glass effect -->
            <div class="relative rounded-2xl overflow-hidden shadow-[0_30px_70px_-15px_rgba(139,92,246,0.20)]">
              <!-- Border gradient - enhanced -->
              <div class="absolute inset-0 rounded-2xl p-[1px] bg-gradient-to-b from-white/20 via-white/[0.06] to-white/[0.02]">
                <div class="w-full h-full rounded-2xl bg-[#0a0a14]"></div>
              </div>
              
              <!-- Glass effect inner container -->
              <div class="relative bg-[#0a0a14]/98 backdrop-blur-2xl rounded-2xl">
                <!-- Top gradient accent line - refined -->
                <div class="h-[2px] w-full bg-gradient-to-r from-transparent via-violet-500/60 to-transparent"></div>
                
                <!-- Terminal component -->
                <div class="relative">
                  <AnimatedTerminal />
                </div>
              </div>
            </div>
            
            <!-- Decorative floating elements - refined -->
            <div class="absolute -z-10 -bottom-12 -right-12 w-44 h-44 bg-gradient-to-br from-violet-500/10 to-fuchsia-500/6 rounded-full blur-3xl animate-pulse-slow"></div>
            <div class="absolute -z-10 -top-12 -left-12 w-52 h-52 bg-gradient-to-tr from-fuchsia-500/8 to-violet-500/5 rounded-full blur-3xl animate-pulse-slow" style="animation-delay: -3s"></div>
            
            <!-- Corner accents - refined -->
            <div class="absolute top-5 right-5 w-2 h-2 rounded-full bg-violet-400/35 animate-pulse"></div>
            <div class="absolute bottom-5 left-5 w-1.5 h-1.5 rounded-full bg-fuchsia-400/35 animate-pulse" style="animation-delay: -1s"></div>
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
      default: 'Build web apps'
    },
    titleLine2: {
      type: String,
      default: 'in minutes.'
    },
    highlightedTitle: {
      type: String,
      default: 'No technical skills needed'
    },
    description: {
      type: String,
      default: 'Tell Imagi what you want to build, then tweak it visually. Natural language + AI help you create screens, data, and workflows — without writing code.'
    },
    primaryButtonText: {
      type: String,
      default: 'Start Building'
    },
    secondaryButtonText: {
      type: String,
      default: 'See How It Works'
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
/* Fade in animation */
@keyframes fade-in {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.animate-fade-in {
  animation: fade-in 1s ease-out forwards;
}

/* Fade in up animation - enhanced */
@keyframes fade-in-up {
  from {
    opacity: 0;
    transform: translateY(25px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in-up {
  opacity: 0;
  animation: fade-in-up 0.9s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

/* Gradient animation - smoother */
@keyframes gradient-x {
  0%, 100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}

.animate-gradient-x {
  animation: gradient-x 5s ease infinite;
}

/* Subtle pulse for underline */
@keyframes pulse-subtle {
  0%, 100% {
    opacity: 0.6;
  }
  50% {
    opacity: 0.9;
  }
}

.animate-pulse-subtle {
  animation: pulse-subtle 3s ease-in-out infinite;
}

/* Slow pulse for decorative elements */
@keyframes pulse-slow {
  0%, 100% {
    opacity: 0.5;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.05);
  }
}

.animate-pulse-slow {
  animation: pulse-slow 6s ease-in-out infinite;
}

/* Pulse glow animation for CTA button */
@keyframes pulse-glow {
  0%, 100% {
    transform: scale(1);
    opacity: 0.5;
  }
  50% {
    transform: scale(1.08);
    opacity: 0.9;
  }
}

.group:hover .group-hover\:animate-pulse-glow {
  animation: pulse-glow 2s ease-in-out infinite;
}
</style>
