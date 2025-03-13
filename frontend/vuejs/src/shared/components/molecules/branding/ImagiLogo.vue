<!--
  ImagiLogo.vue - Standardized logo component
  
  This component provides a consistent representation of the Imagi logo
  across the application. It supports various sizes and customization options.
-->
<template>
  <router-link :to="to" class="flex items-center" :class="[iconOnly ? '' : 'space-x-2']">
    <!-- Logo Icon -->
    <div 
      class="flex items-center justify-center rounded bg-gradient-to-br from-primary-400 to-violet-400"
      :class="[
        size === 'sm' ? 'h-6 w-6' : size === 'md' ? 'h-8 w-8' : size === 'lg' ? 'h-10 w-10' : 'h-8 w-8',
        iconOnly && 'mx-auto'
      ]"
    >
      <span 
        class="font-bold text-dark-900"
        :class="[
          size === 'sm' ? 'text-sm' : size === 'md' ? 'text-lg' : size === 'lg' ? 'text-xl' : 'text-lg'
        ]"
      >
        I
      </span>
    </div>
    
    <!-- Logo Text -->
    <span 
      v-if="!iconOnly" 
      class="font-bold text-transparent bg-clip-text bg-gradient-to-r from-primary-400 to-violet-400"
      :class="[
        size === 'sm' ? 'text-base' : size === 'md' ? 'text-xl' : size === 'lg' ? 'text-2xl' : 'text-xl'
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
    validator: (value: string) => ['sm', 'md', 'lg'].includes(value)
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

<style scoped>
/* Optional animation for rainbow variant */
.bg-gradient-to-r.from-pink-300 {
  background-size: 200% auto;
  animation: gradient-shift 4s ease infinite;
}

@keyframes gradient-shift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
</style> 