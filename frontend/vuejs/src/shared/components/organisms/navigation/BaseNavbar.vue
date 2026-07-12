<!-- Sticky (not fixed) on purpose: iPadOS/iOS WebKit intermittently renders
     position:fixed elements with backdrop-filter at stale viewport offsets
     (content appears squished/clipped under the bar until the tab is
     re-activated). Sticky participates in layout and is immune. The negative
     bottom margin cancels the bar's flow height so content still slides
     underneath it, exactly like the old fixed overlay. -->
<template>
  <nav class="crisp-nav sticky top-0 -mb-14 w-full z-50 bg-white/80 dark:bg-[#0a0a0a]/80 backdrop-blur-xl border-b border-gray-200/80 dark:border-white/[0.08] transition-colors duration-300">
    <div class="relative px-6 sm:px-8 lg:px-12" :class="fluid ? 'w-full' : 'max-w-7xl mx-auto'">
      <div class="relative flex items-center h-14">
        <!-- Left section -->
        <div class="flex items-center z-10">
          <ImagiLogo size="md">
            <slot name="logo">Imagi</slot>
          </ImagiLogo>
          <slot name="left"></slot>
        </div>

        <!-- Center section -->
        <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div class="pointer-events-auto">
            <slot name="center"></slot>
          </div>
        </div>

        <!-- Right section -->
        <div class="ml-auto flex items-center h-full justify-end z-10">
          <slot name="right"></slot>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ImagiLogo } from '@/shared/components/molecules'

defineProps({
  /**
   * When true, the navbar spans the full viewport width with edge padding,
   * keeping the logo and actions in the true corners at every screen size.
   * When false (default), content is capped at max-w-7xl and centered.
   */
  fluid: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped>
/* Crisp, sharp text rendering + hairline separator that stays 1px at any DPI */
.crisp-nav {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
  box-shadow: 0 1px 0 0 rgba(15, 23, 42, 0.02);
  /* Promote to a compositing layer so WebKit repaints the blurred bar
     correctly during scroll instead of reusing stale tiles. */
  transform: translateZ(0);
}

:global(.dark) .crisp-nav {
  box-shadow: 0 1px 0 0 rgba(255, 255, 255, 0.03);
}

nav {
  width: 100%;
  overflow: visible;
}

.justify-end {
  position: relative;
  z-index: 10;
}

@supports (backdrop-filter: blur(20px)) {
  nav {
    backdrop-filter: blur(20px);
  }
}
</style>
