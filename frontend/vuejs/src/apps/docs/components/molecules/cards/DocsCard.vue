<template>
  <div class="crisp-card group relative h-full p-8 rounded-2xl border border-blue-200/70 dark:border-blue-300/[0.14] bg-white/85 dark:bg-white/[0.045] backdrop-blur-sm transition-all duration-300">
    <h3
      v-if="title"
      class="text-xl font-semibold tracking-tight text-blue-950 dark:text-white mb-3 transition-colors duration-300"
    >
      {{ title }}
    </h3>

    <div class="text-blue-950/65 dark:text-blue-100/65 leading-relaxed text-pretty transition-colors duration-300">
      <slot></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title?: string;
}>();
</script>
