<!--
  OrderStatusBadge.vue - Maps Sell's order statuses onto the shared pill.

  The pill itself lives in shared/components/atoms/badges/StatusBadge.vue; this
  file only knows what an order status means.
-->
<template>
  <BaseStatusBadge :tone="tone" :label="status" :pulse="status === 'pending'" />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { StatusBadge as BaseStatusBadge } from '@/shared/components'
import type { StatusTone } from '@/shared/styles'

const props = defineProps<{
  status: string
}>()

const tone = computed<StatusTone>(() => {
  switch (props.status) {
    case 'paid':
      return 'success'
    case 'fulfilled':
      return 'info'
    case 'pending':
      return 'pending'
    case 'refunded':
      return 'danger'
    default:
      // canceled, unknown
      return 'neutral'
  }
})
</script>
