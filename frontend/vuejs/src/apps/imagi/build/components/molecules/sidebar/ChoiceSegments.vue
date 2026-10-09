<!--
  ChoiceSegments.vue — one segmented radio choice, the chosen option lifted.

  The workspace settings' control for a short, ordered list: each option's
  name with an optional line under it (ModelChoice puts the tier there).
-->
<template>
  <div
    role="radiogroup"
    :aria-label="label"
    class="choice-segments"
    :style="{ gridTemplateColumns: `repeat(${options.length}, minmax(0, 1fr))` }"
  >
    <button
      v-for="o in options"
      :key="o.id"
      type="button"
      role="radio"
      :aria-checked="o.id === modelValue"
      :title="o.title"
      class="choice-segments__option iw-press"
      :class="{ 'choice-segments__option--on': o.id === modelValue }"
      @click="o.id !== modelValue && emit('update:modelValue', o.id)"
    >
      <span class="choice-segments__name">{{ o.name }}</span>
      <span v-if="o.sub" class="choice-segments__sub">{{ o.sub }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
export interface ChoiceSegment {
  id: string
  name: string
  /** A short line under the name */
  sub?: string
  /** Hover text */
  title?: string
}

defineProps<{
  options: ChoiceSegment[]
  modelValue: string | null
  /** The group's accessible name */
  label: string
}>()

const emit = defineEmits<{ (e: 'update:modelValue', id: string): void }>()
</script>

<style scoped>
.choice-segments {
  display: grid;
  gap: 0.25rem;
  padding: 0.25rem;
  border-radius: 0.875rem;
  background: rgba(19, 26, 44, 0.05);
}

.dark .choice-segments {
  background: rgba(255, 255, 255, 0.05);
}

.choice-segments__option {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.0625rem;
  padding: 0.5rem 0.25rem;
  border-radius: 0.625rem;
  color: rgba(19, 26, 44, 0.65);
  transition:
    background-color var(--iw-dur-2) var(--iw-ease-out),
    color var(--iw-dur-2) var(--iw-ease-out),
    box-shadow var(--iw-dur-2) var(--iw-ease-out);
}

.choice-segments__option:hover:not(.choice-segments__option--on) {
  color: rgba(19, 26, 44, 0.9);
}

.choice-segments__option--on {
  background: #ffffff;
  color: rgba(19, 26, 44, 0.95);
  box-shadow: 0 1px 2px rgba(19, 26, 44, 0.12), 0 0 0 1px rgba(19, 26, 44, 0.06);
}

.choice-segments__option:focus-visible {
  outline: none;
  box-shadow: var(--iw-focus-ring);
}

.dark .choice-segments__option {
  color: rgba(255, 255, 255, 0.6);
}

.dark .choice-segments__option:hover:not(.choice-segments__option--on) {
  color: rgba(255, 255, 255, 0.9);
}

.dark .choice-segments__option--on {
  background: rgba(255, 255, 255, 0.12);
  color: #ffffff;
  box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.1);
}

.choice-segments__name {
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.choice-segments__sub {
  font-size: 10px;
  opacity: 0.7;
}
</style>
