s<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    class="w-full bg-gradient-to-r from-primary-600 via-primary-500 to-primary-400 
           hover:from-primary-500 hover:via-primary-400 hover:to-primary-300 
           text-white font-semibold py-4 px-6 rounded-xl 
           transition-all duration-500 transform hover:-translate-y-0.5 hover:scale-[1.02] 
           flex items-center justify-center text-base disabled:opacity-50 
           disabled:cursor-not-allowed disabled:hover:translate-y-0 disabled:hover:scale-100
           shadow-[0_8px_16px_-6px_rgba(59,130,246,0.3)] 
           hover:shadow-[0_12px_20px_-6px_rgba(59,130,246,0.4)]
           border border-primary-500/20 hover:border-primary-400/40
           backdrop-blur-sm relative overflow-hidden group"
  >
    <div class="absolute inset-0 bg-gradient-to-r from-primary-400/10 to-violet-400/10 
                group-hover:from-primary-400/20 group-hover:to-violet-400/20 
                transition-all duration-500"></div>
    <span v-if="loading" class="flex items-center justify-center relative z-10">
      <i class="fas fa-circle-notch fa-spin mr-2"></i>
      <span class="font-medium">{{ loadingText }}</span>
    </span>
    <span v-else class="flex items-center justify-center space-x-2 relative z-10">
      <span class="font-medium"><slot></slot></span>
      <i class="fas fa-arrow-right transform transition-transform duration-500 
                group-hover:translate-x-1"></i>
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
