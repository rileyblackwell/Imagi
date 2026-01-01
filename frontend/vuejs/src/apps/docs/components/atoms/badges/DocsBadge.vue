<template>
  <div class="inline-flex items-center gap-3 px-4 py-2 bg-white/[0.03] rounded-full border border-white/[0.08] backdrop-blur-sm hover:bg-white/[0.05] hover:border-white/[0.12] transition-all duration-300 cursor-default">
    <span class="relative flex h-2 w-2">
      <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-violet-400 opacity-75"></span>
      <span class="relative inline-flex rounded-full h-2 w-2 bg-violet-400"></span>
    </span>
    <span class="text-sm font-medium text-white/70 tracking-wide uppercase">{{ text }}</span>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  text: string;
}>();
</script>
