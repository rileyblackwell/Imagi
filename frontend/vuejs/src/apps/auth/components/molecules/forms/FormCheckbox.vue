<template>
  <div class="flex items-start p-4 rounded-xl bg-dark-800/50 border border-dark-700 
              hover:border-primary-400/30 transition-duration-300">
    <div class="flex items-center h-5">
      <Field
        :name="name"
        type="checkbox"
        :value="true"
        v-slot="{ field }"
      >
        <input
          type="checkbox"
          v-bind="field"
          :disabled="disabled"
          class="w-4 h-4 border border-dark-600 rounded bg-dark-800 text-primary-500 
                 focus:ring-primary-400/50 focus:ring-offset-0 focus:ring-2
                 disabled:opacity-50 disabled:cursor-not-allowed
                 transition-all duration-300"
        >
      </Field>
    </div>
    <div class="ml-3">
      <label class="text-sm text-gray-300">
        <slot></slot>
      </label>
      <ErrorMessage :name="name" class="block mt-1 text-sm text-red-400" />
    </div>
  </div>
</template>

<script setup>
import { Field, ErrorMessage } from 'vee-validate'

defineProps({
  name: {
    type: String,
    required: true
  },
  disabled: {
    type: Boolean,
    default: false
  }
})
</script>
