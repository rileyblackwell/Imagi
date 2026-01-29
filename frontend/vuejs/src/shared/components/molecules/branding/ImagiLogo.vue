<!--
  ImagiLogo.vue - Standardized logo component
  
  This component provides a consistent representation of the Imagi logo
  across the application. It supports various sizes and customization options.
-->
<template>
  <router-link :to="to" class="flex items-center" :class="[iconOnly ? '' : 'space-x-2']">
    <!-- Logo Text -->
    <span 
      class="font-bold text-black dark:text-white tracking-tight transition-colors duration-300"
      :class="[
        size === 'sm' ? 'text-base' : 
        size === 'md' ? 'text-xl' : 
        size === 'lg' ? 'text-2xl' : 
        size === 'xl' ? 'text-4xl' : 
        'text-xl'
      ]"
    >
      <slot>Imagi</slot>
    </span>
  </router-link>
</template>

<script setup lang="ts">
defineProps({
  /**
   * Link destination
   */
  to: {
    type: [String, Object],
    default: '/'
  },
  /**
   * Size variant
   */
  size: {
    type: String,
    default: 'md',
    validator: (value: string) => ['sm', 'md', 'lg', 'xl'].includes(value)
  },
  /**
   * Whether to show only the icon
   */
  iconOnly: {
    type: Boolean,
    default: false
  }
})
</script>
