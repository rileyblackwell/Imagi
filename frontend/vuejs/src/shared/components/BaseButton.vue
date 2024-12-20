<template>
  <button
    :class="[
      'btn',
      `btn-${variant}`,
      size && `btn-${size}`,
      { 'w-100': block }
    ]"
    :type="type"
    :disabled="disabled || loading"
    @click="$emit('click', $event)"
  >
    <span v-if="loading" class="spinner"></span>
    <i v-if="icon && !loading" :class="icon"></i>
    <slot></slot>
  </button>
</template>

<script>
export default {
  name: 'BaseButton',
  
  props: {
    variant: {
      type: String,
      default: 'primary',
      validator: value => ['primary', 'secondary', 'success', 'danger'].includes(value)
    },
    size: {
      type: String,
      default: null,
      validator: value => ['sm', 'lg'].includes(value)
    },
    type: {
      type: String,
      default: 'button'
    },
    icon: {
      type: String,
      default: null
    },
    disabled: {
      type: Boolean,
      default: false
    },
    loading: {
      type: Boolean,
      default: false
    },
    block: {
      type: Boolean,
      default: false
    }
  },
  
  emits: ['click']
}
</script>

<style scoped>
.btn {
  background: rgba(255, 255, 255, 0.05);
  color: var(--global-text-color) !important;
  padding: 10px 18px;
  border-radius: 12px;
  font-weight: 500;
  font-size: 0.95rem;
  text-decoration: none !important;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  cursor: pointer;
  transition: all 0.3s ease;
  min-height: 40px;
}

.btn i {
  font-size: 1.1rem;
  color: #00ffcc;
  transition: transform 0.3s ease;
}

/* Button Variants */
.btn-primary {
  background: linear-gradient(135deg, 
    rgba(99, 102, 241, 0.1),
    rgba(0, 255, 204, 0.1)
  );
  border-color: rgba(99, 102, 241, 0.2);
}

.btn-secondary {
  background: linear-gradient(135deg, 
    rgba(236, 72, 153, 0.1),
    rgba(0, 255, 204, 0.1)
  );
  border-color: rgba(236, 72, 153, 0.2);
}

.btn-success {
  background: linear-gradient(135deg, 
    rgba(0, 255, 204, 0.1),
    rgba(0, 162, 255, 0.1)
  );
  border-color: rgba(0, 255, 204, 0.2);
}

.btn-danger {
  background: linear-gradient(135deg, 
    rgba(255, 71, 87, 0.1),
    rgba(255, 126, 126, 0.1)
  );
  border-color: rgba(255, 71, 87, 0.2);
}

/* Button Sizes */
.btn-sm {
  padding: 6px 14px;
  font-size: 0.875rem;
  border-radius: 10px;
  min-height: 32px;
}

.btn-lg {
  padding: 12px 24px;
  font-size: 1rem;
  border-radius: 14px;
  min-height: 48px;
}

/* Disabled State */
.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Loading Spinner */
.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Hover effects */
.btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, 
    rgba(99, 102, 241, 0.2),
    rgba(0, 255, 204, 0.15)
  );
  border-color: rgba(99, 102, 241, 0.3);
}

.btn-secondary:hover:not(:disabled) {
  background: linear-gradient(135deg, 
    rgba(236, 72, 153, 0.2),
    rgba(0, 255, 204, 0.15)
  );
  border-color: rgba(236, 72, 153, 0.3);
}

.btn-success:hover:not(:disabled) {
  background: linear-gradient(135deg, 
    rgba(0, 255, 204, 0.2),
    rgba(0, 162, 255, 0.15)
  );
  border-color: rgba(0, 255, 204, 0.3);
}

.btn-danger:hover:not(:disabled) {
  background: linear-gradient(135deg, 
    rgba(255, 71, 87, 0.2),
    rgba(255, 126, 126, 0.15)
  );
  border-color: rgba(255, 71, 87, 0.3);
}

/* Block button */
.w-100 {
  width: 100%;
}
</style> 