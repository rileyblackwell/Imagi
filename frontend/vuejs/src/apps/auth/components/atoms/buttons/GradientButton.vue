<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    class="btn-primary group w-full text-lg"
  >
    <!-- Content -->
    <span v-if="loading" class="flex items-center justify-center">
      <i class="fas fa-circle-notch fa-spin mr-2"></i>
      <span class="font-medium">{{ loadingText }}</span>
    </span>
    <span v-else class="flex items-center justify-center gap-2">
      <span class="font-medium"><slot></slot></span>
      <i class="fas fa-arrow-right text-sm transition-transform duration-300 group-hover:translate-x-1"></i>
    </span>
  </button>
</template>

<script setup>
defineProps({
  type: {
    type: String,
    default: 'button'
  },
  disabled: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  },
  loadingText: {
    type: String,
    default: 'Loading...'
  }
})
</script>
