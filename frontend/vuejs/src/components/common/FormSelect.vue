<template>
  <div
    class="form-field"
    :class="{
      'form-field-error': error,
      'form-field-success': success,
      'form-field-block': block
    }"
  >
    <label v-if="label" :for="id" class="form-label">
      {{ label }}
      <span v-if="required" class="required-mark">*</span>
    </label>

    <div class="select-wrapper">
      <select
        :id="id"
        v-model="selectValue"
        class="form-select"
        :name="name"
        :disabled="disabled"
        :required="required"
        :multiple="multiple"
        :size="size"
        v-bind="$attrs"
        @change="onChange"
        @blur="onBlur"
        @focus="onFocus"
      >
        <option v-if="placeholder && !multiple" value="" disabled>{{ placeholder }}</option>
        <template v-for="(option, index) in normalizedOptions" :key="option.value">
          <optgroup v-if="option.group" :label="option.group">
            <option
              v-for="item in option.options"
              :key="item.value"
              :value="item.value"
              :disabled="item.disabled"
            >
              {{ item.label }}
            </option>
          </optgroup>
          <option
            v-else
            :value="option.value"
            :disabled="option.disabled"
          >
            {{ option.label }}
          </option>
        </template>
      </select>

      <div class="select-icon">
        <i class="fas fa-chevron-down"></i>
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
    type: [String, Number, Array],
    default: ''
  },
  id: {
    type: String,
    default: () => `select-${Math.random().toString(36).substr(2, 9)}`
  },
  name: {
    type: String,
    default: ''
  },
  label: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: 'Select an option'
  },
  options: {
    type: Array,
    required: true,
    validator: value => {
      return value.every(option => {
        if (option.group) {
          return Array.isArray(option.options) && option.options.every(item => 
            'value' in item && 'label' in item
          );
        }
        return 'value' in option && 'label' in option;
      });
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
  multiple: {
    type: Boolean,
    default: false
  },
  size: {
    type: Number,
    default: undefined
  }
});

const emit = defineEmits(['update:modelValue', 'change', 'blur', 'focus']);

const selectValue = computed({
  get: () => props.modelValue,
  set: value => emit('update:modelValue', value)
});

const normalizedOptions = computed(() => {
  return props.options.map(option => {
    if (option.group) {
      return {
        group: option.group,
        options: option.options.map(item => ({
          value: item.value,
          label: item.label || item.value,
          disabled: item.disabled || false
        }))
      };
    }
    return {
      value: option.value,
      label: option.label || option.value,
      disabled: option.disabled || false
    };
  });
});

function onChange(event) {
  emit('change', event);
}

function onBlur(event) {
  emit('blur', event);
}

function onFocus(event) {
  emit('focus', event);
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

.select-wrapper {
  position: relative;
}

.form-select {
  width: 100%;
  padding: var(--spacing-3);
  padding-right: var(--spacing-10);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  background-color: var(--bg-primary);
  color: var(--text-primary);
  font-size: var(--font-size-sm);
  line-height: 1.5;
  transition: var(--transition-base);
  appearance: none;
  cursor: pointer;
}

.form-select:hover {
  border-color: var(--text-tertiary);
}

.form-select:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.form-select:disabled {
  background-color: var(--bg-secondary);
  cursor: not-allowed;
}

.form-select[multiple] {
  padding-right: var(--spacing-3);
}

.select-icon {
  position: absolute;
  top: 50%;
  right: var(--spacing-3);
  transform: translateY(-50%);
  color: var(--text-tertiary);
  pointer-events: none;
  transition: var(--transition-base);
}

.form-select:focus + .select-icon {
  color: var(--primary-color);
}

/* Option styles */
.form-select option {
  padding: var(--spacing-2) var(--spacing-3);
}

.form-select option:disabled {
  color: var(--text-tertiary);
}

.form-select optgroup {
  color: var(--text-secondary);
  font-weight: 600;
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
.form-field-error .form-select {
  border-color: var(--error-color);
}

.form-field-error .form-select:focus {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

/* Success state */
.form-field-success .form-select {
  border-color: var(--success-color);
}

.form-field-success .form-select:focus {
  box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.1);
}
</style> 