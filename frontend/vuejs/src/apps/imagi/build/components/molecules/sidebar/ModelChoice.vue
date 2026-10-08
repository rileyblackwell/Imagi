<!--
  ModelChoice.vue — Luna, Opus 5.5 or Astra, as one segmented choice.

  The workspace settings' model control: the lineup faster → smarter, each
  with its tier under its name, the chosen one lifted.
-->
<template>
  <div role="radiogroup" :aria-label="label" class="model-choice">
    <button
      v-for="m in models"
      :key="m.id"
      type="button"
      role="radio"
      :aria-checked="m.id === modelValue"
      class="model-choice__option iw-press"
      :class="{ 'model-choice__option--on': m.id === modelValue }"
      @click="m.id !== modelValue && emit('update:modelValue', m.id)"
    >
      <span class="model-choice__name">{{ m.short }}</span>
      <span class="model-choice__tier">{{ m.tier }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAgentStore } from '../../../stores/agentStore'
import { AI_MODELS } from '../../../types/services'

defineProps<{
  modelValue: string | null
  /** The group's accessible name */
  label: string
}>()

const emit = defineEmits<{ (e: 'update:modelValue', id: string): void }>()

const store = useAgentStore()

// Faster → smarter, the order the composer's model menu uses.
const RANK: Record<string, number> = { 'gpt-6-luna': 0, 'claude-opus-5-5': 1, 'gpt-6-astra': 2 }
const TIERS: Record<string, string> = {
  'gpt-6-luna': 'Fast',
  'claude-opus-5-5': 'Balanced',
  'gpt-6-astra': 'Frontier',
}

/** "Luna", "Opus 5.5", "Astra": the name without its family prefix. */
function shortName(name: string): string {
  return name.replace(/^(?:GPT\s*\d+(?:\.\d+)?|Claude)\s*/i, '').trim() || name
}

const models = computed(() => {
  const lineup = store.availableModels.length > 0 ? store.availableModels : AI_MODELS
  return [...lineup]
    .filter(m => m.id in RANK)
    .sort((a, b) => RANK[a.id]! - RANK[b.id]!)
    .map(m => ({ id: m.id, short: shortName(m.name), tier: TIERS[m.id] ?? '' }))
})
</script>

<style scoped>
.model-choice {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.25rem;
  padding: 0.25rem;
  border-radius: 0.875rem;
  background: rgba(19, 26, 44, 0.05);
}

.dark .model-choice {
  background: rgba(255, 255, 255, 0.05);
}

.model-choice__option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.0625rem;
  padding: 0.5rem 0.25rem;
  border-radius: 0.625rem;
  color: rgba(19, 26, 44, 0.65);
  transition:
    background-color var(--iw-dur-2) var(--iw-ease-out),
    color var(--iw-dur-2) var(--iw-ease-out),
    box-shadow var(--iw-dur-2) var(--iw-ease-out);
}

.model-choice__option:hover:not(.model-choice__option--on) {
  color: rgba(19, 26, 44, 0.9);
}

.model-choice__option--on {
  background: #ffffff;
  color: rgba(19, 26, 44, 0.95);
  box-shadow: 0 1px 2px rgba(19, 26, 44, 0.12), 0 0 0 1px rgba(19, 26, 44, 0.06);
}

.model-choice__option:focus-visible {
  outline: none;
  box-shadow: var(--iw-focus-ring);
}

.dark .model-choice__option {
  color: rgba(255, 255, 255, 0.6);
}

.dark .model-choice__option:hover:not(.model-choice__option--on) {
  color: rgba(255, 255, 255, 0.9);
}

.dark .model-choice__option--on {
  background: rgba(255, 255, 255, 0.12);
  color: #ffffff;
  box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.1);
}

.model-choice__name {
  font-size: 12px;
  font-weight: 600;
}

.model-choice__tier {
  font-size: 10px;
  opacity: 0.7;
}
</style>
