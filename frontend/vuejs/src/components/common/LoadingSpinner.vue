<template>
  <div
    class="loading-spinner"
    :class="{
      'loading-spinner-sm': size === 'small',
      'loading-spinner-lg': size === 'large',
      'loading-spinner-center': center,
      'loading-spinner-overlay': overlay
    }"
    :style="{ color }"
  >
    <div class="spinner">
      <svg viewBox="0 0 50 50">
        <circle
          class="path"
          cx="25"
          cy="25"
          r="20"
          fill="none"
          stroke="currentColor"
          stroke-width="5"
        ></circle>
      </svg>
    </div>
    <div v-if="text" class="spinner-text">{{ text }}</div>
  </div>
</template>

<script setup>
defineProps({
  size: {
    type: String,
    default: 'medium',
    validator: value => ['small', 'medium', 'large'].includes(value)
  },
  color: {
    type: String,
    default: 'currentColor'
  },
  text: {
    type: String,
    default: ''
  },
  center: {
    type: Boolean,
    default: false
  },
  overlay: {
    type: Boolean,
    default: false
  }
});
</script>

<style scoped>
.loading-spinner {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-2);
}

.loading-spinner-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.loading-spinner-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.9);
  z-index: var(--z-modal);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.spinner {
  animation: rotate 2s linear infinite;
  width: 32px;
  height: 32px;
}

.loading-spinner-sm .spinner {
  width: 24px;
  height: 24px;
}

.loading-spinner-lg .spinner {
  width: 48px;
  height: 48px;
}

.spinner .path {
  stroke-linecap: round;
  animation: dash 1.5s ease-in-out infinite;
}

.spinner-text {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

@keyframes rotate {
  100% {
    transform: rotate(360deg);
  }
}

@keyframes dash {
  0% {
    stroke-dasharray: 1, 150;
    stroke-dashoffset: 0;
  }
  50% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -35;
  }
  100% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -124;
  }
}
</style> 