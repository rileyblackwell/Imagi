<template>
  <i :class="iconClass" :style="iconStyle" />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { PropType } from 'vue'

const props = defineProps({
  name: { type: String, required: true },
  color: { type: String, default: 'currentColor' },
  size: { type: [String, Number], default: 20 },
  class: { type: String, default: '' }
})

const iconClass = computed(() => [props.name, props.class])
const iconStyle = computed(() => ({
  color: props.color,
  fontSize: typeof props.size === 'number' ? props.size + 'px' : props.size
}))
</script>
