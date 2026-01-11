<template>
  <div class="relative w-full max-w-2xl mx-auto">
    <!-- Terminal Window -->
    <div class="relative bg-[#0a0a0f] rounded-xl overflow-hidden">
      <!-- Terminal Header -->
      <div class="flex items-center justify-between px-3 py-2 bg-white/[0.03] border-b border-white/[0.06]">
        <div class="flex items-center gap-1.5">
          <div class="w-2.5 h-2.5 rounded-full bg-[#ff5f57] hover:opacity-80 transition-opacity cursor-pointer"></div>
          <div class="w-2.5 h-2.5 rounded-full bg-[#febc2e] hover:opacity-80 transition-opacity cursor-pointer"></div>
          <div class="w-2.5 h-2.5 rounded-full bg-[#28c840] hover:opacity-80 transition-opacity cursor-pointer"></div>
        </div>
        <div class="absolute left-1/2 -translate-x-1/2">
          <div class="flex items-center gap-1.5 px-2 py-0.5 text-[10px] text-white/40 bg-white/[0.03] rounded-md border border-white/[0.06] font-mono">
            <i class="fas fa-terminal text-violet-400/60 text-[9px]"></i>
            imagi-builder
          </div>
        </div>
        <div class="flex items-center gap-1.5">
          <span class="relative flex h-1.5 w-1.5">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-400"></span>
          </span>
          <span class="text-[9px] text-white/30 font-mono">connected</span>
        </div>
      </div>

      <!-- Phase Indicator -->
      <div class="flex items-center justify-center gap-1 px-4 py-2 bg-white/[0.02] border-b border-white/[0.04]">
        <div v-for="(phase, idx) in phases" :key="idx" 
             class="flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[10px] font-medium transition-all duration-500"
             :class="currentPhase >= idx 
               ? 'bg-gradient-to-r from-violet-500/20 to-fuchsia-500/20 text-white/80 border border-violet-500/30' 
               : 'text-white/30'">
          <i :class="[phase.icon, 'text-[9px]', currentPhase >= idx ? phase.activeColor : 'text-white/20']"></i>
          <span>{{ phase.label }}</span>
          <i v-if="currentPhase > idx" class="fas fa-check text-[8px] text-emerald-400 ml-0.5"></i>
          <span v-if="phase.comingSoon && currentPhase >= idx" class="ml-1 px-1 py-0.5 bg-amber-500/20 rounded text-[8px] text-amber-300/80">Soon</span>
        </div>
      </div>

      <!-- Terminal Content -->
      <div class="p-3 font-mono text-xs min-h-[200px]">
        <!-- Phase 1: Generate -->
        <div v-if="currentPhase >= 0" class="animate-fade-in">
          <!-- Command Input -->
          <div class="flex items-center text-white/70 mb-2 text-[10px]">
            <span class="text-emerald-400 mr-1">➜</span>
            <span class="text-white/30 mr-1">~</span>
            <span class="font-medium text-violet-400">imagi</span>
            <span class="text-white/40 ml-1">build</span>
          </div>

          <!-- AI Conversation -->
          <div class="ml-3 space-y-2">
            <!-- AI Response -->
            <div class="flex items-start gap-1.5">
              <div class="mt-0.5 w-4 h-4 rounded-full flex items-center justify-center bg-gradient-to-br from-violet-500 to-fuchsia-500 shadow-lg shadow-violet-500/20">
                <i class="fas fa-robot text-[8px] text-white"></i>
              </div>
              <div class="flex-1">
                <div class="rounded-lg rounded-tl-sm bg-white/[0.03] border border-white/[0.06] p-1.5 text-[10px]">
                  <div class="font-medium text-white/50 mb-0.5">Imagi</div>
                  <div class="text-white/70">Describe your app idea and I'll build it for you.</div>
                </div>
              </div>
            </div>

            <!-- User Message -->
            <div class="flex items-start gap-1.5 flex-row-reverse" style="animation-delay: 300ms">
              <div class="mt-0.5 w-4 h-4 rounded-full bg-white/[0.05] border border-white/[0.08] flex items-center justify-center">
                <i class="fas fa-user text-[8px] text-white/40"></i>
              </div>
              <div class="flex-1 max-w-[90%]">
                <div class="rounded-lg rounded-tr-sm bg-violet-500/10 border border-violet-500/20 p-1.5 text-[10px]">
                  <div class="font-medium text-violet-400/70 mb-0.5">You</div>
                  <div class="text-white/70">
                    <span class="typing-text">{{ typedText }}</span>
                    <span v-if="isTyping" class="cursor-blink text-violet-400">│</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Progress Section -->
            <div v-if="showProgress" 
                 class="bg-white/[0.02] rounded-lg border border-white/[0.06] p-2 mt-2 animate-fade-in">
              <div class="flex items-center justify-between mb-1.5 pb-1 border-b border-white/[0.04]">
                <div class="text-[9px] text-white/40 font-medium flex items-center gap-1">
                  <i class="fas fa-cog text-violet-400/60 text-[8px] animate-spin-slow"></i>
                  Generating full-stack application
                </div>
                <div class="text-[9px] text-white/30 font-mono">
                  {{ progressPercent }}%
                </div>
              </div>
              
              <!-- Progress Steps -->
              <div class="space-y-1">
                <div v-for="(step, index) in progressSteps" :key="index"
                     class="flex items-center text-[10px] py-0.5 transition-all duration-300"
                     :class="{ 
                       'text-white/70': currentStep >= index, 
                       'text-white/30': currentStep < index
                     }">
                  <div class="flex-shrink-0 w-3.5 h-3.5 mr-1.5 rounded-full flex items-center justify-center"
                       :class="{ 
                         'bg-violet-500/15': currentStep === index,
                         'bg-emerald-500/15': currentStep > index,
                         'bg-white/[0.03]': currentStep < index
                       }">
                    <i v-if="currentStep === index" class="fas fa-spinner text-[7px] text-violet-400 animate-spin"></i>
                    <i v-else-if="currentStep > index" class="fas fa-check text-[7px] text-emerald-400"></i>
                    <i v-else class="fas fa-circle text-[3px] text-white/20"></i>
                  </div>
                  <span class="flex-1">{{ step.label }}</span>
                  <span class="text-[8px] text-white/20">{{ step.type }}</span>
                </div>
              </div>
              
              <!-- Progress Bar -->
              <div class="mt-2 h-0.5 bg-white/[0.03] rounded-full overflow-hidden">
                <div class="h-full bg-gradient-to-r from-violet-500 to-fuchsia-500 rounded-full transition-all duration-700 ease-out"
                     :style="{width: `${progressPercent}%`}"></div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Phase 2: Deploy (Coming Soon) -->
        <div v-if="currentPhase >= 1 && showDeploy" class="mt-3 animate-fade-in">
          <div class="rounded-lg border border-amber-500/20 bg-amber-500/5 p-2">
            <div class="flex items-start gap-1.5">
              <div class="w-4 h-4 rounded-full flex items-center justify-center bg-amber-500/15 mt-0.5">
                <i class="fas fa-rocket text-[8px] text-amber-400"></i>
              </div>
              <div class="flex-1">
                <div class="flex items-center gap-1.5 mb-1">
                  <span class="text-[10px] text-white/80 font-medium">One-Click Deploy</span>
                  <span class="px-1 py-0.5 bg-amber-500/20 rounded text-[8px] text-amber-300 font-medium">Coming Soon</span>
                </div>
                <p class="text-[9px] text-white/40 mb-1.5">
                  Deploy your app to an Imagi-hosted domain with a single click. Custom domains and SSL included.
                </p>
                <div class="flex items-center gap-1.5">
                  <div class="flex items-center gap-1 px-1.5 py-0.5 bg-white/[0.03] rounded border border-white/[0.06] text-[9px] text-white/50">
                    <i class="fas fa-globe text-[7px]"></i>
                    <span>your-app.imagi.app</span>
                  </div>
                  <button class="px-1.5 py-0.5 bg-amber-500/20 hover:bg-amber-500/30 rounded text-[9px] text-amber-300 font-medium transition-colors border border-amber-500/30">
                    <i class="fas fa-bell text-[7px] mr-0.5"></i>
                    Notify Me
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, onMounted, onBeforeUnmount, ref, computed } from 'vue'

export default defineComponent({
  name: 'AnimatedTerminal',
  setup() {
    const typedText = ref('')
    const isTyping = ref(true)
    const showProgress = ref(false)
    const currentStep = ref(-1)
    const currentPhase = ref(0)
    const showDeploy = ref(false)
    let animationActive = true

    const phases = [
      { label: 'Generate', icon: 'fas fa-wand-magic-sparkles', activeColor: 'text-violet-400' },
      { label: 'Deploy', icon: 'fas fa-rocket', activeColor: 'text-amber-400', comingSoon: true }
    ]

    const progressSteps = [
      { label: 'Analyzing requirements', type: 'AI' },
      { label: 'Generating Vue.js frontend', type: 'Frontend' },
      { label: 'Building Django backend', type: 'Backend' },
      { label: 'Creating API endpoints', type: 'API' },
      { label: 'Optimizing & bundling', type: 'Build' }
    ]

    const progressPercent = computed(() => {
      if (currentStep.value < 0) return 0
      return Math.min(Math.round(((currentStep.value + 1) / progressSteps.length) * 100), 100)
    })

    const typeText = async (text, speed = 35) => {
      for (let i = 0; i < text.length && animationActive; i++) {
        typedText.value += text[i]
        await new Promise(resolve => setTimeout(resolve, speed))
      }
      isTyping.value = false
    }

    const animateProgress = async () => {
      if (!animationActive) return
      await new Promise(resolve => setTimeout(resolve, 600))
      showProgress.value = true
      
      for (let i = 0; i < progressSteps.length && animationActive; i++) {
        currentStep.value = i
        const delay = i === progressSteps.length - 1 ? 1200 : 800
        await new Promise(resolve => setTimeout(resolve, delay))
      }
      
      if (!animationActive) return
      currentStep.value = progressSteps.length
    }

    const animatePhases = async () => {
      // Phase 1: Generate
      const text = "Build a project management dashboard with team collaboration and task tracking"
      await typeText(text)
      await animateProgress()
      
      if (!animationActive) return
      await new Promise(resolve => setTimeout(resolve, 800))
      
      // Phase 2: Deploy (Coming Soon)
      currentPhase.value = 1
      await new Promise(resolve => setTimeout(resolve, 400))
      showDeploy.value = true
    }

    onMounted(() => {
      animatePhases()
    })

    onBeforeUnmount(() => {
      animationActive = false
    })

    return {
      typedText,
      isTyping,
      showProgress,
      currentStep,
      currentPhase,
      phases,
      progressSteps,
      progressPercent,
      showDeploy
    }
  }
})
</script>

<style scoped>
@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.cursor-blink {
  animation: blink 1s step-end infinite;
}

@keyframes fade-in {
  from { 
    opacity: 0;
    transform: translateY(4px);
  }
  to { 
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  opacity: 0;
  animation: fade-in 0.5s ease-out forwards;
}

@keyframes spin-slow {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.animate-spin-slow {
  animation: spin-slow 3s linear infinite;
}
</style>
