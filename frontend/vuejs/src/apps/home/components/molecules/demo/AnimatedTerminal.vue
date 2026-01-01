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
            imagi-cli
          </div>
        </div>
        <div class="flex items-center gap-1.5">
          <span class="relative flex h-1.5 w-1.5">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-400"></span>
          </span>
          <span class="text-[9px] text-white/30 font-mono">online</span>
        </div>
      </div>

      <!-- Terminal Content -->
      <div class="p-4 font-mono text-xs min-h-[240px]">
        <!-- Command Input -->
        <div class="flex items-center text-white/70 mb-3">
          <span class="text-emerald-400 mr-1.5">➜</span>
          <span class="text-white/30 mr-1.5">$</span>
          <span class="font-medium text-violet-400">imagi</span>
          <span class="text-white/40 ml-1">generate app</span>
          <span class="ml-1 animate-blink text-white/50">│</span>
        </div>

        <!-- AI Conversation -->
        <div class="ml-3 space-y-3">
          <!-- AI Response -->
          <div class="flex items-start gap-2 animate-fade-in">
            <div class="mt-0.5 w-5 h-5 rounded-full flex items-center justify-center bg-gradient-to-br from-violet-500 to-fuchsia-500 shadow-lg shadow-violet-500/20">
              <i class="fas fa-robot text-[9px] text-white"></i>
            </div>
            <div class="flex-1">
              <div class="rounded-lg rounded-tl-sm bg-white/[0.03] border border-white/[0.06] p-2 text-[11px]">
                <div class="font-medium text-white/50 mb-0.5">Imagi Assistant</div>
                <div class="text-white/70">What would you like to build today?</div>
              </div>
            </div>
          </div>

          <!-- User Message -->
          <div class="flex items-start gap-2 flex-row-reverse animate-fade-in" style="animation-delay: 300ms">
            <div class="mt-0.5 w-5 h-5 rounded-full bg-white/[0.05] border border-white/[0.08] flex items-center justify-center">
              <i class="fas fa-user text-[9px] text-white/40"></i>
            </div>
            <div class="flex-1 max-w-[90%]">
              <div class="rounded-lg rounded-tr-sm bg-violet-500/10 border border-violet-500/20 p-2 text-[11px]">
                <div class="font-medium text-violet-400/70 mb-0.5">You</div>
                <div class="text-white/70">
                  <span class="typing-text">{{ typedText }}</span>
                  <span class="cursor-blink text-violet-400">│</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Progress Section -->
          <div v-if="showProgress" 
               class="bg-white/[0.02] rounded-lg border border-white/[0.06] p-3 mt-3 animate-fade-in" 
               style="animation-delay: 600ms">
            <div class="flex items-center justify-between mb-2 pb-1.5 border-b border-white/[0.04]">
              <div class="text-[10px] text-white/40 font-medium flex items-center gap-1.5">
                <i class="fas fa-code-branch text-violet-400/60 text-[9px]"></i>
                Building your application
              </div>
              <div class="text-[10px] text-white/30 font-mono">
                {{ Math.min(Math.round((currentStep / (progressSteps.length - 1)) * 100), 100) }}%
              </div>
            </div>
            
            <!-- Progress Steps -->
            <div class="space-y-1.5">
              <div v-for="(step, index) in progressSteps" :key="index"
                   class="flex items-center text-[11px] py-1 transition-all duration-300"
                   :class="{ 
                     'text-white/70': currentStep >= index, 
                     'text-white/30': currentStep < index
                   }">
                <div class="flex-shrink-0 w-4 h-4 mr-2 rounded-full flex items-center justify-center"
                     :class="{ 
                       'bg-violet-500/15': currentStep === index,
                       'bg-emerald-500/15': currentStep > index,
                       'bg-white/[0.03]': currentStep < index
                     }">
                  <i v-if="currentStep === index" class="fas fa-spinner text-[8px] text-violet-400 animate-spin"></i>
                  <i v-else-if="currentStep > index" class="fas fa-check text-[8px] text-emerald-400"></i>
                  <i v-else class="fas fa-circle text-[4px] text-white/20"></i>
                </div>
                <span class="flex-1">{{ step }}</span>
                <span v-if="currentStep >= index" class="text-[9px] text-white/30">
                  {{ index === currentStep && currentStep < progressSteps.length ? 'Processing...' : 'Done' }}
                </span>
              </div>
            </div>
            
            <!-- Progress Bar -->
            <div class="mt-2.5 h-0.5 bg-white/[0.03] rounded-full overflow-hidden">
              <div class="h-full bg-gradient-to-r from-violet-500 to-fuchsia-500 rounded-full transition-all duration-700 ease-out"
                   :style="{width: `${Math.min(Math.round((currentStep / (progressSteps.length - 1)) * 100), 100)}%`}"></div>
            </div>
          </div>
          
          <!-- Success Message -->
          <div v-if="showSuccess" class="mt-3 animate-fade-in" style="animation-delay: 1000ms">
            <div class="flex items-start gap-2">
              <div class="flex-shrink-0 mt-0.5 w-5 h-5 rounded-full flex items-center justify-center bg-emerald-500/15">
                <i class="fas fa-check text-[9px] text-emerald-400"></i>
              </div>
              <div class="flex-1 bg-emerald-500/5 rounded-lg p-2.5 border border-emerald-500/10">
                <div class="flex items-center gap-1.5 mb-1.5">
                  <i class="fas fa-circle-check text-emerald-400 text-xs"></i>
                  <span class="font-medium text-xs text-white/80">App generated successfully!</span>
                </div>
                <p class="text-[10px] text-white/40 mb-2">
                  Your application is ready. Type <code class="text-emerald-400 bg-white/[0.03] px-1 py-0.5 rounded font-mono text-[9px]">imagi deploy</code> to continue.
                </p>
                <div class="flex items-center gap-1.5">
                  <button class="text-[10px] bg-white/[0.05] hover:bg-white/[0.08] transition-colors px-2 py-1 rounded-md text-white/60 flex items-center gap-1 border border-white/[0.06]">
                    <i class="fas fa-eye text-[8px]"></i>
                    <span>Preview</span>
                  </button>
                  <button class="text-[10px] bg-emerald-500/80 hover:bg-emerald-500 transition-colors px-2 py-1 rounded-md text-white flex items-center gap-1 font-medium">
                    <i class="fas fa-rocket text-[8px]"></i>
                    <span>Deploy</span>
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
import { defineComponent, onMounted, onBeforeUnmount, ref } from 'vue'

export default defineComponent({
  name: 'AnimatedTerminal',
  setup() {
    const typedText = ref('')
    const showProgress = ref(false)
    const currentStep = ref(-1)
    const showSuccess = ref(false)
    let animationActive = true

    const progressSteps = [
      'Analyzing requirements',
      'Generating components',
      'Building API endpoints',
      'Optimizing code',
      'Ready to deploy'
    ]

    const typeText = async (text, speed = 40) => {
      for (let i = 0; i < text.length && animationActive; i++) {
        typedText.value += text[i]
        await new Promise(resolve => setTimeout(resolve, speed))
      }
    }

    const animateProgress = async () => {
      if (!animationActive) return
      await new Promise(resolve => setTimeout(resolve, 800))
      showProgress.value = true
      
      for (let i = 0; i < progressSteps.length && animationActive; i++) {
        currentStep.value = i
        
        const delay = i === progressSteps.length - 1 ? 1500 : 1000
        await new Promise(resolve => setTimeout(resolve, delay))
      }
      
      if (!animationActive) return
      await new Promise(resolve => setTimeout(resolve, 300))
      currentStep.value = progressSteps.length
      
      await new Promise(resolve => setTimeout(resolve, 300))
      if (animationActive) {
        showSuccess.value = true
      }
    }

    onMounted(async () => {
      const text = "Create an e-commerce platform with authentication, product catalog, and payment integration"
      await typeText(text)
      await animateProgress()
    })

    onBeforeUnmount(() => {
      animationActive = false
    })

    return {
      typedText,
      showProgress,
      currentStep,
      progressSteps,
      showSuccess
    }
  }
})
</script>

<style scoped>
@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.animate-blink {
  animation: blink 1s step-end infinite;
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
</style>
