<!--
  Docs page masthead — the Spotlight pill eyebrow, headline and lede, at the
  scale a documentation page wants. No coloured word in the title; the light
  is carried by the pill's pip alone.
-->
<template>
  <header class="docs-header">
    <p class="sl-eyebrow sl-pill">
      <span class="sl-pip" aria-hidden="true"></span>
      <span>{{ badgeText }}</span>
    </p>

    <h1 class="sl-display docs-header__title">
      {{ title }}
    </h1>

    <p class="sl-lede docs-header__lede">
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
.docs-header .docs-header__title {
  margin-top: 1.5rem;
  color: var(--sl-text);
  font-size: clamp(40px, 5.6vw, 68px);
  line-height: 1;
  letter-spacing: -0.035em;
}

.docs-header .docs-header__lede {
  margin-top: 1.25rem;
}

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
