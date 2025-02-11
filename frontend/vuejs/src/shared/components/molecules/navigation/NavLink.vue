<template>
  <router-link
    :to="to"
    class="block text-gray-400 hover:text-white transition-colors duration-200"
  >
    <slot></slot>
  </router-link>
</template>

<script setup lang="ts">
defineProps<{
  to: string | { name: string; params?: Record<string, string | number> }
}>()
</script>
