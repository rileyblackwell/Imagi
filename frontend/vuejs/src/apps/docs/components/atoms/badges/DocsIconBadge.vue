<template>
  <div 
    :class="[
      'flex-shrink-0 rounded-full flex items-center justify-center',
      size === 'sm' ? 'w-5 h-5 mr-2 mt-0.5' : size === 'md' ? 'w-6 h-6 mr-3 mt-0.5' : 'w-8 h-8 mr-3'
    ]"
    :style="{
      backgroundColor: `rgba(var(--${color}-rgb), 0.2)`
    }"
  >
    <i :class="[icon, `text-${color}-400`, size === 'sm' ? 'text-xs' : 'text-sm']"></i>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  icon: string;
  color?: string;
  size?: 'sm' | 'md' | 'lg';
}>();
</script>

<style scoped>
:root {
  --primary-rgb: 59, 130, 246;
  --violet-rgb: 139, 92, 246;
  --blue-rgb: 59, 130, 246;
  --green-rgb: 34, 197, 94;
  --purple-rgb: 168, 85, 247;
}
</style> 