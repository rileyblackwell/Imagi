<template>
  <div class="input-wrapper">
    <label v-if="label" :for="id" class="input-label">
      {{ label }}
      <span v-if="required" class="required">*</span>
    </label>
    
    <div class="input-container" :class="{ 'has-error': error }">
      <i v-if="icon" :class="icon" class="input-icon"></i>
      
      <input
        :id="id"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :required="required"
        :autocomplete="autocomplete"
        class="base-input"
        :class="{ 'has-icon': icon }"
        @input="$emit('update:modelValue', $event.target.value)"
        @blur="$emit('blur', $event)"
        @focus="$emit('focus', $event)"
      >
    </div>
    
    <p v-if="error" class="error-message">{{ error }}</p>
    <p v-if="hint" class="hint-message">{{ hint }}</p>
  </div>
</template>

<script>
export default {
  name: 'BaseInput',
  
  props: {
    modelValue: {
      type: [String, Number],
      default: ''
    },
    id: {
      type: String,
      required: true
    },
    label: {
      type: String,
      default: null
    },
    type: {
      type: String,
      default: 'text'
    },
    placeholder: {
      type: String,
      default: ''
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
    },
    autocomplete: {
      type: String,
      default: 'off'
    }
  },
  
  emits: ['update:modelValue', 'blur', 'focus']
}
</script>

<style scoped>
.input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 6px;
  width: 100%;
}

.input-label {
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

.input-container {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 12px;
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.5);
  pointer-events: none;
}

.base-input {
  width: 100%;
  padding: 10px 14px;
  font-size: 0.95rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: var(--global-text-color);
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.base-input.has-icon {
  padding-left: 40px;
}

.base-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.base-input:focus {
  outline: none;
  border-color: rgba(99, 102, 241, 0.4);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
}

.base-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.input-container.has-error .base-input {
  border-color: rgba(255, 71, 87, 0.4);
}

.input-container.has-error .base-input:focus {
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
</style> 