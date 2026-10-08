<!--
  StepNode.vue - A step's node on the Sell console rail: its number while
  it's to do, a check once done (ok), and the amber "needs you" ring (wait)
  when it's started but waiting on the founder.
-->
<template>
  <span class="step-node" :class="`step-node--${state}`" :aria-label="label">
    <svg v-if="state === 'done'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <path d="M5 12.5l4.5 4.5L19 7.5" />
    </svg>
    <span v-else aria-hidden="true">{{ index }}</span>
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  index: number
  state: 'done' | 'wait' | 'todo'
}>()

const label = computed(() => {
  const status = { done: 'done', wait: 'needs you', todo: 'to do' }[props.state]
  return `Step ${props.index}, ${status}`
})
</script>

<style scoped>
.step-node {
  position: absolute;
  left: -2.75rem;
  top: 1.5rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.75rem;
  height: 1.75rem;
  border-radius: 9999px;
  border: 1px solid var(--sl-line-strong);
  background: var(--sl-bg);
  color: var(--sl-muted);
  font-size: 12px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.step-node svg {
  width: 0.875rem;
  height: 0.875rem;
}

.step-node--done {
  border-color: var(--sl-ok);
  color: var(--sl-ok);
}

.step-node--wait {
  border-color: var(--sl-wait);
  color: var(--sl-wait);
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--sl-wait) 18%, transparent);
}

@media (max-width: 640px) {
  .step-node {
    left: -2.25rem;
    width: 1.5rem;
    height: 1.5rem;
    font-size: 11px;
  }
}
</style>
