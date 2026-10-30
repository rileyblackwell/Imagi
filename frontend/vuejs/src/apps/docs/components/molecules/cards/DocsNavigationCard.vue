<!--
  "Read next" link — a ruled row rather than a lifting card, so the docs
  footer matches the hairline language of the rest of the site.
-->
<template>
  <!-- These sit two-up in a `rule-cols--2` grid, which has no column gap of its
       own (its columns pad themselves) — the md: odd/even margins keep the left
       card's arrow from butting into the right card's title. The focus ring
       needs `!` to beat `.spotlight :focus-visible`. -->
  <router-link
    :to="to"
    class="group/next flex h-full items-start justify-between gap-6 border-t border-t-ed-rule pt-6
      transition-[border-color] duration-[180ms] ease-[ease] hover:border-t-ed-accent
      md:odd:mr-6 md:even:ml-6
      focus-visible:outline focus-visible:outline-2 focus-visible:!outline-ed-accent focus-visible:!outline-offset-4"
  >
    <span class="block">
      <span class="block text-[1.0625rem] font-semibold tracking-[-0.01em] text-ed-ink">{{ title }}</span>
      <span class="mt-2 block text-[0.9375rem] leading-[1.6] text-ed-ink-55 text-pretty">{{ description }}</span>
    </span>
    <svg
      class="mt-[0.2rem] h-[1.1rem] w-[1.1rem] flex-none text-ed-ink-40 [transition:transform_0.3s_ease,color_0.18s_ease]
        group-hover/next:translate-x-[3px] group-hover/next:text-ed-accent"
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
