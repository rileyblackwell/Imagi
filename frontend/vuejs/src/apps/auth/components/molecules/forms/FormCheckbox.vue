<template>
  <div class="flex items-start">
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
          class="w-4 h-4 rounded
                 accent-blue-600
                 border-blue-300 dark:border-white/20
                 bg-blue-50 dark:bg-white/[0.05]
                 text-blue-600 focus:ring-blue-500/40 focus:ring-offset-0 focus:ring-2
                 disabled:opacity-50 disabled:cursor-not-allowed
                 transition-all duration-300
                 checked:bg-blue-600 checked:border-blue-600"
        >
      </Field>
    </div>
    <div class="ml-3">
      <label class="text-sm text-blue-950/60 dark:text-white/60 leading-relaxed">
        <slot></slot>
      </label>
      <ErrorMessage v-if="showError && false" :name="name" class="block mt-1 text-sm text-red-400" />
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
  },
  showError: {
    type: Boolean,
    default: true
  }
})
</script>
