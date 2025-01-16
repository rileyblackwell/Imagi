<template>
  <div class="form-group">
    <label v-if="label" :for="id" class="block text-sm font-medium text-gray-300 mb-1">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>
    
    <div class="relative">
      <span v-if="icon" class="absolute inset-y-0 left-0 flex items-center pl-4">
        <i :class="['fas', icon, 'text-gray-400']"></i>
      </span>
      
      <input
        :id="id"
        :type="type"
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
        :required="required"
        :placeholder="placeholder"
        :disabled="disabled"
        :class="[
          'w-full py-3 px-4 bg-dark-800 border rounded-lg text-white placeholder-gray-500',
          'focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500',
          'disabled:opacity-50 disabled:cursor-not-allowed',
          icon ? 'pl-11' : '',
          error ? 'border-red-500' : 'border-dark-700'
        ]"
      >
    </div>
    
    <p v-if="error" class="mt-1 text-sm text-red-500">{{ error }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: ''
  },
  type: {
    type: String,
    default: 'text'
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
  error: {
    type: String,
    default: ''
  },
  icon: {
    type: String,
    default: ''
  }
})

const id = computed(() => `input-${Math.random().toString(36).substr(2, 9)}`)

defineEmits(['update:modelValue'])
</script> 