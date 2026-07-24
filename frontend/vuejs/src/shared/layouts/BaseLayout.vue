<!-- Base layout - Root wrapper for all layouts -->
<template>
  <!-- min-h-dvh (not min-h-screen): 100vh overshoots the visible viewport on
       mobile while browser chrome is showing, which adds phantom page scroll
       that drags fixed-navbar layouts out of alignment. -->
  <div class="flex flex-col min-h-dvh bg-white dark:bg-[#0a0a0a] transition-colors duration-300">
    <!-- Custom scrollbar and focus styles using arbitrary values.

         The blanket focus-visible outline covers buttons, links and cards,
         where a detached blue ring is the right keyboard affordance. Native
         form fields are excluded: they own their focus treatment (see
         shared/styles/forms.ts), which deepens the field's single border
         rather than layering a second edge outside it. Without the :not(),
         this outline draws over every field on the site and the result reads
         as two outlines — a grey border inside a blue ring. -->
    <div class="overflow-auto
                [&::-webkit-scrollbar]:w-2 [&::-webkit-scrollbar]:h-2
                [&::-webkit-scrollbar-track]:bg-transparent
                [&::-webkit-scrollbar-thumb]:bg-blue-950/15 dark:[&::-webkit-scrollbar-thumb]:bg-white/10 [&::-webkit-scrollbar-thumb]:rounded
                [&::-webkit-scrollbar-thumb:hover]:bg-blue-950/25 dark:[&::-webkit-scrollbar-thumb:hover]:bg-white/20
                [&_*:focus-visible:not(input):not(textarea):not(select)]:outline-2 [&_*:focus-visible:not(input):not(textarea):not(select)]:outline-blue-500/40 dark:[&_*:focus-visible:not(input):not(textarea):not(select)]:outline-blue-300/50 [&_*:focus-visible:not(input):not(textarea):not(select)]:outline-offset-2
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