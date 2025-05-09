<template>
  <div class="mb-10">
    <DocsBadge :text="badgeText" class="mb-4" />
    <h1 class="text-4xl md:text-5xl font-bold text-white mb-6 leading-tight">
      {{ title }}
    </h1>
    <p class="text-xl text-gray-300 leading-relaxed">
      {{ description }}
    </p>
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