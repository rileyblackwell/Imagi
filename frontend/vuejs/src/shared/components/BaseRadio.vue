<template>
  <div class="radio-wrapper">
    <label class="radio-container">
      <input
        type="radio"
        :id="id"
        :name="name"
        :value="value"
        :checked="modelValue === value"
        :disabled="disabled"
        :required="required"
        class="radio-input"
        @change="$emit('update:modelValue', value)"
        @blur="$emit('blur', $event)"
        @focus="$emit('focus', $event)"
      >
      
      <span class="radio-custom">
        <span v-if="modelValue === value" class="radio-dot"></span>
      </span>
      
      <span class="radio-label">
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
  name: 'BaseRadio',
  
  props: {
    modelValue: {
      type: [String, Number, Boolean],
      required: true
    },
    value: {
      type: [String, Number, Boolean],
      required: true
    },
    id: {
      type: String,
      required: true
    },
    name: {
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
.radio-wrapper {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.radio-container {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  user-select: none;
}

.radio-container:has(.radio-input:disabled) {
  cursor: not-allowed;
  opacity: 0.6;
}

.radio-input {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}

.radio-custom {
  position: relative;
  height: 20px;
  width: 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
}

.radio-input:checked ~ .radio-custom {
  background: linear-gradient(135deg, 
    rgba(99, 102, 241, 0.2),
    rgba(0, 255, 204, 0.2)
  );
  border-color: rgba(99, 102, 241, 0.4);
}

.radio-dot {
  width: 8px;
  height: 8px;
  background: #00ffcc;
  border-radius: 50%;
  transform: scale(0);
  transition: transform 0.2s ease;
}

.radio-input:checked ~ .radio-custom .radio-dot {
  transform: scale(1);
}

.radio-label {
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
.radio-input:focus ~ .radio-custom {
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
  border-color: rgba(99, 102, 241, 0.4);
}

/* Hover styles */
.radio-container:hover .radio-custom {
  border-color: rgba(255, 255, 255, 0.2);
}

.radio-container:hover .radio-input:checked ~ .radio-custom {
  border-color: rgba(99, 102, 241, 0.6);
}

/* Error state */
.radio-wrapper:has(.error-message) .radio-custom {
  border-color: rgba(255, 71, 87, 0.4);
}

.radio-wrapper:has(.error-message) .radio-input:focus ~ .radio-custom {
  box-shadow: 0 0 0 3px rgba(255, 71, 87, 0.15);
}
</style> 