<!--
  AgentActivityFeed.vue — what the agent is doing, step by step.

  Live, this is the transcript's ticker: each tool call lands as a new line
  under a spinner. Once the run is over the whole thing folds into a single
  quiet summary the user can open again if they care how it was done.

  Steps arrive one at a time over SSE, so they enter as a group (each new line
  slides up into place rather than materialising), and the fold opens by
  animating its own height rather than snapping.
-->
<template>
  <div class="text-xs">
    <!-- Once the run is over the feed folds into a one-line summary -->
    <button
      v-if="!streaming"
      type="button"
      class="feed-toggle inline-flex items-center gap-1.5 rounded text-blue-950/50 dark:text-white/45 hover:text-blue-950/80 dark:hover:text-white/75"
      :aria-expanded="expanded"
      @click="expanded = !expanded"
    >
      <i
        class="fas fa-chevron-right feed-chevron text-[8px]"
        :class="{ 'is-open': expanded }"
      ></i>
      <span>Completed {{ steps.length }} {{ steps.length === 1 ? 'step' : 'steps' }}</span>
    </button>

    <!-- Streaming: the list is simply there, growing. Settled: it lives in a
         fold that opens to whatever height it needs. -->
    <TransitionGroup
      v-if="streaming"
      name="feed-step"
      tag="ul"
      class="feed-list"
      aria-label="Agent activity"
    >
      <li
        v-for="(step, index) in steps"
        :key="`${index}-${step.label}`"
        class="feed-step flex items-start gap-2 min-w-0 leading-relaxed"
      >
        <span class="flex w-3.5 shrink-0 items-center justify-center mt-[3px]">
          <i
            v-if="index === steps.length - 1"
            class="fas fa-circle-notch fa-spin text-[9px] text-blue-600 dark:text-blue-300"
          ></i>
          <i v-else class="fas fa-check text-[9px] text-blue-600/60 dark:text-blue-300/60"></i>
        </span>
        <span class="shrink-0 text-blue-950/70 dark:text-white/65">{{ step.label }}</span>
        <span
          v-if="step.detail"
          class="min-w-0 flex-1 truncate font-mono text-[10px] leading-relaxed text-blue-950/45 dark:text-white/40 mt-px"
          :title="step.detail"
        >{{ step.detail }}</span>
      </li>
    </TransitionGroup>

    <FoldTransition v-else>
      <ul v-if="expanded" class="feed-list mt-1.5" aria-label="Agent activity">
        <li
          v-for="(step, index) in steps"
          :key="index"
          class="flex items-start gap-2 min-w-0 leading-relaxed"
        >
          <span class="flex w-3.5 shrink-0 items-center justify-center mt-[3px]">
            <i class="fas fa-check text-[9px] text-blue-600/60 dark:text-blue-300/60"></i>
          </span>
          <span class="shrink-0 text-blue-950/70 dark:text-white/65">{{ step.label }}</span>
          <span
            v-if="step.detail"
            class="min-w-0 flex-1 truncate font-mono text-[10px] leading-relaxed text-blue-950/45 dark:text-white/40 mt-px"
            :title="step.detail"
          >{{ step.detail }}</span>
        </li>
      </ul>
    </FoldTransition>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { AgentActivityStep } from '@/apps/imagi/build/types/services'
import FoldTransition from '@/apps/imagi/build/components/molecules/common/FoldTransition.vue'

defineProps<{
  steps: AgentActivityStep[]
  streaming?: boolean
}>()

const expanded = ref(false)
</script>

<style scoped>
.feed-list {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.feed-toggle {
  transition: color var(--iw-dur-2) var(--iw-ease-out);
}

.feed-toggle:focus-visible {
  outline: none;
  box-shadow: var(--iw-focus-ring);
}

.feed-chevron {
  transition: transform var(--iw-dur-3) var(--iw-ease-inout);
}

.feed-chevron.is-open {
  transform: rotate(90deg);
}

/* A step lands from below as the agent reports it, so the ticker reads as
   work accumulating rather than as text being rewritten. */
.feed-step-enter-active {
  transition:
    opacity var(--iw-dur-2) var(--iw-ease-out),
    transform var(--iw-dur-3) var(--iw-ease-out);
}

.feed-step-enter-from {
  opacity: 0;
  transform: translateY(4px);
}

.feed-step-move {
  transition: transform var(--iw-dur-3) var(--iw-ease-out);
}
</style>
