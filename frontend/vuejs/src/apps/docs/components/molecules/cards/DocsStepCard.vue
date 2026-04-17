<template>
  <div class="relative p-8 rounded-2xl border border-gray-200 dark:border-gray-300 bg-white dark:bg-white shadow-md transition-all duration-300 my-8">
    <div class="flex items-start gap-6">
      <div class="text-4xl font-bold text-gray-900 dark:text-black flex-shrink-0 leading-none w-10">
        {{ number }}
      </div>
      <div class="flex-1">
        <h3 class="text-2xl font-semibold text-gray-900 dark:text-black mb-4 transition-colors duration-300">
          {{ title }}
        </h3>
        <div class="text-gray-600 dark:text-black leading-relaxed transition-colors duration-300">
          <slot></slot>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  number: string | number;
  title: string;
}>(), {});
</script>
