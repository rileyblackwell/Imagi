<!--
  AgentPlanChecklist.vue — the agent's plan, ticking itself off.

  The list is written once and then re-graded as the run proceeds: pending →
  in progress → completed. Because the same row changes state under the user's
  eye, the interesting motion here is not entrance but transition — the marker
  swaps with a small pop, and the text settles into (or fades out of) its new
  weight rather than switching between two different-looking rows.
-->
<template>
  <ul class="plan-list" aria-label="Agent plan">
    <li
      v-for="(step, index) in steps"
      :key="index"
      class="flex items-start gap-2 min-w-0 text-xs leading-relaxed"
    >
      <span class="flex w-3.5 shrink-0 items-center justify-center mt-[3px]">
        <!-- Keyed on the status so each grade change plays its own pop
             instead of one icon silently becoming another. -->
        <Transition name="plan-mark" mode="out-in">
          <i
            v-if="step.status === 'completed'"
            key="done"
            class="fas fa-check text-[9px] text-blue-600/70 dark:text-blue-300/70"
          ></i>
          <i
            v-else-if="step.status === 'in_progress'"
            key="running"
            class="fas fa-circle-notch fa-spin text-[9px] text-blue-600 dark:text-blue-300"
          ></i>
          <span
            v-else
            key="pending"
            class="w-[7px] h-[7px] rounded-full border border-blue-950/25 dark:border-white/25"
          ></span>
        </Transition>
      </span>
      <span class="plan-step min-w-0 break-words" :class="stepTextClass(step)">{{ step.step }}</span>
    </li>
  </ul>
</template>

<script setup lang="ts">
import type { AgentPlanStep } from '@/apps/imagi/build/types/services'

defineProps<{
  steps: AgentPlanStep[]
}>()

function stepTextClass(step: AgentPlanStep): string {
  if (step.status === 'completed') return 'text-blue-950/40 dark:text-white/35'
  if (step.status === 'in_progress') return 'font-medium text-blue-950 dark:text-white/90'
  return 'text-blue-950/65 dark:text-white/60'
}
</script>

<style scoped>
.plan-list {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

/* The row the agent is on brightens, and finished rows recede — both over the
   same interval, so the plan reads as one thing being re-graded. */
.plan-step {
  transition: color var(--iw-dur-3) var(--iw-ease-out);
}

.plan-mark-enter-active {
  transition:
    opacity var(--iw-dur-1) var(--iw-ease-out),
    transform var(--iw-dur-2) var(--iw-ease-spring);
}

.plan-mark-leave-active {
  transition:
    opacity var(--iw-dur-1) var(--iw-ease-out),
    transform var(--iw-dur-1) var(--iw-ease-out);
}

.plan-mark-enter-from {
  opacity: 0;
  transform: scale(0.4);
}

.plan-mark-leave-to {
  opacity: 0;
  transform: scale(0.6);
}
</style>
