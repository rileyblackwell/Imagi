<template>
  <router-link
    :to="to"
    class="crisp-card group relative block h-full p-8 rounded-2xl border border-blue-200/70 dark:border-blue-300/[0.14] bg-white/85 dark:bg-white/[0.045] backdrop-blur-sm transition-all duration-300 hover:-translate-y-1 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0c0c0e]"
  >
    <div class="flex items-start gap-4">
      <div class="flex-1">
        <h3 class="text-xl font-semibold tracking-tight text-blue-950 dark:text-white mb-2 transition-colors duration-300">
          {{ title }}
        </h3>
        <p class="text-blue-950/65 dark:text-blue-100/65 leading-relaxed text-pretty transition-colors duration-300">
          {{ description }}
        </p>
      </div>
      <span
        aria-hidden="true"
        class="nav-tile flex items-center justify-center w-10 h-10 rounded-xl ring-1 flex-shrink-0 bg-gradient-to-br from-[#dbeeff] to-[#9ecdf3] dark:from-blue-400/[0.18] dark:to-blue-500/[0.22] ring-blue-900/[0.08] dark:ring-blue-300/[0.18] text-blue-600 dark:text-blue-300 transition-all duration-300"
      >
        <svg
          class="w-4 h-4 transition-transform duration-300 group-hover:translate-x-0.5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
        </svg>
      </span>
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
