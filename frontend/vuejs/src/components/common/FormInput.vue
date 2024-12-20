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

    <div class="input-wrapper" :class="{ 'has-icon': leftIcon || rightIcon }">
      <i v-if="leftIcon" :class="leftIcon" class="input-icon input-icon-left"></i>
      
      <template v-if="type === 'textarea'">
        <textarea
          :id="id"
          v-model="inputValue"
          class="form-input"
          :class="{
            'pl-10': leftIcon,
            'pr-10': rightIcon || clearable
          }"
          :name="name"
          :placeholder="placeholder"
          :rows="rows"
          :disabled="disabled"
          :readonly="readonly"
          :required="required"
          v-bind="$attrs"
          @input="onInput"
          @blur="onBlur"
          @focus="onFocus"
        ></textarea>
      </template>
      
      <template v-else>
        <input
          :id="id"
          v-model="inputValue"
          :type="type"
          class="form-input"
          :class="{
            'pl-10': leftIcon,
            'pr-10': rightIcon || clearable || type === 'password'
          }"
          :name="name"
          :placeholder="placeholder"
          :disabled="disabled"
          :readonly="readonly"
          :required="required"
          :min="min"
          :max="max"
          :step="step"
          :pattern="pattern"
          v-bind="$attrs"
          @input="onInput"
          @blur="onBlur"
          @focus="onFocus"
        />
      </template>

      <template v-if="type === 'password'">
        <button
          type="button"
          class="input-icon input-icon-right clickable"
          @click="togglePasswordVisibility"
        >
          <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
        </button>
      </template>
      
      <template v-else>
        <i v-if="rightIcon" :class="rightIcon" class="input-icon input-icon-right"></i>
        
        <button
          v-if="clearable && inputValue"
          type="button"
          class="input-icon input-icon-right clickable"
          @click="clearInput"
        >
          <i class="fas fa-times"></i>
        </button>
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
import { ref, computed } from 'vue';

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: ''
  },
  id: {
    type: String,
    default: () => `input-${Math.random().toString(36).substr(2, 9)}`
  },
  name: {
    type: String,
    default: ''
  },
  label: {
    type: String,
    default: ''
  },
  type: {
    type: String,
    default: 'text',
    validator: value => [
      'text',
      'password',
      'email',
      'number',
      'tel',
      'url',
      'search',
      'date',
      'time',
      'datetime-local',
      'textarea'
    ].includes(value)
  },
  placeholder: {
    type: String,
    default: ''
  },
  disabled: {
    type: Boolean,
    default: false
  },
  readonly: {
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
  leftIcon: {
    type: String,
    default: ''
  },
  rightIcon: {
    type: String,
    default: ''
  },
  clearable: {
    type: Boolean,
    default: false
  },
  block: {
    type: Boolean,
    default: true
  },
  rows: {
    type: Number,
    default: 3
  },
  min: {
    type: [Number, String],
    default: undefined
  },
  max: {
    type: [Number, String],
    default: undefined
  },
  step: {
    type: [Number, String],
    default: undefined
  },
  pattern: {
    type: String,
    default: undefined
  }
});

const emit = defineEmits(['update:modelValue', 'input', 'blur', 'focus', 'clear']);

const showPassword = ref(false);
const inputValue = computed({
  get: () => props.modelValue,
  set: value => emit('update:modelValue', value)
});

function onInput(event) {
  emit('input', event);
}

function onBlur(event) {
  emit('blur', event);
}

function onFocus(event) {
  emit('focus', event);
}

function clearInput() {
  inputValue.value = '';
  emit('clear');
}

function togglePasswordVisibility() {
  showPassword.value = !showPassword.value;
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

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.form-input {
  width: 100%;
  padding: var(--spacing-3);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  background-color: var(--bg-primary);
  color: var(--text-primary);
  font-size: var(--font-size-sm);
  line-height: 1.5;
  transition: var(--transition-base);
}

.form-input:hover {
  border-color: var(--text-tertiary);
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.form-input:disabled,
.form-input:read-only {
  background-color: var(--bg-secondary);
  cursor: not-allowed;
}

.form-input::placeholder {
  color: var(--text-tertiary);
}

/* Icon styles */
.has-icon .form-input {
  padding-left: var(--spacing-10);
}

.has-icon .form-input.pr-10 {
  padding-right: var(--spacing-10);
}

.input-icon {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-tertiary);
  font-size: var(--font-size-base);
  pointer-events: none;
}

.input-icon-left {
  left: var(--spacing-3);
}

.input-icon-right {
  right: var(--spacing-3);
}

.input-icon.clickable {
  pointer-events: auto;
  cursor: pointer;
  padding: var(--spacing-2);
  border: none;
  background: none;
  transition: var(--transition-base);
}

.input-icon.clickable:hover {
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
.form-field-error .form-input {
  border-color: var(--error-color);
}

.form-field-error .form-input:focus {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

/* Success state */
.form-field-success .form-input {
  border-color: var(--success-color);
}

.form-field-success .form-input:focus {
  box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.1);
}

/* Textarea specific styles */
textarea.form-input {
  resize: vertical;
  min-height: 80px;
}
</style> 