<!-- Base layout - Root wrapper for all layouts.
     IMPORTANT: keep this free of overflow/scroll styles. The window must remain
     the ONLY scroll container. A nested full-page `overflow-auto` wrapper makes
     Safari (especially iPadOS/iOS) scroll the wrapper instead of the window,
     which breaks scroll-to-top on navigation (pages appear pre-scrolled with
     the hero clipped under the navbar) and traps touch scrolling mid-page.
     Scrollbar and focus-visible styling lives in src/assets/main.css. -->
<template>
  <div class="flex flex-col min-h-screen bg-white dark:bg-[#0a0a0a] transition-colors duration-300">
    <slot></slot>
  </div>
</template>

<script>
export default {
  name: 'BaseLayout'
}
</script>
