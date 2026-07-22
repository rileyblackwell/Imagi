<template>
  <div class="form-group">
    <label class="relative block group">
      <span class="sr-only">{{ label }}</span>
      <span class="absolute inset-y-0 left-0 flex items-center pl-4 z-10 pointer-events-none">
        <i :class="[icon, 'text-blue-950/40 dark:text-blue-100/40 transition-colors duration-200']"></i>
      </span>
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
        class="w-full py-4 pl-12 pr-4 rounded-xl
               text-blue-950 dark:text-white
               placeholder-blue-950/40 dark:placeholder-blue-100/35
               disabled:opacity-50 disabled:cursor-not-allowed
               transition-all duration-200
               border bg-white/70 dark:bg-white/[0.04] backdrop-blur-sm
               focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0c0c0e]"
        :class="{
          'border-red-500/50 dark:border-red-400/40 bg-red-50 dark:bg-red-500/5': hasError,
          'border-blue-950/[0.12] dark:border-white/[0.14] hover:border-blue-950/25 dark:hover:border-white/25': !hasError
        }"
      >
    </label>
    <ErrorMessage v-if="showError" :name="name" class="mt-2 text-sm text-red-600 dark:text-red-400 flex items-center gap-2">
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
  icon: {
    type: String,
    required: true
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
  -webkit-text-fill-color: #172554;
  -webkit-box-shadow: 0 0 0px 1000px rgba(253, 249, 242, 1) inset;
  transition: background-color 5000s ease-in-out 0s;
  border-color: rgba(23, 37, 84, 0.25) !important;
}

/* Autofill styling for dark mode */
:root.dark input:-webkit-autofill,
:root.dark input:-webkit-autofill:hover,
:root.dark input:-webkit-autofill:focus {
  -webkit-text-fill-color: white;
  -webkit-box-shadow: 0 0 0px 1000px rgba(28, 29, 33, 1) inset;
  transition: background-color 5000s ease-in-out 0s;
  border-color: rgba(255, 255, 255, 0.14) !important;
}

@media (prefers-reduced-motion: reduce) {
  input {
    transition: none;
  }
}
</style>
