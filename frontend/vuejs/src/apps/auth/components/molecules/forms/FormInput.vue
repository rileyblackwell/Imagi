<template>
  <div class="form-group">
    <label class="relative block group">
      <span class="sr-only">{{ label }}</span>
      <span class="absolute inset-y-0 left-0 flex items-center pl-4 z-10 pointer-events-none">
        <i :class="[icon, 'text-sl-faint transition-colors duration-200']"></i>
      </span>
      <!-- The field wears the auth panel's Spotlight colours (its only home):
           one chip-coloured fill, a hairline that deepens on hover and turns
           to the focus colour with a soft amber halo on focus. `!` on the halo
           so it still replaces the autofill inset below. An error is told by
           the message under the field; the panel never tinted the field. -->
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
        class="w-full py-4 pl-12 pr-4 rounded-[14px] appearance-none [&::-moz-focus-inner]:border-0
               font-sl-body text-sl-text placeholder:text-sl-faint
               disabled:opacity-50 disabled:cursor-not-allowed
               transition-colors duration-200 motion-reduce:[transition:none]
               border border-sl-line-strong bg-sl-chip-bg backdrop-blur-sm
               hover:border-[color:color-mix(in_srgb,var(--sl-text)_28%,transparent)]
               focus:outline-none focus:border-sl-focus
               focus:![box-shadow:0_0_0_4px_color-mix(in_srgb,var(--sl-amber)_16%,transparent)]"
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
