<!-- Base layout - Root wrapper for all layouts -->
<template>
  <div class="min-h-screen bg-dark-950 font-sans antialiased text-white selection:bg-primary-500/20">
    <slot></slot>
  </div>
</template>

<script>
export default {
  name: 'BaseLayout'
}
</script>

<style>
/* Scrollbar styling */
::-webkit-scrollbar {
  @apply w-2 h-2;
}

::-webkit-scrollbar-track {
  @apply bg-dark-900;
}

::-webkit-scrollbar-thumb {
  @apply bg-dark-700 rounded;
}

::-webkit-scrollbar-thumb:hover {
  @apply bg-dark-800;
}

/* Focus styles */
*:focus-visible {
  @apply outline-2 outline-primary-500 outline-offset-2;
}
</style> 