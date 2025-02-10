<template>
  <div class="form-group">
    <label class="relative block group">
      <span class="sr-only">{{ label }}</span>
      <span class="absolute inset-y-0 left-0 flex items-center pl-4">
        <i :class="[icon, 'text-gray-400 group-hover:text-primary-400 transition-colors']"></i>
      </span>
      <Field
        :name="name"
        :type="type"
        :rules="rules"
        :validateOnInput="validateOnInput"
        v-slot="{ field, errorMessage }"
      >
        <input
          v-bind="field"
          :disabled="disabled"
          :placeholder="placeholder"
          :type="inputType"
          class="w-full py-3.5 pl-11 pr-4 bg-dark-800 border border-dark-700 rounded-xl 
                 text-white placeholder-gray-500 outline-none focus:ring-0
                 focus:border-primary-400 disabled:opacity-50 disabled:cursor-not-allowed 
                 transition-all duration-500 ease-out hover:border-primary-400/50
                 hover:bg-dark-800/80"
          :class="{ 'border-red-500': errorMessage }"
        >
      </Field>
    </label>
    <ErrorMessage v-if="showError" :name="name" class="mt-2 text-sm text-red-400" />
  </div>
</template>

<script setup>
import { Field, ErrorMessage } from 'vee-validate'
import { computed } from 'vue'

const props = defineProps({
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
  rules: {
    type: [String, Object, Function],
    default: ''
  },
  disabled: {
    type: Boolean,
    default: false
  },
  placeholder: {
    type: String,
    default: ''
  },
  validateOnInput: {
    type: Boolean,
    default: false
  },
  showError: {
    type: Boolean,
    default: true
  }
})

const inputType = computed(() => {
  return props.type
})
</script>
