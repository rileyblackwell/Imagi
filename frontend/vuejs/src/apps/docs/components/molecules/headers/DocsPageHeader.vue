<template>
  <div class="mb-12 md:mb-16">
    <!-- Hero title -->
    <h1 class="text-3xl sm:text-4xl md:text-5xl font-semibold tracking-tight mb-6 leading-[1.15] text-gray-900 dark:text-white transition-colors duration-300">
      {{ title }}
    </h1>
    
    <!-- Description -->
    <p class="text-lg sm:text-xl text-gray-700 dark:text-white/70 leading-relaxed max-w-3xl tracking-wide font-medium transition-colors duration-300">
      {{ description }}
    </p>
    
    <!-- Simple divider -->
    <div class="relative py-6 md:py-8">
      <div class="h-px bg-gray-200 dark:bg-white/10"></div>
    </div>
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

<style scoped>
/* No animations */
</style>
