<!-- Product Tour Section - Interactive Tabs/Stepper -->
<template>
  <section class="py-24 md:py-32 px-6 sm:px-8 lg:px-12 relative overflow-hidden">
    <div class="max-w-7xl mx-auto relative">
      <!-- Section header -->
      <div class="text-center mb-10 md:mb-14">
        <SectionPill
          class="mb-7"
          tone="violet"
          icon="fas fa-play-circle"
          label="Product Tour"
        />
        
        <h2 class="text-3xl sm:text-4xl md:text-5xl font-bold text-white mb-5 tracking-[-0.02em]">
          See Imagi in Action
        </h2>
        <p class="text-lg text-white/70 max-w-2xl mx-auto leading-relaxed font-light">
          From idea to deployed app in three simple steps. No coding, no complexity.
        </p>
      </div>

      <!-- Pipeline Indicator -->
      <div 
        class="flex items-center justify-center gap-2.5 mb-10"
        role="tablist"
        aria-label="Product tour steps"
        @keydown="handleKeyNav"
      >
        <button
          v-for="(step, idx) in steps"
          :key="idx"
          :ref="el => { if (el) tabRefs[idx] = el }"
          @click="activeStep = idx"
          class="group relative flex items-center gap-3 px-5 py-3 rounded-xl transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-violet-500/40 focus:ring-offset-2 focus:ring-offset-[#08081a]"
          :class="activeStep === idx 
            ? 'bg-gradient-to-r from-violet-500/20 to-fuchsia-500/20 border border-violet-500/35' 
            : 'bg-white/[0.05] border border-white/[0.10] hover:bg-white/[0.07] hover:border-white/[0.15]'"
          :aria-selected="activeStep === idx"
          :tabindex="activeStep === idx ? 0 : -1"
          :id="`tour-tab-${idx}`"
          :aria-controls="`tour-panel-${idx}`"
          role="tab"
        >
          <!-- Step number -->
          <div 
            class="flex items-center justify-center w-8 h-8 rounded-lg text-sm font-semibold transition-all duration-300"
            :class="activeStep === idx 
              ? 'bg-gradient-to-br from-violet-500 to-fuchsia-500 text-white shadow-lg shadow-violet-500/30' 
              : 'bg-white/[0.08] text-white/50 group-hover:text-white/70'"
          >
            {{ idx + 1 }}
          </div>
          
          <!-- Step info -->
          <div class="text-left hidden sm:block">
            <div class="text-sm font-medium transition-colors duration-300"
                 :class="activeStep === idx ? 'text-white/95' : 'text-white/65 group-hover:text-white/80'">
              {{ step.title }}
            </div>
            <div class="text-xs transition-colors duration-300"
                 :class="activeStep === idx ? 'text-white/65' : 'text-white/45'">
              {{ step.subtitle }}
            </div>
          </div>
          
          <!-- Coming soon badge -->
          <span v-if="step.comingSoon" 
                class="absolute -top-2 -right-2 px-1.5 py-0.5 bg-amber-500/25 border border-amber-500/40 rounded text-[9px] text-amber-300 font-medium">
            Soon
          </span>
        </button>
      </div>

      <!-- Content Panel -->
      <div class="relative">
        <!-- Background glow -->
        <div class="absolute -inset-5 bg-gradient-to-r from-violet-600/15 via-fuchsia-600/15 to-violet-600/15 rounded-3xl blur-2xl opacity-55"></div>
        
        <!-- Panel container -->
        <div class="relative rounded-2xl border border-white/[0.15] bg-[#0c0c18]/90 backdrop-blur-xl overflow-hidden">
          <!-- Accent line -->
          <div class="h-[2px] w-full bg-gradient-to-r from-transparent via-violet-500/50 to-transparent"></div>
          
          <!-- Panel content with transition -->
          <div class="p-6 md:p-10">
            <transition name="fade-slide" mode="out-in">
              <div 
                :key="activeStep" 
                :id="`tour-panel-${activeStep}`"
                :aria-labelledby="`tour-tab-${activeStep}`"
                role="tabpanel"
                class="grid md:grid-cols-2 gap-8 md:gap-12 items-center"
              >
                <!-- Left: Description -->
                <div>
                  <div class="flex items-center gap-3 mb-4">
                    <div class="flex items-center justify-center w-10 h-10 rounded-xl"
                         :class="steps[activeStep].iconBg">
                      <i :class="[steps[activeStep].icon, 'text-lg', steps[activeStep].iconColor]"></i>
                    </div>
                    <h3 class="text-xl md:text-2xl font-semibold text-white">
                      {{ steps[activeStep].title }}
                    </h3>
                  </div>
                  
                  <p class="text-white/70 leading-relaxed mb-6">
                    {{ steps[activeStep].description }}
                  </p>
                  
                  <!-- Feature list -->
                  <ul class="space-y-3">
                    <li v-for="(feature, fIdx) in steps[activeStep].features" :key="fIdx"
                        class="flex items-start gap-3">
                      <div class="flex-shrink-0 flex items-center justify-center w-5 h-5 rounded-full mt-0.5"
                           :class="steps[activeStep].checkBg">
                        <i class="fas fa-check text-[10px]" :class="steps[activeStep].checkColor"></i>
                      </div>
                      <span class="text-white/80 text-sm">{{ feature }}</span>
                    </li>
                  </ul>
                  
                  <!-- CTA for this step -->
                  <div class="mt-8">
                    <router-link 
                      v-if="!steps[activeStep].comingSoon"
                      :to="steps[activeStep].ctaLink"
                      class="inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-violet-600 to-fuchsia-600 rounded-lg text-white text-sm font-medium shadow-lg shadow-violet-500/25 hover:shadow-xl hover:shadow-violet-500/30 transition-all duration-300 hover:-translate-y-0.5"
                    >
                      {{ steps[activeStep].ctaText }}
                      <i class="fas fa-arrow-right text-xs"></i>
                    </router-link>
                    <button 
                      v-else
                      class="inline-flex items-center gap-2 px-5 py-2.5 bg-amber-500/20 border border-amber-500/30 rounded-lg text-amber-300 text-sm font-medium transition-all duration-300 hover:bg-amber-500/30"
                    >
                      <i class="fas fa-bell text-xs"></i>
                      {{ steps[activeStep].ctaText }}
                    </button>
                  </div>
                </div>
                
                <!-- Right: Visual -->
                <div class="relative">
                  <div class="rounded-xl border border-white/[0.08] bg-[#0d0d12] overflow-hidden shadow-2xl">
                    <!-- Visual header -->
                    <div class="flex items-center gap-2 px-4 py-2.5 bg-white/[0.03] border-b border-white/[0.06]">
                      <div class="flex items-center gap-1.5">
                        <div class="w-2.5 h-2.5 rounded-full bg-[#ff5f57]"></div>
                        <div class="w-2.5 h-2.5 rounded-full bg-[#febc2e]"></div>
                        <div class="w-2.5 h-2.5 rounded-full bg-[#28c840]"></div>
                      </div>
                      <div class="flex-1 text-center">
                        <span class="text-[10px] text-white/30 font-mono">{{ steps[activeStep].visualTitle }}</span>
                      </div>
                    </div>
                    
                    <!-- Visual content -->
                    <div class="p-4 min-h-[200px]">
                      <!-- Build step visual -->
                      <div v-if="activeStep === 0" class="space-y-3">
                        <div class="flex items-center gap-2 text-xs text-white/40 mb-4">
                          <i class="fas fa-terminal text-violet-400/60"></i>
                          <span>Describe your app...</span>
                        </div>
                        <div class="bg-violet-500/10 border border-violet-500/20 rounded-lg p-3">
                          <p class="text-[11px] text-white/70 leading-relaxed">
                            "Build a customer portal with login, dashboard showing recent orders, and a support ticket system"
                          </p>
                        </div>
                        <div class="flex items-center gap-2 mt-4">
                          <div class="h-1 flex-1 bg-white/[0.06] rounded-full overflow-hidden">
                            <div class="h-full w-3/4 bg-gradient-to-r from-violet-500 to-fuchsia-500 rounded-full animate-pulse"></div>
                          </div>
                          <span class="text-[10px] text-white/40">Generating...</span>
                        </div>
                      </div>
                      
                      <!-- Refine step visual -->
                      <div v-else-if="activeStep === 1" class="space-y-3">
                        <div class="flex items-start gap-2">
                          <div class="w-6 h-6 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center flex-shrink-0">
                            <i class="fas fa-robot text-[10px] text-white"></i>
                          </div>
                          <div class="bg-white/[0.03] border border-white/[0.06] rounded-lg rounded-tl-sm p-2.5 text-[11px] text-white/60">
                            Your dashboard is ready! Want me to add charts or change the color scheme?
                          </div>
                        </div>
                        <div class="flex items-start gap-2 flex-row-reverse">
                          <div class="w-6 h-6 rounded-full bg-white/[0.05] border border-white/[0.08] flex items-center justify-center flex-shrink-0">
                            <i class="fas fa-user text-[10px] text-white/40"></i>
                          </div>
                          <div class="bg-violet-500/10 border border-violet-500/20 rounded-lg rounded-tr-sm p-2.5 text-[11px] text-white/70">
                            Add a bar chart for monthly sales and make the header dark blue
                          </div>
                        </div>
                        <div class="flex items-center gap-2 text-[10px] text-emerald-400/70 mt-2">
                          <i class="fas fa-check-circle"></i>
                          <span>Changes applied instantly</span>
                        </div>
                      </div>
                      
                      <!-- Deploy step visual -->
                      <div v-else class="space-y-3">
                        <div class="flex items-center justify-between mb-4">
                          <span class="text-xs text-white/50">Deployment Status</span>
                          <span class="px-2 py-0.5 bg-amber-500/20 rounded text-[10px] text-amber-300">Coming Soon</span>
                        </div>
                        <div class="space-y-2">
                          <div class="flex items-center gap-3 p-2.5 bg-white/[0.02] rounded-lg border border-white/[0.06]">
                            <i class="fas fa-globe text-violet-400/60"></i>
                            <div class="flex-1">
                              <div class="text-[11px] text-white/70">your-app.imagi.app</div>
                              <div class="text-[9px] text-white/30">Custom domain support</div>
                            </div>
                            <i class="fas fa-lock text-emerald-400/60 text-xs"></i>
                          </div>
                          <div class="flex items-center gap-3 p-2.5 bg-white/[0.02] rounded-lg border border-white/[0.06]">
                            <i class="fas fa-server text-fuchsia-400/60"></i>
                            <div class="flex-1">
                              <div class="text-[11px] text-white/70">Auto-scaling infrastructure</div>
                              <div class="text-[9px] text-white/30">Managed hosting</div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Decorative elements -->
                  <div class="absolute -z-10 -bottom-4 -right-4 w-24 h-24 bg-violet-500/10 rounded-full blur-2xl"></div>
                </div>
              </div>
            </transition>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { defineComponent, ref, reactive } from 'vue'
import { SectionPill } from '@/apps/home/components/atoms'

export default defineComponent({
  name: 'ProductTourSection',
  components: {
    SectionPill
  },
  setup() {
    const activeStep = ref(0)
    const tabRefs = reactive({})
    
    const handleKeyNav = (e) => {
      const totalSteps = 3
      let newIndex = activeStep.value
      
      if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
        e.preventDefault()
        newIndex = (activeStep.value + 1) % totalSteps
      } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
        e.preventDefault()
        newIndex = (activeStep.value - 1 + totalSteps) % totalSteps
      } else if (e.key === 'Home') {
        e.preventDefault()
        newIndex = 0
      } else if (e.key === 'End') {
        e.preventDefault()
        newIndex = totalSteps - 1
      }
      
      if (newIndex !== activeStep.value) {
        activeStep.value = newIndex
        tabRefs[newIndex]?.focus()
      }
    }
    
    const steps = [
      {
        title: 'Build',
        subtitle: 'Describe your app',
        icon: 'fas fa-wand-magic-sparkles',
        iconBg: 'bg-violet-500/15',
        iconColor: 'text-violet-400',
        checkBg: 'bg-violet-500/15',
        checkColor: 'text-violet-400',
        description: 'Simply describe what you want to build in plain English. Imagi\'s AI understands your requirements and generates a complete full-stack application with Vue.js frontend and Django backend.',
        features: [
          'Natural language input — no technical jargon needed',
          'Generates both frontend UI and backend APIs',
          'Creates data models and business logic automatically',
          'Production-ready code structure from the start'
        ],
        visualTitle: 'imagi-builder',
        ctaText: 'Start Building',
        ctaLink: '/auth/login'
      },
      {
        title: 'Refine',
        subtitle: 'Iterate via chat',
        icon: 'fas fa-comments',
        iconBg: 'bg-fuchsia-500/15',
        iconColor: 'text-fuchsia-400',
        checkBg: 'bg-fuchsia-500/15',
        checkColor: 'text-fuchsia-400',
        description: 'Make changes through natural conversation. Ask for new features, design tweaks, or functionality updates — the AI modifies your entire stack in real-time.',
        features: [
          'Chat-based editing for frontend and backend',
          'See changes reflected instantly in preview',
          'Add features incrementally as you go',
          'No need to understand the underlying code'
        ],
        visualTitle: 'imagi-chat',
        ctaText: 'Try It Now',
        ctaLink: '/auth/login'
      },
      {
        title: 'Deploy',
        subtitle: 'Go live instantly',
        icon: 'fas fa-rocket',
        iconBg: 'bg-amber-500/15',
        iconColor: 'text-amber-400',
        checkBg: 'bg-amber-500/15',
        checkColor: 'text-amber-400',
        description: 'Publish your app to the web with a single click. Imagi handles hosting, SSL certificates, and scaling — you just share your link.',
        features: [
          'One-click deployment to Imagi-hosted domains',
          'Automatic SSL and security configuration',
          'Custom domain support (coming soon)',
          'Built-in analytics and monitoring'
        ],
        visualTitle: 'imagi-deploy',
        ctaText: 'Get Notified',
        ctaLink: '/contact',
        comingSoon: true
      }
    ]
    
    return {
      activeStep,
      steps,
      tabRefs,
      handleKeyNav
    }
  }
})
</script>

<style scoped>
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}
</style>
