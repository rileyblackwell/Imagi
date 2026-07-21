<template>
  <div :class="['text-center mb-12', animationClass]">
    <h1 class="font-display font-semibold text-4xl lg:text-5xl mb-6 text-center tracking-[-0.02em] leading-[1.05] text-balance">
      <span class="text-blue-950 dark:text-white block transition-colors duration-300">{{ titlePrefix }}</span>
      <em class="header-accent not-italic">{{ highlightedTitle }}</em>
    </h1>
    <div class="w-24 h-px bg-gradient-to-r from-transparent via-blue-950/25 to-transparent dark:via-white/25 mx-auto mb-4" aria-hidden="true"></div>
    <p v-if="subtitle" class="text-lg text-blue-950/65 dark:text-blue-100/65 leading-relaxed text-pretty max-w-2xl mx-auto transition-colors duration-300">
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

@media (prefers-reduced-motion: reduce) {
  .animate-fade-in-up {
    animation: none;
  }
}

/* Italic serif accent with the warm gradient ink */
.header-accent {
  font-style: italic;
  font-variation-settings: 'SOFT' 30, 'WONK' 1;
  background: linear-gradient(115deg, #c2410c 5%, #ea580c 55%, #b45309 95%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent;
  padding-right: 0.06em;
}

.dark .header-accent {
  background: linear-gradient(115deg, #fb923c 5%, #fcd34d 60%, #f59e0b 95%);
  -webkit-background-clip: text;
  background-clip: text;
}
</style> 