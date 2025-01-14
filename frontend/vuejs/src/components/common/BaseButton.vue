<template>
  <button
    :type="type"
    :class="[
      'inline-flex items-center justify-center px-4 py-2 rounded-lg font-medium transition-colors',
      'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500',
      'disabled:opacity-50 disabled:cursor-not-allowed',
      variantClasses,
      block ? 'w-full' : '',
    ]"
    :disabled="loading || disabled"
  >
    <span v-if="loading" class="mr-2">
      <i class="fas fa-circle-notch fa-spin"></i>
    </span>
    <slot></slot>
  </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'button'
  },
  variant: {
    type: String,
    default: 'primary'
  },
  block: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

const variantClasses = computed(() => {
  const variants = {
    primary: 'bg-primary-600 hover:bg-primary-700 text-white',
    secondary: 'bg-dark-700 hover:bg-dark-600 text-white',
    outline: 'border border-primary-600 text-primary-600 hover:bg-primary-600 hover:text-white',
    ghost: 'text-primary-600 hover:bg-primary-600/10'
  }
  return variants[props.variant] || variants.primary
})
</script> 