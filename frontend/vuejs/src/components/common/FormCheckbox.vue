<template>
  <div
    class="form-field"
    :class="{
      'form-field-error': error,
      'form-field-success': success,
      'form-field-block': block
    }"
  >
    <label v-if="label" class="form-label">
      {{ label }}
      <span v-if="required" class="required-mark">*</span>
    </label>

    <div
      class="checkbox-group"
      :class="{
        'checkbox-group-vertical': vertical,
        'checkbox-group-horizontal': !vertical
      }"
    >
      <template v-if="options">
        <div
          v-for="option in normalizedOptions"
          :key="option.value"
          class="checkbox-wrapper"
        >
          <label class="checkbox-label">
            <input
              type="checkbox"
              :value="option.value"
              v-model="checkboxValue"
              :name="name"
              :disabled="disabled || option.disabled"
              :required="required"
              v-bind="$attrs"
              @change="onChange"
            />
            <span class="checkbox-control">
              <i class="fas fa-check checkbox-icon"></i>
            </span>
            <span class="checkbox-text">{{ option.label }}</span>
          </label>
        </div>
      </template>
      <template v-else>
        <label class="checkbox-label">
          <input
            type="checkbox"
            v-model="checkboxValue"
            :name="name"
            :disabled="disabled"
            :required="required"
            v-bind="$attrs"
            @change="onChange"
          />
          <span class="checkbox-control">
            <i class="fas fa-check checkbox-icon"></i>
          </span>
          <span class="checkbox-text">
            <slot></slot>
          </span>
        </label>
      </template>
    </div>

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
    type: [Boolean, Array],
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
  options: {
    type: Array,
    default: null,
    validator: value => {
      if (!value) return true;
      return value.every(option => 'value' in option && 'label' in option);
    }
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
    default: true
  },
  vertical: {
    type: Boolean,
    default: true
  }
});

const emit = defineEmits(['update:modelValue', 'change']);

const checkboxValue = computed({
  get: () => props.modelValue,
  set: value => emit('update:modelValue', value)
});

const normalizedOptions = computed(() => {
  if (!props.options) return null;
  return props.options.map(option => ({
    value: option.value,
    label: option.label || option.value,
    disabled: option.disabled || false
  }));
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

.form-label {
  display: block;
  margin-bottom: var(--spacing-2);
  color: var(--text-primary);
  font-size: var(--font-size-sm);
  font-weight: 500;
}

.required-mark {
  color: var(--error-color);
  margin-left: var(--spacing-1);
}

.checkbox-group {
  display: flex;
  gap: var(--spacing-4);
}

.checkbox-group-vertical {
  flex-direction: column;
  gap: var(--spacing-2);
}

.checkbox-group-horizontal {
  flex-direction: row;
  flex-wrap: wrap;
}

.checkbox-wrapper {
  display: inline-flex;
}

.checkbox-label {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-2);
  cursor: pointer;
  user-select: none;
}

.checkbox-label input {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.checkbox-control {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border: 2px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  background-color: var(--bg-primary);
  transition: var(--transition-base);
}

.checkbox-icon {
  font-size: 12px;
  color: white;
  opacity: 0;
  transform: scale(0.8);
  transition: var(--transition-base);
}

/* Hover state */
.checkbox-label:hover .checkbox-control {
  border-color: var(--primary-color);
}

/* Checked state */
.checkbox-label input:checked + .checkbox-control {
  background-color: var(--primary-color);
  border-color: var(--primary-color);
}

.checkbox-label input:checked + .checkbox-control .checkbox-icon {
  opacity: 1;
  transform: scale(1);
}

/* Focus state */
.checkbox-label input:focus + .checkbox-control {
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

/* Disabled state */
.checkbox-label input:disabled + .checkbox-control {
  background-color: var(--bg-secondary);
  border-color: var(--border-color);
  cursor: not-allowed;
}

.checkbox-label input:disabled ~ .checkbox-text {
  color: var(--text-tertiary);
  cursor: not-allowed;
}

.checkbox-label input:disabled:checked + .checkbox-control {
  background-color: var(--bg-tertiary);
}

.checkbox-text {
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
.form-field-error .checkbox-control {
  border-color: var(--error-color);
}

.form-field-error .checkbox-label input:checked + .checkbox-control {
  background-color: var(--error-color);
  border-color: var(--error-color);
}

.form-field-error .checkbox-label input:focus + .checkbox-control {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

/* Success state */
.form-field-success .checkbox-control {
  border-color: var(--success-color);
}

.form-field-success .checkbox-label input:checked + .checkbox-control {
  background-color: var(--success-color);
  border-color: var(--success-color);
}

.form-field-success .checkbox-label input:focus + .checkbox-control {
  box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.1);
}
</style> 