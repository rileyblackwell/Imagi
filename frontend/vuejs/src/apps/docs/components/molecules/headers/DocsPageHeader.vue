<template>
  <div class="mb-12 md:mb-16 text-center">
    <p class="text-sm font-medium text-gray-600 dark:text-white/60 uppercase tracking-widest mb-4 transition-colors duration-300">
      {{ badgeText }}
    </p>
    <h1 class="text-4xl sm:text-5xl md:text-6xl font-semibold tracking-tight text-gray-900 dark:text-white mb-6 leading-[1.1] transition-colors duration-300">
      {{ title }}
    </h1>
    <p class="text-xl text-gray-700 dark:text-white/70 max-w-3xl mx-auto leading-relaxed transition-colors duration-300">
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
