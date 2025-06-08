<template>
  <div class="mb-12">
    <DocsBadge :text="badgeText" class="mb-6" />
    <h1 class="text-4xl md:text-5xl font-bold text-white mb-4 leading-tight">
      {{ title }}
    </h1>
    <p class="text-xl text-gray-300 leading-relaxed max-w-3xl">
      {{ description }}
    </p>
    
    <!-- Modern divider -->
    <div class="w-full h-px bg-gradient-to-r from-transparent via-indigo-500/30 to-transparent mt-8"></div>
  </div>
</template>

<script setup lang="ts">
import DocsBadge from '../../atoms/badges/DocsBadge.vue';

withDefaults(defineProps<{
  title: string;
  description: string;
  badgeText?: string;
}>(), {
  badgeText: 'DOCUMENTATION'
});
</script> 