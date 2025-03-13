<template>
  <button
    :class="[
      'inline-flex items-center justify-center rounded-md transition-all duration-200',
      variant === 'primary' ? 'bg-primary-500 text-white hover:bg-primary-600' : 'text-gray-400 hover:text-white hover:bg-dark-700',
      size === 'sm' ? 'w-8 h-8' : 'w-10 h-10',
      disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer',
      'relative group',
      className
    ]"
    :disabled="disabled"
    title=""
    v-bind="filteredAttrs"
  >
    <!-- Tooltip -->
    <span 
      v-if="title"
      class="absolute left-full ml-3 px-2.5 py-1.5 bg-dark-800 border border-dark-600 text-white text-xs font-medium rounded-md whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-[100] shadow-xl"
      :class="{'sidebar-tooltip': isSidebarIcon}"
      style="transform: translateY(-50%); top: 50%;"
    >
      {{ title }}
    </span>

    <!-- Icon with pulse effect when active -->
    <i :class="[
      'fas', 
      iconClass, 
      size === 'sm' ? 'text-sm' : 'text-base',
      'transform transition-all duration-200 group-hover:scale-110',
      variant === 'primary' && !disabled ? 'animate-pulse' : ''
    ]"></i>
    
    <!-- Optional Text -->
    <span v-if="text" class="ml-2 text-sm truncate">{{ text }}</span>
  </button>
</template>

<script setup lang="ts">
import { computed, useAttrs } from 'vue'

const props = defineProps<{
  iconClass: string
  text?: string
  title?: string
  variant?: 'primary' | 'default'
  size?: 'sm' | 'md'
  className?: string
  disabled?: boolean
  isSidebarIcon?: boolean
}>()

// Prevent title attribute from being passed through to the button element
defineOptions({
  inheritAttrs: false
})

// Get all attributes and filter out 'title'
const attrs = useAttrs()
const filteredAttrs = computed(() => {
  const result = { ...attrs }
  delete result.title
  return result
})
</script>

<style scoped>
/* Ensure tooltips are visible in the sidebar */
.sidebar-tooltip {
  left: calc(100% + 0.75rem);
  z-index: 999;
}

/* Apply styles to make tooltips more visible */
button:hover span {
  visibility: visible;
  opacity: 1 !important;
}
</style>
