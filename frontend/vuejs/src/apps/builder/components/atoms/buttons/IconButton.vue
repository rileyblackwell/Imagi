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
    :title="title"
    v-bind="$attrs"
  >
    <!-- Tooltip -->
    <span 
      v-if="title"
      class="absolute left-full ml-2.5 px-2 py-1 bg-dark-800 border border-dark-600 text-white text-xs rounded-md whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50 shadow-lg"
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
defineProps<{
  iconClass: string
  text?: string
  title?: string
  variant?: 'primary' | 'default'
  size?: 'sm' | 'md'
  className?: string
  disabled?: boolean
}>()
</script>
