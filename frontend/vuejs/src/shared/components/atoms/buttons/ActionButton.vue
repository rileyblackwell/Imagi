<template>
  <button
    :class="[
      'inline-flex items-center px-4 py-2 border rounded-md shadow-sm text-sm font-medium',
      'focus:outline-none focus:ring-2 focus:ring-offset-2',
      variantClasses[variant],
      { 'opacity-50 cursor-not-allowed': disabled }
    ]"
    :disabled="disabled"
    @click="$emit('click', $event)"
  >
    <slot name="icon-left"></slot>
    <slot></slot>
    <slot name="icon-right"></slot>
  </button>
</template>

<script setup lang="ts">
interface Props {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost'
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  disabled: false
})

const variantClasses = {
  primary: 'text-white bg-primary-500 hover:bg-primary-600 focus:ring-primary-500',
  secondary: 'text-gray-700 bg-white hover:bg-gray-50 focus:ring-primary-500',
  danger: 'text-white bg-red-500 hover:bg-red-600 focus:ring-red-500',
  ghost: 'text-gray-400 hover:text-white bg-transparent hover:bg-dark-700'
}
</script>
