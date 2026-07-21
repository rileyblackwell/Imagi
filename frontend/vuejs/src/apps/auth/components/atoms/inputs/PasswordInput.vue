<template>
  <div>
    <label v-if="label" :for="id" class="sr-only">{{ label }}</label>
    <div class="relative group">
      <span class="absolute inset-y-0 left-0 flex items-center pl-4 z-10 pointer-events-none">
        <i class="fas fa-lock text-blue-950/40 dark:text-blue-100/40 transition-colors duration-200"></i>
      </span>
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
        class="w-full py-4 pl-12 pr-12 rounded-xl
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
      <button
        type="button"
        @click="togglePassword"
        :aria-label="isVisible ? 'Hide password' : 'Show password'"
        class="absolute inset-y-2 right-2 flex items-center justify-center w-9 my-auto rounded-lg
               text-blue-950/40 dark:text-blue-100/40
               hover:text-blue-950 dark:hover:text-white
               focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0c0c0e]
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
  input,
  button {
    transition: none;
  }
}
</style>
