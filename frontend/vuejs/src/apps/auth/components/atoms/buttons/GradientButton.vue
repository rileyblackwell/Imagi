<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    class="btn-3d btn-accent group relative w-full inline-flex items-center justify-center gap-2 px-8 py-4
           text-blue-950
           rounded-full
           font-medium
           border border-white/60
           focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0a0a0a]
           transition-all duration-300
           disabled:opacity-50 disabled:cursor-not-allowed
           overflow-hidden"
  >
    <!-- Top edge highlight for 3D effect -->
    <span class="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/70 to-transparent"></span>
    <!-- Bottom edge shadow for depth -->
    <span class="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-blue-900/15 to-transparent"></span>
    <!-- Content -->
    <span v-if="loading" class="relative z-10 flex items-center justify-center">
      <i class="fas fa-circle-notch fa-spin mr-2"></i>
      <span class="font-medium">{{ loadingText }}</span>
    </span>
    <span v-else class="relative z-10 flex items-center justify-center gap-2">
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

<style scoped>
/* Soft 3D button effect - tight, layered, crisp. Blue-tinted shadows to suit the light baby-blue fill. */
.btn-3d {
  transform: translateY(0) translateZ(0);
  transition: transform 0.3s ease, box-shadow 0.3s ease, background 0.3s ease;
  box-shadow:
    0 1px 2px rgba(30, 58, 138, 0.14),
    0 4px 10px -2px rgba(30, 58, 138, 0.16),
    0 10px 20px -6px rgba(30, 58, 138, 0.18),
    inset 0 1px 1px 0 rgba(255, 255, 255, 0.75),
    inset 0 -2px 4px -1px rgba(30, 58, 138, 0.12);
}

.btn-3d:active {
  transform: translateY(0) translateZ(0);
  transition-duration: 0.1s;
}

/* Soft baby-blue gradient fill */
.btn-accent {
  background: linear-gradient(155deg, #dbeeff 0%, #b7ddf7 55%, #9ecdf3 100%);
}

.dark .btn-accent {
  background: linear-gradient(155deg, #dbeeff 0%, #b7ddf7 55%, #9ecdf3 100%);
}
</style>
