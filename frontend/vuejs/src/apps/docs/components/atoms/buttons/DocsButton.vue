<template>
  <component 
    :is="to ? (isExternalLink ? 'a' : 'router-link') : 'button'" 
    :to="!isExternalLink && to ? to : undefined"
    :href="isExternalLink && to ? to : undefined"
    :target="isExternalLink ? '_blank' : undefined"
    :rel="isExternalLink ? 'noopener noreferrer' : undefined"
    :type="type"
    :class="[
      'inline-flex items-center justify-center px-4 py-2 rounded-lg font-medium transition-all duration-200',
      'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-dark-900 focus:ring-primary-500',
      variantClasses,
      sizeClasses,
      { 'opacity-70 cursor-not-allowed': disabled }
    ]"
    :disabled="disabled"
    @click="onClick"
  >
    <i v-if="icon" :class="[icon, 'mr-2']"></i>
    <slot>{{ text }}</slot>
    <i v-if="isExternalLink && to" class="fas fa-external-link-alt text-xs ml-2"></i>
  </component>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps({
  text: {
    type: String,
    default: ''
  },
  to: {
    type: String,
    default: ''
  },
  type: {
    type: String,
    default: 'button'
  },
  variant: {
    type: String,
    default: 'primary',
    validator: (value: string) => ['primary', 'secondary', 'outline', 'text'].includes(value)
  },
  size: {
    type: String,
    default: 'md',
    validator: (value: string) => ['sm', 'md', 'lg'].includes(value)
  },
  icon: {
    type: String,
    default: ''
  },
  disabled: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['click']);

// Determine if this is an external link
const isExternalLink = computed(() => {
  if (!props.to) return false;
  return props.to.startsWith('http://') || 
         props.to.startsWith('https://') || 
         props.to.startsWith('//');
});

// Compute classes based on variant
const variantClasses = computed(() => {
  switch (props.variant) {
    case 'primary':
      return 'bg-primary-500 hover:bg-primary-600 text-white shadow-sm';
    case 'secondary':
      return 'bg-dark-800 hover:bg-dark-700 text-gray-200 shadow-sm';
    case 'outline':
      return 'bg-transparent border border-primary-500 text-primary-400 hover:bg-primary-500/10';
    case 'text':
      return 'bg-transparent text-primary-400 hover:text-primary-300 hover:bg-primary-500/5';
    default:
      return '';
  }
});

// Compute classes based on size
const sizeClasses = computed(() => {
  switch (props.size) {
    case 'sm':
      return 'text-sm py-1.5 px-3';
    case 'md':
      return 'text-base py-2 px-4';
    case 'lg':
      return 'text-lg py-2.5 px-5';
    default:
      return '';
  }
});

// Handle click event
const onClick = (event: Event) => {
  if (!props.disabled) {
    emit('click', event);
  }
};
</script> 