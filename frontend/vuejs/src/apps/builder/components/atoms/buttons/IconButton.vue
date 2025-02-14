<template>
  <button
    :class="[
      'inline-flex items-center justify-center transition-colors',
      variant === 'primary' ? 'text-white hover:text-gray-200' : 'text-gray-400 hover:text-white',
      size === 'sm' ? 'p-1' : 'p-2',
      className
    ]"
    v-bind="$attrs"
  >
    <i :class="['fas', iconClass]"></i>
    <span v-if="text" class="ml-2">{{ text }}</span>
  </button>
</template>

<script setup lang="ts">
defineProps<{
  iconClass: string;
  text?: string;
  variant?: 'primary' | 'default';
  size?: 'sm' | 'md';
  className?: string;
}>();
</script>
