<template>
  <div class="crisp-card group relative h-full p-8 rounded-2xl border border-blue-200/70 bg-white transition-all duration-300">
    <h3
      v-if="title"
      class="text-xl font-semibold text-blue-950 mb-3 transition-colors duration-300"
    >
      {{ title }}
    </h3>

    <div class="text-blue-950/70 leading-relaxed transition-colors duration-300">
      <slot></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title?: string;
}>();
</script>
