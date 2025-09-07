<template>
  <div class="group relative transform transition-all duration-300 hover:-translate-y-1" :class="animate ? 'animate-fade-in-up animation-delay-450' : ''">
    <!-- Enhanced glass morphism effect with glow -->
    <div class="absolute -inset-0.5 rounded-2xl opacity-30 group-hover:opacity-70 blur group-hover:blur-md transition-all duration-300 bg-gradient-to-r from-violet-500/50 to-purple-500/50"></div>
    
    <!-- Card with enhanced glass morphism -->
    <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
      <!-- Sleek gradient header -->
      <div class="h-1 w-full bg-gradient-to-r from-violet-400 via-purple-400 to-violet-400 opacity-80"></div>
      
      <!-- Subtle background effects -->
      <div class="absolute -top-32 -left-32 w-64 h-64 bg-gradient-to-br from-violet-400/4 to-purple-400/4 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"></div>
      
      <div class="relative z-10 p-6 sm:p-8">
        <!-- Modern pill badge -->
        <div class="inline-flex items-center px-3 py-1 bg-gradient-to-r from-violet-500/15 to-purple-500/15 border border-violet-400/20 rounded-full mb-6 backdrop-blur-sm">
          <div class="w-1.5 h-1.5 bg-violet-400 rounded-full mr-2 animate-pulse"></div>
          <span class="text-violet-300 font-medium text-xs tracking-wide uppercase">{{ title }}</span>
        </div>
        
        <div class="grid grid-cols-1 gap-4">
          <!-- Model price cards with modern styling -->
          <div 
            v-for="model in models"
            :key="model.id"
            class="flex items-center justify-between p-4 rounded-xl bg-white/5 border border-white/10 backdrop-blur-sm hover:border-violet-500/30 hover:bg-white/10 transition-all duration-300"
          >
            <div class="flex flex-col">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-violet-500/20 to-purple-500/20 border border-violet-500/20 flex items-center justify-center">
                  <i class="fas fa-robot text-violet-400"></i>
                </div>
                <span class="font-medium text-white">{{ model.name }}</span>
              </div>
              <p v-if="model.description" class="text-xs text-gray-400 ml-11 mt-1">{{ model.description }}</p>
            </div>
            <div class="flex items-baseline gap-1">
              <span class="font-semibold text-white">${{ model.price.toFixed(2) }}</span>
              <span class="text-xs text-gray-400">per use</span>
            </div>
          </div>
        </div>
        
        <!-- Information note -->
        <div class="mt-4 p-3 rounded-xl bg-white/5 border border-violet-500/10">
          <div class="flex items-start gap-2">
            <i class="fas fa-info-circle text-violet-400 mt-0.5"></i>
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
        id: 'gpt-5', 
        name: 'GPT-5', 
        price: 0.04,
        description: 'OpenAI\'s next-generation model for complex tasks'
      },
      { 
        id: 'claude-sonnet-4-20250514', 
        name: 'Claude Sonnet 4', 
        price: 0.04,
        description: 'Anthropic\'s advanced model for nuanced tasks'
      },
      {
        id: 'gpt-5-nano',
        name: 'GPT-5 Nano',
        price: 0.01,
        description: 'Lightweight GPT-5 for fast, low-cost tasks'
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