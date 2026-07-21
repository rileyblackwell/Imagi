<template>
  <div class="mb-12 md:mb-16 text-center">
    <!-- Editorial kicker: tracked small caps flanked by fading hairline rules -->
    <div class="docs-hero-item flex items-center justify-center gap-4 mb-6" style="animation-delay: 0ms">
      <span aria-hidden="true" class="hidden sm:block h-px w-10 md:w-14 bg-gradient-to-l from-blue-950/25 to-transparent dark:from-white/25"></span>
      <span class="flex items-center gap-3">
        <span aria-hidden="true" class="w-1 h-1 rotate-45 bg-orange-500/80 dark:bg-orange-400/80"></span>
        <span class="text-[10px] sm:text-[11px] font-semibold uppercase tracking-[0.25em] leading-none text-blue-950/70 dark:text-blue-100/55 whitespace-nowrap transition-colors duration-300">{{ badgeText }}</span>
        <span aria-hidden="true" class="w-1 h-1 rotate-45 bg-orange-500/80 dark:bg-orange-400/80"></span>
      </span>
      <span aria-hidden="true" class="hidden sm:block h-px w-10 md:w-14 bg-gradient-to-r from-blue-950/25 to-transparent dark:from-white/25"></span>
    </div>

    <h1 class="docs-hero-item font-display font-semibold text-4xl sm:text-5xl md:text-6xl tracking-[-0.02em] text-blue-950 dark:text-white mb-6 leading-[1.05] text-balance transition-colors duration-300" style="animation-delay: 90ms">
      {{ titleLead }} <em class="docs-accent not-italic">{{ titleAccent }}</em>
    </h1>

    <p class="docs-hero-item text-xl text-blue-950/70 dark:text-blue-100/70 max-w-3xl mx-auto leading-relaxed text-pretty transition-colors duration-300" style="animation-delay: 180ms">
      {{ description }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = withDefaults(defineProps<{
  title: string;
  description: string;
  badgeText?: string;
}>(), {
  badgeText: 'DOCUMENTATION'
});

// Split the title so its final word carries the italic gradient accent
const titleLead = computed(() => props.title.split(' ').slice(0, -1).join(' '));
const titleAccent = computed(() => props.title.split(' ').slice(-1)[0]);
</script>

<style scoped>
/* Staggered entrance mirroring the home page's hero rise */
.docs-hero-item {
  animation: docs-hero-rise 0.9s cubic-bezier(0.22, 1, 0.36, 1) both;
}

@keyframes docs-hero-rise {
  from {
    opacity: 0;
    transform: translateY(22px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (prefers-reduced-motion: reduce) {
  .docs-hero-item {
    animation: none;
  }
}

/* Italic serif accent with the warm gradient ink from the home hero */
.docs-accent {
  font-style: italic;
  font-variation-settings: 'SOFT' 30, 'WONK' 1;
  background: linear-gradient(115deg, #c2410c 5%, #ea580c 55%, #b45309 95%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent;
  padding-right: 0.06em;
}

:root.dark .docs-accent {
  background: linear-gradient(115deg, #fb923c 5%, #fcd34d 60%, #f59e0b 95%);
  -webkit-background-clip: text;
  background-clip: text;
}
</style>
