<template>
  <div class="textarea-wrapper">
    <label v-if="label" :for="id" class="textarea-label">
      {{ label }}
      <span v-if="required" class="required">*</span>
    </label>
    
    <div class="textarea-container" :class="{ 'has-error': error }">
      <textarea
        :id="id"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :required="required"
        :rows="rows"
        :maxlength="maxLength"
        class="base-textarea"
        @input="$emit('update:modelValue', $event.target.value)"
        @blur="$emit('blur', $event)"
        @focus="$emit('focus', $event)"
      ></textarea>
      
      <div v-if="maxLength" class="character-count">
        {{ modelValue.length }}/{{ maxLength }}
      </div>
    </div>
    
    <p v-if="error" class="error-message">{{ error }}</p>
    <p v-if="hint" class="hint-message">{{ hint }}</p>
  </div>
</template>

<script>
export default {
  name: 'BaseTextarea',
  
  props: {
    modelValue: {
      type: String,
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
    placeholder: {
      type: String,
      default: ''
    },
    rows: {
      type: Number,
      default: 4
    },
    maxLength: {
      type: Number,
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
.textarea-wrapper {
  display: flex;
  flex-direction: column;
  gap: 6px;
  width: 100%;
}

.textarea-label {
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

.textarea-container {
  position: relative;
}

.base-textarea {
  width: 100%;
  padding: 12px 14px;
  font-size: 0.95rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: var(--global-text-color);
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  resize: vertical;
  min-height: 100px;
  line-height: 1.5;
}

.base-textarea::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.base-textarea:focus {
  outline: none;
  border-color: rgba(99, 102, 241, 0.4);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
}

.base-textarea:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  resize: none;
}

.textarea-container.has-error .base-textarea {
  border-color: rgba(255, 71, 87, 0.4);
}

.textarea-container.has-error .base-textarea:focus {
  box-shadow: 0 0 0 3px rgba(255, 71, 87, 0.15);
}

.character-count {
  position: absolute;
  bottom: 8px;
  right: 12px;
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.6);
  pointer-events: none;
  background: rgba(30, 30, 30, 0.8);
  padding: 2px 6px;
  border-radius: 6px;
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

/* Hover effect */
.base-textarea:not(:disabled):hover {
  border-color: rgba(255, 255, 255, 0.2);
}

/* Scrollbar styles */
.base-textarea::-webkit-scrollbar {
  width: 8px;
}

.base-textarea::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
}

.base-textarea::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
}

.base-textarea::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}
</style> 