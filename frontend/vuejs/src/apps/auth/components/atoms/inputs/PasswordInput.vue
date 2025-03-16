<template>
  <div>
    <label v-if="label" :for="id" class="sr-only">{{ label }}</label>
    <div class="relative group">
      <span class="absolute inset-y-0 left-0 flex items-center pl-4">
        <i class="fas fa-lock text-gray-400 group-hover:text-primary-400 transition-colors"></i>
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
        class="w-full py-3.5 pl-11 pr-10 bg-dark-800 border rounded-xl 
               text-white placeholder-gray-500 outline-none focus:outline-none
               disabled:opacity-50 disabled:cursor-not-allowed 
               transition-colors duration-300"
        :class="{ 
          'border-red-500 ring-1 ring-red-500': hasError,
          'border-dark-700 focus:border-primary-400 focus:ring-1 focus:ring-primary-400': !hasError,
          'hover:border-dark-600': !hasError && !disabled
        }"
      >
      <button
        type="button"
        @click="togglePassword"
        class="absolute inset-y-0 right-0 flex items-center pr-4 text-gray-400 
               hover:text-primary-400 transition-colors duration-300"
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
    required: true
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