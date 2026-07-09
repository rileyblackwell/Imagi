<template>
  <div class="mb-12 md:mb-16 text-center">
    <p class="inline-flex items-center px-3.5 py-1.5 rounded-full border border-blue-200/70 dark:border-blue-400/25 bg-blue-50/80 dark:bg-blue-400/10 text-xs font-semibold text-blue-700 dark:text-blue-300 uppercase tracking-[0.18em] mb-5 transition-colors duration-300">
      {{ badgeText }}
    </p>
    <h1 class="text-4xl sm:text-5xl md:text-6xl font-semibold tracking-[-0.025em] text-blue-950 dark:text-white mb-6 leading-[1.08] text-balance transition-colors duration-300">
      {{ title }}
    </h1>
    <p class="text-xl text-blue-950/70 dark:text-blue-100/70 max-w-3xl mx-auto leading-relaxed text-pretty transition-colors duration-300">
      {{ description }}
    </p>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  title: string;
  description: string;
  badgeText?: string;
}>(), {
  badgeText: 'DOCUMENTATION'
});
</script>
