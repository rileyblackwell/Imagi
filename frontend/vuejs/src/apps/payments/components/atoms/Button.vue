<template>
  <button 
    :type="type"
    :disabled="disabled" 
    :class="[
      'px-6 py-3 rounded-lg transition-colors focus:outline-none',
      variant === 'primary' ? 'bg-primary-600 hover:bg-primary-700 text-white' : '',
      variant === 'secondary' ? 'bg-dark-700 hover:bg-dark-600 text-white' : '',
      variant === 'danger' ? 'bg-red-600 hover:bg-red-700 text-white' : '',
      variant === 'outline' ? 'bg-transparent border border-primary-500 text-primary-500 hover:bg-primary-500/10' : '',
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
      type: String as PropType<'primary' | 'secondary' | 'danger' | 'outline'>,
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
</style> 