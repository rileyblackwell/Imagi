<template>
  <div :class="['text-center mb-12', animationClass]">
    <h1 class="text-4xl lg:text-5xl font-bold mb-6 text-center">
      <span class="text-white block">{{ titlePrefix }}</span>
      <span class="bg-gradient-to-r from-primary-400 to-primary-500 bg-clip-text text-transparent">{{ highlightedTitle }}</span>
    </h1>
    <div class="w-24 h-1 bg-gradient-to-r from-primary-500 to-violet-500 rounded-full mx-auto mb-4"></div>
    <p v-if="subtitle" class="text-lg text-white/70 max-w-2xl mx-auto">
      {{ subtitle }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps({
  titlePrefix: {
    type: String,
    default: 'Upgrade Your'
  },
  highlightedTitle: {
    type: String,
    default: 'Imagi Experience'
  },
  subtitle: {
    type: String,
    default: ''
  },
  animate: {
    type: Boolean,
    default: true
  },
  animationDelay: {
    type: Number,
    default: 0
  }
});

const animationClass = computed(() => {
  if (!props.animate) return '';
  
  let classes = 'animate-fade-in-up';
  if (props.animationDelay > 0) {
    classes += ` animation-delay-${props.animationDelay}`;
  }
  
  return classes;
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

.animation-delay-150 {
  animation-delay: 150ms;
}
</style> 