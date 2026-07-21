<template>
  <div
    class="crisp-card relative p-8 rounded-2xl border bg-white/85 dark:bg-white/[0.045] backdrop-blur-sm transition-all duration-300 my-8"
    :class="isAlt ? 'border-orange-200/70 dark:border-orange-300/[0.14]' : 'border-blue-200/70 dark:border-blue-300/[0.14]'"
  >
    <div class="flex items-start gap-6">
      <div
        class="flex items-center justify-center w-12 h-12 rounded-xl ring-1 flex-shrink-0 font-display text-2xl font-semibold leading-none transition-all duration-300"
        :class="isAlt ? 'bg-orange-100 dark:bg-orange-400/[0.14] ring-orange-900/[0.08] dark:ring-orange-300/[0.18] text-orange-700 dark:text-orange-200' : 'bg-gradient-to-br from-[#dbeeff] to-[#9ecdf3] dark:from-blue-400/[0.18] dark:to-blue-500/[0.22] ring-blue-900/[0.08] dark:ring-blue-300/[0.18] text-blue-700 dark:text-blue-200'"
      >
        {{ number }}
      </div>
      <div class="flex-1">
        <h3 class="text-2xl font-semibold tracking-tight text-blue-950 dark:text-white mb-4 transition-colors duration-300">
          {{ title }}
        </h3>
        <div class="text-blue-950/70 dark:text-blue-100/70 leading-relaxed transition-colors duration-300">
          <slot></slot>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = withDefaults(defineProps<{
  number: string | number;
  title: string;
}>(), {});

// Alternate the hairline tint and number tile between blue and orange steps
const isAlt = computed(() => Number(props.number) % 2 === 0);
</script>
