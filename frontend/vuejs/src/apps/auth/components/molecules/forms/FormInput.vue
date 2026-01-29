<template>
  <div class="form-group">
    <label class="relative block group">
      <span class="sr-only">{{ label }}</span>
      <span class="absolute inset-y-0 left-0 flex items-center pl-4 z-10">
        <i :class="[icon, 'text-black dark:text-white transition-colors duration-200']"></i>
      </span>
      <input
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
        @blur="onBlur"
        @change="onChange"
        :name="name"
        :type="inputType"
        :disabled="disabled"
        :placeholder="placeholder"
        class="w-full py-4 pl-12 pr-4 rounded-xl 
               text-black dark:text-white 
               placeholder-gray-400 dark:placeholder-white/30 
               outline-none focus:outline-none
               disabled:opacity-50 disabled:cursor-not-allowed 
               transition-all duration-200
               border bg-gray-50 dark:bg-white/[0.03] backdrop-blur-sm
               focus:ring-0"
        :class="{ 
          'border-red-500/50 bg-red-50 dark:bg-red-500/5': hasError, 
          'border-gray-200 dark:border-white/[0.08]': !hasError
        }"
      >
    </label>
    <ErrorMessage v-if="showError" :name="name" class="mt-2 text-sm text-red-400 flex items-center gap-2">
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
  showError: {
    type: Boolean,
    default: true
  },
  hasError: {
    type: Boolean,
    default: false
  },
  // Vee-validate field props
  onBlur: {
    type: Function,
    default: () => {}
  },
  onChange: {
    type: Function,
    default: () => {}
  }
})

defineEmits(['update:modelValue'])

const inputType = computed(() => {
  return props.type
})
</script>

<style scoped>
/* Completely remove all focus styles and outlines */
input,
input:focus,
input:active,
input:focus-within,
input:focus-visible {
  outline: none !important;
  outline-width: 0 !important;
  outline-style: none !important;
  outline-color: transparent !important;
  box-shadow: none !important;
  -webkit-appearance: none !important;
  -moz-appearance: none !important;
  appearance: none !important;
}

/* Remove any ring effects */
input {
  --tw-ring-shadow: 0 0 #0000 !important;
  --tw-ring-offset-shadow: 0 0 #0000 !important;
  --tw-ring-color: transparent !important;
  --tw-ring-offset-color: transparent !important;
}

/* Remove browser default focus ring */
input::-moz-focus-inner {
  border: 0 !important;
}

/* Autofill styling for light mode */
input:-webkit-autofill,
input:-webkit-autofill:hover,
input:-webkit-autofill:focus {
  -webkit-text-fill-color: black;
  -webkit-box-shadow: 0 0 0px 1000px rgba(249, 250, 251, 1) inset;
  transition: background-color 5000s ease-in-out 0s;
  border-color: rgb(229, 231, 235) !important;
}

/* Autofill styling for dark mode */
:root.dark input:-webkit-autofill,
:root.dark input:-webkit-autofill:hover,
:root.dark input:-webkit-autofill:focus {
  -webkit-text-fill-color: white;
  -webkit-box-shadow: 0 0 0px 1000px rgba(255, 255, 255, 0.03) inset;
  transition: background-color 5000s ease-in-out 0s;
  border-color: rgba(255, 255, 255, 0.08) !important;
}
</style>
