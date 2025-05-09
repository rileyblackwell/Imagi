<template>
  <div class="relative group" :class="animate ? 'animate-fade-in-up animation-delay-450' : ''">
    <!-- Enhanced glass morphism effect with glow -->
    <div class="absolute -inset-0.5 rounded-xl opacity-30 group-hover:opacity-70 blur group-hover:blur-md transition-all duration-300 bg-gradient-to-r from-primary-500/50 to-violet-500/50"></div>
    
    <!-- Card with enhanced glass morphism -->
    <div class="relative bg-dark-900/70 backdrop-blur-lg rounded-xl overflow-hidden border border-dark-800/50 group-hover:border-opacity-0 transition-all duration-300">
      <!-- Card header with gradient -->
      <div class="h-2 w-full bg-gradient-to-r from-primary-500 to-violet-500"></div>
      
      <div class="p-6 sm:p-8">
        <h2 class="text-xl font-bold mb-6 bg-gradient-to-r from-primary-400 to-violet-400 bg-clip-text text-transparent">
          {{ title }}
        </h2>
        
        <div class="grid grid-cols-1 gap-4">
          <!-- Model price cards with modern styling -->
          <div 
            v-for="model in models"
            :key="model.id"
            class="flex items-center justify-between p-4 rounded-lg bg-dark-800/50 border border-dark-700/40 backdrop-blur-sm hover:border-primary-500/30 transition-all duration-300"
          >
            <div class="flex flex-col">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-full bg-primary-500/10 border border-primary-500/20 flex items-center justify-center">
                  <i class="fas fa-robot text-primary-400"></i>
                </div>
                <span class="font-medium text-white">{{ model.name }}</span>
              </div>
              <p v-if="model.description" class="text-xs text-gray-400 ml-11 mt-1">{{ model.description }}</p>
            </div>
            <div class="flex items-baseline gap-1">
              <span class="font-semibold text-white">${{ model.price.toFixed(4) }}</span>
              <span class="text-xs text-gray-400">per use</span>
            </div>
          </div>
        </div>
        
        <!-- Information note -->
        <div class="mt-4 p-3 rounded-lg bg-dark-800/40 border border-primary-500/10">
          <div class="flex items-start gap-2">
            <i class="fas fa-info-circle text-primary-400 mt-0.5"></i>
            <p class="text-sm text-gray-300">Model usage is charged per request. Funds are deducted from your account balance automatically.</p>
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
  price: number;
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
        id: 'gpt-4.1', 
        name: 'GPT-4.1', 
        price: 0.04,
        description: 'OpenAI\'s most powerful model for complex tasks'
      },
      { 
        id: 'gpt-4.1-nano', 
        name: 'GPT-4.1 Nano', 
        price: 0.01,
        description: 'Faster, more cost-effective model with high capability'
      },
      { 
        id: 'claude-3-7-sonnet-20250219', 
        name: 'Claude 3.7 Sonnet', 
        price: 0.04,
        description: 'Anthropic\'s advanced model for nuanced tasks'
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