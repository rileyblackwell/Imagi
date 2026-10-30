<!--
  AgentActivityFeed.vue — what the agent is doing, step by step.

  Live, this is the transcript's ticker: each tool call lands as a new line
  under a spinner. Once the run is over the whole thing folds into a single
  quiet line that says so, and opens again for anyone who wants to see how it
  was done.

  Every step is written for the person paying for the app rather than the one
  who would read the diff — "Updated your home page", not "Edited
  HomeView.vue" over a file path in monospace. That path used to sit beside
  each label and was the one thing on the screen its reader could not read.

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
      class="inline-flex items-center gap-1.5 rounded text-ink/50 dark:text-white/45 hover:text-ink/80 dark:hover:text-white/75
        [transition:color_var(--iw-dur-2)_var(--iw-ease-out)] focus-visible:shadow-iw-focus focus-visible:![outline:none]"
      :aria-expanded="expanded"
      @click="expanded = !expanded"
    >
      <i
        class="fas fa-chevron-right text-[8px] [transition:transform_var(--iw-dur-3)_var(--iw-ease-inout)]"
        :class="{ 'rotate-90': expanded }"
      ></i>
      <span>{{ foldLabel }}</span>
    </button>

    <!-- Streaming: the list is simply there, growing. Settled: it lives in a
         fold that opens to whatever height it needs. -->
    <!-- A step lands from below as the agent reports it, so the ticker reads
         as work accumulating rather than as text being rewritten. -->
    <TransitionGroup
      v-if="streaming"
      tag="ul"
      class="flex flex-col gap-1"
      aria-label="Agent activity"
      enter-active-class="[transition:opacity_var(--iw-dur-2)_var(--iw-ease-out),transform_var(--iw-dur-3)_var(--iw-ease-out)]"
      enter-from-class="translate-y-1 opacity-0"
      move-class="[transition:transform_var(--iw-dur-3)_var(--iw-ease-out)]"
    >
      <li
        v-for="(step, index) in steps"
        :key="`${index}-${step.label}`"
        class="flex items-start gap-2 min-w-0 leading-relaxed"
      >
        <span class="flex w-3.5 shrink-0 items-center justify-center mt-[3px]">
          <!-- The step in progress wears the workspace's live dot
               (styles/workspace.css), sized to the check marks beside it. -->
          <span v-if="index === steps.length - 1" class="iw-live !h-1.5 !w-1.5"></span>
          <!-- Steps done take the rail's green, like the plan's ticks. -->
          <i v-else class="fas fa-check text-[9px] text-sl-ok"></i>
        </span>
        <span class="min-w-0 text-ink/70 dark:text-white/65">{{ step.label }}</span>
      </li>
    </TransitionGroup>

    <FoldTransition v-else>
      <ul v-if="expanded" class="mt-1.5 flex flex-col gap-1" aria-label="Agent activity">
        <li
          v-for="(step, index) in steps"
          :key="index"
          class="flex items-start gap-2 min-w-0 leading-relaxed"
        >
          <span class="flex w-3.5 shrink-0 items-center justify-center mt-[3px]">
            <i class="fas fa-check text-[9px] text-sl-ok"></i>
          </span>
          <span class="min-w-0 text-ink/70 dark:text-white/65">{{ step.label }}</span>
        </li>
      </ul>
    </FoldTransition>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { AgentActivityStep } from '@/apps/imagi/build/types/services'
import FoldTransition from '@/apps/imagi/build/components/molecules/common/FoldTransition.vue'

const props = defineProps<{
  steps: AgentActivityStep[]
  streaming?: boolean
}>()

const expanded = ref(false)

/**
 * The one line this collapses to once the run is over. It does two jobs, and
 * both matter to someone who does not read code: it says the work is
 * finished — the fold appearing IS the run ending — and it says what is
 * behind it, so opening the steps is an offer rather than a guess at a
 * caret.
 */
const foldLabel = computed(() => {
  if (expanded.value) return 'Hide the steps'
  const count = props.steps.length
  return `Finished — see the ${count} ${count === 1 ? 'step' : 'steps'} it took`
})
</script>
