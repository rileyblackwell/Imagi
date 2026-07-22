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
                 accent-blue-950 dark:accent-blue-400
                 border-blue-950/[0.25] dark:border-white/25
                 bg-white/70 dark:bg-white/[0.05]
                 text-blue-950 dark:text-blue-400
                 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0c0c0e]
                 disabled:opacity-50 disabled:cursor-not-allowed
                 transition-all duration-300
                 checked:bg-blue-950 checked:border-blue-950 dark:checked:bg-blue-400 dark:checked:border-blue-400"
        >
      </Field>
    </div>
    <div class="ml-3">
      <label class="text-sm text-blue-950/65 dark:text-blue-100/65 leading-relaxed">
        <slot></slot>
      </label>
      <ErrorMessage v-if="showError && false" :name="name" class="block mt-1 text-sm text-red-600 dark:text-red-400" />
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
