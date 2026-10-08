<template>
  <div class="auth-field" :class="{ 'auth-field--error': hasError }">
    <label class="auth-label" :for="id">{{ label }}</label>
    <div class="auth-control">
      <FieldIcon :name="icon" />
      <input
        :id="id"
        class="auth-input"
        :value="modelValue"
        :name="name"
        :type="type"
        :autocomplete="autocomplete"
        :placeholder="placeholder"
        :disabled="disabled"
        :aria-invalid="hasError || undefined"
        :aria-describedby="error ? `${id}-error` : undefined"
        @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
        @blur="$emit('blur', $event)"
      >
    </div>
    <p v-if="error" :id="`${id}-error`" class="auth-field-error">{{ error }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import FieldIcon from './FieldIcon.vue'

const props = withDefaults(defineProps<{
  modelValue?: string
  name: string
  label: string
  icon?: 'user' | 'mail' | 'lock'
  type?: string
  autocomplete?: string
  placeholder?: string
  disabled?: boolean
  hasError?: boolean
  error?: string
}>(), {
  modelValue: '',
  icon: 'user',
  type: 'text',
  autocomplete: 'off',
  placeholder: '',
  disabled: false,
  hasError: false,
  error: ''
})

defineEmits<{
  'update:modelValue': [value: string]
  blur: [event: FocusEvent]
}>()

const id = computed(() => `auth-${props.name}`)
</script>
