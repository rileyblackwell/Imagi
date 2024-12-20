<template>
  <div 
    class="spinner"
    :class="[
      size,
      variant,
      { 'with-overlay': overlay }
    ]"
    :style="{
      '--spinner-size': customSize,
      '--spinner-color': color
    }"
  >
    <div v-if="overlay" class="spinner-overlay">
      <div class="spinner-content">
        <div class="spinner-circle"></div>
        <span v-if="text" class="spinner-text">{{ text }}</span>
      </div>
    </div>
    <div v-else class="spinner-circle"></div>
  </div>
</template>

<script>
export default {
  name: 'BaseSpinner',
  
  props: {
    size: {
      type: String,
      default: 'md',
      validator: value => ['sm', 'md', 'lg', 'xl'].includes(value)
    },
    customSize: {
      type: String,
      default: null
    },
    variant: {
      type: String,
      default: 'primary',
      validator: value => [
        'primary',
        'secondary',
        'success',
        'warning',
        'error',
        'info'
      ].includes(value)
    },
    color: {
      type: String,
      default: null
    },
    overlay: {
      type: Boolean,
      default: false
    },
    text: {
      type: String,
      default: null
    }
  }
}
</script>

<style scoped>
.spinner {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

/* Sizes */
.spinner.sm {
  --spinner-size: 20px;
}

.spinner.md {
  --spinner-size: 32px;
}

.spinner.lg {
  --spinner-size: 48px;
}

.spinner.xl {
  --spinner-size: 64px;
}

/* Spinner circle */
.spinner-circle {
  width: var(--spinner-size);
  height: var(--spinner-size);
  border-radius: 50%;
  border: calc(var(--spinner-size) * 0.1) solid transparent;
  animation: spin 1s linear infinite;
}

/* Variants */
.spinner.primary .spinner-circle {
  border-top-color: #6366f1;
  border-right-color: rgba(99, 102, 241, 0.2);
  border-bottom-color: rgba(99, 102, 241, 0.2);
  border-left-color: rgba(99, 102, 241, 0.2);
}

.spinner.secondary .spinner-circle {
  border-top-color: #ec4899;
  border-right-color: rgba(236, 72, 153, 0.2);
  border-bottom-color: rgba(236, 72, 153, 0.2);
  border-left-color: rgba(236, 72, 153, 0.2);
}

.spinner.success .spinner-circle {
  border-top-color: #00ffcc;
  border-right-color: rgba(0, 255, 204, 0.2);
  border-bottom-color: rgba(0, 255, 204, 0.2);
  border-left-color: rgba(0, 255, 204, 0.2);
}

.spinner.warning .spinner-circle {
  border-top-color: #ffab40;
  border-right-color: rgba(255, 171, 64, 0.2);
  border-bottom-color: rgba(255, 171, 64, 0.2);
  border-left-color: rgba(255, 171, 64, 0.2);
}

.spinner.error .spinner-circle {
  border-top-color: #ff4757;
  border-right-color: rgba(255, 71, 87, 0.2);
  border-bottom-color: rgba(255, 71, 87, 0.2);
  border-left-color: rgba(255, 71, 87, 0.2);
}

.spinner.info .spinner-circle {
  border-top-color: #00a2ff;
  border-right-color: rgba(0, 162, 255, 0.2);
  border-bottom-color: rgba(0, 162, 255, 0.2);
  border-left-color: rgba(0, 162, 255, 0.2);
}

/* Custom color */
.spinner .spinner-circle {
  border-top-color: var(--spinner-color, currentColor);
  border-right-color: var(--spinner-color, currentColor);
  border-bottom-color: var(--spinner-color, currentColor);
  border-left-color: var(--spinner-color, currentColor);
  opacity: 0.2;
}

.spinner .spinner-circle {
  border-top-color: var(--spinner-color, currentColor);
  opacity: 1;
}

/* Overlay */
.spinner-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.spinner-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.spinner-text {
  color: white;
  font-size: 1rem;
  font-weight: 500;
}

/* Animation */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Gradient effect */
.spinner-circle::before {
  content: '';
  position: absolute;
  top: -1px;
  left: -1px;
  right: -1px;
  bottom: -1px;
  border-radius: 50%;
  padding: 1px;
  background: linear-gradient(
    135deg,
    var(--spinner-color, currentColor) 0%,
    transparent 50%
  );
  -webkit-mask: 
    linear-gradient(#fff 0 0) content-box, 
    linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  opacity: 0.5;
  animation: spin 1s linear infinite;
}
</style> 