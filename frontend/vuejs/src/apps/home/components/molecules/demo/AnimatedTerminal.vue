<template>
  <div class="relative w-full max-w-2xl mx-auto">
    <!-- Terminal Window - Glass Morphism Style -->
    <div class="relative bg-dark-900/90 backdrop-blur-xl rounded-2xl border border-primary-500/10 shadow-2xl overflow-hidden transform-gpu transition-all duration-400 ease-out hover:-translate-y-1 hover:shadow-xl hover:shadow-primary-500/10">
      <!-- Terminal Header -->
      <div class="flex items-center justify-between px-5 py-3 bg-gradient-to-r from-dark-950/90 to-dark-900/90 border-b border-dark-800/50">
        <div class="flex items-center space-x-2.5">
          <div class="w-3 h-3 rounded-full bg-red-500/90 hover:opacity-80 transition-opacity cursor-pointer"></div>
          <div class="w-3 h-3 rounded-full bg-yellow-500/90 hover:opacity-80 transition-opacity cursor-pointer"></div>
          <div class="w-3 h-3 rounded-full bg-green-500/90 hover:opacity-80 transition-opacity cursor-pointer"></div>
        </div>
        <div class="absolute left-0 right-0 flex justify-center pointer-events-none">
          <div class="px-3 py-0.5 text-xs text-gray-400 bg-dark-800/50 rounded-md flex items-center font-mono font-medium border border-dark-700/30">
            <i class="fas fa-terminal mr-1.5 text-primary-400 text-[10px]"></i>
            imagi-cli
          </div>
        </div>
        <div class="flex items-center gap-2">
          <div class="w-1.5 h-1.5 rounded-full bg-green-400/60"></div>
          <div class="text-2xs text-gray-400 font-mono">online</div>
        </div>
      </div>

      <!-- Terminal Content -->
      <div class="p-4 font-mono text-sm bg-gradient-to-b from-dark-950 to-dark-900 min-h-[280px] max-h-[380px] overflow-hidden">
        <!-- First Section: Command Input -->
        <div class="flex items-center text-gray-300 mb-3">
          <div class="flex-shrink-0 flex items-center">
            <span class="text-emerald-400 mr-2">➜</span>
            <span class="text-emerald-500/90 mr-1.5">$</span>
          </div>
          <div class="flex-1">
            <span class="font-bold text-violet-400">imagi</span>
            <span class="text-gray-400"> generate app</span>
            <span class="ml-1 animate-blink text-gray-300">|</span>
          </div>
        </div>

        <!-- AI Assistant Interaction -->
        <div class="ml-3 space-y-3">
          <!-- AI Response -->
          <div class="flex items-start gap-2.5 transform-gpu animate-fade-slide-up">
            <div class="mt-0.5 w-5 h-5 rounded-full flex items-center justify-center bg-gradient-to-br from-violet-500 to-primary-600 p-0.5 ring-1 ring-primary-500/30 shadow-lg">
              <i class="fas fa-robot text-[10px] text-white"></i>
            </div>
            <div class="flex-1 break-words">
              <div class="rounded-xl rounded-tl-sm bg-dark-800/60 border border-dark-700/40 p-2 text-2xs text-gray-200">
                <div class="font-medium mb-1">Imagi Assistant</div>
                <div class="text-gray-300">What would you like to build today?</div>
              </div>
            </div>
          </div>

          <!-- User Message -->
          <div class="flex items-start gap-2.5 flex-row-reverse transform-gpu animate-fade-slide-up animate-delay-300">
            <div class="mt-0.5 w-5 h-5 rounded-full bg-dark-700 ring-1 ring-primary-500/20 flex items-center justify-center">
              <i class="fas fa-user text-[10px] text-gray-300"></i>
            </div>
            <div class="flex-1 break-words max-w-[90%]">
              <div class="rounded-xl rounded-tr-sm bg-primary-500/10 border border-primary-500/20 p-2 text-2xs text-gray-200">
                <div class="font-medium mb-1 text-primary-300">You</div>
                <div class="text-gray-300">
                  <span ref="typedText" class="typing-text"></span>
                  <span class="cursor-blink text-primary-300">|</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Process Steps Container -->
          <div v-if="showProgress" 
              class="bg-dark-800/40 rounded-xl border border-dark-700/50 p-2 mt-4 transform-gpu animate-fade-slide-up animate-delay-600">
            <div class="flex items-center justify-between mb-1.5 pb-1 border-b border-dark-700/30">
              <div class="text-2xs text-gray-400 font-medium flex items-center">
                <i class="fas fa-code-branch mr-1.5 text-primary-400"></i>
                Building your application
              </div>
              <div class="text-2xs text-gray-500">
                {{ Math.min(Math.round((currentStep / (progressSteps.length - 1)) * 100), 100) }}%
              </div>
            </div>
            
            <!-- Progress Steps -->
            <div class="space-y-1 px-0.5">
              <div v-for="(step, index) in progressSteps" :key="index"
                   class="relative flex items-center text-2xs py-1 transition-all duration-300"
                   :class="{ 
                     'text-gray-300': currentStep >= index, 
                     'text-gray-500': currentStep < index,
                     'font-medium': currentStep === index
                   }">
                
                <!-- Status Icon -->
                <div class="flex-shrink-0 w-4 h-4 mr-2 rounded-full flex items-center justify-center"
                     :class="{ 
                       'bg-dark-700/80': currentStep === index,
                       'bg-emerald-500/10': currentStep > index,
                       'bg-dark-800/50': currentStep < index
                     }">
                  <i v-if="currentStep === index" class="fas fa-spinner text-[0.6rem] text-primary-300 animate-spin"></i>
                  <i v-else-if="currentStep > index" class="fas fa-check text-[0.6rem] text-emerald-400"></i>
                  <i v-else class="fas fa-circle text-[0.5rem] text-dark-600"></i>
                </div>
                
                <div class="flex-1">{{ step }}</div>
                
                <!-- Time indicator -->
                <div v-if="currentStep >= index" class="flex-shrink-0 text-[10px] text-gray-500">
                  <span v-if="index === currentStep && currentStep < progressSteps.length">Processing...</span>
                  <span v-else>Done</span>
                </div>
              </div>
            </div>
            
            <!-- Progress Bar -->
            <div class="mt-2 h-1 bg-dark-700/50 rounded-full overflow-hidden">
              <div class="h-full bg-gradient-to-r from-primary-500 to-violet-500 rounded-full transition-all duration-700 ease-out"
                   :style="{width: `${Math.min(Math.round((currentStep / (progressSteps.length - 1)) * 100), 100)}%`}"></div>
            </div>
          </div>
          
          <!-- Generated Code Output -->
          <div v-if="showCodeOutput" class="mt-3 transform-gpu animate-fade-slide-up animate-delay-800">
            <div class="bg-dark-900/80 rounded-xl border border-dark-700/50 overflow-hidden">
              <div class="flex items-center justify-between text-2xs px-3 py-1.5 bg-dark-800/50 border-b border-dark-700/50">
                <div class="flex items-center">
                  <i class="fas fa-code text-primary-400 mr-1.5"></i>
                  <span class="text-gray-300">imagi.js</span>
                </div>
                <div class="flex items-center space-x-2 text-gray-400">
                  <i class="fas fa-copy hover:text-gray-300 cursor-pointer transition-colors"></i>
                  <i class="fas fa-expand hover:text-gray-300 cursor-pointer transition-colors"></i>
                </div>
              </div>
              <div class="bg-dark-950 p-2 relative">
                <pre class="text-2xs text-gray-300 overflow-x-auto max-h-[120px] font-mono">
<span class="text-violet-400">const</span> <span class="text-emerald-400">app</span> = <span class="text-violet-400">await</span> <span class="text-yellow-400">imagi</span>.<span class="text-blue-400">generate</span>({
  <span class="text-gray-500">name:</span> <span class="text-green-300">"{{ appName }}"</span>,
  <span class="text-gray-500">features:</span> [
    <span class="text-green-300">"auth"</span>, 
    <span class="text-green-300">"products"</span>, 
    <span class="text-green-300">"cart"</span>, 
    <span class="text-green-300">"payments"</span>
  ],
  <span class="text-gray-500">ui:</span> <span class="text-green-300">"modern"</span>
});</pre>
                <!-- Line numbers -->
                <div class="absolute left-0.5 top-2 bottom-0 text-[10px] text-gray-700 flex flex-col items-end pr-2 opacity-50">
                  <div v-for="n in 8" :key="`line-${n}`" class="leading-[1.4rem]">{{ n }}</div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Success Message -->
          <div v-if="showSuccess" class="mt-4 transform-gpu animate-fade-slide-up animate-delay-1000">
            <div class="flex items-start gap-2.5">
              <div class="flex-shrink-0 mt-0.5 w-5 h-5 rounded-full flex items-center justify-center bg-emerald-500/20 ring-1 ring-emerald-500/30">
                <i class="fas fa-check text-[0.65rem] text-emerald-400"></i>
              </div>
              <div class="flex-1 bg-gradient-to-r from-emerald-500/10 to-green-500/5 rounded-xl p-2.5 border border-emerald-500/20">
                <div class="flex items-center gap-2 mb-1">
                  <i class="fas fa-circle-check text-emerald-400"></i>
                  <span class="font-medium text-sm text-gray-200">App generated successfully!</span>
                </div>
                <div class="text-2xs text-gray-400 pl-0.5">
                  Your application is ready to be deployed. Type <span class="text-emerald-400 font-mono bg-dark-900/70 px-1.5 py-0.5 rounded">imagi deploy</span> to continue.
                </div>
                <div class="flex items-center gap-2 mt-2 text-2xs">
                  <button class="bg-dark-800/70 hover:bg-dark-700/70 transition-colors px-2.5 py-1 rounded-md text-gray-300 flex items-center gap-1.5">
                    <i class="fas fa-eye"></i>
                    <span>Preview</span>
                  </button>
                  <button class="bg-emerald-500/80 hover:bg-emerald-500/90 transition-colors px-2.5 py-1 rounded-md text-dark-900 flex items-center gap-1.5">
                    <i class="fas fa-rocket"></i>
                    <span>Deploy</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Enhanced Ambient Effects -->
    <div class="absolute -inset-0.5 bg-gradient-to-r from-primary-500/50 to-violet-500/50 opacity-10 blur-2xl -z-10 animate-pulse-slow"></div>
    <div class="absolute -inset-1 bg-gradient-conic from-primary-500/20 via-violet-500/20 to-primary-500/20 opacity-15 animate-spin-slow -z-20"></div>
    
    <!-- Terminal reflection -->
    <div class="absolute w-[60%] h-6 -bottom-2 left-[20%] bg-primary-500/5 blur-md rounded-full"></div>
  </div>
</template>

<script>
import { defineComponent, onMounted, ref } from 'vue'

export default defineComponent({
  name: 'AnimatedTerminal',
  setup() {
    const typedText = ref(null)
    const showProgress = ref(false)
    const currentStep = ref(-1)
    const showCodeOutput = ref(false)
    const showSuccess = ref(false)
    const appName = ref('e-commerce-platform')

    const progressSteps = [
      'Analyzing requirements',
      'Generating components',
      'Building API endpoints',
      'Optimizing code',
      'Ready to deploy'
    ]

    const typeText = async (element, text, speed = 40) => {
      for (let i = 0; i < text.length; i++) {
        element.textContent += text[i]
        await new Promise(resolve => setTimeout(resolve, speed))
      }
    }

    const animateProgress = async () => {
      // Wait a moment before starting the progress animation
      await new Promise(resolve => setTimeout(resolve, 800))
      showProgress.value = true
      
      // Animate through each progress step
      for (let i = 0; i < progressSteps.length; i++) {
        currentStep.value = i
        
        // Show code output after analyzing requirements
        if (i === 1 && !showCodeOutput.value) {
          await new Promise(resolve => setTimeout(resolve, 400))
          showCodeOutput.value = true
        }
        
        // Adjust timing for different steps
        const delay = i === progressSteps.length - 1 ? 1500 : 1000
        await new Promise(resolve => setTimeout(resolve, delay))
      }
      
      // Mark the last step as completed with a checkmark
      await new Promise(resolve => setTimeout(resolve, 300))
      currentStep.value = progressSteps.length
      
      // Show success message after the last step is marked as completed
      await new Promise(resolve => setTimeout(resolve, 300))
      showSuccess.value = true
    }

    onMounted(async () => {
      const text = "Create a modern e-commerce platform with user authentication, product catalog, shopping cart, and secure payment integration"
      await typeText(typedText.value, text)
      await animateProgress()
    })

    return {
      typedText,
      showProgress,
      currentStep,
      progressSteps,
      showCodeOutput,
      showSuccess,
      appName
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

@keyframes fade-slide-up {
  from { 
    opacity: 0;
    transform: translateY(8px);
  }
  to { 
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-slide-up {
  animation: fade-slide-up 0.5s ease-out forwards;
}

.animate-delay-300 {
  animation-delay: 300ms;
}

.animate-delay-600 {
  animation-delay: 600ms;
}

.animate-delay-800 {
  animation-delay: 800ms;
}

.animate-delay-1000 {
  animation-delay: 1000ms;
}

@keyframes pulse-slow {
  0%, 100% { opacity: 0.1; }
  50% { opacity: 0.15; }
}

.animate-pulse-slow {
  animation: pulse-slow 4s ease-in-out infinite;
}

.animate-spin-slow {
  animation: spin 10s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Typography */
.text-2xs {
  font-size: 0.65rem;
  line-height: 1rem;
}

/* Override any dark-950 if not available in Tailwind config */
.bg-dark-950 {
  background-color: rgba(9, 11, 17, 0.95);
}

.from-dark-950 {
  --tw-gradient-from: rgba(9, 11, 17, 0.95);
}

.to-dark-950 {
  --tw-gradient-to: rgba(9, 11, 17, 0.95);
}
</style>

