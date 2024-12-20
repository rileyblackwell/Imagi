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
      class="radio-group"
      :class="{
        'radio-group-vertical': vertical,
        'radio-group-horizontal': !vertical
      }"
    >
      <div
        v-for="option in normalizedOptions"
        :key="option.value"
        class="radio-wrapper"
      >
        <label class="radio-label">
          <input
            type="radio"
            :value="option.value"
            v-model="radioValue"
            :name="name"
            :disabled="disabled || option.disabled"
            :required="required"
            v-bind="$attrs"
            @change="onChange"
          />
          <span class="radio-control">
            <span class="radio-dot"></span>
          </span>
          <span class="radio-text">{{ option.label }}</span>
        </label>
      </div>
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
    type: [String, Number, Boolean],
    default: ''
  },
  name: {
    type: String,
    required: true
  },
  label: {
    type: String,
    default: ''
  },
  options: {
    type: Array,
    required: true,
    validator: value => value.every(option => 'value' in option && 'label' in option)
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

const radioValue = computed({
  get: () => props.modelValue,
  set: value => emit('update:modelValue', value)
});

const normalizedOptions = computed(() => {
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

.radio-group {
  display: flex;
  gap: var(--spacing-4);
}

.radio-group-vertical {
  flex-direction: column;
  gap: var(--spacing-2);
}

.radio-group-horizontal {
  flex-direction: row;
  flex-wrap: wrap;
}

.radio-wrapper {
  display: inline-flex;
}

.radio-label {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-2);
  cursor: pointer;
  user-select: none;
}

.radio-label input {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.radio-control {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border: 2px solid var(--border-color);
  border-radius: var(--border-radius-full);
  background-color: var(--bg-primary);
  transition: var(--transition-base);
}

.radio-dot {
  width: 8px;
  height: 8px;
  border-radius: var(--border-radius-full);
  background-color: white;
  opacity: 0;
  transform: scale(0.8);
  transition: var(--transition-base);
}

/* Hover state */
.radio-label:hover .radio-control {
  border-color: var(--primary-color);
}

/* Checked state */
.radio-label input:checked + .radio-control {
  background-color: var(--primary-color);
  border-color: var(--primary-color);
}

.radio-label input:checked + .radio-control .radio-dot {
  opacity: 1;
  transform: scale(1);
}

/* Focus state */
.radio-label input:focus + .radio-control {
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

/* Disabled state */
.radio-label input:disabled + .radio-control {
  background-color: var(--bg-secondary);
  border-color: var(--border-color);
  cursor: not-allowed;
}

.radio-label input:disabled ~ .radio-text {
  color: var(--text-tertiary);
  cursor: not-allowed;
}

.radio-label input:disabled:checked + .radio-control {
  background-color: var(--bg-tertiary);
}

.radio-text {
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
.form-field-error .radio-control {
  border-color: var(--error-color);
}

.form-field-error .radio-label input:checked + .radio-control {
  background-color: var(--error-color);
  border-color: var(--error-color);
}

.form-field-error .radio-label input:focus + .radio-control {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

/* Success state */
.form-field-success .radio-control {
  border-color: var(--success-color);
}

.form-field-success .radio-label input:checked + .radio-control {
  background-color: var(--success-color);
  border-color: var(--success-color);
}

.form-field-success .radio-label input:focus + .radio-control {
  box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.1);
}
</style> 