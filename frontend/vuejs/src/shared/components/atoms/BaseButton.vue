<template>
  <button :class="['px-4 py-2 rounded transition font-medium', colorClass, customClass]">
    <slot />
  </button>
</template>

<script setup lang="ts">
const props = defineProps({
  color: { type: String, default: 'emerald' },
  customClass: { type: String, default: '' }
})

const colorClass = `bg-${props.color}-500 text-white hover:bg-${props.color}-600`
</script>
