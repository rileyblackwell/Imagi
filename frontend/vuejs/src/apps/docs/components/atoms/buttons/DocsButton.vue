<template>
  <component
    :is="to ? (isExternalLink ? 'a' : 'router-link') : 'button'"
    :to="!isExternalLink && to ? to : undefined"
    :href="isExternalLink && to ? to : undefined"
    :target="isExternalLink ? '_blank' : undefined"
    :rel="isExternalLink ? 'noopener noreferrer' : undefined"
    :type="type"
    :class="[baseClasses, variantClasses, { 'opacity-70 cursor-not-allowed': disabled }]"
    :disabled="disabled"
    @click="onClick"
  >
    <span v-if="isPrimary" class="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/30 to-transparent dark:via-white/60"></span>
    <span v-if="isPrimary" class="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-black/30 to-transparent dark:via-black/10"></span>

    <i v-if="icon && !isArrowIcon" :class="[icon, 'relative mr-2']"></i>
    <span class="relative">
      <slot>{{ text }}</slot>
    </span>
    <svg
      v-if="isArrowIcon"
      class="relative w-5 h-5 ml-1 transition-transform duration-300 group-hover:translate-x-1"
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
    </svg>
    <i v-if="isExternalLink && to" class="relative fas fa-external-link-alt text-xs ml-2"></i>
  </component>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps({
  text: { type: String, default: '' },
  to: { type: String, default: '' },
  type: { type: String, default: 'button' },
  variant: {
    type: String,
    default: 'primary',
    validator: (value: string) => ['primary', 'secondary', 'outline', 'text'].includes(value)
  },
  icon: { type: String, default: '' },
  disabled: { type: Boolean, default: false }
});

const emit = defineEmits(['click']);

const isExternalLink = computed(() => {
  if (!props.to) return false;
  return props.to.startsWith('http://') || props.to.startsWith('https://') || props.to.startsWith('//');
});

const isPrimary = computed(() => props.variant === 'primary');
const isArrowIcon = computed(() => props.icon === 'arrow');

const baseClasses = computed(() => {
  if (isPrimary.value) {
    return 'btn-3d group relative inline-flex items-center justify-center gap-3 px-8 py-4 rounded-full font-medium text-lg transition-all duration-300 overflow-hidden';
  }
  return 'inline-flex items-center justify-center px-5 py-2.5 rounded-full font-medium text-base transition-all duration-200 focus:outline-none';
});

const variantClasses = computed(() => {
  switch (props.variant) {
    case 'primary':
      return 'bg-gradient-to-b from-gray-800 via-gray-900 to-gray-950 dark:from-white dark:via-gray-50 dark:to-gray-100 text-white dark:text-gray-900 border border-gray-700/50 dark:border-gray-300/50';
    case 'secondary':
      return 'bg-gray-100 dark:bg-gray-100 text-gray-900 dark:text-gray-900 hover:bg-gray-200 dark:hover:bg-gray-200 border border-gray-200 dark:border-gray-300';
    case 'outline':
      return 'bg-transparent border border-gray-300 dark:border-gray-300 text-gray-900 dark:text-gray-900 hover:bg-gray-50 dark:hover:bg-gray-50';
    case 'text':
      return 'bg-transparent text-gray-700 dark:text-gray-700 hover:text-gray-900 dark:hover:text-gray-900';
    default:
      return '';
  }
});

const onClick = (event: Event) => {
  if (!props.disabled) emit('click', event);
};
</script>

<style scoped>
.btn-3d {
  transform: translateZ(0);
  box-shadow:
    0 2px 3px -1px rgba(0, 0, 0, 0.4),
    0 6px 12px -3px rgba(0, 0, 0, 0.35),
    0 16px 32px -8px rgba(0, 0, 0, 0.3),
    0 24px 48px -12px rgba(0, 0, 0, 0.2),
    0 3px 0 -1px rgba(0, 0, 0, 0.5),
    inset 0 2px 4px 0 rgba(255, 255, 255, 0.2),
    inset 0 -4px 8px -2px rgba(0, 0, 0, 0.3);
}

:global(.dark) .btn-3d {
  box-shadow:
    0 2px 3px -1px rgba(0, 0, 0, 0.1),
    0 6px 12px -3px rgba(0, 0, 0, 0.1),
    0 16px 32px -8px rgba(0, 0, 0, 0.1),
    0 24px 48px -12px rgba(0, 0, 0, 0.08),
    0 3px 0 -1px rgba(0, 0, 0, 0.15),
    inset 0 3px 6px 0 rgba(255, 255, 255, 0.9),
    inset 0 -4px 8px -2px rgba(0, 0, 0, 0.08);
}
</style>
