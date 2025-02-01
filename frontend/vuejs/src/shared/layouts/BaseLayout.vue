<!-- Base layout - Root wrapper for all layouts -->
<template>
  <div class="min-h-screen bg-dark-950">
    <!-- Page transition wrapper -->
    <transition
      name="page"
      mode="out-in"
      @before-enter="beforeEnter"
      @enter="enter"
      @after-enter="afterEnter"
      @enter-cancelled="enterCancelled"
      @before-leave="beforeLeave"
      @leave="leave"
      @after-leave="afterLeave"
      @leave-cancelled="leaveCancelled"
    >
      <slot></slot>
    </transition>
  </div>
</template>

<script>
export default {
  name: 'BaseLayout',
  methods: {
    beforeEnter(el) {
      el.style.opacity = 0
      el.style.transform = 'translateY(10px)'
    },
    enter(el, done) {
      gsap.to(el, {
        duration: 0.3,
        opacity: 1,
        y: 0,
        onComplete: done,
        ease: 'power2.out'
      })
    },
    afterEnter(el) {
      // Cleanup if needed
    },
    enterCancelled(el) {
      // Handle cancellation if needed
    },
    beforeLeave(el) {
      el.style.opacity = 1
    },
    leave(el, done) {
      gsap.to(el, {
        duration: 0.2,
        opacity: 0,
        y: -10,
        onComplete: done,
        ease: 'power2.in'
      })
    },
    afterLeave(el) {
      // Cleanup if needed
    },
    leaveCancelled(el) {
      // Handle cancellation if needed
    }
  }
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

/* Transition classes */
.page-enter-active,
.page-leave-active {
  transition: opacity var(--transition-smooth), transform var(--transition-smooth);
}

.page-enter-from,
.page-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

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