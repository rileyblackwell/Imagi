<template>
  <div class="field">
    <label :for="id" class="field__label">{{ label || 'Password' }}</label>
    <div class="relative">
      <input
        :id="id"
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
        @blur="$emit('blur', $event)"
        @change="$emit('change', $event)"
        :type="inputType"
        :name="name"
        :autocomplete="autocomplete"
        :placeholder="placeholder"
        :required="required"
        :disabled="disabled"
        class="field__input pr-11 disabled:opacity-50 disabled:cursor-not-allowed"
        :class="{ 'field__input--error': hasError }"
        :aria-invalid="hasError ? 'true' : undefined"
      >
      <button
        type="button"
        @click="togglePassword"
        :aria-label="isVisible ? 'Hide password' : 'Show password'"
        class="absolute inset-y-0 right-0 flex items-center justify-center w-9 rounded-md
               text-ink/40 dark:text-bone/40
               hover:text-ink dark:hover:text-bone
               focus-ring
               transition-colors duration-200 z-10"
      >
        <i :class="['fas', isVisible ? 'fa-eye-slash' : 'fa-eye']" class="text-sm"></i>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const isVisible = ref(false)

const togglePassword = () => {
  isVisible.value = !isVisible.value
}

const inputType = computed(() => isVisible.value ? 'text' : 'password')

defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  label: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: ''
  },
  autocomplete: {
    type: String,
    default: 'current-password'
  },
  required: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  },
  id: {
    type: String,
    default: () => `password-input-${Math.random().toString(36).substr(2, 9)}`
  },
  hasError: {
    type: Boolean,
    default: false
  },
  name: {
    type: String,
    default: 'password'
  }
})

defineEmits(['update:modelValue', 'blur', 'change'])
</script>

<style scoped>
/* Remove browser default appearance; the canonical focus-visible ring takes over */
input {
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
}

/* Remove browser default focus ring */
input::-moz-focus-inner {
  border: 0;
}

/* Autofill styling for light mode (warm porcelain, ink text) */
input:-webkit-autofill,
input:-webkit-autofill:hover,
input:-webkit-autofill:focus {
  -webkit-text-fill-color: #131a2c;
  -webkit-box-shadow: 0 0 0px 1000px rgba(255, 255, 255, 1) inset;
  transition: background-color 5000s ease-in-out 0s;
  border-color: rgba(19, 26, 44, 0.25) !important;
}

/* Autofill styling for dark mode */
:root.dark input:-webkit-autofill,
:root.dark input:-webkit-autofill:hover,
:root.dark input:-webkit-autofill:focus {
  -webkit-text-fill-color: #f6f4f0;
  -webkit-box-shadow: 0 0 0px 1000px rgba(18, 18, 20, 1) inset;
  transition: background-color 5000s ease-in-out 0s;
  border-color: rgba(255, 255, 255, 0.14) !important;
}

@media (prefers-reduced-motion: reduce) {
  input,
  button {
    transition: none;
  }
}
</style>
