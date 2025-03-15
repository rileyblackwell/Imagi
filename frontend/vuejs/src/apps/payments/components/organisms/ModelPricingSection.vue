<template>
  <PaymentCard contentClass="p-8" :class="animate ? 'animate-fade-in-up animation-delay-450' : ''">
    <h2 class="text-2xl font-semibold mb-6 bg-gradient-to-r from-primary-300 to-primary-500 bg-clip-text text-transparent">
      {{ title }}
    </h2>
    
    <div class="grid grid-cols-1 gap-4">
      <ModelPriceCard
        v-for="model in models"
        :key="model.id"
        :model-name="model.name"
        :price="model.price"
        :unit="'per use'"
      />
    </div>
  </PaymentCard>
</template>

<script setup lang="ts">
import PaymentCard from '../atoms/Card.vue';
import ModelPriceCard from '../molecules/ModelPriceCard.vue';

interface PricingModel {
  id: string;
  name: string;
  price: number;
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
        id: 'claude-sonnet', 
        name: 'Claude-Sonnet', 
        price: 0.04
      },
      { 
        id: 'gpt4o', 
        name: 'GPT-4o', 
        price: 0.04
      },
      { 
        id: 'gpt4o-mini', 
        name: 'GPT-4o-mini', 
        price: 0.005
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
/* Animation delays */
.animation-delay-450 {
  animation-delay: 450ms;
}

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
</style> 