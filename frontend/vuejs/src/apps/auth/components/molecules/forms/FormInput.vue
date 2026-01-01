<template>
  <div class="form-group">
    <label class="relative block group">
      <span class="sr-only">{{ label }}</span>
      <span class="absolute inset-y-0 left-0 flex items-center pl-4 z-10">
        <i :class="[icon, 'text-white/40 group-hover:text-violet-400 transition-colors duration-300']"></i>
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
        class="w-full py-4 pl-12 pr-4 rounded-xl text-white placeholder-white/30 
               outline-none focus:outline-none
               disabled:opacity-50 disabled:cursor-not-allowed 
               transition-all duration-300
               border bg-white/[0.03] backdrop-blur-sm"
        :class="{ 
          'border-red-500/50 bg-red-500/5 focus:border-red-400 focus:ring-1 focus:ring-red-400/50': hasError, 
          'border-white/[0.08] hover:border-white/[0.15] focus:border-violet-500/50 focus:bg-white/[0.05] focus:ring-1 focus:ring-violet-500/30': !hasError
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
