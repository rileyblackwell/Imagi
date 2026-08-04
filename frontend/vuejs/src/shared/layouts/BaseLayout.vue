<!-- Base layout - Root wrapper for all layouts -->
<template>
  <!-- min-h-dvh (not min-h-screen): 100vh overshoots the visible viewport on
       mobile while browser chrome is showing, which adds phantom page scroll
       that drags fixed-navbar layouts out of alignment. -->
  <div class="flex flex-col min-h-dvh bg-canvas transition-colors duration-300">
    <!-- The scrollbar and the keyboard focus ring both used to live here as
         arbitrary variants, which scoped them to this slot: a modal teleported
         to <body> fell outside the focus rule, and the notification toast had
         no focus treatment at all as a result. Both now come from
         shared/styles/tokens.css, where there is one definition of each. -->
    <div class="app-scroll overflow-auto">
      <slot></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BaseLayout'
}
</script>