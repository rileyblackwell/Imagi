<template>
  <div
    class="model-price-card group flex items-center justify-between backdrop-blur-sm bg-white/85 dark:bg-white/[0.045] border border-blue-200/70 dark:border-blue-300/[0.14] hover:border-blue-300/80 dark:hover:border-blue-300/[0.24] rounded-2xl px-6 py-4 transition-all duration-300"
  >
    <!-- Model Name -->
    <div class="font-medium tracking-tight text-blue-950 dark:text-white transition-colors duration-300">
      {{ modelName }}
    </div>

    <!-- Price -->
    <div class="flex items-center">
      <div class="text-lg font-semibold tabular-nums text-blue-700 dark:text-blue-300 mr-2 transition-colors duration-300">
        ${{ formattedPrice }}
      </div>
      <span class="text-xs text-blue-950/60 dark:text-blue-100/55 transition-colors duration-300">{{ unit }}</span>
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

<style scoped>
/* Crisp hairline row with a whisper of depth */
.model-price-card {
  box-shadow:
    0 1px 2px rgba(15, 23, 42, 0.05),
    0 2px 6px -2px rgba(15, 23, 42, 0.06);
}

.dark .model-price-card {
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.4),
    0 2px 6px -2px rgba(0, 0, 0, 0.35);
}
</style> 