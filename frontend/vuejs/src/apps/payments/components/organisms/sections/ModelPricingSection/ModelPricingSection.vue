<template>
  <div class="relative" :class="animate ? 'animate-fade-in-up animation-delay-450' : ''">
    <!-- Card with clean design (matching home page) -->
    <div class="relative p-8 rounded-3xl bg-white/80 dark:bg-white/[0.02] backdrop-blur-sm border border-gray-200/80 dark:border-white/[0.08] transition-all duration-300 hover:shadow-xl hover:shadow-gray-200/30 dark:hover:shadow-none">
      
      <div class="relative z-10">
        <!-- Clean section title -->
        <div class="mb-8">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-2 transition-colors duration-300">{{ title }}</h2>
          <p class="text-gray-500 dark:text-white/60 transition-colors duration-300">Token-based pricing for AI models</p>
        </div>
        
        <div class="grid grid-cols-1 gap-4">
          <!-- Model price cards with clean styling -->
          <div 
            v-for="model in models"
            :key="model.id"
            class="flex flex-col sm:flex-row sm:items-center sm:justify-between p-5 rounded-2xl bg-gray-50 dark:bg-white/[0.03] border border-gray-200/50 dark:border-white/[0.06] transition-all duration-300 gap-4"
          >
            <div class="flex flex-col flex-1">
              <div class="flex items-center gap-3 mb-1">
                <span class="font-semibold text-gray-900 dark:text-white transition-colors duration-300">{{ model.name }}</span>
              </div>
              <p v-if="model.description" class="text-sm text-gray-500 dark:text-white/50 transition-colors duration-300">{{ model.description }}</p>
            </div>
            <div class="flex flex-col items-start sm:items-end gap-1.5">
              <div class="flex items-baseline gap-2">
                <span class="text-lg font-semibold text-gray-900 dark:text-white transition-colors duration-300">${{ model.inputPrice }}</span>
                <span class="text-xs text-gray-500 dark:text-white/50 transition-colors duration-300">per 1M input tokens</span>
              </div>
              <div class="flex items-baseline gap-2">
                <span class="text-lg font-semibold text-gray-900 dark:text-white transition-colors duration-300">${{ model.outputPrice }}</span>
                <span class="text-xs text-gray-500 dark:text-white/50 transition-colors duration-300">per 1M output tokens</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Information note with clean styling -->
        <div class="mt-6 p-4 rounded-2xl bg-gray-50 dark:bg-white/[0.03] border border-gray-200/50 dark:border-white/[0.06] transition-colors duration-300">
          <div class="flex items-start gap-3">
            <svg class="w-5 h-5 text-gray-600 dark:text-white/60 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
            </svg>
            <p class="text-sm text-gray-600 dark:text-white/60 leading-relaxed transition-colors duration-300">Pricing is based on tokens processed. Input tokens (prompts) and output tokens (responses) are charged separately per million tokens. Credits are automatically deducted from your account balance.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface PricingModel {
  id: string;
  name: string;
  inputPrice: number;
  outputPrice: number;
  description?: string;
}

const props = defineProps({
  title: {
    type: String,
    default: 'Model Pricing'
  },
  models: {
    type: Array as () => PricingModel[],
    default: () => [
      { 
        id: 'opus-4.5', 
        name: 'Opus 4.5', 
        inputPrice: 10,
        outputPrice: 25,
        description: 'Premium model for the most demanding tasks'
      },
      { 
        id: 'claude-sonnet-4.5-20250514', 
        name: 'Claude Sonnet 4.5', 
        inputPrice: 2,
        outputPrice: 15,
        description: 'Anthropic\'s advanced model for nuanced tasks'
      },
      { 
        id: 'codex-5.2', 
        name: 'Codex 5.2', 
        inputPrice: 2,
        outputPrice: 15,
        description: 'Specialized model for code generation and analysis'
      },
      { 
        id: 'gpt-5.2', 
        name: 'GPT-5.2', 
        inputPrice: 2,
        outputPrice: 15,
        description: 'OpenAI\'s next-generation model for complex tasks'
      },
      {
        id: 'gpt-5.2-nano',
        name: 'GPT-5.2 Nano',
        inputPrice: 1,
        outputPrice: 2,
        description: 'Lightweight GPT-5.2 for fast, low-cost tasks'
      }
    ]
  },
  animate: {
    type: Boolean,
    default: false
  }
});
</script>

<style scoped>
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
  animation: fade-in-up 0.7s ease-out forwards;
}

.animation-delay-450 {
  animation-delay: 450ms;
}
</style>
