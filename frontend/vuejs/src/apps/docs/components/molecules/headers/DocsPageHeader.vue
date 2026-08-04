<!--
  Docs page masthead — the site's standard eyebrow + headline + lede, at the
  scale a documentation page wants. No coloured word in the title; the accent
  is carried by the eyebrow alone.
-->
<template>
  <header class="docs-header">
    <p class="eyebrow">
      <span class="eyebrow__rule" aria-hidden="true"></span>
      <span>{{ badgeText }}</span>
    </p>

    <h1 class="display mt-6 text-[2.4rem] sm:text-5xl md:text-[3.4rem]">
      {{ title }}
    </h1>

    <p class="lede mt-5 text-lg max-w-2xl">
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
.docs-header {
  margin-bottom: 3rem;
  animation: docs-header-rise 0.8s var(--app-ease) both;
}

@media (min-width: 768px) {
  .docs-header {
    margin-bottom: 3.5rem;
  }
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
