<!--
  ModelChoice.vue — Haiku, Sonnet, Opus or Fable, as one segmented choice.

  The workspace settings' model control: the lineup faster → smarter, each
  with its tier under its name, the chosen one lifted.
-->
<template>
  <ChoiceSegments
    :options="models"
    :model-value="modelValue"
    :label="label"
    @update:model-value="id => emit('update:modelValue', id)"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAgentStore } from '../../../stores/agentStore'
import { AI_MODELS } from '../../../types/services'
import ChoiceSegments from './ChoiceSegments.vue'

defineProps<{
  modelValue: string | null
  /** The group's accessible name */
  label: string
}>()

const emit = defineEmits<{ (e: 'update:modelValue', id: string): void }>()

const store = useAgentStore()

// Faster → smarter, the order the composer's model menu uses.
const RANK: Record<string, number> = {
  'claude-haiku-5-5': 0,
  'claude-sonnet-5-5': 1,
  'claude-opus-5-5': 2,
  'claude-fable-5-1': 3,
}
const TIERS: Record<string, string> = {
  'claude-haiku-5-5': 'Fast',
  'claude-sonnet-5-5': 'Quick',
  'claude-opus-5-5': 'Balanced',
  'claude-fable-5-1': 'Frontier',
}

/** "Haiku 5.5", "Opus 5.5", "Fable 5.1": the name without its family prefix. */
function shortName(name: string): string {
  return name.replace(/^(?:GPT\s*\d+(?:\.\d+)?|Claude)\s*/i, '').trim() || name
}

const models = computed(() => {
  const lineup = store.availableModels.length > 0 ? store.availableModels : AI_MODELS
  return [...lineup]
    .filter(m => m.id in RANK)
    .sort((a, b) => RANK[a.id]! - RANK[b.id]!)
    .map(m => ({ id: m.id, name: shortName(m.name), sub: TIERS[m.id] ?? '' }))
})
</script>
