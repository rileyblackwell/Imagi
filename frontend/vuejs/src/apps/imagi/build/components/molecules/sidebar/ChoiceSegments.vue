<!--
  ChoiceSegments.vue — one segmented radio choice, the chosen option lifted.

  The workspace settings' control for a short, ordered list: each option's
  name with an optional line under it (ModelChoice puts the tier there).
-->
<template>
  <div
    role="radiogroup"
    :aria-label="label"
    class="grid gap-1 p-1 rounded-[0.875rem] bg-ink/5 dark:bg-white/5"
    :style="{ gridTemplateColumns: `repeat(${options.length}, minmax(0, 1fr))` }"
  >
    <!-- The chosen option is lifted onto a white chip. (Teleported with the
         settings panel to <body>, outside .spotlight.) -->
    <button
      v-for="o in options"
      :key="o.id"
      type="button"
      role="radio"
      :aria-checked="o.id === modelValue"
      :title="o.title"
      class="iw-press flex flex-col items-center justify-center gap-px py-2 px-1 rounded-[0.625rem]
        [transition:background-color_var(--iw-dur-2)_var(--iw-ease-out),color_var(--iw-dur-2)_var(--iw-ease-out),box-shadow_var(--iw-dur-2)_var(--iw-ease-out)]
        focus-visible:[outline:none] focus-visible:shadow-iw-focus"
      :class="o.id === modelValue
        ? 'bg-white text-ink/95 shadow-[0_1px_2px_rgba(19,26,44,0.12),0_0_0_1px_rgba(19,26,44,0.06)] dark:bg-white/[0.12] dark:text-white dark:shadow-[0_0_0_1px_rgba(255,255,255,0.1)]'
        : 'text-ink/65 hover:text-ink/90 dark:text-white/60 dark:hover:text-white/90'"
      @click="o.id !== modelValue && emit('update:modelValue', o.id)"
    >
      <span class="choice-segments__name text-[12px] font-semibold whitespace-nowrap">{{ o.name }}</span>
      <span v-if="o.sub" class="text-[10px] opacity-70">{{ o.sub }}</span>
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
