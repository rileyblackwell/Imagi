<!-- How It Works Section - Premium Timeline Design -->
<template>
  <section id="how-it-works" class="py-20 md:py-32 px-6 sm:px-8 lg:px-12 relative overflow-hidden">
    <div class="max-w-7xl mx-auto relative">
      <!-- Section header -->
      <div class="text-center mb-16 md:mb-20">
        <!-- Badge -->
        <div class="inline-flex items-center gap-2 px-4 py-2 bg-white/[0.08] rounded-full border border-white/20 mb-6">
          <i class="fas fa-route text-xs text-violet-400"></i>
          <span class="text-sm font-medium text-white/90">Simple Process</span>
        </div>
        
        <h2 class="text-3xl sm:text-4xl md:text-5xl font-semibold text-white mb-5 tracking-tight">{{ title }}</h2>
        <p class="text-lg text-white/85 max-w-2xl mx-auto leading-relaxed">{{ subtitle }}</p>
      </div>

      <!-- Steps timeline -->
      <div class="relative max-w-4xl mx-auto">
        <!-- Vertical connector line -->
        <div class="absolute left-8 md:left-1/2 top-0 bottom-0 w-px bg-gradient-to-b from-violet-500/40 via-fuchsia-500/30 to-transparent md:-translate-x-px hidden sm:block"></div>
        
        <!-- Steps -->
        <div class="space-y-8 md:space-y-0">
          <div 
            v-for="(step, index) in steps" 
            :key="index"
            class="relative"
          >
            <!-- Step container -->
            <div 
              class="relative flex flex-col md:flex-row items-start gap-6 md:gap-12"
              :class="index % 2 === 0 ? 'md:flex-row' : 'md:flex-row-reverse'"
            >
              <!-- Bubble-to-card connector -->
              <div 
                class="hidden md:block absolute left-1/2 top-14 h-px w-[calc(50%-5rem)] pointer-events-none"
                :class="[
                  index % 2 === 0 ? '-translate-x-full bg-gradient-to-l' : 'translate-x-0 bg-gradient-to-r',
                  getConnectorClass(step.color)
                ]"
              ></div>

              <!-- Timeline node -->
              <div class="hidden md:flex absolute left-1/2 top-5 -translate-x-1/2 z-10">
                <div class="relative">
                  <!-- Outer glow -->
                  <div class="absolute -inset-2 rounded-full blur-2xl opacity-50" :class="getGlowClass(step.color)"></div>
                  <!-- Bubble -->
                  <div class="relative flex items-center justify-center w-14 h-14">
                    <!-- Glass highlight -->
                    <div class="absolute inset-0 rounded-full bg-white/10 blur-xl opacity-60"></div>
                    <div class="relative w-full h-full rounded-full border border-white/10 bg-[#05050d] shadow-[0_10px_28px_rgba(0,0,0,0.5)]">
                      <div class="absolute inset-[2px] rounded-full border border-white/15 overflow-hidden" :class="getNodeClass(step.color)">
                        <div class="absolute top-0 inset-x-1.5 h-1/2 rounded-full bg-white/30 blur-md opacity-60"></div>
                        <div class="absolute bottom-1 inset-x-2 h-1/4 rounded-full bg-black/30 opacity-40 blur-sm"></div>
                      </div>
                      <div class="relative flex items-center justify-center w-full h-full">
                        <span class="text-white/95 font-semibold text-base tracking-[0.15em] drop-shadow-[0_2px_6px_rgba(0,0,0,0.45)]">{{ index + 1 }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Mobile node -->
              <div class="sm:hidden flex items-center gap-4 mb-4">
                <div class="relative flex items-center justify-center w-11 h-11 rounded-full">
                  <div class="absolute inset-0 rounded-full bg-white/20 blur-lg opacity-40"></div>
                  <div class="relative w-full h-full rounded-full border border-white/10 bg-[#05050d]">
                    <div class="absolute inset-px rounded-full overflow-hidden border border-white/10" :class="getNodeClass(step.color)">
                      <div class="absolute top-0 inset-x-1 h-1/2 rounded-full bg-white/30 blur-sm opacity-70"></div>
                    </div>
                    <div class="relative flex items-center justify-center w-full h-full">
                      <span class="text-white/95 font-semibold text-sm tracking-[0.1em] drop-shadow-[0_1px_4px_rgba(0,0,0,0.45)]">{{ index + 1 }}</span>
                    </div>
                  </div>
                </div>
                <h3 class="text-lg font-semibold text-white/90">{{ step.title }}</h3>
              </div>
              
              <!-- Content card -->
              <div 
                class="relative flex-1 md:w-[calc(50%-4rem)]"
                :class="index % 2 === 0 ? 'md:pr-8' : 'md:pl-8'"
              >
                <div class="group relative p-6 md:p-8 rounded-2xl border border-white/15 bg-white/[0.07] backdrop-blur-sm hover:bg-white/[0.1] hover:border-white/25 transition-all duration-500 overflow-hidden">
                  <!-- Hover glow -->
                  <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
                    <div class="absolute inset-0 bg-gradient-to-br opacity-[0.08]" :class="getGradientClass(step.color)"></div>
                  </div>
                  
                  <!-- Icon and title -->
                  <div class="relative flex items-center gap-4 mb-5">
                    <div 
                      class="flex items-center justify-center w-11 h-11 rounded-xl border transition-all duration-300"
                      :class="getIconContainerClass(step.color)"
                    >
                      <i :class="[step.icon, 'text-base', getIconClass(step.color)]"></i>
                    </div>
                    <div>
                      <div class="text-xs font-medium uppercase tracking-wider mb-1" :class="getLabelClass(step.color)">Step {{ index + 1 }}</div>
                      <h3 class="hidden sm:block text-lg font-semibold text-white">{{ step.title }}</h3>
                    </div>
                  </div>
                  
                  <!-- Description -->
                  <p class="relative text-white/85 text-sm leading-relaxed mb-6">{{ step.description }}</p>
                  
                  <!-- Features list -->
                  <ul class="relative space-y-3">
                    <li 
                      v-for="(feature, fIndex) in step.features" 
                      :key="fIndex" 
                      class="flex items-start gap-3"
                    >
                      <div 
                        class="flex-shrink-0 flex items-center justify-center w-5 h-5 rounded-full mt-0.5"
                        :class="getCheckClass(step.color)"
                      >
                        <i class="fas fa-check text-[10px]" :class="getCheckIconClass(step.color)"></i>
                      </div>
                      <span class="text-white/90 text-sm">{{ feature }}</span>
                    </li>
                  </ul>

                  <!-- Bottom accent -->
                  <div 
                    class="absolute bottom-0 left-0 right-0 h-px opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                    :class="getAccentClass(step.color)"
                  ></div>
                </div>
              </div>
              
              <!-- Spacer for alternating layout -->
              <div class="hidden md:block flex-1 md:w-[calc(50%-4rem)]"></div>
            </div>
            
            <!-- Spacing between steps on desktop -->
            <div v-if="index < steps.length - 1" class="hidden md:block h-16"></div>
          </div>
        </div>
      </div>
      
      <!-- CTA button -->
      <div class="text-center mt-16">
        <HomeNavbarButton
          :to="{ name: isAuthenticated ? 'builder-dashboard' : 'login' }"
          class="group inline-flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-violet-600 to-fuchsia-600 rounded-xl text-white font-medium shadow-lg shadow-violet-500/25 hover:shadow-xl hover:shadow-violet-500/30 transition-all duration-300 hover:-translate-y-0.5"
        >
          Try It Yourself
          <i class="fas fa-arrow-right text-sm transform group-hover:translate-x-1 transition-transform duration-300"></i>
        </HomeNavbarButton>
      </div>
    </div>
  </section>
</template>

<script>
import { defineComponent, computed } from 'vue'
import { useAuthStore } from '@/shared/stores/auth'
import { HomeNavbarButton } from '@/apps/home/components/atoms/buttons'

export default defineComponent({
  name: 'HowItWorksSection',
  components: {
    HomeNavbarButton
  },
  props: {
    title: {
      type: String,
      default: 'From Idea to Working App'
    },
    subtitle: {
      type: String,
      default: 'Four simple steps to transform your vision into a production-ready full-stack application.'
    },
    steps: {
      type: Array,
      default: () => [
        {
          title: 'Describe Your App',
          description: 'Tell Imagi what you want to build using plain English. Describe features, user flows, and functionality — no technical jargon required.',
          icon: 'fas fa-lightbulb',
          color: 'violet',
          features: [
            'Natural language input',
            'Describe what, not how',
            'No coding knowledge needed'
          ]
        },
        {
          title: 'AI Generates Everything',
          description: 'Imagi\'s AI builds your complete application: Vue.js frontend with modern UI components and Django backend with APIs and data models.',
          icon: 'fas fa-wand-magic-sparkles',
          color: 'fuchsia',
          features: [
            'Full Vue.js frontend generated',
            'Django backend with REST APIs',
            'Connected and working together'
          ]
        },
        {
          title: 'Iterate via Chat',
          description: 'Refine your app through conversation. Request changes, add features, or adjust the design — Imagi updates your entire stack instantly.',
          icon: 'fas fa-comments',
          color: 'blue',
          features: [
            'Chat-based modifications',
            'Real-time preview updates',
            'Unlimited iterations'
          ]
        },
        {
          title: 'Download & Deploy',
          description: 'Export your complete source code and deploy anywhere. Imagi-hosted deployment with custom domains coming soon.',
          icon: 'fas fa-rocket',
          color: 'emerald',
          features: [
            'Download full source code',
            'Deploy to any host',
            'Imagi hosting coming soon'
          ]
        }
      ]
    }
  },
  setup() {
    const authStore = useAuthStore()
    
    return {
      isAuthenticated: computed(() => authStore.isAuthenticated)
    }
  },
  methods: {
    getGradientClass(color) {
      const gradients = {
        violet: 'from-violet-500 to-purple-500',
        fuchsia: 'from-fuchsia-500 to-pink-500',
        blue: 'from-blue-500 to-cyan-500',
        emerald: 'from-emerald-500 to-teal-500'
      }
      return gradients[color] || gradients.violet
    },
    getNodeClass(color) {
      const classes = {
        violet: 'bg-gradient-to-br from-violet-500 to-violet-600',
        fuchsia: 'bg-gradient-to-br from-fuchsia-500 to-fuchsia-600',
        blue: 'bg-gradient-to-br from-blue-500 to-blue-600',
        emerald: 'bg-gradient-to-br from-emerald-500 to-emerald-600'
      }
      return classes[color] || classes.violet
    },
    getGlowClass(color) {
      const classes = {
        violet: 'bg-violet-500',
        fuchsia: 'bg-fuchsia-500',
        blue: 'bg-blue-500',
        emerald: 'bg-emerald-500'
      }
      return classes[color] || classes.violet
    },
    getIconContainerClass(color) {
      const classes = {
        violet: 'bg-violet-500/15 border-violet-500/30 group-hover:bg-violet-500/20 group-hover:border-violet-500/40',
        fuchsia: 'bg-fuchsia-500/15 border-fuchsia-500/30 group-hover:bg-fuchsia-500/20 group-hover:border-fuchsia-500/40',
        blue: 'bg-blue-500/15 border-blue-500/30 group-hover:bg-blue-500/20 group-hover:border-blue-500/40',
        emerald: 'bg-emerald-500/15 border-emerald-500/30 group-hover:bg-emerald-500/20 group-hover:border-emerald-500/40'
      }
      return classes[color] || classes.violet
    },
    getIconClass(color) {
      const classes = {
        violet: 'text-violet-400',
        fuchsia: 'text-fuchsia-400',
        blue: 'text-blue-400',
        emerald: 'text-emerald-400'
      }
      return classes[color] || classes.violet
    },
    getLabelClass(color) {
      const classes = {
        violet: 'text-violet-400/85',
        fuchsia: 'text-fuchsia-400/85',
        blue: 'text-blue-400/85',
        emerald: 'text-emerald-400/85'
      }
      return classes[color] || classes.violet
    },
    getCheckClass(color) {
      const classes = {
        violet: 'bg-violet-500/20',
        fuchsia: 'bg-fuchsia-500/20',
        blue: 'bg-blue-500/20',
        emerald: 'bg-emerald-500/20'
      }
      return classes[color] || classes.violet
    },
    getCheckIconClass(color) {
      const classes = {
        violet: 'text-violet-400',
        fuchsia: 'text-fuchsia-400',
        blue: 'text-blue-400',
        emerald: 'text-emerald-400'
      }
      return classes[color] || classes.violet
    },
    getAccentClass(color) {
      const classes = {
        violet: 'bg-gradient-to-r from-transparent via-violet-500/60 to-transparent',
        fuchsia: 'bg-gradient-to-r from-transparent via-fuchsia-500/60 to-transparent',
        blue: 'bg-gradient-to-r from-transparent via-blue-500/60 to-transparent',
        emerald: 'bg-gradient-to-r from-transparent via-emerald-500/60 to-transparent'
      }
      return classes[color] || classes.violet
    },
    getConnectorClass(color) {
      const classes = {
        violet: 'from-violet-400/80 via-violet-400/30 to-transparent',
        fuchsia: 'from-fuchsia-400/80 via-fuchsia-400/30 to-transparent',
        blue: 'from-blue-400/80 via-blue-400/30 to-transparent',
        emerald: 'from-emerald-400/80 via-emerald-400/30 to-transparent'
      }
      return classes[color] || classes.violet
    }
  }
})
</script>

<style scoped>
</style>
