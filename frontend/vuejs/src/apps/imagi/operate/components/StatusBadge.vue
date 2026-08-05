<!--
  StatusBadge.vue - Maps Operate's status vocabulary onto the shared pill.

  The pill itself lives in shared/components/atoms/badges/StatusBadge.vue; this
  file only knows what an invoice or a task status means.
-->
<template>
  <BaseStatusBadge :tone="tone" :label="label" />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { StatusBadge as BaseStatusBadge } from '@/shared/components'
import type { StatusTone } from '@/shared/styles'

const props = defineProps<{
  status: string
}>()

// Invoice statuses (draft/sent/paid/void + derived overdue) and task
// statuses (todo/in_progress/done), by tone.
const SUCCESS = new Set(['paid', 'done'])
const DANGER = new Set(['overdue'])
const INFO = new Set(['sent'])
const PENDING = new Set(['in_progress'])

const label = computed(() => props.status.replace(/_/g, ' '))

const tone = computed<StatusTone>(() => {
  const status = props.status
  if (SUCCESS.has(status)) return 'success'
  if (DANGER.has(status)) return 'danger'
  if (INFO.has(status)) return 'info'
  if (PENDING.has(status)) return 'pending'
  // draft, todo, void, unknown
  return 'neutral'
})
</script>
