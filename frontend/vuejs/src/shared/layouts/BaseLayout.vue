<template>
  <div class="min-h-screen bg-dark-950">
    <!-- Header -->
    <app-header />

    <!-- Hero Section -->
    <section class="relative pt-24 min-h-[60vh] flex items-center justify-center overflow-hidden">
      <slot name="hero"></slot>
    </section>

    <!-- Main Content -->
    <main>
      <slot></slot>
    </main>
  </div>
</template>

<script>
import AppHeader from '@/shared/components/AppHeader.vue'

export default {
  name: 'BaseLayout',
  components: {
    AppHeader
  }
}
</script>

<style>
:root {
  --color-dark-950: #0a0b0f;
  --color-dark-900: #111318;
  --color-dark-800: #1a1d24;
  --color-dark-700: #282c35;
  --color-primary-400: #60a5fa;
  --color-primary-500: #3b82f6;
  --color-primary-600: #2563eb;
}

.bg-dark-950 {
  background-color: var(--color-dark-950);
}

.shadow-glow {
  box-shadow: 0 0 25px -5px var(--color-primary-500);
}
</style> 