<!--
  OrderStatusBadge.vue - Colored pill for order statuses.
-->
<template>
  <span
    class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full border text-[11px] font-semibold uppercase tracking-[0.1em] whitespace-nowrap transition-colors duration-300"
    :class="colorClasses"
  >
    <span v-if="status === 'pending'" class="w-1.5 h-1.5 rounded-full bg-current animate-pulse"></span>
    {{ status }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  status: string
}>()

const colorClasses = computed(() => {
  switch (props.status) {
    case 'paid':
      return 'border-emerald-200/80 dark:border-emerald-400/25 bg-emerald-50/80 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-300'
    case 'fulfilled':
      return 'border-blue-200/80 dark:border-blue-400/25 bg-blue-50/80 dark:bg-blue-400/10 text-blue-700 dark:text-blue-300'
    case 'pending':
      return 'border-amber-200/80 dark:border-amber-400/25 bg-amber-50/80 dark:bg-amber-400/10 text-amber-700 dark:text-amber-300'
    case 'refunded':
      return 'border-red-200/80 dark:border-red-400/25 bg-red-50/80 dark:bg-red-500/10 text-red-600 dark:text-red-300'
    default:
      // canceled, unknown
      return 'border-blue-950/10 dark:border-white/15 bg-blue-950/[0.03] dark:bg-white/[0.04] text-blue-950/60 dark:text-white/60'
  }
})
</script>
