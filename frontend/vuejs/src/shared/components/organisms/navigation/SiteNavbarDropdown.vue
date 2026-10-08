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
    <button
      type="button"
      class="site-nav-link group relative"
      aria-haspopup="true"
      :aria-expanded="isOpen ? 'true' : 'false'"
      @click="toggleDropdown"
    >
      <slot name="trigger">
        <span class="flex items-center gap-1.5 relative z-10">
          <slot></slot>
          <i class="fas fa-chevron-down nav-menu-chevron" :class="{ 'is-open': isOpen }" aria-hidden="true"></i>
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
        <!-- The panel is its own small Spotlight stage: `.spotlight` brings the
             --sl-* tokens for both themes (the navbar sits outside every
             page's .spotlight root), and .nav-menu lights it — a warm
             gradient hairline and a pool of light falling from the top edge,
             the same treatment as the homepage's prompt bar and screenshots. -->
        <div class="spotlight nav-menu">
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
.nav-menu-chevron {
  font-size: 9px;
  opacity: 0.55;
  transition: transform 0.2s ease-in-out, opacity 0.2s ease;
}

.nav-menu-chevron.is-open {
  transform: rotate(180deg);
  opacity: 0.9;
}

/* Doubled class so it outranks `.spotlight`'s own page background. */
.spotlight.nav-menu {
  position: relative;
  min-width: 300px;
  padding: 6px;
  border: 1px solid transparent;
  border-radius: 18px;
  /* Gradient hairline: the surface on the padding box, the warm edge on the
     border box showing through the transparent border. */
  background:
    linear-gradient(var(--sl-surface), var(--sl-surface)) padding-box,
    var(--sl-win-edge) border-box;
  box-shadow: var(--sl-win-shadow);
  overflow: hidden;
  isolation: isolate;
}

/* The light from above, kept faint so the item reads first. */
.spotlight.nav-menu::before {
  content: '';
  position: absolute;
  inset: 0;
  z-index: -1;
  pointer-events: none;
  background: radial-gradient(ellipse 70% 90% at 50% -30%, var(--sl-spot-mid) 0%, transparent 70%);
}
</style>
