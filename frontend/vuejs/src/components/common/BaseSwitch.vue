<template>
  <div class="switch-wrapper">
    <label class="switch-container">
      <input
        type="checkbox"
        :id="id"
        :checked="modelValue"
        :disabled="disabled"
        :required="required"
        class="switch-input"
        @change="$emit('update:modelValue', $event.target.checked)"
        @blur="$emit('blur', $event)"
        @focus="$emit('focus', $event)"
      >
      
      <span class="switch-track">
        <span class="switch-thumb">
          <i v-if="modelValue" class="fas fa-check switch-icon"></i>
          <i v-else class="fas fa-times switch-icon"></i>
        </span>
      </span>
      
      <span class="switch-label">
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
  name: 'BaseSwitch',
  
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
.switch-wrapper {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.switch-container {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  user-select: none;
}

.switch-container:has(.switch-input:disabled) {
  cursor: not-allowed;
  opacity: 0.6;
}

.switch-input {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}

.switch-track {
  position: relative;
  width: 44px;
  height: 24px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  backdrop-filter: blur(10px);
}

.switch-thumb {
  position: absolute;
  left: 2px;
  width: 20px;
  height: 20px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.switch-input:checked ~ .switch-track {
  background: linear-gradient(135deg, 
    rgba(99, 102, 241, 0.2),
    rgba(0, 255, 204, 0.2)
  );
  border-color: rgba(99, 102, 241, 0.4);
}

.switch-input:checked ~ .switch-track .switch-thumb {
  left: calc(100% - 22px);
  background: #00ffcc;
}

.switch-icon {
  font-size: 0.7rem;
  color: rgba(30, 30, 30, 0.9);
}

.switch-label {
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
.switch-input:focus ~ .switch-track {
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
  border-color: rgba(99, 102, 241, 0.4);
}

/* Hover styles */
.switch-container:hover .switch-track {
  border-color: rgba(255, 255, 255, 0.2);
}

.switch-container:hover .switch-input:checked ~ .switch-track {
  border-color: rgba(99, 102, 241, 0.6);
}

/* Error state */
.switch-wrapper:has(.error-message) .switch-track {
  border-color: rgba(255, 71, 87, 0.4);
}

.switch-wrapper:has(.error-message) .switch-input:focus ~ .switch-track {
  box-shadow: 0 0 0 3px rgba(255, 71, 87, 0.15);
}

/* Animation */
.switch-thumb {
  transform: scale(0.9);
  transition: all 0.3s ease;
}

.switch-input:checked ~ .switch-track .switch-thumb {
  transform: scale(1);
}

/* Gradient border effect */
.switch-track::before {
  content: '';
  position: absolute;
  top: -1px;
  left: -1px;
  right: -1px;
  bottom: -1px;
  border-radius: 12px;
  padding: 1px;
  background: linear-gradient(
    135deg,
    rgba(99, 102, 241, 0.2),
    rgba(0, 255, 204, 0.2)
  );
  -webkit-mask: 
    linear-gradient(#fff 0 0) content-box, 
    linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.switch-input:checked ~ .switch-track::before {
  opacity: 1;
}
</style> 