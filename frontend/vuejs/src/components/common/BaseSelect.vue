<template>
  <div class="select-wrapper">
    <label v-if="label" :for="id" class="select-label">
      {{ label }}
      <span v-if="required" class="required">*</span>
    </label>
    
    <div class="select-container" :class="{ 'has-error': error }">
      <i v-if="icon" :class="icon" class="select-icon"></i>
      
      <select
        :id="id"
        :value="modelValue"
        :disabled="disabled"
        :required="required"
        class="base-select"
        :class="{ 'has-icon': icon }"
        @change="$emit('update:modelValue', $event.target.value)"
        @blur="$emit('blur', $event)"
        @focus="$emit('focus', $event)"
      >
        <option v-if="placeholder" value="" disabled selected>{{ placeholder }}</option>
        <option
          v-for="option in options"
          :key="option.value"
          :value="option.value"
          :disabled="option.disabled"
        >
          {{ option.label }}
        </option>
      </select>
      
      <i class="fas fa-chevron-down chevron-icon"></i>
    </div>
    
    <p v-if="error" class="error-message">{{ error }}</p>
    <p v-if="hint" class="hint-message">{{ hint }}</p>
  </div>
</template>

<script>
export default {
  name: 'BaseSelect',
  
  props: {
    modelValue: {
      type: [String, Number],
      default: ''
    },
    id: {
      type: String,
      required: true
    },
    options: {
      type: Array,
      required: true,
      validator: options => options.every(option => 
        'value' in option && 'label' in option
      )
    },
    label: {
      type: String,
      default: null
    },
    placeholder: {
      type: String,
      default: null
    },
    required: {
      type: Boolean,
      default: false
    },
    disabled: {
      type: Boolean,
      default: false
    },
    error: {
      type: String,
      default: null
    },
    hint: {
      type: String,
      default: null
    },
    icon: {
      type: String,
      default: null
    }
  },
  
  emits: ['update:modelValue', 'blur', 'focus']
}
</script>

<style scoped>
.select-wrapper {
  display: flex;
  flex-direction: column;
  gap: 6px;
  width: 100%;
}

.select-label {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--global-text-color);
  display: flex;
  align-items: center;
  gap: 4px;
}

.required {
  color: #ff4757;
}

.select-container {
  position: relative;
  display: flex;
  align-items: center;
}

.select-icon {
  position: absolute;
  left: 12px;
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.5);
  pointer-events: none;
  z-index: 1;
}

.chevron-icon {
  position: absolute;
  right: 12px;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.5);
  pointer-events: none;
  transition: transform 0.2s ease;
}

.base-select {
  width: 100%;
  padding: 10px 14px;
  padding-right: 36px;
  font-size: 0.95rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: var(--global-text-color);
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  appearance: none;
  cursor: pointer;
}

.base-select.has-icon {
  padding-left: 40px;
}

.base-select:focus {
  outline: none;
  border-color: rgba(99, 102, 241, 0.4);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
}

.base-select:focus + .chevron-icon {
  transform: rotate(180deg);
}

.base-select:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.select-container.has-error .base-select {
  border-color: rgba(255, 71, 87, 0.4);
}

.select-container.has-error .base-select:focus {
  box-shadow: 0 0 0 3px rgba(255, 71, 87, 0.15);
}

.error-message {
  font-size: 0.85rem;
  color: #ff4757;
  margin: 0;
}

.hint-message {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
}

/* Option styles */
.base-select option {
  background-color: #1e1e1e;
  color: var(--global-text-color);
  padding: 8px;
}

.base-select option:disabled {
  color: rgba(255, 255, 255, 0.4);
}

/* Hover effect */
.base-select:not(:disabled):hover {
  border-color: rgba(255, 255, 255, 0.2);
}
</style> 