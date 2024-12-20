<template>
  <div class="checkbox-wrapper">
    <label class="checkbox-container">
      <input
        type="checkbox"
        :id="id"
        :checked="modelValue"
        :disabled="disabled"
        :required="required"
        class="checkbox-input"
        @change="$emit('update:modelValue', $event.target.checked)"
        @blur="$emit('blur', $event)"
        @focus="$emit('focus', $event)"
      >
      
      <span class="checkbox-custom">
        <i v-if="modelValue" class="fas fa-check check-icon"></i>
      </span>
      
      <span class="checkbox-label">
        <slot>{{ label }}</slot>
        <span v-if="required" class="required">*</span>
      </span>
    </label>
    
    <p v-if="error" class="error-message">{{ error }}</p>
    <p v-if="hint" class="hint-message">{{ hint }}</p>
  </div>
</template>

<script>
export default {
  name: 'BaseCheckbox',
  
  props: {
    modelValue: {
      type: Boolean,
      default: false
    },
    id: {
      type: String,
      required: true
    },
    label: {
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
    }
  },
  
  emits: ['update:modelValue', 'blur', 'focus']
}
</script>

<style scoped>
.checkbox-wrapper {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.checkbox-container {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  user-select: none;
}

.checkbox-container:has(.checkbox-input:disabled) {
  cursor: not-allowed;
  opacity: 0.6;
}

.checkbox-input {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}

.checkbox-custom {
  position: relative;
  height: 20px;
  width: 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
}

.checkbox-input:checked ~ .checkbox-custom {
  background: linear-gradient(135deg, 
    rgba(99, 102, 241, 0.2),
    rgba(0, 255, 204, 0.2)
  );
  border-color: rgba(99, 102, 241, 0.4);
}

.check-icon {
  color: #00ffcc;
  font-size: 0.8rem;
}

.checkbox-label {
  font-size: 0.95rem;
  color: var(--global-text-color);
  display: flex;
  align-items: center;
  gap: 4px;
}

.required {
  color: #ff4757;
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

/* Focus styles */
.checkbox-input:focus ~ .checkbox-custom {
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
  border-color: rgba(99, 102, 241, 0.4);
}

/* Hover styles */
.checkbox-container:hover .checkbox-custom {
  border-color: rgba(255, 255, 255, 0.2);
}

.checkbox-container:hover .checkbox-input:checked ~ .checkbox-custom {
  border-color: rgba(99, 102, 241, 0.6);
}

/* Animation */
.check-icon {
  transform: scale(0);
  transition: transform 0.2s ease;
}

.checkbox-input:checked ~ .checkbox-custom .check-icon {
  transform: scale(1);
}

/* Error state */
.checkbox-wrapper:has(.error-message) .checkbox-custom {
  border-color: rgba(255, 71, 87, 0.4);
}

.checkbox-wrapper:has(.error-message) .checkbox-input:focus ~ .checkbox-custom {
  box-shadow: 0 0 0 3px rgba(255, 71, 87, 0.15);
}
</style> 