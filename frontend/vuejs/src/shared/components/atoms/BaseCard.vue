<template>
  <div :class="['rounded-lg bg-white/5 shadow p-4', customClass]">
    <slot />
  </div>
</template>

<script setup lang="ts">
const props = defineProps({
  customClass: { type: String, default: '' }
})
</script>
