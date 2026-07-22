<template>
  <div class="text-xs">
    <!-- Once the run is over the feed folds into a one-line summary -->
    <button
      v-if="!streaming"
      type="button"
      class="inline-flex items-center gap-1.5 text-blue-950/50 dark:text-white/45 hover:text-blue-950/80 dark:hover:text-white/75 transition-colors"
      :aria-expanded="expanded"
      @click="expanded = !expanded"
    >
      <i
        class="fas fa-chevron-right text-[8px] transition-transform duration-150"
        :class="{ 'rotate-90': expanded }"
      ></i>
      <span>Completed {{ steps.length }} {{ steps.length === 1 ? 'step' : 'steps' }}</span>
    </button>

    <ul
      v-if="streaming || expanded"
      class="space-y-1"
      :class="{ 'mt-1.5': !streaming }"
      aria-label="Agent activity"
    >
      <li
        v-for="(step, index) in steps"
        :key="index"
        class="flex items-start gap-2 min-w-0 leading-relaxed"
      >
        <span class="flex w-3.5 shrink-0 items-center justify-center mt-[3px]">
          <i
            v-if="streaming && index === steps.length - 1"
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
    </ul>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { AgentActivityStep } from '@/apps/imagi/build/types/services'

defineProps<{
  steps: AgentActivityStep[]
  streaming?: boolean
}>()

const expanded = ref(false)
</script>
