<!--
  A numbered step. The numeral is set in Fraunces against a hairline rule
  rather than in a tinted tile, matching the step eyebrows on the home page.
-->
<template>
  <section class="step">
    <p class="step__num">{{ number }}</p>
    <div class="step__body">
      <h3 class="step__title">{{ title }}</h3>
      <div class="step__text">
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

<style scoped>
.step {
  display: flex;
  align-items: baseline;
  gap: 1.5rem;
  padding-top: 1.75rem;
  margin-top: 1.75rem;
  border-top: 1px solid var(--rule);
}

.step__num {
  flex: none;
  width: 2rem;
  font-family: 'Fraunces', Georgia, serif;
  font-size: 1.25rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  color: var(--accent);
}

.step__body {
  flex: 1;
}

.step__title {
  font-size: 1.25rem;
  font-weight: 600;
  letter-spacing: -0.01em;
  color: var(--ink);
}

.step__text {
  margin-top: 0.65rem;
  line-height: 1.7;
  color: var(--ink-55);
  text-wrap: pretty;
}
</style>
