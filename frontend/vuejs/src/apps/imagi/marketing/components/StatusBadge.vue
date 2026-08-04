<!--
  StatusBadge.vue - Maps Market's status vocabulary onto the shared pill.

  The pill itself — shape, tone colours, the in-progress dot — lives in
  shared/components/atoms/badges/StatusBadge.vue. All this file knows is which
  Twilio and ad-platform statuses mean "went well" and which mean "failed".
-->
<template>
  <BaseStatusBadge :tone="tone" :label="label" :pulse="pulse" />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { StatusBadge as BaseStatusBadge } from '@/shared/components'
import type { StatusTone } from '@/shared/styles'

const props = defineProps<{
  status: string
}>()

// Campaign/consent statuses, raw Twilio message/call statuses, and normalized
// ad campaign statuses, by tone.
const SUCCESS = new Set(['sent', 'delivered', 'read', 'completed', 'received', 'subscribed', 'active'])
const DANGER = new Set(['failed', 'undelivered', 'busy', 'no-answer'])
const INFO = new Set(['scheduled', 'accepted'])
const PENDING = new Set(['sending', 'queued', 'initiated', 'ringing', 'in-progress', 'paused'])

const pulse = computed(() => props.status === 'sending' || props.status === 'in-progress')

const label = computed(() => props.status.replace(/-/g, ' '))

const tone = computed<StatusTone>(() => {
  const status = props.status
  if (SUCCESS.has(status)) return 'success'
  if (DANGER.has(status)) return 'danger'
  if (INFO.has(status)) return 'info'
  if (PENDING.has(status)) return 'pending'
  // draft, canceled, unknown
  return 'neutral'
})
</script>
