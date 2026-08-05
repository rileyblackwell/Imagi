<!--
  StatusBadge.vue — the one status pill.

  Sell, Market and Operate each had their own copy of this component, and all
  three carried a byte-identical set of colour strings for what a status means:
  emerald for "went well", red for "failed", blue for "in flight", amber for
  "working on it", ink for "nothing has happened yet". Only the vocabulary
  differed — orders are `paid`, campaigns are `delivered`, tasks are `done`.

  So the mapping stays with the domain that owns the words, and the pill lives
  here. Callers pass a tone, not a colour; see `statusTones` in shared/styles/ui.ts.
-->
<template>
  <span
    class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full border text-[11px] font-semibold uppercase tracking-[0.1em] whitespace-nowrap transition-colors duration-300"
    :class="statusTones[tone]"
  >
    <!-- A slow pulse for work still in progress. Suppressed under
         prefers-reduced-motion, where a blinking dot is just noise. -->
    <span
      v-if="pulse"
      class="w-1.5 h-1.5 rounded-full bg-current animate-pulse motion-reduce:animate-none"
    ></span>
    {{ label }}
  </span>
</template>

<script setup lang="ts">
import { statusTones, type StatusTone } from '@/shared/styles'

withDefaults(
  defineProps<{
    /** Semantic tone. The domain decides which of its statuses maps to which. */
    tone: StatusTone
    /** Display text. Already humanised by the caller (underscores, dashes). */
    label: string
    /** Show the in-progress dot. */
    pulse?: boolean
  }>(),
  { pulse: false }
)
</script>
