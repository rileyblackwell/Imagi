<template>
  <div
    class="form-field"
    :class="{
      'form-field-error': error,
      'form-field-success': success,
      'form-field-block': block
    }"
  >
    <label class="switch-label">
      <input
        type="checkbox"
        v-model="switchValue"
        :name="name"
        :disabled="disabled"
        :required="required"
        v-bind="$attrs"
        @change="onChange"
      />
      <span
        class="switch-control"
        :class="{
          'switch-sm': size === 'small',
          'switch-lg': size === 'large'
        }"
      >
        <span class="switch-toggle"></span>
      </span>
      <span v-if="$slots.default" class="switch-text">
        <slot></slot>
      </span>
      <span v-else-if="label" class="switch-text">{{ label }}</span>
    </label>

    <div v-if="error" class="form-message error">
      <i class="fas fa-exclamation-circle"></i>
      {{ error }}
    </div>
    
    <div v-else-if="success" class="form-message success">
      <i class="fas fa-check-circle"></i>
      {{ success }}
    </div>
    
    <div v-else-if="hint" class="form-message hint">
      {{ hint }}
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  name: {
    type: String,
    default: ''
  },
  label: {
    type: String,
    default: ''
  },
  disabled: {
    type: Boolean,
    default: false
  },
  required: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: ''
  },
  success: {
    type: String,
    default: ''
  },
  hint: {
    type: String,
    default: ''
  },
  block: {
    type: Boolean,
    default: false
  },
  size: {
    type: String,
    default: 'medium',
    validator: value => ['small', 'medium', 'large'].includes(value)
  }
});

const emit = defineEmits(['update:modelValue', 'change']);

const switchValue = computed({
  get: () => props.modelValue,
  set: value => emit('update:modelValue', value)
});

function onChange(event) {
  emit('change', event);
}
</script>

<style scoped>
.form-field {
  margin-bottom: var(--spacing-4);
}

.form-field-block {
  width: 100%;
}

.switch-label {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-2);
  cursor: pointer;
  user-select: none;
}

.switch-label input {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.switch-control {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
  border-radius: var(--border-radius-full);
  background-color: var(--bg-tertiary);
  transition: var(--transition-base);
}

.switch-toggle {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  border-radius: var(--border-radius-full);
  background-color: white;
  box-shadow: var(--shadow-sm);
  transition: var(--transition-base);
}

/* Sizes */
.switch-sm {
  width: 36px;
  height: 20px;
}

.switch-sm .switch-toggle {
  width: 16px;
  height: 16px;
}

.switch-lg {
  width: 52px;
  height: 28px;
}

.switch-lg .switch-toggle {
  width: 24px;
  height: 24px;
}

/* Hover state */
.switch-label:hover .switch-control {
  background-color: var(--text-tertiary);
}

/* Checked state */
.switch-label input:checked + .switch-control {
  background-color: var(--primary-color);
}

.switch-label input:checked + .switch-control .switch-toggle {
  transform: translateX(20px);
}

.switch-label input:checked + .switch-sm .switch-toggle {
  transform: translateX(16px);
}

.switch-label input:checked + .switch-lg .switch-toggle {
  transform: translateX(24px);
}

/* Focus state */
.switch-label input:focus + .switch-control {
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

/* Disabled state */
.switch-label input:disabled + .switch-control {
  background-color: var(--bg-secondary);
  cursor: not-allowed;
}

.switch-label input:disabled + .switch-control .switch-toggle {
  background-color: var(--bg-tertiary);
}

.switch-label input:disabled ~ .switch-text {
  color: var(--text-tertiary);
  cursor: not-allowed;
}

.switch-text {
  font-size: var(--font-size-sm);
  color: var(--text-primary);
}

/* Message styles */
.form-message {
  margin-top: var(--spacing-2);
  font-size: var(--font-size-sm);
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.form-message.error {
  color: var(--error-color);
}

.form-message.success {
  color: var(--success-color);
}

.form-message.hint {
  color: var(--text-secondary);
}

/* Error state */
.form-field-error .switch-control {
  background-color: var(--error-color);
}

.form-field-error .switch-label input:focus + .switch-control {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

/* Success state */
.form-field-success .switch-control {
  background-color: var(--success-color);
}

.form-field-success .switch-label input:focus + .switch-control {
  box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.1);
}
</style> 