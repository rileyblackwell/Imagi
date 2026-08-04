<!--
  "Read next" link — a ruled row rather than a lifting card, so the docs
  footer matches the hairline language of the rest of the site.
-->
<template>
  <router-link :to="to" class="docs-next group">
    <span class="docs-next__body">
      <span class="docs-next__title">{{ title }}</span>
      <span class="docs-next__desc">{{ description }}</span>
    </span>
    <svg
      class="docs-next__arrow"
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
    </svg>
  </router-link>
</template>

<script setup lang="ts">
import type { RouteLocationRaw } from 'vue-router'

defineProps<{
  to: RouteLocationRaw
  title: string
  description: string
}>()
</script>

<style scoped>
.docs-next {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1.5rem;
  height: 100%;
  padding: 1.5rem 0 0;
  border-top: 1px solid var(--rule);
  transition: border-color 0.18s ease;
}

.docs-next:hover {
  border-top-color: var(--accent);
}

.docs-next:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 4px;
}

.docs-next__body {
  display: block;
}

.docs-next__title {
  display: block;
  font-size: 1.0625rem;
  font-weight: 600;
  letter-spacing: -0.01em;
  color: var(--ink);
}

.docs-next__desc {
  display: block;
  margin-top: 0.5rem;
  font-size: 0.9375rem;
  line-height: 1.6;
  color: var(--ink-55);
  text-wrap: pretty;
}

.docs-next__arrow {
  flex: none;
  width: 1.1rem;
  height: 1.1rem;
  margin-top: 0.2rem;
  color: var(--ink-40);
  transition: transform 0.3s ease, color 0.18s ease;
}

.docs-next:hover .docs-next__arrow {
  transform: translateX(3px);
  color: var(--accent);
}
</style>
