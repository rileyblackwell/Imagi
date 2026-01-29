<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    class="group relative w-full inline-flex items-center justify-center gap-2 px-8 py-4 
           bg-black dark:bg-white 
           rounded-xl 
           text-white dark:text-gray-900 
           font-medium 
           shadow-sm 
           hover:bg-gray-800 dark:hover:bg-gray-100 
           transition-all duration-200
           disabled:opacity-50 disabled:cursor-not-allowed
           overflow-hidden"
  >
    <!-- Content -->
    <span v-if="loading" class="relative z-10 flex items-center justify-center">
      <i class="fas fa-circle-notch fa-spin mr-2"></i>
      <span class="font-medium">{{ loadingText }}</span>
    </span>
    <span v-else class="relative z-10 flex items-center justify-center gap-2">
      <span class="font-medium"><slot></slot></span>
      <i class="fas fa-arrow-right text-sm"></i>
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
