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
    <!-- SiteNavbar's quiet link recipe, plus the open state -->
    <button
      type="button"
      class="site-nav-link group relative inline-flex items-center justify-center gap-1.5 py-2 px-3 rounded-full text-[0.875rem] whitespace-nowrap bg-transparent
             [transition:color_0.2s_cubic-bezier(0.22,1,0.36,1),background-color_0.2s_cubic-bezier(0.22,1,0.36,1)]
             hover:text-sl-text hover:bg-sl-chip-bg-hover aria-expanded:text-sl-text aria-expanded:bg-sl-chip-bg-hover"
      :class="active ? 'is-active text-sl-text font-semibold' : 'text-sl-muted font-medium'"
      aria-haspopup="true"
      :aria-expanded="isOpen ? 'true' : 'false'"
      @click="toggleDropdown"
    >
      <slot name="trigger">
        <span class="flex items-center gap-1.5 relative z-10">
          <slot></slot>
          <i
            class="fas fa-chevron-down nav-menu-chevron text-[9px] [transition:transform_0.2s_ease-in-out,opacity_0.2s_ease]"
            :class="isOpen ? 'is-open rotate-180 opacity-90' : 'opacity-[0.55]'"
            aria-hidden="true"
          ></i>
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
             the same treatment as the homepage's prompt bar and screenshots.
             The hairline: the surface on the padding box, the warm edge on the
             border box showing through the transparent border; `!` so it
             outranks `.spotlight`'s own page background. The ::before is the
             light from above, kept faint so the item reads first. -->
        <div
          class="spotlight nav-menu relative min-w-[300px] p-[6px] border border-transparent rounded-[18px]
                 ![background:linear-gradient(var(--sl-surface),var(--sl-surface))_padding-box,var(--sl-win-edge)_border-box]
                 [box-shadow:var(--sl-win-shadow)] overflow-hidden isolate
                 before:content-[''] before:absolute before:inset-0 before:z-[-1] before:pointer-events-none
                 before:[background:radial-gradient(ellipse_70%_90%_at_50%_-30%,var(--sl-spot-mid)_0%,transparent_70%)]"
        >
          <slot name="menu"></slot>
        </div>
      </div>
    </transition>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed, type SlotsType } from 'vue'

export default defineComponent({
  name: 'SiteNavbarDropdown',
  props: {
    modelValue: {
      type: Boolean,
      default: false
    },
    // The current page is one of the menu's own (the projects pages), so the
    // trigger reads as the bar's current link
    active: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:modelValue'],
  slots: Object as SlotsType<{ default?: () => unknown; trigger?: () => unknown; menu?: () => unknown }>,
  setup(props, { emit }) {
    const isOpen = computed({
      get: () => props.modelValue,
      set: (value) => emit('update:modelValue', value)
    })

    let closeTimer: ReturnType<typeof setTimeout> | null = null

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
