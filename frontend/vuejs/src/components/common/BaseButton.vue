<template>
  <button
    :type="type"
    :class="[
      'base-button',
      variant,
      size,
      { block, loading, disabled }
    ]"
    :disabled="disabled || loading"
    @click="$emit('click', $event)"
  >
    <span v-if="loading" class="loading-spinner">
      <LoadingSpinner size="sm" />
    </span>
    <span v-else class="button-content">
      <slot name="left-icon"></slot>
      <slot></slot>
      <slot name="right-icon"></slot>
    </span>
  </button>
</template>

<script setup>
import LoadingSpinner from './LoadingSpinner.vue'

defineProps({
  type: {
    type: String,
    default: 'button'
  },
  variant: {
    type: String,
    default: 'primary'
  },
  size: {
    type: String,
    default: 'md'
  },
  block: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped>
.base-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: var(--font-weight-medium);
  border-radius: var(--border-radius-md);
  transition: all 0.2s;
  cursor: pointer;
  outline: none;
  border: none;
  gap: var(--spacing-sm);
}

.base-button.block {
  width: 100%;
}

.base-button.disabled,
.base-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.base-button.loading {
  cursor: wait;
}

/* Variants */
.base-button.primary {
  background: var(--color-primary);
  color: white;
}

.base-button.primary:hover:not(:disabled) {
  background: var(--color-primary-dark);
}

.base-button.secondary {
  background: var(--color-secondary);
  color: white;
}

.base-button.secondary:hover:not(:disabled) {
  background: var(--color-secondary-dark);
}

.base-button.outline {
  background: transparent;
  border: 2px solid var(--color-primary);
  color: var(--color-primary);
}

.base-button.outline:hover:not(:disabled) {
  background: var(--color-primary);
  color: white;
}

/* Sizes */
.base-button.sm {
  padding: var(--spacing-xs) var(--spacing-sm);
  font-size: var(--font-size-sm);
}

.base-button.md {
  padding: var(--spacing-sm) var(--spacing-md);
  font-size: var(--font-size-base);
}

.base-button.lg {
  padding: var(--spacing-md) var(--spacing-lg);
  font-size: var(--font-size-lg);
}

.loading-spinner {
  display: flex;
  align-items: center;
  justify-content: center;
}

.button-content {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}
</style> 