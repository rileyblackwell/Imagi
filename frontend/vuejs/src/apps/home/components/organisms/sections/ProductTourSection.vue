<!-- Product Tour Section - Clean Apple/Cursor-inspired design -->
<template>
  <section class="py-24 md:py-32 px-6 sm:px-8 lg:px-12">
    <div class="max-w-6xl mx-auto">
      
      <!-- Section header -->
      <div class="text-center mb-16">
        <p class="text-sm font-medium text-gray-500 dark:text-white/50 uppercase tracking-widest mb-4 transition-colors duration-300">How it works</p>
        <h2 class="text-4xl sm:text-5xl md:text-6xl font-semibold text-gray-900 dark:text-white mb-6 tracking-tight transition-colors duration-300">
          Three simple steps
        </h2>
        <p class="text-xl text-gray-500 dark:text-white/60 max-w-2xl mx-auto transition-colors duration-300">
          From idea to deployed app in minutes. No coding, no complexity.
        </p>
      </div>

      <!-- Step tabs -->
      <div 
        class="flex items-center justify-center gap-2 mb-12"
        role="tablist"
        aria-label="Product tour steps"
      >
        <button
          v-for="(step, idx) in steps"
          :key="idx"
          @click="activeStep = idx"
          class="relative flex items-center gap-3 px-5 py-3 rounded-full transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-gray-300 dark:focus:ring-white/20"
          :class="activeStep === idx 
            ? 'bg-gray-900 dark:bg-white text-white dark:text-gray-900' 
            : 'bg-gray-100 dark:bg-white/5 text-gray-600 dark:text-white/60 hover:bg-gray-200 dark:hover:bg-white/10'"
          :aria-selected="activeStep === idx"
          role="tab"
        >
          <span class="text-sm font-medium">{{ idx + 1 }}. {{ step.title }}</span>
          <span v-if="step.comingSoon" 
                class="px-2 py-0.5 bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400 rounded text-[10px] font-medium">
            Soon
          </span>
        </button>
      </div>

      <!-- Content Panel -->
      <div class="relative">
        <div class="rounded-2xl border border-gray-200 dark:border-white/10 bg-white dark:bg-white/[0.02] overflow-hidden transition-colors duration-300">
          <transition name="fade" mode="out-in">
            <div 
              :key="activeStep" 
              class="grid md:grid-cols-2 gap-8 md:gap-12 p-8 md:p-12"
            >
              <!-- Left: Description -->
              <div class="flex flex-col justify-center">
                <div class="flex items-center gap-3 mb-4">
                  <div class="flex items-center justify-center w-10 h-10 rounded-xl bg-gray-100 dark:bg-white/5 transition-colors duration-300">
                    <i :class="[steps[activeStep].icon, 'text-lg text-gray-700 dark:text-white/70']"></i>
                  </div>
                  <h3 class="text-2xl font-semibold text-gray-900 dark:text-white transition-colors duration-300">
                    {{ steps[activeStep].title }}
                  </h3>
                </div>
                
                <p class="text-gray-500 dark:text-white/60 leading-relaxed mb-6 transition-colors duration-300">
                  {{ steps[activeStep].description }}
                </p>
                
                <!-- Feature list -->
                <ul class="space-y-3 mb-8">
                  <li v-for="(feature, fIdx) in steps[activeStep].features" :key="fIdx"
                      class="flex items-start gap-3">
                    <svg class="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                    <span class="text-gray-600 dark:text-white/70 transition-colors duration-300">{{ feature }}</span>
                  </li>
                </ul>
                
                <!-- CTA -->
                <div>
                  <router-link 
                    v-if="!steps[activeStep].comingSoon"
                    :to="steps[activeStep].ctaLink"
                    class="inline-flex items-center gap-2 px-6 py-3 bg-gray-900 dark:bg-white text-white dark:text-gray-900 rounded-full font-medium transition-all duration-300 hover:scale-[1.02]"
                  >
                    {{ steps[activeStep].ctaText }}
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
                    </svg>
                  </router-link>
                  <button 
                    v-else
                    class="inline-flex items-center gap-2 px-6 py-3 bg-gray-100 dark:bg-white/5 text-gray-600 dark:text-white/60 rounded-full font-medium transition-colors duration-300"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                    </svg>
                    {{ steps[activeStep].ctaText }}
                  </button>
                </div>
              </div>
              
              <!-- Right: Visual -->
              <div class="relative">
                <div class="rounded-xl border border-gray-200 dark:border-white/10 bg-gray-50 dark:bg-[#0a0a0a] overflow-hidden transition-colors duration-300">
                  <!-- Visual header -->
                  <div class="flex items-center gap-2 px-4 py-3 bg-white dark:bg-white/[0.02] border-b border-gray-200 dark:border-white/10 transition-colors duration-300">
                    <div class="flex items-center gap-1.5">
                      <div class="w-3 h-3 rounded-full bg-red-400"></div>
                      <div class="w-3 h-3 rounded-full bg-yellow-400"></div>
                      <div class="w-3 h-3 rounded-full bg-green-400"></div>
                    </div>
                    <div class="flex-1 text-center">
                      <span class="text-xs text-gray-400 dark:text-white/30 font-mono">{{ steps[activeStep].visualTitle }}</span>
                    </div>
                  </div>
                  
                  <!-- Visual content -->
                  <div class="p-6 min-h-[240px]">
                    <!-- Build step visual -->
                    <div v-if="activeStep === 0" class="space-y-4">
                      <div class="flex items-center gap-2 text-sm text-gray-400 dark:text-white/40 mb-4">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                        <span>Describe your app...</span>
                      </div>
                      <div class="bg-white dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-lg p-4 transition-colors duration-300">
                        <p class="text-sm text-gray-600 dark:text-white/70 leading-relaxed">
                          "Build a customer portal with login, dashboard showing recent orders, and a support ticket system"
                        </p>
                      </div>
                      <div class="flex items-center gap-3 mt-6">
                        <div class="h-1 flex-1 bg-gray-200 dark:bg-white/10 rounded-full overflow-hidden">
                          <div class="h-full w-3/4 bg-gray-400 dark:bg-white/40 rounded-full animate-pulse"></div>
                        </div>
                        <span class="text-xs text-gray-400 dark:text-white/40">Generating...</span>
                      </div>
                    </div>
                    
                    <!-- Refine step visual -->
                    <div v-else-if="activeStep === 1" class="space-y-4">
                      <div class="flex items-start gap-3">
                        <div class="w-8 h-8 rounded-full bg-gray-100 dark:bg-white/10 flex items-center justify-center flex-shrink-0 transition-colors duration-300">
                          <svg class="w-4 h-4 text-gray-500 dark:text-white/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                          </svg>
                        </div>
                        <div class="bg-gray-100 dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-lg rounded-tl-none p-3 transition-colors duration-300">
                          <p class="text-sm text-gray-600 dark:text-white/60">Your dashboard is ready! Want me to add charts or change the color scheme?</p>
                        </div>
                      </div>
                      <div class="flex items-start gap-3 flex-row-reverse">
                        <div class="w-8 h-8 rounded-full bg-gray-900 dark:bg-white flex items-center justify-center flex-shrink-0">
                          <svg class="w-4 h-4 text-white dark:text-gray-900" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                          </svg>
                        </div>
                        <div class="bg-gray-900 dark:bg-white rounded-lg rounded-tr-none p-3">
                          <p class="text-sm text-white dark:text-gray-900">Add a bar chart for monthly sales and make the header dark blue</p>
                        </div>
                      </div>
                      <div class="flex items-center gap-2 text-sm text-green-600 dark:text-green-400 mt-4">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                        </svg>
                        <span>Changes applied instantly</span>
                      </div>
                    </div>
                    
                    <!-- Deploy step visual -->
                    <div v-else class="space-y-4">
                      <div class="flex items-center justify-between mb-6">
                        <span class="text-sm text-gray-500 dark:text-white/50">Deployment Status</span>
                        <span class="px-2 py-1 bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400 rounded text-xs font-medium">Coming Soon</span>
                      </div>
                      <div class="space-y-3">
                        <div class="flex items-center gap-4 p-4 bg-white dark:bg-white/5 rounded-lg border border-gray-200 dark:border-white/10 transition-colors duration-300">
                          <svg class="w-5 h-5 text-gray-500 dark:text-white/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                          </svg>
                          <div class="flex-1">
                            <div class="text-sm font-medium text-gray-700 dark:text-white/80">your-app.imagi.app</div>
                            <div class="text-xs text-gray-400 dark:text-white/40">Custom domain support</div>
                          </div>
                          <svg class="w-4 h-4 text-gray-400 dark:text-white/40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                          </svg>
                        </div>
                        <div class="flex items-center gap-4 p-4 bg-white dark:bg-white/5 rounded-lg border border-gray-200 dark:border-white/10 transition-colors duration-300">
                          <svg class="w-5 h-5 text-gray-500 dark:text-white/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
                          </svg>
                          <div class="flex-1">
                            <div class="text-sm font-medium text-gray-700 dark:text-white/80">Auto-scaling infrastructure</div>
                            <div class="text-xs text-gray-400 dark:text-white/40">Managed hosting</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </transition>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { defineComponent, ref } from 'vue'

export default defineComponent({
  name: 'ProductTourSection',
  setup() {
    const activeStep = ref(0)
    
    const steps = [
      {
        title: 'Build',
        icon: 'fas fa-wand-magic-sparkles',
        description: 'Describe what you want to build in plain English. Imagi\'s AI understands your requirements and generates a complete full-stack application.',
        features: [
          'Natural language input — no technical jargon',
          'Generates both frontend UI and backend APIs',
          'Creates data models automatically',
          'Production-ready code structure'
        ],
        visualTitle: 'imagi-builder',
        ctaText: 'Start Building',
        ctaLink: '/auth/login'
      },
      {
        title: 'Refine',
        icon: 'fas fa-comments',
        description: 'Make changes through natural conversation. Ask for new features, design tweaks, or functionality updates — the AI modifies your entire stack in real-time.',
        features: [
          'Chat-based editing for frontend and backend',
          'See changes reflected instantly',
          'Add features incrementally',
          'No need to understand the code'
        ],
        visualTitle: 'imagi-chat',
        ctaText: 'Try It Now',
        ctaLink: '/auth/login'
      },
      {
        title: 'Deploy',
        icon: 'fas fa-rocket',
        description: 'Publish your app to the web with a single click. Imagi handles hosting, SSL certificates, and scaling — you just share your link.',
        features: [
          'One-click deployment',
          'Automatic SSL and security',
          'Custom domain support',
          'Built-in analytics'
        ],
        visualTitle: 'imagi-deploy',
        ctaText: 'Get Notified',
        ctaLink: '/contact',
        comingSoon: true
      }
    ]
    
    return {
      activeStep,
      steps
    }
  }
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
