<template>
  <div class="group relative p-8 rounded-2xl border border-gray-200 dark:border-gray-300 bg-white dark:bg-white shadow-md transition-all duration-300">
    <h3
      v-if="title"
      class="text-xl font-semibold text-gray-900 dark:text-black mb-3 transition-colors duration-300"
    >
      {{ title }}
    </h3>

    <div class="text-gray-600 dark:text-black leading-relaxed transition-colors duration-300">
      <slot></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title?: string;
}>();
</script>
