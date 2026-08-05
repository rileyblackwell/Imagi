<!-- The site's standard page frame: navbar, routed content, footer.

     Two navbars, because two kinds of page use this frame. Most of the site —
     home, the project hub, and the Sell/Market/Operate workspaces — wants the
     full bar with the Product menu, Pricing and the session controls. Sign-in
     and the payment pages want the bar reduced to the wordmark, so nothing
     competes with the one thing being asked of the visitor; those opt in with
     `minimal-nav`.

     There is deliberately no page transition here. App.vue crossfades the
     routed component, and this layout is *inside* that component — every view
     renders its own DefaultLayout — so a transition at this level has no child
     swap to animate. There used to be one, driven by GSAP; it never once ran. -->
<template>
  <BaseLayout>
    <BaseNavbar v-if="minimalNav" />
    <SiteNavbar v-else />

    <main class="flex-1 relative">
      <slot></slot>
    </main>

    <BaseFooter class="z-10 relative" />
  </BaseLayout>
</template>

<script setup lang="ts">
import BaseLayout from './BaseLayout.vue'
import { BaseNavbar, BaseFooter, SiteNavbar } from '@/shared/components'

withDefaults(
  defineProps<{
    /** Reduce the top bar to the wordmark — sign-in and payment pages. */
    minimalNav?: boolean
  }>(),
  { minimalNav: false }
)
</script>
