<!--
  Docs page masthead — the Spotlight pill eyebrow, headline and lede, at the
  scale a documentation page wants. No coloured word in the title; the light
  is carried by the pill's pip alone.
-->
<template>
  <header class="docs-header mb-12 md:mb-14">
    <p class="sl-eyebrow sl-pill">
      <span class="sl-pip" aria-hidden="true"></span>
      <span>{{ badgeText }}</span>
    </p>

    <!-- `!` beats .sl-display / .sl-lede's `margin: 0` -->
    <h1 class="sl-display !mt-6 text-[clamp(40px,5.6vw,68px)] leading-none tracking-[-0.035em] text-sl-text">
      {{ title }}
    </h1>

    <p class="sl-lede !mt-5">
      {{ description }}
    </p>

    <div class="section-rule mt-10" aria-hidden="true"></div>
  </header>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    title: string
    description: string
    badgeText?: string
  }>(),
  { badgeText: 'Documentation' }
)
</script>

<style scoped>
/* The masthead's rise: keyframes stay in CSS (scoped names are hashed). */
.docs-header {
  animation: docs-header-rise 0.8s var(--app-ease) both;
}

@keyframes docs-header-rise {
  from {
    opacity: 0;
    transform: translateY(16px);
  }
  to {
    opacity: 1;
    transform: none;
  }
}

@media (prefers-reduced-motion: reduce) {
  .docs-header {
    animation: none;
  }
}
</style>
