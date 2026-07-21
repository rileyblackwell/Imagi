<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    class="group relative w-full inline-flex items-center justify-center gap-3 px-8 py-4
           rounded-full
           font-medium text-lg
           bg-blue-950 text-[#fdf9f2] hover:bg-blue-900
           dark:bg-[#f3ede2] dark:text-blue-950 dark:hover:bg-white
           shadow-[0_1px_2px_rgba(23,37,84,0.25),0_8px_20px_-6px_rgba(23,37,84,0.35),inset_0_1px_0_rgba(255,255,255,0.12)]
           hover:shadow-[0_2px_3px_rgba(23,37,84,0.22),0_14px_28px_-8px_rgba(23,37,84,0.4),inset_0_1px_0_rgba(255,255,255,0.12)]
           dark:shadow-[0_1px_2px_rgba(0,0,0,0.5),0_10px_24px_-8px_rgba(0,0,0,0.55)]
           dark:hover:shadow-[0_2px_3px_rgba(0,0,0,0.5),0_14px_30px_-8px_rgba(0,0,0,0.6)]
           focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0c0c0e]
           transition-all duration-200 hover:-translate-y-0.5 active:translate-y-0
           disabled:opacity-50 disabled:cursor-not-allowed"
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
