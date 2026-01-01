<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    class="group relative w-full inline-flex items-center justify-center gap-2 px-8 py-4 
           bg-gradient-to-r from-violet-600 to-fuchsia-600 rounded-xl text-white font-medium 
           shadow-lg shadow-violet-500/25 hover:shadow-xl hover:shadow-violet-500/30 
           transition-all duration-300 hover:-translate-y-0.5
           disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:translate-y-0 disabled:hover:shadow-lg
           overflow-hidden"
  >
    <!-- Subtle hover glow overlay -->
    <div class="absolute inset-0 bg-gradient-to-r from-violet-500 to-fuchsia-500 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
    
    <!-- Content -->
    <span v-if="loading" class="relative z-10 flex items-center justify-center">
      <i class="fas fa-circle-notch fa-spin mr-2"></i>
      <span class="font-medium">{{ loadingText }}</span>
    </span>
    <span v-else class="relative z-10 flex items-center justify-center gap-2">
      <span class="font-medium"><slot></slot></span>
      <i class="fas fa-arrow-right text-sm transform transition-transform duration-300 group-hover:translate-x-1"></i>
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
