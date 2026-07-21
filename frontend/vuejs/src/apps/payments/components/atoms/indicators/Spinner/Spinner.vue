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
/* Navy-ink spinner: dual-theme, no neon */
.spinner {
  position: relative;
  border-radius: 50%;
  animation: spin 1.2s cubic-bezier(0.65, 0, 0.35, 1) infinite;
}

.spinner-sm {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(23, 37, 84, 0.08);
  border-top: 2px solid #172554;
  border-right: 2px solid rgba(23, 37, 84, 0.25);
}

.spinner-md {
  width: 24px;
  height: 24px;
  border: 3px solid rgba(23, 37, 84, 0.08);
  border-top: 3px solid #172554;
  border-right: 3px solid rgba(23, 37, 84, 0.25);
}

.spinner-lg {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(23, 37, 84, 0.08);
  border-top: 4px solid #172554;
  border-right: 4px solid rgba(23, 37, 84, 0.25);
}

.dark .spinner-sm {
  border: 2px solid rgba(255, 255, 255, 0.08);
  border-top: 2px solid #f3ede2;
  border-right: 2px solid rgba(255, 255, 255, 0.25);
}

.dark .spinner-md {
  border: 3px solid rgba(255, 255, 255, 0.08);
  border-top: 3px solid #f3ede2;
  border-right: 3px solid rgba(255, 255, 255, 0.25);
}

.dark .spinner-lg {
  border: 4px solid rgba(255, 255, 255, 0.08);
  border-top: 4px solid #f3ede2;
  border-right: 4px solid rgba(255, 255, 255, 0.25);
}

.spinner-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 150%;
  height: 150%;
  background: radial-gradient(circle, rgba(158, 205, 243, 0.25) 0%, rgba(158, 205, 243, 0) 70%);
  border-radius: 50%;
  z-index: -1;
  animation: pulse 2s ease-in-out infinite;
}

.dark .spinner-glow {
  background: radial-gradient(circle, rgba(96, 165, 250, 0.15) 0%, rgba(96, 165, 250, 0) 70%);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes pulse {
  0%, 100% { opacity: 0.3; transform: translate(-50%, -50%) scale(0.8); }
  50% { opacity: 0.7; transform: translate(-50%, -50%) scale(1.2); }
}

@media (prefers-reduced-motion: reduce) {
  .spinner-glow {
    animation: none;
  }
}
</style> 