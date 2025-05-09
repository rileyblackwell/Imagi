<template>
  <div :class="[
    'bg-dark-900/50 border border-dark-800 rounded-xl p-6 my-8',
    colorVariant === 'primary' ? 'bg-primary-500/10 border-primary-500/20' : ''
  ]">
    <slot></slot>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  colorVariant?: 'default' | 'primary';
}>(), {
  colorVariant: 'default'
});
</script> 