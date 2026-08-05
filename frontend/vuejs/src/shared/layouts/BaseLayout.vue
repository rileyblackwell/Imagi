<!-- Base layout - Root wrapper for all layouts -->
<template>
  <!-- Two page shapes, and the difference is load-bearing.

       Ordinary pages scroll: min-h-dvh (not min-h-screen, because 100vh
       overshoots the visible viewport while mobile browser chrome is showing,
       which adds phantom page scroll that drags fixed-navbar layouts out of
       alignment), and the wrapper below carries the thin scrollbar treatment.

       App shells — the builder workspace — must not scroll at page level at
       all, so the shell is taken out of flow entirely: a fixed box pinned to
       the top and sized to the dynamic viewport. Out of flow means the
       document has nothing to scroll, on any browser, at any zoom.

       That is stronger than it looks, and it is the point. The workspace's
       chrome is not all fixed: the navbar and the sidebar are, but the
       browser pane's toolbar — the file selector above the preview — sits in
       normal flow. So a single scrollable pixel at page level slides that
       toolbar up under the navbar while the navbar and the agent panel stay
       exactly where they are. `h-dvh` alone leaves that pixel available,
       because 100dvh and the visible viewport need not round to the same
       integer at fractional zoom or device pixel ratios. Taking the shell out
       of flow removes the pixel instead of hoping it rounds away. -->
  <div
    class="flex flex-col bg-canvas transition-colors duration-300"
    :class="appShell ? 'app-shell-frame fixed inset-x-0 top-0 h-dvh overscroll-none' : 'min-h-dvh'"
  >
    <!-- The scrollbar and the keyboard focus ring both used to live here as
         arbitrary variants, which scoped them to this slot: a modal teleported
         to <body> fell outside the focus rule, and the notification toast had
         no focus treatment at all as a result. Both now come from
         shared/styles/tokens.css, where there is one definition of each. -->
    <div class="app-scroll" :class="appShell ? 'app-shell-frame h-full min-h-0' : 'overflow-auto'">
      <slot></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: 'BaseLayout' })

defineProps<{
  // Full-screen app shell (the builder workspace): the page itself is pinned
  // to the viewport and never scrolls. See the template comment for why this
  // is not the same as sizing it to the viewport.
  appShell?: boolean
}>()
</script>

<style scoped>
/* clip, not hidden. `overflow: hidden` still builds a scroll container — it
   only refuses to scroll it for the *user*. Anything that scrolls it in code
   still lands: a focus() on a partially-offscreen control, a scrollIntoView,
   a browser restoring position. That is enough to slide the whole workspace
   up under the navbar, toolbar included. `overflow: clip` builds no scroll
   container at all, so there is nothing left to move. hidden stays first as
   the fallback for browsers without clip. */
.app-shell-frame {
  overflow: hidden;
  overflow: clip;
}
</style>
