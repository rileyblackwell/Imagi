<!--
  QuestionChoices.vue — the one-tap answers (and sketch) on an agent's question.

  When the coordinator or a thread asks the user something with ask_user, it
  can offer a few short answers and a small SVG sketch of what it means. The
  sketch is model-written markup, so it is sanitized to plain SVG shapes and
  text before it is drawn. Typing an answer instead always still works; the
  choices are a shortcut, not the only way.
-->
<template>
  <div class="mt-2 flex flex-col gap-2">
    <!-- eslint-disable-next-line vue/no-v-html -- sanitized to SVG shapes only -->
    <div
      v-if="safeVisual"
      class="question-visual overflow-hidden rounded-iw-md border border-ink/[0.08] bg-white/70 p-2 text-ink/80
        dark:border-white/10 dark:bg-white/[0.04] dark:text-white/[0.82]
        [&_svg]:block [&_svg]:h-auto [&_svg]:max-h-56 [&_svg]:w-full"
      role="img"
      aria-label="Sketch for this question"
      v-html="safeVisual"
    ></div>
    <!-- Stacked rows, one answer each — the rail's list of choices. Hovering
         one warms it toward the amber of a question waiting; the one picked
         turns the green of something settled, with a check. -->
    <div v-if="options.length" class="flex flex-col gap-1.5" role="group" aria-label="Answers">
      <button
        v-for="option in options"
        :key="option"
        type="button"
        class="question-option iw-press flex w-full items-center gap-2 rounded-[0.625rem] border
          bg-sl-surface px-3 py-2 text-left text-[0.8125rem] text-sl-text
          ![transition:background-color_var(--iw-dur-2)_var(--iw-ease-out),border-color_var(--iw-dur-2)_var(--iw-ease-out),color_var(--iw-dur-2)_var(--iw-ease-out)]
          enabled:hover:border-[color:color-mix(in_srgb,var(--sl-wait)_55%,transparent)]
          enabled:hover:bg-[color:color-mix(in_srgb,var(--sl-wait)_8%,var(--sl-surface))]
          focus-visible:shadow-iw-focus focus-visible:![outline:none] disabled:cursor-default
          data-[picked]:before:font-black data-[picked]:before:text-[0.625rem] data-[picked]:before:text-sl-ok
          data-[picked]:before:content-['\f00c'] data-[picked]:before:[font-family:'Font_Awesome_6_Free']"
        :class="option === picked
          ? 'question-option--picked border-[color:color-mix(in_srgb,var(--sl-ok)_55%,transparent)] bg-[color:color-mix(in_srgb,var(--sl-ok)_12%,var(--sl-surface))] font-semibold'
          : 'border-sl-line-strong font-medium disabled:opacity-[0.45]'"
        :data-picked="option === picked || undefined"
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
