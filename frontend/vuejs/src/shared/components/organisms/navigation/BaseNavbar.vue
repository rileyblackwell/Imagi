<template>
  <!-- top-0 left-0 right-0 is load-bearing, not decoration. A fixed box with
       `top: auto` is painted at its *static* position — where it would have sat
       in normal flow — so without the anchor the bar's placement is a function
       of whatever else happens to be in flow above it. That is fine on a hard
       load and wrong during a route change: App.vue crossfades the two pages,
       so for one layout pass the outgoing page is still in flow above the
       incoming one, and the bar resolves to the bottom of the page you just
       left. It stayed there until the next reload. -->
  <!-- Crisp text, and a hairline shadow under the border that stays 1px at
       any DPI. The 20px blur is `!` because it used to be a scoped rule that
       outranked the blur a layout passes in (DashboardLayout's backdrop-blur-md). -->
  <nav
    class="crisp-text fixed top-0 left-0 right-0 z-50 w-full overflow-visible font-body bg-canvas/80 backdrop-blur-xl
           supports-[backdrop-filter:blur(20px)]:!backdrop-blur-[20px]
           border-b border-ink/[0.08] dark:border-white/[0.08]
           [box-shadow:0_1px_0_0_rgba(15,23,42,0.02)] dark:[box-shadow:0_1px_0_0_rgba(255,255,255,0.03)]
           transition-colors duration-300"
  >
    <div class="relative px-6 sm:px-8 lg:px-12" :class="fluid ? 'w-full' : 'max-w-7xl mx-auto'">
      <!-- The bar is fixed, so everything below it is pushed down by the
           `nav` spacing token (tailwind.config.js) — this row's height plus
           the hairline above. Change one and change the other. -->
      <div class="relative flex items-center h-14">
        <!-- Left section -->
        <div class="flex items-center z-10">
          <!-- Leading slot sits before the wordmark (e.g. the sidebar toggle) -->
          <slot name="left-leading"></slot>
          <ImagiLogo size="md" />
          <slot name="left"></slot>
        </div>

        <!-- Center section -->
        <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div class="pointer-events-auto">
            <slot name="center"></slot>
          </div>
        </div>

        <!-- Right section -->
        <div class="relative ml-auto flex items-center h-full justify-end z-10">
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
