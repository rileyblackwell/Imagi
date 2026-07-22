<template>
  <div>
    <label v-if="label" :for="id" class="block text-sm font-medium text-blue-950/80 dark:text-blue-100/80 mb-2 transition-colors duration-300">
      {{ label }}
    </label>
    <div class="relative" :class="{ 'mt-2': !!label }">
      <span v-if="prefix" class="absolute left-4 top-1/2 transform -translate-y-1/2 text-blue-950/60 dark:text-blue-100/55">
        {{ prefix }}
      </span>
      <input
        :id="id"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :min="min"
        :max="max"
        :step="step"
        :required="required"
        :disabled="disabled"
        :readonly="readonly"
        :class="[
          'w-full px-4 py-3 bg-white dark:bg-white/[0.05] backdrop-blur-sm border border-blue-950/[0.12] dark:border-white/[0.14] rounded-xl text-blue-950 dark:text-white',
          'transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:border-blue-500/50 dark:focus-visible:border-blue-300/50',
          'disabled:opacity-50 disabled:cursor-not-allowed placeholder:text-blue-950/40 dark:placeholder:text-blue-100/30',
          prefix ? 'pl-8' : '',
          error ? 'border-red-500/50 dark:border-red-400/50 focus-visible:border-red-500/50 dark:focus-visible:border-red-400/50 focus-visible:ring-red-500/40 dark:focus-visible:ring-red-400/40' : '',
          customClass,
        ]"
        @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
        @blur="$emit('blur', $event)"
        @focus="$emit('focus', $event)"
      >
    </div>
    <p v-if="helpText" class="mt-2 text-sm text-blue-950/60 dark:text-blue-100/55 transition-colors duration-300">
      {{ helpText }}
    </p>
    <p v-if="error" class="mt-2 text-sm text-red-600 dark:text-red-400">
      {{ error }}
    </p>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import type { PropType } from 'vue'

export default defineComponent({
  name: 'PaymentInput',
  props: {
    modelValue: {
      type: [String, Number],
      default: ''
    },
    id: {
      type: String,
      default: () => `input-${Math.random().toString(36).substring(2, 9)}`
    },
    label: {
      type: String,
      default: ''
    },
    type: {
      type: String as PropType<'text' | 'number' | 'email' | 'password' | 'tel' | 'url'>,
      default: 'text'
    },
    prefix: {
      type: String,
      default: ''
    },
    placeholder: {
      type: String,
      default: ''
    },
    helpText: {
      type: String,
      default: ''
    },
    error: {
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
    readonly: {
      type: Boolean,
      default: false
    },
    min: {
      type: [String, Number],
      default: undefined
    },
    max: {
      type: [String, Number],
      default: undefined
    },
    step: {
      type: [String, Number],
      default: undefined
    },
    customClass: {
      type: String,
      default: ''
    }
  },
  emits: ['update:modelValue', 'blur', 'focus']
})
</script>

<style scoped>
/* Hide browser spinner on number inputs */
input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

input[type="number"] {
  -moz-appearance: textfield;
}
</style> 