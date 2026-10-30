<!--
  A numbered step. The numeral is set in Fraunces against a hairline rule
  rather than in a tinted tile, matching the step eyebrows on the home page.
-->
<template>
  <section class="mt-7 flex items-baseline gap-6 border-t border-t-ed-rule pt-7">
    <p
      class="w-8 flex-none bg-sl-grad bg-clip-text font-[family-name:var(--font-display)] text-[1.25rem] font-extrabold
        tabular-nums text-transparent"
    >{{ number }}</p>
    <div class="flex-1">
      <h3 class="text-[1.25rem] font-semibold tracking-[-0.01em] text-ed-ink">{{ title }}</h3>
      <div class="mt-[0.65rem] leading-[1.7] text-ed-ink-55 text-pretty">
        <slot></slot>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  number: string | number
  title: string
}>()
</script>
