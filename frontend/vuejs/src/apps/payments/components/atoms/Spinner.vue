<template>
  <div 
    :class="[
      'spinner',
      `spinner-${size}`,
      customClass
    ]"
  ></div>
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
  border-radius: 50%;
  border-top-color: #00ffc6;
  animation: spin 1s linear infinite;
}

.spinner-sm {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(0, 255, 198, 0.1);
  border-top: 2px solid #00ffc6;
}

.spinner-md {
  width: 24px;
  height: 24px;
  border: 3px solid rgba(0, 255, 198, 0.1);
  border-top: 3px solid #00ffc6;
}

.spinner-lg {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(0, 255, 198, 0.1);
  border-top: 4px solid #00ffc6;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style> 