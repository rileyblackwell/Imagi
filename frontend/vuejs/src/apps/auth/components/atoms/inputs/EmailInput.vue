<template>
  <div>
    <label v-if="label" :for="id" class="sr-only">{{ label }}</label>
    <div class="relative">
      <span class="absolute inset-y-0 left-0 flex items-center pl-3">
        <i class="fas fa-envelope text-gray-400 group-hover:text-primary-400 transition-colors"></i>
      </span>
      <input
        :id="id"
        type="email"
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
        :placeholder="placeholder"
        :required="required"
        :disabled="disabled"
        class="appearance-none rounded-lg relative block w-full pl-10 py-3 border border-dark-700
               bg-dark-800 text-white placeholder-gray-500 focus:outline-none focus:ring-2
               focus:ring-primary-500 focus:border-transparent disabled:opacity-50
               disabled:cursor-not-allowed transition-all duration-300 ease-in-out
               group-hover:bg-dark-700"
      >
    </div>
  </div>
</template>

<script setup>
defineProps({
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
    default: () => `email-input-${Math.random().toString(36).substr(2, 9)}`
  }
})

defineEmits(['update:modelValue'])
</script>