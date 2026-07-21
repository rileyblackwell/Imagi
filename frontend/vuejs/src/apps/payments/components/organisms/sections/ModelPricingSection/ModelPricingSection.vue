<template>
  <div class="relative" :class="animate ? 'animate-fade-in-up animation-delay-450' : ''">
    <!-- Crisp card with hairline blue tint -->
    <div class="model-pricing-card relative p-8 rounded-2xl bg-white/85 dark:bg-white/[0.045] backdrop-blur-sm border border-blue-200/70 dark:border-blue-300/[0.14] transition-all duration-300">

      <div class="relative z-10">
        <!-- Clean section title -->
        <div class="mb-8">
          <h2 class="text-2xl font-semibold tracking-tight text-blue-950 dark:text-white mb-2 transition-colors duration-300">{{ title }}</h2>
          <p class="text-blue-950/65 dark:text-blue-100/65 transition-colors duration-300">Token-based pricing for AI models</p>
        </div>

        <div class="grid grid-cols-1 gap-4">
          <!-- Model price rows with hairline styling -->
          <div
            v-for="model in models"
            :key="model.id"
            class="flex flex-col sm:flex-row sm:items-center sm:justify-between p-5 rounded-2xl bg-white/70 dark:bg-white/[0.03] border border-blue-950/[0.08] dark:border-white/[0.1] transition-all duration-300 gap-4"
          >
            <div class="flex flex-col flex-1">
              <div class="flex items-center gap-3 mb-1">
                <span class="font-semibold tracking-tight text-blue-950 dark:text-white transition-colors duration-300">{{ model.name }}</span>
              </div>
              <p v-if="model.description" class="text-sm text-blue-950/60 dark:text-blue-100/55 transition-colors duration-300">{{ model.description }}</p>
            </div>
            <div class="flex flex-col items-start sm:items-end gap-1.5">
              <div class="flex items-baseline gap-2">
                <span class="text-lg font-semibold tabular-nums text-blue-950 dark:text-white transition-colors duration-300">${{ model.inputPrice }}</span>
                <span class="text-xs text-blue-950/60 dark:text-blue-100/55 transition-colors duration-300">per 1M input tokens</span>
              </div>
              <div class="flex items-baseline gap-2">
                <span class="text-lg font-semibold tabular-nums text-blue-950 dark:text-white transition-colors duration-300">${{ model.outputPrice }}</span>
                <span class="text-xs text-blue-950/60 dark:text-blue-100/55 transition-colors duration-300">per 1M output tokens</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Information note with clean styling -->
        <div class="mt-6 p-4 rounded-2xl bg-blue-50/60 dark:bg-blue-400/[0.06] border border-blue-200/70 dark:border-blue-300/[0.14] transition-colors duration-300">
          <div class="flex items-start gap-3">
            <svg class="w-5 h-5 text-blue-600 dark:text-blue-300 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
            </svg>
            <p class="text-sm text-blue-950/70 dark:text-blue-100/70 leading-relaxed transition-colors duration-300">Pricing is based on tokens processed. Input tokens (prompts) and output tokens (responses) are charged separately per million tokens. Credits are automatically deducted from your account balance.</p>
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
        id: 'gpt-5.6-sol',
        name: 'GPT 5.6 Sol',
        inputPrice: 6,
        outputPrice: 30,
        description: 'OpenAI | GPT 5.6 Sol — flagship model for the most demanding building tasks'
      },
      {
        id: 'gpt-5.6-terra',
        name: 'GPT 5.6 Terra',
        inputPrice: 3,
        outputPrice: 15,
        description: 'OpenAI | GPT 5.6 Terra — balanced model for everyday chat and building assistance'
      },
      {
        id: 'gpt-5.6-luna',
        name: 'GPT 5.6 Luna',
        inputPrice: 1,
        outputPrice: 5,
        description: 'OpenAI | GPT 5.6 Luna — light, fast and economical model for quick tasks'
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

@media (prefers-reduced-motion: reduce) {
  .animate-fade-in-up {
    animation: none;
  }
}

/* Crisp, sharply-defined card: hairline edge + tight layered shadow */
.model-pricing-card {
  box-shadow:
    0 0 0 1px rgba(15, 23, 42, 0.03),
    0 1px 2px rgba(15, 23, 42, 0.06),
    0 4px 10px -2px rgba(15, 23, 42, 0.07),
    0 12px 28px -10px rgba(15, 23, 42, 0.10);
}

.dark .model-pricing-card {
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.04),
    0 1px 2px rgba(0, 0, 0, 0.5),
    0 4px 10px -2px rgba(0, 0, 0, 0.45),
    0 12px 28px -10px rgba(0, 0, 0, 0.55);
}
</style>
