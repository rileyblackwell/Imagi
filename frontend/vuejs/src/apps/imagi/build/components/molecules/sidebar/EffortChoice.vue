<!--
  EffortChoice.vue — Low to Max, as one segmented choice.

  The workspace settings' effort control: the ladder faster → smarter, each
  rung's one-line description on hover.
-->
<template>
  <ChoiceSegments
    :options="efforts"
    :model-value="modelValue"
    :label="label"
    @update:model-value="id => emit('update:modelValue', id as ReasoningEffort)"
  />
</template>

<script setup lang="ts">
import { REASONING_EFFORTS, type ReasoningEffort } from '../../../types/services'
import ChoiceSegments from './ChoiceSegments.vue'

defineProps<{
  modelValue: ReasoningEffort | null
  /** The group's accessible name */
  label: string
}>()

const emit = defineEmits<{ (e: 'update:modelValue', id: ReasoningEffort): void }>()

const efforts = REASONING_EFFORTS.map(e => ({ id: e.id, name: e.name, title: e.description }))
</script>
