<template>
  <button 
    :type="type"
    :disabled="disabled" 
    :class="[
      'px-6 py-3 rounded-xl transition-all duration-300 transform font-medium',
      variant === 'primary' ? 'bg-gradient-to-r from-primary-600 to-primary-500 hover:from-primary-500 hover:to-primary-400 text-white shadow-lg shadow-primary-500/20 hover:shadow-xl hover:shadow-primary-500/30 hover:scale-[1.02]' : '',
      variant === 'secondary' ? 'bg-white/5 backdrop-blur-sm border border-white/20 text-white hover:bg-white/10 hover:scale-[1.02]' : '',
      variant === 'danger' ? 'bg-gradient-to-r from-red-600 to-red-500 hover:from-red-500 hover:to-red-400 text-white shadow-lg shadow-red-500/20 hover:shadow-xl hover:shadow-red-500/30 hover:scale-[1.02]' : '',
      variant === 'outline' ? 'bg-transparent border border-primary-500 text-primary-400 hover:bg-primary-500/10 hover:scale-[1.02]' : '',
      variant === 'success' ? 'bg-gradient-to-r from-green-600 to-green-500 hover:from-green-500 hover:to-green-400 text-white shadow-lg shadow-green-500/20 hover:shadow-xl hover:shadow-green-500/30 hover:scale-[1.02]' : '',
      disabled ? 'opacity-50 cursor-not-allowed transform-none hover:scale-100' : '',
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
.spinner-sm {
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top: 2px solid #fff;
  width: 16px;
  height: 16px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Gradient animation for buttons */
@keyframes gradient-shift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.bg-gradient-to-r {
  background-size: 200% auto;
  animation: gradient-shift 8s ease infinite;
}
</style> 