<template>
  <div class="inline-flex items-center gap-3 px-4 py-2 bg-white/50 dark:bg-white/[0.03] rounded-full border border-gray-200/50 dark:border-white/[0.08] backdrop-blur-sm hover:bg-white dark:hover:bg-white/[0.05] hover:border-gray-300 dark:hover:border-white/[0.12] transition-all duration-300 cursor-default">
    <span class="relative flex h-2 w-2">
      <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-500 dark:bg-emerald-400 opacity-75"></span>
      <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500 dark:bg-emerald-400"></span>
    </span>
    <span class="text-sm font-medium text-gray-600 dark:text-white/70 tracking-wide uppercase transition-colors duration-300">{{ text }}</span>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  text: string;
}>();
</script>
