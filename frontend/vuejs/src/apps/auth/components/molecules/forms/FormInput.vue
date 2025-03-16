<template>
  <div class="form-group">
    <label class="relative block group">
      <span class="sr-only">{{ label }}</span>
      <span class="absolute inset-y-0 left-0 flex items-center pl-4">
        <i :class="[icon, 'text-gray-400 group-hover:text-primary-400 transition-colors']"></i>
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
        class="w-full py-3.5 pl-11 pr-4 bg-dark-800 border rounded-xl 
               text-white placeholder-gray-500 outline-none focus:outline-none
               disabled:opacity-50 disabled:cursor-not-allowed 
               transition-colors duration-300"
        :class="{ 
          'border-red-500 ring-1 ring-red-500': hasError, 
          'border-dark-700 focus:border-primary-400 focus:ring-1 focus:ring-primary-400': !hasError,
          'hover:border-dark-600': !hasError && !disabled
        }"
      >
    </label>
    <ErrorMessage v-if="showError" :name="name" class="mt-2 text-sm text-red-400" />
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
/* Custom focus styles */
input:focus {
  outline: none !important;
  box-shadow: none !important;
}

/* Override browser-specific focus styles */
input:focus-visible {
  outline: none !important;
}
</style>
