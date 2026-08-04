<!--
  SiteNavbarDropdown.vue — the navbar's "Product" menu.

  This used to carry a gradient-button system: two colour maps, a `gradientType`
  prop validating six values, and a `textStyle` flag. Its one caller passed
  `gradient-type="minimal" text-style`, which returned from the first branch of
  both computeds, so nothing below that line ever ran. What is left is what the
  component actually rendered.
-->
<template>
  <div class="relative" @mouseenter="openDropdown" @mouseleave="startCloseTimer">
    <button type="button" class="site-nav-link group relative" @click="toggleDropdown">
      <slot name="trigger">
        <span class="flex items-center gap-2 relative z-10">
          <slot></slot>
        </span>
      </slot>
    </button>

    <transition
      enter-active-class="transition ease-out duration-200"
      enter-from-class="opacity-0 scale-95 -translate-y-2"
      enter-to-class="opacity-100 scale-100 translate-y-0"
      leave-active-class="transition ease-in duration-150"
      leave-from-class="opacity-100 scale-100 translate-y-0"
      leave-to-class="opacity-0 scale-95 -translate-y-2"
    >
      <div v-show="isOpen" class="absolute left-1/2 -translate-x-1/2 pt-3 w-max origin-top z-50">
        <!-- crisp-card is the shared shadow ladder from tokens.css; this panel
             had its own copy of it under a different class name. -->
        <div class="crisp-card rounded-2xl bg-paper-raised/95 border border-blue-200/60 dark:border-blue-400/[0.14] backdrop-blur-xl overflow-hidden p-1.5 transition-colors duration-300">
          <slot name="menu"></slot>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import { defineComponent, computed } from 'vue'

export default defineComponent({
  name: 'SiteNavbarDropdown',
  props: {
    modelValue: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const isOpen = computed({
      get: () => props.modelValue,
      set: (value) => emit('update:modelValue', value)
    })

    let closeTimer = null

    const openDropdown = () => {
      if (closeTimer) {
        clearTimeout(closeTimer)
        closeTimer = null
      }
      isOpen.value = true
    }

    // A short grace period, so crossing the gap between the trigger and the
    // panel does not close the menu.
    const startCloseTimer = () => {
      closeTimer = setTimeout(() => {
        isOpen.value = false
      }, 150)
    }

    const toggleDropdown = () => {
      isOpen.value = !isOpen.value
    }

    return {
      isOpen,
      openDropdown,
      startCloseTimer,
      toggleDropdown
    }
  }
})
</script>

<style scoped>
/* Add transition for dropdown chevron */
.fa-chevron-down {
  transition: transform 0.2s ease-in-out;
}
</style>
