<template>
  <!-- The editorial field: a tracked label over a hairline underline, the
       same treatment as the "Start a project" form on the projects page. -->
  <div class="form-group">
    <label class="field">
      <span class="field__label">{{ label }}</span>
      <input
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
        @blur="$emit('blur', $event)"
        @change="$emit('change', $event)"
        :name="name"
        :type="inputType"
        :autocomplete="autocomplete"
        :disabled="disabled"
        :placeholder="placeholder"
        class="field__input disabled:opacity-50 disabled:cursor-not-allowed"
        :class="{ 'field__input--error': hasError }"
        :aria-invalid="hasError ? 'true' : undefined"
      >
    </label>
    <ErrorMessage v-if="showError" :name="name" class="field__error flex items-center gap-2">
      <i class="fas fa-exclamation-circle text-xs"></i>
    </ErrorMessage>
  </div>
</template>

<script setup>
import { ErrorMessage } from 'vee-validate'
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  name: {
    type: String,
    required: true
  },
  label: {
    type: String,
    required: true
  },
  type: {
    type: String,
    default: 'text'
  },
  // Accepted for backwards compatibility; the editorial field has no icon.
  icon: {
    type: String,
    default: ''
  },
  disabled: {
    type: Boolean,
    default: false
  },
  placeholder: {
    type: String,
    default: ''
  },
  autocomplete: {
    type: String,
    default: 'off'
  },
  showError: {
    type: Boolean,
    default: true
  },
  hasError: {
    type: Boolean,
    default: false
  }
})

defineEmits(['update:modelValue', 'blur', 'change'])

const inputType = computed(() => {
  return props.type
})
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
  input {
    transition: none;
  }
}
</style>
