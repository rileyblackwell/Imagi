<!--
  ImagiLogo.vue - Standardized logo component
  
  This component provides a consistent representation of the Imagi logo
  across the application. It supports various sizes and customization options.
-->
<template>
  <router-link :to="to" class="flex items-center" :class="[iconOnly ? '' : 'space-x-2']">
    <!-- Logo Container with Gradient Border -->
    <div class="rounded-2xl bg-gradient-to-br p-[1px] from-primary-300/40 to-violet-300/40
                hover:from-primary-200/50 hover:to-violet-200/50 transition-all duration-300">
      <div class="flex items-center justify-center px-2 py-1 rounded-2xl bg-dark-900/95 backdrop-blur-xl
                  shadow-[0_0_15px_-3px_rgba(99,102,241,0.4)]"
           :class="[
             size === 'sm' ? 'px-1.5 py-0.5' : size === 'md' ? 'px-2 py-1' : size === 'lg' ? 'px-3 py-1.5' : 'px-2 py-1',
           ]">
        <!-- Logo Text with Gradient -->
        <span 
          class="font-bold bg-gradient-to-r from-pink-300 via-emerald-300 to-yellow-200 
                 bg-clip-text text-transparent tracking-tight
                 drop-shadow-[0_0_12px_rgba(236,72,153,0.3)]
                 animate-gradient"
          :class="[
            size === 'sm' ? 'text-base' : size === 'md' ? 'text-xl' : size === 'lg' ? 'text-2xl' : 'text-xl'
          ]"
        >
          <slot>Imagi</slot>
        </span>
      </div>
    </div>
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
@keyframes gradient-shift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.animate-gradient {
  background-size: 200% auto;
  animation: gradient-shift 4s ease infinite;
}
</style> 