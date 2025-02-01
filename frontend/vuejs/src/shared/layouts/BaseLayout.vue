<!-- Base layout - Root wrapper for all layouts -->
<template>
  <div class="min-h-screen bg-dark-950">
    <slot></slot>
  </div>
</template>

<script>
export default {
  name: 'BaseLayout'
}
</script>

<style>
/* Global styles */
:root {
  /* Color system */
  --color-dark-950: #0a0b0f;
  --color-dark-900: #111318;
  --color-dark-800: #1a1d24;
  --color-dark-700: #282c35;
  --color-primary-300: #93c5fd;
  --color-primary-400: #60a5fa;
  --color-primary-500: #3b82f6;
  --color-primary-600: #2563eb;
  
  /* Typography */
  --font-sans: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  
  /* Transitions */
  --transition-base: 0.2s ease-in-out;
  --transition-smooth: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Base styles */
html {
  font-family: var(--font-sans);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  @apply bg-dark-950 text-white;
  margin: 0;
  padding: 0;
}

/* Utility classes */
.bg-dark-950 { background-color: var(--color-dark-950); }
.bg-dark-900 { background-color: var(--color-dark-900); }
.bg-dark-800 { background-color: var(--color-dark-800); }
.bg-dark-700 { background-color: var(--color-dark-700); }

/* Focus styles */
*:focus-visible {
  outline: 2px solid var(--color-primary-500);
  outline-offset: 2px;
}

/* Scrollbar styling */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: var(--color-dark-900);
}

::-webkit-scrollbar-thumb {
  background: var(--color-dark-700);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--color-dark-800);
}

/* Shadow utilities */
.shadow-glow {
  box-shadow: 0 0 25px -5px var(--color-primary-500);
}
</style> 