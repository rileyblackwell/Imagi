<template>
  <button
    :class="[
      'flex items-center justify-center px-4 py-2 rounded-lg transition-all duration-200',
      variant === 'primary' ? 'bg-gradient-to-r from-primary-500 to-indigo-500 hover:from-primary-400 hover:to-indigo-400 text-white' :
      variant === 'secondary' ? 'border border-dark-600 text-gray-400 hover:text-white hover:border-dark-500' :
      'bg-dark-700 hover:bg-dark-600 text-white',
      disabled ? 'opacity-50 cursor-not-allowed' : '',
      fullWidth ? 'w-full' : ''
    ]"
    :disabled="disabled"
    @click="$emit('click')"
  >
    <i v-if="icon" :class="['fas', icon, iconPosition === 'left' ? 'mr-2' : 'ml-2']"></i>
    <slot></slot>
  </button>
</template>

<script setup>
defineProps({
  variant: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'secondary', 'tertiary'].includes(value)
  },
  icon: {
    type: String,
    default: ''
  },
  iconPosition: {
    type: String,
    default: 'left',
    validator: (value) => ['left', 'right'].includes(value)
  },
  disabled: {
    type: Boolean,
    default: false
  },
  fullWidth: {
    type: Boolean,
    default: false
  }
});

defineEmits(['click']);
</script>
