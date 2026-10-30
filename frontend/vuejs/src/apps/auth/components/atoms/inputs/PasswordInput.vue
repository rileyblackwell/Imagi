<template>
  <div>
    <label v-if="label" :for="id" class="sr-only">{{ label }}</label>
    <div class="relative group">
      <span class="absolute inset-y-0 left-0 flex items-center pl-4 z-10 pointer-events-none">
        <i class="fas fa-lock text-sl-faint transition-colors duration-200"></i>
      </span>
      <!-- The field wears the auth panel's Spotlight colours (its only home):
           one chip-coloured fill, a hairline that deepens on hover and turns
           to the focus colour with a soft amber halo on focus. `!` on the halo
           so it still replaces the autofill inset below. An error is told by
           the message under the field; the panel never tinted the field. -->
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
        class="w-full py-4 pl-12 pr-12 rounded-[14px] appearance-none [&::-moz-focus-inner]:border-0
               font-sl-body text-sl-text placeholder:text-sl-faint
               disabled:opacity-50 disabled:cursor-not-allowed
               transition-colors duration-200 motion-reduce:[transition:none]
               border border-sl-line-strong bg-sl-chip-bg backdrop-blur-sm
               hover:border-[color:color-mix(in_srgb,var(--sl-text)_28%,transparent)]
               focus:outline-none focus:border-sl-focus
               focus:![box-shadow:0_0_0_4px_color-mix(in_srgb,var(--sl-amber)_16%,transparent)]"
      >
      <button
        type="button"
        @click="togglePassword"
        :aria-label="isVisible ? 'Hide password' : 'Show password'"
        class="absolute inset-y-2 right-2 flex items-center justify-center w-9 my-auto rounded-lg
               text-sl-faint hover:text-sl-text
               focus-ring
               transition-colors duration-200 motion-reduce:[transition:none] z-10"
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
/* Stays CSS: autofill is a browser state with its own !important border, and
   the light/dark pair would be unreadable as arbitrary variants.
   Autofill styling for light mode (warm porcelain, ink text) */
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
</style>
