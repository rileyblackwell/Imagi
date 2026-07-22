<template>
  <button
    :type="type"
    :disabled="disabled"
    :class="[
      'inline-flex items-center justify-center px-6 py-3 rounded-full transition-colors duration-200 font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0a0a0a]',
      variant === 'primary' ? 'bg-blue-950 text-[#fdf9f2] hover:bg-blue-900 dark:bg-[#f3ede2] dark:text-blue-950 dark:hover:bg-white shadow-[0_1px_2px_rgba(23,37,84,0.2),0_3px_8px_-2px_rgba(23,37,84,0.25)] dark:shadow-[0_1px_2px_rgba(0,0,0,0.4),0_3px_8px_-2px_rgba(0,0,0,0.45)]' : '',
      variant === 'secondary' ? 'border border-blue-950/[0.14] text-blue-950/80 hover:text-blue-950 hover:border-blue-950/30 hover:bg-blue-950/[0.03] dark:border-white/[0.16] dark:text-blue-100/80 dark:hover:text-white dark:hover:border-white/30 dark:hover:bg-white/[0.06]' : '',
      variant === 'danger' ? 'bg-red-600 text-white hover:bg-red-500 dark:bg-red-500 dark:text-white dark:hover:bg-red-400 shadow-[0_1px_2px_rgba(127,29,29,0.2),0_3px_8px_-2px_rgba(127,29,29,0.25)] dark:shadow-[0_1px_2px_rgba(0,0,0,0.4),0_3px_8px_-2px_rgba(0,0,0,0.45)]' : '',
      variant === 'outline' ? 'bg-transparent border border-blue-950/[0.14] text-blue-950/80 hover:text-blue-950 hover:border-blue-950/30 hover:bg-blue-950/[0.03] dark:border-white/[0.16] dark:text-blue-100/80 dark:hover:text-white dark:hover:border-white/30 dark:hover:bg-white/[0.06]' : '',
      variant === 'success' ? 'bg-emerald-600 text-white hover:bg-emerald-500 dark:bg-emerald-500 dark:text-white dark:hover:bg-emerald-400 shadow-[0_1px_2px_rgba(6,78,59,0.2),0_3px_8px_-2px_rgba(6,78,59,0.25)] dark:shadow-[0_1px_2px_rgba(0,0,0,0.4),0_3px_8px_-2px_rgba(0,0,0,0.45)]' : '',
      disabled ? 'opacity-50 cursor-not-allowed' : '',
      fullWidth ? 'w-full' : '',
      loading ? 'relative' : '',
      customClass
    ]"
    @click="$emit('click', $event)"
  >
    <div v-if="loading" class="absolute inset-0 flex items-center justify-center">
      <div class="spinner-sm"></div>
    </div>
    <div :class="{ 'opacity-0': loading }">
      <slot>Button</slot>
    </div>
  </button>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import type { PropType } from 'vue'

export default defineComponent({
  name: 'PaymentButton',
  props: {
    variant: {
      type: String as PropType<'primary' | 'secondary' | 'danger' | 'outline' | 'success'>,
      default: 'primary'
    },
    type: {
      type: String as PropType<'button' | 'submit' | 'reset'>,
      default: 'button'
    },
    fullWidth: {
      type: Boolean,
      default: false
    },
    disabled: {
      type: Boolean,
      default: false
    },
    loading: {
      type: Boolean,
      default: false
    },
    customClass: {
      type: String,
      default: ''
    }
  },
  emits: ['click']
})
</script>

<style scoped>
/* Spinner inherits the button's ink color so it reads in both themes */
.spinner-sm {
  border: 2px solid rgba(128, 128, 128, 0.25);
  border-radius: 50%;
  border-top: 2px solid currentColor;
  width: 16px;
  height: 16px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style> 