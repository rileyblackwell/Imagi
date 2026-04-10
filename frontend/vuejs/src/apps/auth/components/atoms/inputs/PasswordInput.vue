<template>
  <div>
    <label v-if="label" :for="id" class="sr-only">{{ label }}</label>
    <div class="relative group">
      <span class="absolute inset-y-0 left-0 flex items-center pl-4 z-10">
        <i class="fas fa-lock text-black dark:text-white transition-colors duration-200"></i>
      </span>
      <input
        :id="id"
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
        @blur="onBlur"
        @change="onChange"
        :type="inputType"
        :name="name"
        :placeholder="placeholder"
        :required="required"
        :disabled="disabled"
        class="w-full py-4 pl-12 pr-12 rounded-xl 
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
      <button
        type="button"
        @click="togglePassword"
        class="absolute inset-y-0 right-0 flex items-center pr-4 
               text-black dark:text-white 
               hover:text-black/70 dark:hover:text-white/80 
               transition-colors duration-200 z-10"
      >
        <i :class="['fas', isVisible ? 'fa-eye-slash' : 'fa-eye']"></i>
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

const props = defineProps({
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

/* Ensure button doesn't show outline either */
button,
button:focus,
button:active,
button:focus-visible {
  outline: none !important;
  outline-width: 0 !important;
  box-shadow: none !important;
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
