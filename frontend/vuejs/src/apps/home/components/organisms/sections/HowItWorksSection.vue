<!-- How It Works Section - Premium Timeline Design -->
<template>
  <section id="how-it-works" class="py-24 md:py-32 px-6 sm:px-8 lg:px-12 relative overflow-hidden">
    <div class="max-w-7xl mx-auto relative">
      <!-- Section header -->
      <div class="text-center mb-14 md:mb-18">
        <SectionPill
          class="mb-7"
          tone="neutral"
          icon="fas fa-route"
          label="Simple Process"
        />
        
        <h2 class="text-3xl sm:text-4xl md:text-5xl font-bold text-white mb-5 tracking-[-0.02em]">{{ title }}</h2>
        <p class="text-lg text-white/70 max-w-2xl mx-auto leading-relaxed font-light">{{ subtitle }}</p>
      </div>

      <!-- Steps timeline -->
      <div class="relative max-w-4xl mx-auto">
        <!-- Vertical connector line -->
        <div class="absolute left-8 md:left-1/2 top-0 bottom-0 w-px bg-gradient-to-b from-white/20 via-white/10 to-transparent md:-translate-x-px hidden sm:block"></div>
        
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
                class="hidden md:block absolute left-1/2 top-14 h-px w-[calc(50%-5rem)] pointer-events-none bg-gradient-to-r from-white/20 via-white/10 to-transparent"
                :class="index % 2 === 0 ? '-translate-x-full bg-gradient-to-l' : 'translate-x-0 bg-gradient-to-r'"
              ></div>

              <!-- Timeline node -->
              <div class="hidden md:flex absolute left-1/2 top-5 -translate-x-1/2 z-10">
                <div class="relative">
                  <!-- Bubble -->
                  <div class="relative flex items-center justify-center w-14 h-14">
                    <!-- Glass highlight -->
                    <div class="absolute inset-0 rounded-full bg-white/10 blur-xl opacity-60"></div>
                    <div class="relative w-full h-full rounded-full border border-white/10 bg-[#05050d] shadow-[0_10px_28px_rgba(0,0,0,0.5)]">
                      <div class="absolute inset-[2px] rounded-full border border-white/15 overflow-hidden bg-white/5">
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
                    <div class="absolute inset-px rounded-full overflow-hidden border border-white/10 bg-white/5">
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
                <div class="relative p-6 md:p-7 rounded-2xl bg-white dark:bg-white border border-gray-200 dark:border-gray-300 transition-colors duration-300 shadow-md">
                  
                  <!-- Title -->
                  <div class="relative mb-5">
                    <div class="text-xs font-medium uppercase tracking-wider mb-1 text-gray-600 dark:text-black">Step {{ index + 1 }}</div>
                    <h3 class="hidden sm:block text-lg font-semibold text-gray-900 dark:text-black">{{ step.title }}</h3>
                  </div>
                  
                  <!-- Description -->
                  <p class="relative text-gray-600 dark:text-black text-sm leading-relaxed mb-6">{{ step.description }}</p>
                  
                  <!-- Features list -->
                  <ul class="relative space-y-2.5">
                    <li 
                      v-for="(feature, fIndex) in step.features" 
                      :key="fIndex" 
                      class="flex items-start"
                    >
                      <span class="text-gray-600 dark:text-black text-sm">{{ feature }}</span>
                    </li>
                  </ul>

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
      
      <!-- CTA button - clean -->
      <div class="text-center mt-14">
        <HomeNavbarButton
          :to="{ name: isAuthenticated ? 'projects' : 'login' }"
          class="group relative inline-flex items-center gap-3 px-8 py-4 rounded-xl font-semibold overflow-hidden"
        >
          <!-- Button background -->
          <div class="absolute inset-0 bg-white rounded-xl transition-all duration-300"></div>
          <!-- Inner highlight -->
          <div class="absolute inset-[1px] bg-gradient-to-b from-white/[0.08] to-transparent rounded-xl opacity-50"></div>
          <!-- Content -->
          <span class="relative text-[#08081a]">Try It Yourself</span>
          <i class="fas fa-arrow-right text-sm relative text-[#08081a] transform group-hover:translate-x-1 transition-transform duration-300"></i>
        </HomeNavbarButton>
      </div>
    </div>
  </section>
</template>

<script>
import { defineComponent, computed } from 'vue'
import { useAuthStore } from '@/shared/stores/auth'
import { HomeNavbarButton } from '@/apps/home/components/atoms/buttons'
import { SectionPill } from '@/apps/home/components/atoms'

export default defineComponent({
  name: 'HowItWorksSection',
  components: {
    HomeNavbarButton,
    SectionPill
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
  }
})
</script>

<style scoped>
/* Styles removed - cards now use simple shadows */
</style>
