<template>
  <ul class="space-y-1" aria-label="Agent plan">
    <li
      v-for="(step, index) in steps"
      :key="index"
      class="flex items-start gap-2 min-w-0 text-xs leading-relaxed"
    >
      <span class="flex w-3.5 shrink-0 items-center justify-center mt-[3px]">
        <i
          v-if="step.status === 'completed'"
          class="fas fa-check text-[9px] text-blue-600/70 dark:text-blue-300/70"
        ></i>
        <i
          v-else-if="step.status === 'in_progress'"
          class="fas fa-circle-notch fa-spin text-[9px] text-blue-600 dark:text-blue-300"
        ></i>
        <span
          v-else
          class="w-[7px] h-[7px] rounded-full border border-blue-950/25 dark:border-white/25"
        ></span>
      </span>
      <span class="min-w-0 break-words" :class="stepTextClass(step)">{{ step.step }}</span>
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
