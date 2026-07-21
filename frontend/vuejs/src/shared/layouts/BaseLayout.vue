<!-- Base layout - Root wrapper for all layouts -->
<template>
  <!-- min-h-dvh (not min-h-screen): 100vh overshoots the visible viewport on
       mobile while browser chrome is showing, which adds phantom page scroll
       that drags fixed-navbar layouts out of alignment. -->
  <div class="flex flex-col min-h-dvh bg-white dark:bg-[#0a0a0a] transition-colors duration-300">
    <!-- Custom scrollbar and focus styles using arbitrary values -->
    <div class="overflow-auto
                [&::-webkit-scrollbar]:w-2 [&::-webkit-scrollbar]:h-2
                [&::-webkit-scrollbar-track]:bg-transparent
                [&::-webkit-scrollbar-thumb]:bg-blue-950/15 dark:[&::-webkit-scrollbar-thumb]:bg-white/10 [&::-webkit-scrollbar-thumb]:rounded
                [&::-webkit-scrollbar-thumb:hover]:bg-blue-950/25 dark:[&::-webkit-scrollbar-thumb:hover]:bg-white/20
                [&_*:focus-visible]:outline-2 [&_*:focus-visible]:outline-blue-500/40 dark:[&_*:focus-visible]:outline-blue-300/50 [&_*:focus-visible]:outline-offset-2
                [scrollbar-width]:thin">
      <slot></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BaseLayout'
}
</script>