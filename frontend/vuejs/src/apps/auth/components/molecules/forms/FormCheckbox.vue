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
                 border-black/20 dark:border-white/20 
                 bg-black/[0.05] dark:bg-white/[0.05] 
                 text-violet-500 focus:ring-violet-500/50 focus:ring-offset-0 focus:ring-2
                 disabled:opacity-50 disabled:cursor-not-allowed
                 transition-all duration-300
                 checked:bg-violet-500 checked:border-violet-500"
        >
      </Field>
    </div>
    <div class="ml-3">
      <label class="text-sm text-black/60 dark:text-white/60 leading-relaxed">
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
