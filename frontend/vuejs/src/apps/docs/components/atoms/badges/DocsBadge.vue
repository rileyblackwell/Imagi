<template>
  <div class="inline-flex items-center px-4 py-1.5 bg-gradient-to-r from-indigo-500/10 to-violet-500/10 rounded-full border border-indigo-400/20 backdrop-blur-sm">
    <div class="w-1.5 h-1.5 bg-indigo-400 rounded-full mr-2 animate-pulse"></div>
    <span class="text-indigo-300 font-medium text-sm tracking-wide uppercase">{{ text }}</span>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  text: string;
}>();
</script> 