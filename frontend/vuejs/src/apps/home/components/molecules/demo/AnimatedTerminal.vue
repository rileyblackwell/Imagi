<template>
  <div class="relative w-full max-w-2xl mx-auto">
    <!-- Terminal Window -->
    <div class="relative bg-dark-800/80 backdrop-blur-xl rounded-xl border border-dark-700/50 shadow-2xl overflow-hidden">
      <!-- Terminal Header -->
      <div class="flex items-center justify-between px-4 py-2 bg-dark-900/50 border-b border-dark-700/50">
        <div class="flex items-center space-x-2">
          <div class="w-3 h-3 rounded-full bg-red-500"></div>
          <div class="w-3 h-3 rounded-full bg-yellow-500"></div>
          <div class="w-3 h-3 rounded-full bg-green-500"></div>
        </div>
        <div class="text-sm text-gray-400">imagi-cli</div>
      </div>

      <!-- Terminal Content -->
      <div class="p-4 font-mono text-sm">
        <div class="space-y-2">
          <!-- Command Line -->
          <div class="flex items-center text-gray-300">
            <span class="text-primary-400">➜</span>
            <span class="ml-2 text-violet-400">imagi</span>
            <span class="ml-2 text-gray-500">generate app</span>
          </div>

          <!-- AI Response -->
          <div class="pl-4">
            <div class="flex items-center text-primary-300 mb-2">
              <i class="fas fa-robot mr-2"></i>
              <span>AI Assistant ready. What would you like to build?</span>
            </div>

            <!-- Typed User Request -->
            <div class="text-gray-300 mb-3">
              <span class="text-violet-400">"</span>
              <span ref="typedText" class="typing-text"></span>
              <span class="animate-pulse">|</span>
              <span class="text-violet-400">"</span>
            </div>

            <!-- Progress Indicators -->
            <div v-if="showProgress" class="space-y-2 transition-opacity"
                 :class="{ 'opacity-100': showProgress, 'opacity-0': !showProgress }">
              <div v-for="(step, index) in progressSteps" :key="index"
                   class="flex items-center text-gray-400"
                   :class="{ 'text-primary-400': currentStep >= index }">
                <i class="fas fa-circle-notch mr-2" 
                   :class="{ 'animate-spin': currentStep === index }"></i>
                {{ step }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Decorative Elements -->
    <div class="absolute -inset-0.5 bg-gradient-to-r from-primary-500 to-violet-500 opacity-20 blur-2xl -z-10"></div>
    <div class="absolute -inset-1 bg-gradient-conic from-primary-500/40 via-violet-500/40 to-primary-500/40 opacity-30 animate-spin-slow -z-20"></div>
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

    const progressSteps = [
      'Analyzing requirements...',
      'Generating components...',
      'Building API endpoints...',
      'Optimizing code...',
      'Ready to deploy!'
    ]

    const typeText = async (element, text, speed = 50) => {
      for (let i = 0; i < text.length; i++) {
        element.textContent += text[i]
        await new Promise(resolve => setTimeout(resolve, speed))
      }
    }

    const animateProgress = async () => {
      showProgress.value = true
      for (let i = 0; i <= progressSteps.length; i++) {
        currentStep.value = i
        await new Promise(resolve => setTimeout(resolve, 1000))
      }
    }

    onMounted(async () => {
      const text = "Create a modern e-commerce platform with user authentication, product catalog, shopping cart, and secure payments"
      await typeText(typedText.value, text)
      await animateProgress()
    })

    return {
      typedText,
      showProgress,
      currentStep,
      progressSteps
    }
  }
})
</script>

<style scoped>
.animate-spin-slow {
  animation: spin 8s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
