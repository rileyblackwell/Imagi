<template>
  <div>
    <label v-if="label" :for="id" class="sr-only">{{ label }}</label>
    <div class="relative group">
      <span class="absolute inset-y-0 left-0 flex items-center pl-4 z-10">
        <i class="fas fa-lock text-white/40 group-hover:text-violet-400 transition-colors duration-300"></i>
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
        class="w-full py-4 pl-12 pr-12 rounded-xl text-white placeholder-white/30 
               outline-none focus:outline-none
               disabled:opacity-50 disabled:cursor-not-allowed 
               transition-all duration-300
               border bg-white/[0.03] backdrop-blur-sm"
        :class="{ 
          'border-red-500/50 bg-red-500/5 focus:border-red-400 focus:ring-1 focus:ring-red-400/50': hasError,
          'border-white/[0.08] hover:border-white/[0.15] focus:border-violet-500/50 focus:bg-white/[0.05] focus:ring-1 focus:ring-violet-500/30': !hasError
        }"
      >
      <button
        type="button"
        @click="togglePassword"
        class="absolute inset-y-0 right-0 flex items-center pr-4 text-white/40 
               hover:text-violet-400 transition-colors duration-300 z-10"
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
/* Custom focus styles */
input:focus {
  outline: none !important;
  box-shadow: none !important;
}

/* Override browser-specific focus styles */
input:focus-visible {
  outline: none !important;
}

/* Autofill styling to match dark theme */
input:-webkit-autofill,
input:-webkit-autofill:hover,
input:-webkit-autofill:focus {
  -webkit-text-fill-color: white;
  -webkit-box-shadow: 0 0 0px 1000px rgba(255, 255, 255, 0.03) inset;
  transition: background-color 5000s ease-in-out 0s;
}
</style>
