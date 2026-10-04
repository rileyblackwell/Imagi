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
                 accent-ink dark:accent-blue-400
                 border-ink/[0.25] dark:border-white/25
                 bg-white/70 dark:bg-white/[0.05]
                 text-ink dark:text-blue-400
                 disabled:opacity-50 disabled:cursor-not-allowed
                 transition-all duration-300
                 checked:bg-ink checked:border-ink dark:checked:bg-blue-400 dark:checked:border-blue-400"
          :class="controlFocus"
        >
      </Field>
    </div>
    <div class="ml-3">
      <label class="text-sm text-ink/65 dark:text-bone/65 leading-relaxed">
        <slot></slot>
      </label>
    </div>
  </div>
</template>

<script setup>
import { Field } from 'vee-validate'
import { controlFocus } from '@/shared/styles/forms'

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
