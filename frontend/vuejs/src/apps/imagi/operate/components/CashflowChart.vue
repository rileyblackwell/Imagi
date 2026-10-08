<!--
  CashflowChart.vue - Monthly money in vs money out, as grouped bars.
  `incomeLabel` names the first series ("Revenue" on the dashboard, where it
  counts Sell payments as well as recorded income).

  Series colors (#059669 emerald / #f43f5e rose) were validated for lightness,
  chroma, CVD separation, and surface contrast in both light and dark modes —
  keep them as a pair. Identity is never color-alone: the legend names the
  series and the hover tooltip carries exact values per month.
-->
<template>
  <div>
    <!-- Legend -->
    <div class="flex items-center gap-5 mb-4">
      <span v-for="entry in legend" :key="entry.label" class="inline-flex items-center gap-2">
        <span class="w-2.5 h-2.5 rounded-[3px]" :style="{ backgroundColor: entry.color }"></span>
        <span class="text-xs font-medium text-ink/60 dark:text-bone/60">{{ entry.label }}</span>
      </span>
    </div>

    <div v-if="!hasData" class="flex items-center justify-center h-40 rounded-xl border border-dashed border-ink/10 dark:border-white/[0.12]">
      <p class="text-sm text-ink/50 dark:text-bone/50 px-6 text-center">{{ emptyText }}</p>
    </div>

    <div v-else class="relative">
      <!-- Tooltip -->
      <div
        v-if="hovered"
        class="absolute z-10 -top-2 -translate-y-full -translate-x-1/2 px-3 py-2 rounded-xl bg-ink dark:bg-[#26262c] text-white text-xs shadow-lg whitespace-nowrap pointer-events-none"
        :style="{ left: `${(hoveredIndex + 0.5) / points.length * 100}%` }"
      >
        <p class="font-semibold mb-1">{{ hovered.label }}</p>
        <p class="tabular-nums"><span class="inline-block w-2 h-2 rounded-[2px] mr-1.5" :style="{ backgroundColor: INCOME_COLOR }"></span>{{ incomeLabel }}: {{ formatMoney(hovered.income, currency) }}</p>
        <p class="tabular-nums"><span class="inline-block w-2 h-2 rounded-[2px] mr-1.5" :style="{ backgroundColor: EXPENSE_COLOR }"></span>Expenses: {{ formatMoney(hovered.expenses, currency) }}</p>
        <p class="tabular-nums mt-1 pt-1 border-t border-white/20">{{ netLabel }}: {{ formatMoney(hovered.net, currency) }}</p>
      </div>

      <!-- Bars -->
      <div class="flex items-stretch h-40">
        <button
          v-for="(point, index) in points"
          :key="point.month"
          type="button"
          class="flex-1 flex flex-col justify-end items-center group rounded-lg focus-ring"
          :aria-label="`${point.label}: ${incomeLabel.toLowerCase()} ${formatMoney(point.income, currency)}, expenses ${formatMoney(point.expenses, currency)}`"
          @mouseenter="hoveredIndex = index"
          @mouseleave="hoveredIndex = -1"
          @focus="hoveredIndex = index"
          @blur="hoveredIndex = -1"
        >
          <div
            class="flex items-end gap-[2px] w-full max-w-[44px] h-full px-1.5 pt-1 rounded-lg transition-colors duration-150"
            :class="hoveredIndex === index ? 'bg-ink/[0.04] dark:bg-white/[0.05]' : ''"
          >
            <div
              class="flex-1 rounded-t-[4px] min-h-[2px]"
              :style="{ height: `${barHeight(point.income)}%`, backgroundColor: INCOME_COLOR }"
            ></div>
            <div
              class="flex-1 rounded-t-[4px] min-h-[2px]"
              :style="{ height: `${barHeight(point.expenses)}%`, backgroundColor: EXPENSE_COLOR }"
            ></div>
          </div>
        </button>
      </div>

      <!-- Baseline + month labels -->
      <div class="border-t border-ink/10 dark:border-white/[0.1] mt-0.5 pt-1.5 flex">
        <span
          v-for="point in points"
          :key="point.month"
          class="flex-1 text-center text-[11px] text-ink/50 dark:text-bone/50"
        >
          {{ point.label }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { CashflowPoint } from '../types'
import { formatMoney } from '../utils/ui'

const INCOME_COLOR = '#059669'
const EXPENSE_COLOR = '#f43f5e'

const props = withDefaults(defineProps<{
  points: CashflowPoint[]
  incomeLabel?: string
  netLabel?: string
  currency?: string
  emptyText?: string
}>(), {
  incomeLabel: 'Income',
  netLabel: 'Net',
  currency: 'usd',
  emptyText: 'No transactions yet. The chart fills in as you record income and expenses.',
})

const legend = computed(() => [
  { label: props.incomeLabel, color: INCOME_COLOR },
  { label: 'Expenses', color: EXPENSE_COLOR },
])

const hoveredIndex = ref(-1)
const hovered = computed(() => props.points[hoveredIndex.value] ?? null)

const maxValue = computed(() =>
  Math.max(...props.points.map(p => Math.max(p.income, p.expenses)), 0)
)

const hasData = computed(() => maxValue.value > 0)

function barHeight(value: number): number {
  if (maxValue.value <= 0) return 0
  return Math.round((value / maxValue.value) * 100)
}
</script>
