<!--
  ModelChoice.vue — the model, as a family toggle over one segmented choice.

  The workspace settings' model control: Anthropic or OpenAI on top, then
  that family's lineup faster → smarter, each with its tier under its name,
  the chosen one lifted. The toggle only changes which family is shown.
-->
<template>
  <div>
    <ChoiceSegments
      :options="FAMILIES"
      :model-value="family"
      :label="`${label} family`"
      @update:model-value="id => (family = id as Family)"
    />
    <ChoiceSegments
      class="mt-2"
      :options="models"
      :model-value="modelValue"
      :label="label"
      @update:model-value="id => emit('update:modelValue', id)"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useAgentStore } from '../../../stores/agentStore'
import { AI_MODELS, modelProvider } from '../../../types/services'
import ChoiceSegments from './ChoiceSegments.vue'

const props = defineProps<{
  modelValue: string | null
  /** The group's accessible name */
  label: string
}>()

const emit = defineEmits<{ (e: 'update:modelValue', id: string): void }>()

const store = useAgentStore()

type Family = 'anthropic' | 'openai'
const FAMILIES = [
  { id: 'anthropic', name: 'Anthropic' },
  { id: 'openai', name: 'OpenAI' },
]
// Opens on the family of the model in use, and follows it when it changes.
const family = ref<Family>(modelProvider(props.modelValue))
watch(() => props.modelValue, id => { family.value = modelProvider(id) })

// Faster → smarter within each family, the order the composer's model menu uses.
const RANK: Record<string, number> = {
  'claude-haiku-5-5': 0,
  'claude-sonnet-5-5': 1,
  'claude-opus-5-5': 2,
  'claude-fable-5-1': 3,
  'gpt-6-luna': 10,
  'gpt-6.1-terra': 11,
  'gpt-6.1-sol': 12,
  'gpt-6-astra': 13,
}
const TIERS: Record<string, string> = {
  'claude-haiku-5-5': 'Fast',
  'claude-sonnet-5-5': 'Quick',
  'claude-opus-5-5': 'Balanced',
  'claude-fable-5-1': 'Frontier',
  'gpt-6-luna': 'Fast',
  'gpt-6.1-terra': 'Quick',
  'gpt-6.1-sol': 'Balanced',
  'gpt-6-astra': 'Frontier',
}

/** "Haiku 5.5", "Sol", "Fable 5.1": the name without its family prefix. */
function shortName(name: string): string {
  return name.replace(/^(?:GPT\s*\d+(?:\.\d+)?|Claude)\s*/i, '').trim() || name
}

const models = computed(() => {
  const lineup = store.availableModels.length > 0 ? store.availableModels : AI_MODELS
  return [...lineup]
    .filter(m => m.id in RANK && modelProvider(m.id) === family.value)
    .sort((a, b) => RANK[a.id]! - RANK[b.id]!)
    .map(m => ({ id: m.id, name: shortName(m.name), sub: TIERS[m.id] ?? '' }))
})
</script>
