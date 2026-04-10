<template>
  <div class="flex flex-col items-center justify-center p-8 text-center">
    <i :class="[icon, 'text-4xl text-gray-500 mb-4']"></i>
    <h3 class="text-lg font-semibold text-white mb-2">{{ title }}</h3>
    <p class="text-gray-400">{{ description }}</p>
    <slot name="action"></slot>
  </div>
</template>

<script setup lang="ts">
defineProps({
  icon: {
    type: String,
    required: true
  },
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    required: true
  }
})
</script>
