<template>
  <div class="crisp-card relative p-8 rounded-2xl border border-blue-200/70 bg-white transition-all duration-300 my-8">
    <div class="flex items-start gap-6">
      <div class="text-4xl font-bold text-blue-600 flex-shrink-0 leading-none w-10">
        {{ number }}
      </div>
      <div class="flex-1">
        <h3 class="text-2xl font-semibold text-blue-950 mb-4 transition-colors duration-300">
          {{ title }}
        </h3>
        <div class="text-blue-950/70 leading-relaxed transition-colors duration-300">
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
