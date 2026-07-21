<!--
  ImagiLogo.vue - Standardized logo component

  Serif wordmark set in the brand display face (Fraunces) with an orange
  terminal period — "Imagi." — navy ink in light mode, white in dark.
  Supports the same size variants as before.
-->
<template>
  <router-link :to="to" class="flex items-center" :class="[iconOnly ? '' : 'space-x-2']">
    <!-- Logo Text -->
    <span
      class="wordmark font-display font-semibold leading-none tracking-[-0.01em] text-blue-950 dark:text-white transition-colors duration-300"
      :class="[
        size === 'sm' ? 'text-lg' :
        size === 'md' ? 'text-[1.35rem]' :
        size === 'lg' ? 'text-2xl' :
        size === 'xl' ? 'text-4xl' :
        'text-[1.35rem]'
      ]"
    >
      <slot>Imagi</slot><span class="text-orange-600 dark:text-orange-400" aria-hidden="true">.</span>
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

<style scoped>
/* Warm cut of Fraunces; no WONK — the wordmark stays steady while
   headline accent words carry the quirk */
.wordmark {
  font-variation-settings: 'SOFT' 30, 'WONK' 0;
  font-optical-sizing: auto;
}
</style>
