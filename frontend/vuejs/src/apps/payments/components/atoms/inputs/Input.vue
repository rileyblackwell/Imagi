<template>
  <div>
    <label v-if="label" :for="id" class="block text-sm font-medium text-white/80 mb-2">
      {{ label }}
    </label>
    <div class="relative" :class="{ 'mt-2': !!label }">
      <span v-if="prefix" class="absolute left-4 top-1/2 transform -translate-y-1/2 text-white/60">
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
          'w-full px-4 py-3 bg-white/5 backdrop-blur-sm border border-white/20 rounded-xl text-white',
          'focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500/50 transition-all duration-300',
          'disabled:opacity-50 disabled:cursor-not-allowed placeholder:text-white/40',
          prefix ? 'pl-8' : '',
          error ? 'border-red-500/50 focus:border-red-500/50 focus:ring-red-500/50' : '',
          customClass,
        ]"
        @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
        @blur="$emit('blur', $event)"
        @focus="$emit('focus', $event)"
      >
    </div>
    <p v-if="helpText" class="mt-2 text-sm text-white/60">
      {{ helpText }}
    </p>
    <p v-if="error" class="mt-2 text-sm text-red-400">
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

/* Input focus glow effect */
input:focus {
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1), 0 0 10px 2px rgba(59, 130, 246, 0.1);
}

input.border-red-500\/50:focus {
  box-shadow: 0 0 0 2px rgba(239, 68, 68, 0.1), 0 0 10px 2px rgba(239, 68, 68, 0.1);
}
</style> 