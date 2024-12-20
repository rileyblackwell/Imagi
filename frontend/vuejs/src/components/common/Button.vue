<template>
  <component
    :is="tag"
    class="btn"
    :class="[
      `btn-${variant}`,
      `btn-${size}`,
      {
        'btn-block': block,
        'btn-loading': loading,
        'btn-icon': icon,
        'btn-disabled': disabled
      }
    ]"
    :disabled="disabled || loading"
    v-bind="$attrs"
  >
    <LoadingSpinner
      v-if="loading"
      size="small"
      :color="spinnerColor"
    />
    <span v-else-if="$slots.default" class="btn-content">
      <i v-if="leftIcon" :class="leftIcon" class="btn-icon-left"></i>
      <slot></slot>
      <i v-if="rightIcon" :class="rightIcon" class="btn-icon-right"></i>
    </span>
    <i v-else :class="icon" class="btn-icon-only"></i>
  </component>
</template>

<script setup>
import { computed } from 'vue';
import LoadingSpinner from './LoadingSpinner.vue';

const props = defineProps({
  variant: {
    type: String,
    default: 'primary',
    validator: value => [
      'primary',
      'secondary',
      'success',
      'warning',
      'error',
      'outline',
      'ghost',
      'link'
    ].includes(value)
  },
  size: {
    type: String,
    default: 'medium',
    validator: value => ['small', 'medium', 'large'].includes(value)
  },
  tag: {
    type: String,
    default: 'button'
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
  },
  icon: {
    type: String,
    default: ''
  },
  leftIcon: {
    type: String,
    default: ''
  },
  rightIcon: {
    type: String,
    default: ''
  }
});

const spinnerColor = computed(() => {
  switch (props.variant) {
    case 'primary':
    case 'success':
    case 'error':
      return 'white';
    default:
      return 'currentColor';
  }
});
</script>

<style scoped>
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
  padding: var(--spacing-2) var(--spacing-4);
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-sm);
  font-weight: 500;
  line-height: 1.5;
  text-decoration: none;
  white-space: nowrap;
  cursor: pointer;
  user-select: none;
  transition: var(--transition-base);
  border: 1px solid transparent;
}

/* Variants */
.btn-primary {
  background-color: var(--primary-color);
  color: white;
}

.btn-primary:hover:not(.btn-disabled) {
  background-color: var(--primary-hover);
}

.btn-secondary {
  background-color: var(--bg-secondary);
  color: var(--text-primary);
}

.btn-secondary:hover:not(.btn-disabled) {
  background-color: var(--bg-tertiary);
}

.btn-success {
  background-color: var(--success-color);
  color: white;
}

.btn-success:hover:not(.btn-disabled) {
  filter: brightness(0.9);
}

.btn-warning {
  background-color: var(--warning-color);
  color: white;
}

.btn-warning:hover:not(.btn-disabled) {
  filter: brightness(0.9);
}

.btn-error {
  background-color: var(--error-color);
  color: white;
}

.btn-error:hover:not(.btn-disabled) {
  filter: brightness(0.9);
}

.btn-outline {
  background-color: transparent;
  border-color: var(--border-color);
  color: var(--text-secondary);
}

.btn-outline:hover:not(.btn-disabled) {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.btn-ghost {
  background-color: transparent;
  color: var(--text-secondary);
}

.btn-ghost:hover:not(.btn-disabled) {
  background-color: var(--bg-secondary);
  color: var(--text-primary);
}

.btn-link {
  background-color: transparent;
  color: var(--primary-color);
  padding: 0;
}

.btn-link:hover:not(.btn-disabled) {
  text-decoration: underline;
}

/* Sizes */
.btn-small {
  padding: var(--spacing-1) var(--spacing-3);
  font-size: var(--font-size-xs);
}

.btn-large {
  padding: var(--spacing-3) var(--spacing-6);
  font-size: var(--font-size-base);
}

/* States */
.btn-block {
  display: flex;
  width: 100%;
}

.btn-loading {
  cursor: wait;
}

.btn-disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Icon buttons */
.btn-icon {
  padding: var(--spacing-2);
  border-radius: var(--border-radius-full);
}

.btn-icon.btn-small {
  padding: var(--spacing-1);
}

.btn-icon.btn-large {
  padding: var(--spacing-3);
}

.btn-icon-left {
  margin-right: var(--spacing-1);
}

.btn-icon-right {
  margin-left: var(--spacing-1);
}

.btn-icon-only {
  margin: 0;
}

/* Focus styles */
.btn:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.4);
}

.btn:focus:not(:focus-visible) {
  box-shadow: none;
}
</style> 