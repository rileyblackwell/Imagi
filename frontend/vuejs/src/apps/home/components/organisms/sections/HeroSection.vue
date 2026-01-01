<!-- Hero Section Component - Premium Design -->
<template>
  <section class="relative min-h-[85vh] flex items-center justify-center overflow-hidden pt-28 pb-16 sm:pt-32 sm:pb-20 md:pt-36 md:pb-24">
    <!-- Local background effects -->
    <div class="absolute inset-0 pointer-events-none">
      <!-- Spotlight effect -->
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[140%] h-[80%] bg-[radial-gradient(ellipse_at_center,rgba(139,92,246,0.08)_0%,transparent_60%)]"></div>
    </div>

    <!-- Content -->
    <div class="relative w-full max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
      <div class="flex flex-col lg:flex-row items-center gap-12 lg:gap-16">
        <!-- Left side - Main content -->
        <div class="flex-1 text-center lg:text-left">
          <!-- Animated badge -->
          <div class="mb-8 inline-block animate-fade-in">
            <div class="group inline-flex items-center gap-3 px-4 py-2 bg-white/[0.03] rounded-full border border-white/[0.08] backdrop-blur-sm hover:bg-white/[0.05] hover:border-white/[0.12] transition-all duration-300 cursor-default">
              <span class="relative flex h-2 w-2">
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-violet-400 opacity-75"></span>
                <span class="relative inline-flex rounded-full h-2 w-2 bg-violet-400"></span>
              </span>
              <span class="text-sm font-medium text-white/70 tracking-wide">AI-Powered Web Development</span>
              <i class="fas fa-arrow-right text-xs text-white/40 group-hover:text-violet-400 group-hover:translate-x-0.5 transition-all duration-300"></i>
            </div>
          </div>

          <!-- Hero title with staggered animation -->
          <h1 class="text-4xl sm:text-5xl md:text-6xl lg:text-[3.5rem] xl:text-6xl font-semibold tracking-tight mb-8 leading-[1.1]">
            <span class="block text-white/90 animate-fade-in-up" style="animation-delay: 100ms">{{ titleLine1 }}</span>
            <span class="block text-white/90 animate-fade-in-up" style="animation-delay: 200ms">{{ titleLine2 }}</span>
            <span class="block mt-3 animate-fade-in-up" style="animation-delay: 300ms">
              <span class="relative inline-block">
                <span class="bg-gradient-to-r from-violet-400 via-fuchsia-400 to-violet-400 bg-clip-text text-transparent bg-[length:200%_auto] animate-gradient-x">
                  {{ highlightedTitle }}
                </span>
                <!-- Underline accent -->
                <span class="absolute -bottom-2 left-0 right-0 h-px bg-gradient-to-r from-transparent via-violet-400/50 to-transparent"></span>
              </span>
            </span>
          </h1>

          <!-- Description -->
          <p class="text-lg sm:text-xl text-white/50 mb-10 max-w-xl mx-auto lg:mx-0 leading-relaxed animate-fade-in-up" style="animation-delay: 400ms">
            {{ description }}
          </p>

          <!-- CTA buttons -->
          <div class="flex flex-col sm:flex-row items-center gap-4 justify-center lg:justify-start animate-fade-in-up" style="animation-delay: 500ms">
            <!-- Primary button with modern design -->
            <HomeNavbarButton
              :to="{ name: isAuthenticated ? 'builder-dashboard' : 'login' }"
              class="group relative w-full sm:w-auto overflow-hidden"
            >
              <!-- Animated gradient background -->
              <div class="absolute inset-0 bg-gradient-to-r from-violet-600 via-fuchsia-600 to-violet-600 bg-[length:200%_100%] transition-all duration-500 group-hover:bg-[length:150%_100%]"></div>
              
              <!-- Shimmer effect on hover -->
              <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-700">
                <div class="absolute inset-0 -translate-x-full group-hover:translate-x-full transition-transform duration-1000 bg-gradient-to-r from-transparent via-white/20 to-transparent skew-x-12"></div>
              </div>
              
              <!-- Subtle glow effect -->
              <div class="absolute -inset-[1px] bg-gradient-to-r from-violet-400/0 via-fuchsia-400/50 to-violet-400/0 opacity-0 group-hover:opacity-100 blur-sm transition-opacity duration-300 rounded-xl"></div>
              
              <!-- Button content -->
              <span class="relative flex items-center justify-center gap-3 px-8 py-4 rounded-xl text-white font-semibold text-base backdrop-blur-sm border border-white/10 group-hover:border-white/20 transition-all duration-300 group-hover:scale-[1.02] group-hover:shadow-lg group-hover:shadow-violet-500/25">
                <span class="flex items-center justify-center w-5 h-5 rounded-lg bg-white/15 group-hover:bg-white/25 transition-colors duration-300 group-hover:rotate-[-5deg]">
                  <i class="fas fa-rocket text-xs"></i>
                </span>
                <span class="tracking-wide">{{ primaryButtonText }}</span>
                <i class="fas fa-arrow-right text-sm transform group-hover:translate-x-1.5 transition-transform duration-300"></i>
              </span>
            </HomeNavbarButton>

            <!-- Secondary button -->
            <a 
              :href="secondaryButtonHref" 
              class="group flex items-center gap-3 px-6 py-3.5 text-white/70 hover:text-white transition-all duration-300"
            >
              <span class="flex items-center justify-center w-9 h-9 rounded-full bg-white/[0.05] border border-white/[0.08] group-hover:bg-white/[0.08] group-hover:border-white/[0.12] transition-all duration-300">
                <i class="fas fa-play text-xs text-violet-400"></i>
              </span>
              <span class="font-medium text-sm">{{ secondaryButtonText }}</span>
            </a>
          </div>

          <!-- Trust indicators -->
          <div class="mt-12 pt-10 border-t border-white/[0.06] animate-fade-in-up" style="animation-delay: 600ms">
            <div class="flex flex-col sm:flex-row items-center gap-6 sm:gap-10 justify-center lg:justify-start">
              <div class="flex items-center gap-2 text-white/40">
                <i class="fas fa-bolt text-amber-400/80 text-sm"></i>
                <span class="text-sm">Built in minutes</span>
              </div>
              <div class="flex items-center gap-2 text-white/40">
                <i class="fas fa-shield-check text-emerald-400/80 text-sm"></i>
                <span class="text-sm">Production ready</span>
              </div>
              <div class="flex items-center gap-2 text-white/40">
                <i class="fas fa-dollar-sign text-violet-400/80 text-sm"></i>
                <span class="text-sm">Pay per build</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Right side - Interactive Demo -->
        <div class="flex-1 w-full max-w-xl mx-auto lg:mx-0 animate-fade-in-up" style="animation-delay: 400ms">
          <div class="group relative">
            <!-- Glow effect behind terminal -->
            <div class="absolute -inset-4 bg-gradient-to-r from-violet-600/20 via-fuchsia-600/20 to-violet-600/20 rounded-3xl blur-2xl opacity-40 group-hover:opacity-60 transition-opacity duration-500"></div>
            
            <!-- Terminal container -->
            <div class="relative rounded-2xl border border-white/[0.08] bg-[#0a0a0f]/80 backdrop-blur-xl shadow-2xl overflow-hidden">
              <!-- Gradient accent line -->
              <div class="h-px w-full bg-gradient-to-r from-transparent via-violet-500/50 to-transparent"></div>
              
              <!-- Terminal component -->
              <div class="relative">
                <AnimatedTerminal />
              </div>
            </div>
            
            <!-- Decorative elements -->
            <div class="absolute -z-10 -bottom-8 -right-8 w-32 h-32 bg-violet-500/10 rounded-full blur-2xl"></div>
            <div class="absolute -z-10 -top-8 -left-8 w-40 h-40 bg-fuchsia-500/10 rounded-full blur-2xl"></div>
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
      default: 'Perfect for non-technical users! Create professional web applications with Vue.js frontends and Django backends in minutes. Just describe what you want in plain English.'
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
  animation: fade-in 0.8s ease-out forwards;
}

/* Fade in up animation */
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

.animate-fade-in-up {
  opacity: 0;
  animation: fade-in-up 0.8s ease-out forwards;
}

/* Gradient animation */
@keyframes gradient-x {
  0%, 100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}

.animate-gradient-x {
  animation: gradient-x 4s ease infinite;
}
</style>
