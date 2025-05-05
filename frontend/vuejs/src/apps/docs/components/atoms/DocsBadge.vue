<template>
  <div class="inline-block px-4 py-1.5 bg-primary-500/10 rounded-full">
    <span class="text-primary-400 font-semibold text-sm tracking-wider">{{ text }}</span>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  text: string;
}>();
</script> 