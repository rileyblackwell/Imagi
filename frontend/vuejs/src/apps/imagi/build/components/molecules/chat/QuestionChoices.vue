<!--
  QuestionChoices.vue — the one-tap answers (and sketch) on an agent's question.

  When the coordinator or a thread asks the user something with ask_user, it
  can offer a few short answers and a small SVG sketch of what it means. The
  sketch is model-written markup, so it is sanitized to plain SVG shapes and
  text before it is drawn. Typing an answer instead always still works; the
  choices are a shortcut, not the only way.
-->
<template>
  <div class="question-choices">
    <!-- eslint-disable-next-line vue/no-v-html -- sanitized to SVG shapes only -->
    <div v-if="safeVisual" class="question-visual" role="img" aria-label="Sketch for this question" v-html="safeVisual"></div>
    <div v-if="options.length" class="question-options" role="group" aria-label="Answers">
      <button
        v-for="option in options"
        :key="option"
        type="button"
        class="question-option iw-press"
        :class="{ 'question-option--picked': option === picked }"
        :disabled="disabled"
        @click="emit('pick', option)"
      >
        {{ option }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import DOMPurify from 'isomorphic-dompurify'

const props = withDefaults(
  defineProps<{
    options?: string[]
    visual?: string
    /** Answered already, or the agent is busy: show the choices, but inert */
    disabled?: boolean
    /** The option the user went with, when it is known */
    picked?: string
  }>(),
  { options: () => [], visual: '', disabled: false, picked: '' }
)

const emit = defineEmits<{ (e: 'pick', option: string): void }>()

/** Plain SVG only: no scripts, no event handlers, no links out, no embedded
 *  HTML or images. What is left is shapes and text, which is all a sketch of
 *  a choice needs. */
const safeVisual = computed(() => {
  const raw = (props.visual || '').trim()
  if (!raw.toLowerCase().startsWith('<svg')) return ''
  return DOMPurify.sanitize(raw, {
    USE_PROFILES: { svg: true, svgFilters: true },
    FORBID_TAGS: ['a', 'image', 'foreignObject', 'use', 'style', 'script'],
    FORBID_ATTR: ['href', 'xlink:href', 'style'],
  })
})
</script>

<style scoped>
.question-choices {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.question-visual {
  border-radius: var(--iw-r-md, 0.75rem);
  border: 1px solid rgba(19, 26, 44, 0.08);
  background: rgba(255, 255, 255, 0.7);
  padding: 0.5rem;
  color: rgba(19, 26, 44, 0.8);
  overflow: hidden;
}

.dark .question-visual {
  border-color: rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.04);
  color: rgba(255, 255, 255, 0.82);
}

.question-visual :deep(svg) {
  display: block;
  width: 100%;
  height: auto;
  max-height: 14rem;
}

.question-options {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
}

.question-option {
  padding: 0.3rem 0.75rem;
  border-radius: 9999px;
  border: 1px solid rgba(19, 26, 44, 0.16);
  background: rgba(255, 255, 255, 0.8);
  font-size: 0.75rem;
  font-weight: 600;
  color: rgba(19, 26, 44, 0.85);
  transition:
    background-color var(--iw-dur-2) var(--iw-ease-out),
    border-color var(--iw-dur-2) var(--iw-ease-out),
    color var(--iw-dur-2) var(--iw-ease-out);
}

.question-option:hover:not(:disabled) {
  background: theme('colors.blue.950');
  border-color: theme('colors.blue.950');
  color: #ffffff;
}

.question-option:focus-visible {
  outline: none;
  box-shadow: var(--iw-focus-ring);
}

.question-option:disabled {
  cursor: default;
  opacity: 0.55;
}

.question-option--picked,
.question-option--picked:disabled {
  opacity: 1;
  background: theme('colors.blue.950');
  border-color: theme('colors.blue.950');
  color: #ffffff;
}

.dark .question-option {
  border-color: rgba(255, 255, 255, 0.16);
  background: rgba(255, 255, 255, 0.04);
  color: rgba(255, 255, 255, 0.85);
}

.dark .question-option:hover:not(:disabled),
.dark .question-option--picked {
  background: #f3ede2;
  border-color: #f3ede2;
  color: theme('colors.blue.950');
}
</style>
