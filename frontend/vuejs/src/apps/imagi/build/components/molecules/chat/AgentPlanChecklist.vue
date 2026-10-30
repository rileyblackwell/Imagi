<!--
  AgentPlanChecklist.vue — the agent's plan, ticking itself off.

  The list is written once and then re-graded as the run proceeds: pending →
  in progress → completed. Because the same row changes state under the user's
  eye, the interesting motion here is not entrance but transition — the marker
  swaps with a small pop, and the text settles into (or fades out of) its new
  weight rather than switching between two different-looking rows.
-->
<template>
  <ul class="flex flex-col gap-1" aria-label="Agent plan">
    <li
      v-for="(step, index) in steps"
      :key="index"
      class="flex items-start gap-2 min-w-0 text-xs leading-relaxed"
    >
      <span class="flex w-3.5 shrink-0 items-center justify-center mt-[3px]">
        <!-- Keyed on the status so each grade change plays its own pop
             instead of one icon silently becoming another. -->
        <Transition
          mode="out-in"
          enter-active-class="[transition:opacity_var(--iw-dur-1)_var(--iw-ease-out),transform_var(--iw-dur-2)_var(--iw-ease-spring)]"
          enter-from-class="scale-[0.4] opacity-0"
          leave-active-class="[transition:opacity_var(--iw-dur-1)_var(--iw-ease-out),transform_var(--iw-dur-1)_var(--iw-ease-out)]"
          leave-to-class="scale-[0.6] opacity-0"
        >
          <!-- A finished step: the rail's green, a filled tick. -->
          <i
            v-if="step.status === 'completed'"
            key="done"
            class="fas fa-check grid h-3.5 w-3.5 place-items-center rounded-[50%] bg-sl-ok text-[0.4375rem] text-[color:rgb(var(--app-canvas,255_255_255))]"
          ></i>
          <i
            v-else-if="step.status === 'in_progress'"
            key="running"
            class="fas fa-circle-notch fa-spin text-[9px] text-blue-600 dark:text-blue-300"
          ></i>
          <span
            v-else
            key="pending"
            class="w-[7px] h-[7px] rounded-full border border-ink/25 dark:border-white/25"
          ></span>
        </Transition>
      </span>
      <!-- The row the agent is on brightens, and finished rows recede — both
           over the same interval, so the plan reads as one thing being
           re-graded. -->
      <span
        class="min-w-0 break-words [transition:color_var(--iw-dur-3)_var(--iw-ease-out)]"
        :class="stepTextClass(step)"
      >{{ step.step }}</span>
    </li>
  </ul>
</template>

<script setup lang="ts">
import type { AgentPlanStep } from '@/apps/imagi/build/types/services'

defineProps<{
  steps: AgentPlanStep[]
}>()

function stepTextClass(step: AgentPlanStep): string {
  if (step.status === 'completed') return 'text-ink/40 dark:text-white/35'
  if (step.status === 'in_progress') return 'font-medium text-ink dark:text-white/90'
  return 'text-ink/65 dark:text-white/60'
}
</script>
