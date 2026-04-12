<template>
  <div 
    class="group flex items-center justify-between backdrop-blur-sm border border-white/10 hover:border-primary-500/30 rounded-xl px-6 py-4 transition-all duration-300 hover:shadow-[0_0_15px_-5px_rgba(59,130,246,0.5)] bg-dark-800/30"
  >
    <!-- Model Name -->
    <div class="font-medium text-white">
      {{ modelName }}
    </div>
    
    <!-- Price -->
    <div class="flex items-center">
      <div class="text-lg font-semibold text-primary-300 mr-2">
        ${{ formattedPrice }}
      </div>
      <span class="text-xs text-white/60">{{ unit }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps({
  modelName: {
    type: String,
    required: true
  },
  price: {
    type: Number,
    required: true
  },
  unit: {
    type: String,
    default: 'per use'
  }
});

const formattedPrice = computed(() => {
  return props.price.toFixed(props.price < 0.01 ? 3 : 2);
});
</script> 