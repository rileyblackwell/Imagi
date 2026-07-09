<template>
  <router-link
    :to="to"
    class="crisp-card group relative block h-full p-8 rounded-2xl border border-blue-200/70 dark:border-blue-300/[0.16] bg-white dark:bg-white/[0.05] transition-all duration-300 hover:-translate-y-0.5"
  >
    <div class="flex items-start gap-4">
      <div class="flex-1">
        <h3 class="text-xl font-semibold text-blue-950 dark:text-white mb-2 transition-colors duration-300">
          {{ title }}
        </h3>
        <p class="text-blue-950/70 dark:text-blue-100/70 leading-relaxed transition-colors duration-300">
          {{ description }}
        </p>
      </div>
      <svg
        class="w-5 h-5 text-blue-500 dark:text-blue-300 transition-transform duration-300 group-hover:translate-x-1 flex-shrink-0 mt-1"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
      </svg>
    </div>
  </router-link>
</template>

<script setup lang="ts">
import type { RouteLocationRaw } from 'vue-router';

defineProps<{
  to: RouteLocationRaw;
  title: string;
  description: string;
}>();
</script>
