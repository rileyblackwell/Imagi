<template>
  <div 
    :class="[
      'spinner',
      `spinner-${size}`,
      customClass
    ]"
  >
    <div class="spinner-glow"></div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import type { PropType } from 'vue'

export default defineComponent({
  name: 'PaymentSpinner',
  props: {
    size: {
      type: String as PropType<'sm' | 'md' | 'lg'>,
      default: 'md'
    },
    customClass: {
      type: String,
      default: ''
    }
  }
})
</script>

<style scoped>
.spinner {
  position: relative;
  border-radius: 50%;
  border-top-color: #00ffc6;
  animation: spin 1.2s cubic-bezier(0.65, 0, 0.35, 1) infinite;
}

.spinner-sm {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(0, 255, 198, 0.05);
  border-top: 2px solid #00ffc6;
  border-right: 2px solid rgba(0, 255, 198, 0.2);
}

.spinner-md {
  width: 24px;
  height: 24px;
  border: 3px solid rgba(0, 255, 198, 0.05);
  border-top: 3px solid #00ffc6;
  border-right: 3px solid rgba(0, 255, 198, 0.2);
}

.spinner-lg {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(0, 255, 198, 0.05);
  border-top: 4px solid #00ffc6;
  border-right: 4px solid rgba(0, 255, 198, 0.2);
}

.spinner-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 150%;
  height: 150%;
  background: radial-gradient(circle, rgba(0, 255, 198, 0.2) 0%, rgba(0, 255, 198, 0) 70%);
  border-radius: 50%;
  z-index: -1;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes pulse {
  0%, 100% { opacity: 0.3; transform: translate(-50%, -50%) scale(0.8); }
  50% { opacity: 0.7; transform: translate(-50%, -50%) scale(1.2); }
}
</style> 