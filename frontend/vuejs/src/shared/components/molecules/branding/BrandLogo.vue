<template>
  <router-link to="/" class="flex items-center space-x-2">
    <div class="h-8 w-8 rounded bg-gradient-to-br from-primary-400 to-violet-400 flex items-center justify-center">
      <span class="text-lg font-bold text-dark-900">I</span>
    </div>
    <span class="text-xl font-bold bg-gradient-to-r from-primary-400 to-violet-400 text-transparent bg-clip-text">
      <slot>Imagi</slot>
    </span>
  </router-link>
</template>

<script setup lang="ts">
// Component is purely presentational, no props or logic needed
</script>
