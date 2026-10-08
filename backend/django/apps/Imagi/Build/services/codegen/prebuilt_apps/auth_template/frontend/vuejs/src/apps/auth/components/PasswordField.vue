<template>
  <div class="auth-field" :class="{ 'auth-field--error': hasError }">
    <label class="auth-label" :for="id">{{ label }}</label>
    <div class="auth-control">
      <FieldIcon name="lock" />
      <input
        :id="id"
        class="auth-input auth-input--password"
        :value="modelValue"
        :name="name"
        :type="visible ? 'text' : 'password'"
        :autocomplete="autocomplete"
        :placeholder="placeholder"
        :disabled="disabled"
        :aria-invalid="hasError || undefined"
        :aria-describedby="error ? `${id}-error` : undefined"
        @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
        @blur="$emit('blur', $event)"
      >
      <button
        type="button"
        class="auth-reveal"
        :aria-label="visible ? 'Hide password' : 'Show password'"
        :aria-pressed="visible"
        @click="visible = !visible"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"
             stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z" />
          <circle cx="12" cy="12" r="3" />
          <path v-if="visible" d="m3 3 18 18" />
        </svg>
      </button>
    </div>
    <p v-if="error" :id="`${id}-error`" class="auth-field-error">{{ error }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import FieldIcon from './FieldIcon.vue'

const props = withDefaults(defineProps<{
  modelValue?: string
  name: string
  label: string
  autocomplete?: string
  placeholder?: string
  disabled?: boolean
  hasError?: boolean
  error?: string
}>(), {
  modelValue: '',
  autocomplete: 'current-password',
  placeholder: '',
  disabled: false,
  hasError: false,
  error: ''
})

defineEmits<{
  'update:modelValue': [value: string]
  blur: [event: FocusEvent]
}>()

const visible = ref(false)
const id = computed(() => `auth-${props.name}`)
</script>
