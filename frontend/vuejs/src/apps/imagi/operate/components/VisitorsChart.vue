<!--
  VisitorsChart.vue - Visitors per day as a single run of bars.

  One series, so one colour: `--sl-cool`, the Build half's counter-light,
  which the app side of the dashboard wears. The exact count for a day is in
  the hover/focus tooltip and each bar's label, never colour alone.
-->
<template>
  <div>
    <div v-if="!hasData" class="flex items-center justify-center h-40 rounded-xl border border-dashed border-ink/10 dark:border-white/[0.12]">
      <p class="text-sm text-ink/50 dark:text-bone/50 px-6 text-center">{{ emptyText }}</p>
    </div>

    <div v-else class="relative">
      <div
        v-if="hovered"
        class="absolute z-10 -top-2 -translate-y-full -translate-x-1/2 px-3 py-2 rounded-xl bg-ink dark:bg-[#26262c] text-white text-xs shadow-lg whitespace-nowrap pointer-events-none"
        :style="{ left: `${(hoveredIndex + 0.5) / days.length * 100}%` }"
      >
        <p class="font-semibold">{{ hovered.label }}</p>
        <p class="tabular-nums">{{ hovered.visitors.toLocaleString() }} visitor{{ hovered.visitors === 1 ? '' : 's' }}</p>
      </div>

      <div class="flex items-stretch h-40">
        <button
          v-for="(day, index) in days"
          :key="day.date"
          type="button"
          class="flex-1 flex flex-col justify-end items-center rounded-md focus-ring"
          :aria-label="`${day.label}: ${day.visitors} visitor${day.visitors === 1 ? '' : 's'}`"
          @mouseenter="hoveredIndex = index"
          @mouseleave="hoveredIndex = -1"
          @focus="hoveredIndex = index"
          @blur="hoveredIndex = -1"
        >
          <div
            class="w-full max-w-[22px] h-full flex items-end px-[3px] pt-1 rounded-md transition-colors duration-150"
            :class="hoveredIndex === index ? 'bg-ink/[0.04] dark:bg-white/[0.05]' : ''"
          >
            <div
              class="w-full rounded-t-[3px] min-h-[2px] bg-[color:var(--sl-cool)]"
              :style="{ height: `${barHeight(day.visitors)}%` }"
            ></div>
          </div>
        </button>
      </div>

      <div class="border-t border-ink/10 dark:border-white/[0.1] mt-0.5 pt-1.5 flex justify-between text-[11px] text-ink/50 dark:text-bone/50">
        <span>{{ days[0]?.label }}</span>
        <span>{{ days[days.length - 1]?.label }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { AppSummary } from '../types'

const props = withDefaults(defineProps<{
  days: AppSummary['traffic']['daily']
  emptyText?: string
}>(), {
  emptyText: 'No visitors in the last two weeks.',
})

const hoveredIndex = ref(-1)
const hovered = computed(() => props.days[hoveredIndex.value] ?? null)
const maxValue = computed(() => Math.max(...props.days.map(d => d.visitors), 0))
const hasData = computed(() => maxValue.value > 0)

function barHeight(value: number): number {
  if (maxValue.value <= 0) return 0
  return Math.round((value / maxValue.value) * 100)
}
</script>
