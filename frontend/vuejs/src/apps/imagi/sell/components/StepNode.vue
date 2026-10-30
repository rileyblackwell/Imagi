<!--
  StepNode.vue - A step's node on the Sell console rail: its number while
  it's to do, a check once done (ok), and the amber "needs you" ring (wait)
  when it's started but waiting on the founder.
-->
<template>
  <!-- Sits on the rail, outside its step's left edge -->
  <span
    class="absolute left-[-2.75rem] top-6 inline-flex h-7 w-7 items-center justify-center rounded-full border bg-sl-bg
      text-[12px] font-semibold tabular-nums
      max-[640px]:left-[-2.25rem] max-[640px]:h-6 max-[640px]:w-6 max-[640px]:text-[11px]"
    :class="{
      done: 'border-sl-ok text-sl-ok',
      wait: 'border-sl-wait text-sl-wait shadow-[0_0_0_4px_color-mix(in_srgb,var(--sl-wait)_18%,transparent)]',
      todo: 'border-sl-line-strong text-sl-muted',
    }[state]"
    :aria-label="label"
  >
    <svg v-if="state === 'done'" class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
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
