<!--
  StarterDesign.vue — step 03 of the create page: the app's first design
  system, as two choices.

  Style is a grid of tiles, each a small picture of the founder's own app in
  that style (StarterPreview), so nobody has to imagine what "Elegant" means.
  Colours are one row of dots, two of them dark schemes, plus the founder's
  own brand colour. Fonts, corners and light or dark come with the picks. A
  large preview below follows both (unless the page shows its own, as the
  create page's pinned Studio preview does, with hide-preview), and a quiet
  "Add a note" opens a box for
  anything the presets don't cover. Each pick is undone by tapping it again,
  and "let Imagi choose" (in the step's hint, see Projects.vue) clears them.

  The parent turns the value into text for the build with
  composeDesignPreferences (utils/projectBrief.ts).
-->
<template>
  <div class="design grid gap-[1.5rem]" :class="{ 'design--compact': compact }">
    <div class="m-0 grid min-w-0 gap-[0.65rem]">
      <p id="design-style-label" :class="LABEL">
        Style
        <span v-if="selectedStyle" :class="LABEL_NOTE">{{ selectedStyle.line }}</span>
      </p>
      <!-- Style tiles: three across, two on a phone. In a narrow column the
           tiles keep their names; the picked style's line still shows beside
           the Style label. -->
      <div
        class="grid grid-cols-3 max-[560px]:grid-cols-2"
        :class="compact ? 'gap-[0.6rem]' : 'gap-[0.75rem]'"
        role="radiogroup"
        aria-labelledby="design-style-label"
      >
        <button
          v-for="style in STYLES"
          :key="style.id"
          type="button"
          role="radio"
          class="tile grid gap-[0.45rem] rounded-[0.9rem] border bg-sl-surface px-[0.375rem] pb-[0.65rem] pt-[0.375rem] text-left
            [transition:border-color_0.2s_cubic-bezier(0.22,1,0.36,1),transform_0.2s_cubic-bezier(0.22,1,0.36,1),box-shadow_0.2s_ease]
            enabled:hover:-translate-y-px enabled:hover:border-sl-line-strong disabled:cursor-not-allowed disabled:opacity-50 motion-reduce:[transition:none]"
          :class="modelValue.style === style.id
            ? 'border-transparent shadow-[0_0_0_2px_var(--sl-amber),0_10px_30px_-14px_var(--sl-glow)]'
            : 'border-sl-line'"
          :aria-checked="modelValue.style === style.id"
          :disabled="disabled"
          @click="toggle('style', style.id)"
        >
          <StarterPreview
            tile
            :style-id="style.id"
            :scheme="scheme"
            :app-name="appName"
            :app-text="previewText"
          />
          <span class="tile__name px-[0.25rem] text-[0.85rem] font-semibold text-sl-text">{{ style.label }}</span>
          <span class="-mt-[0.3rem] px-[0.25rem] text-[0.75rem] leading-[1.35] text-sl-muted" :class="compact && 'hidden'">{{ style.line }}</span>
        </button>
      </div>
    </div>

    <div class="m-0 grid min-w-0 gap-[0.65rem]">
      <p id="design-colour-label" :class="LABEL">
        Colours
        <span v-if="compact && selectedScheme" :class="LABEL_NOTE">{{ selectedScheme.label }}</span>
      </p>
      <!-- Colour dots -->
      <div
        class="flex flex-wrap"
        :class="compact ? 'gap-[0.5rem]' : 'gap-x-[0.6rem] gap-y-[0.9rem]'"
        role="radiogroup"
        aria-labelledby="design-colour-label"
      >
        <button
          v-for="option in schemeOptions"
          :key="option.id"
          type="button"
          role="radio"
          class="swatch group/swatch grid justify-items-center gap-[0.45rem] p-0 [border:0] text-center text-[0.75rem] leading-[1.25]
            focus-visible:rounded-[0.5rem] disabled:cursor-not-allowed disabled:opacity-50"
          :class="[
            compact ? 'w-auto' : 'w-[3.6rem]',
            modelValue.scheme === option.id ? 'font-semibold text-sl-text' : 'text-sl-muted',
          ]"
          :aria-checked="modelValue.scheme === option.id"
          :title="option.dark ? `${option.label} (dark)` : option.label"
          :disabled="disabled"
          @click="toggle('scheme', option.id)"
        >
          <span
            v-if="option.id === CUSTOM_SCHEME_ID && modelValue.scheme !== CUSTOM_SCHEME_ID"
            class="grid place-items-center border-[1.5px] border-dashed border-sl-line-strong"
            :class="[DOT, compact ? 'h-[2.15rem] w-[2.15rem]' : 'h-[2.5rem] w-[2.5rem]']"
            aria-hidden="true"
          >
            <svg class="h-[1rem] w-[1rem]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M12 5v14M5 12h14" /></svg>
          </span>
          <span
            v-else
            :class="[
              DOT,
              compact ? 'h-[2.15rem] w-[2.15rem]' : 'h-[2.5rem] w-[2.5rem]',
              modelValue.scheme === option.id
                ? 'shadow-[0_0_0_2px_var(--sl-bg),0_0_0_4px_var(--sl-amber)]'
                : 'shadow-[0_0_0_1px_var(--sl-line-strong)]',
            ]"
            :style="{ background: dotFill(option) }"
            aria-hidden="true"
          ></span>
          <span :class="{ 'sr-only': compact }">{{ option.label }}</span>
        </button>
      </div>
      <label v-if="isCustom" class="brand flex items-center gap-[0.75rem] text-[0.85rem] text-sl-muted">
        <input
          type="color"
          class="h-[2.25rem] w-[2.25rem] cursor-pointer rounded-[0.6rem] border border-sl-line-strong bg-transparent bg-none p-0
            [&::-webkit-color-swatch-wrapper]:p-[3px] [&::-webkit-color-swatch]:rounded-[0.4rem] [&::-webkit-color-swatch]:[border:0]"
          :value="modelValue.brandColor"
          :disabled="disabled"
          aria-label="Brand colour"
          @input="set('brandColor', ($event.target as HTMLInputElement).value)"
        >
        <span>Pick your brand colour and Imagi builds the scheme around it.</span>
      </label>
    </div>

    <figure v-if="!hidePreview && (modelValue.style || modelValue.scheme)" class="preview m-0 grid min-w-0 gap-[0.65rem]">
      <figcaption :class="LABEL">Your app</figcaption>
      <StarterPreview
        :style-id="modelValue.style"
        :scheme="scheme"
        :app-name="appName"
        :app-text="previewText"
      />
    </figure>
    <p v-else-if="!hidePreview" class="text-[0.85rem] text-sl-muted">Nothing picked yet. Imagi chooses a look that fits your app.</p>

    <div v-if="notesOpen" class="m-0 grid min-w-0 gap-[0.65rem]">
      <label :class="LABEL" for="project-design">Anything else about the look?</label>
      <textarea
        id="project-design"
        ref="notesField"
        :value="modelValue.notes"
        rows="2"
        class="field__input resize-none disabled:opacity-50 disabled:cursor-not-allowed"
        placeholder="Your logo’s colours, or a site whose look you like."
        :disabled="disabled"
        @input="set('notes', ($event.target as HTMLTextAreaElement).value)"
        @focus="$emit('focus')"
        @blur="$emit('blur')"
      ></textarea>
    </div>
    <div v-else>
      <!-- The quiet way to add words about the look -->
      <button
        type="button"
        class="note-btn inline-flex items-center gap-[0.5rem] rounded-[999px] border border-sl-line bg-sl-chip-bg px-[0.85rem] py-[0.45rem] text-[0.8125rem] text-sl-muted
          [transition:background_0.2s_ease,border-color_0.2s_ease,color_0.2s_ease] enabled:hover:border-sl-line-strong enabled:hover:bg-sl-chip-bg-hover enabled:hover:text-sl-text
          disabled:cursor-not-allowed disabled:opacity-50 motion-reduce:[transition:none]"
        :disabled="disabled"
        @click="openNotes"
      >
        <svg class="h-[0.95rem] w-[0.95rem]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 20h4L19 9l-4-4L4 16v4z" /></svg>
        Add a note about the look
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue'
import StarterPreview from './StarterPreview.vue'
import {
  STYLES,
  SCHEMES,
  CUSTOM_SCHEME_ID,
  customScheme,
  schemeFor,
  type ColourScheme,
  previewTextFor,
  type StarterDesign,
} from '../../../utils/projectBrief'

const props = defineProps<{
  modelValue: StarterDesign
  appName?: string
  /** What the app is (step 2), shown as the sample screen's intro text. */
  appDescription?: string
  disabled?: boolean
  /** The page shows the large preview itself, so leave it out here. */
  hidePreview?: boolean
  /** Narrow column: tiles show their names only, and the colour dots fit
   * one row with the picked scheme named beside the Colours label. */
  compact?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: StarterDesign): void
  (e: 'focus'): void
  (e: 'blur'): void
}>()

const LABEL = 'flex justify-between gap-[0.75rem] text-[0.72rem] font-semibold uppercase tracking-[0.16em] text-sl-muted'
const LABEL_NOTE = 'font-medium normal-case tracking-[0] text-sl-faint'
// A colour dot (or the dashed "your colour" plus): it lifts with its button.
const DOT = 'rounded-[999px] [transition:transform_0.2s_cubic-bezier(0.22,1,0.36,1),box-shadow_0.2s_ease] group-[:hover:not(:disabled)]/swatch:-translate-y-px motion-reduce:[transition:none]'

const set = <K extends keyof StarterDesign>(key: K, value: StarterDesign[K]) =>
  emit('update:modelValue', { ...props.modelValue, [key]: value })

// One tap to choose, one tap to undo, so "none" never needs its own button.
const toggle = (key: 'style' | 'scheme', id: string) =>
  set(key, props.modelValue[key] === id ? null : id)

const selectedStyle = computed(() => STYLES.find((s) => s.id === props.modelValue.style) ?? null)
const scheme = computed(() => schemeFor(props.modelValue))
const selectedScheme = computed(() => (props.modelValue.scheme ? scheme.value : null))
const isCustom = computed(() => props.modelValue.scheme === CUSTOM_SCHEME_ID)
const schemeOptions = computed<ColourScheme[]>(() => [...SCHEMES, customScheme(props.modelValue.brandColor)])

// A dot shows the scheme as primary, accent and background slices.
const dotFill = (s: ColourScheme) =>
  `conic-gradient(from 225deg, ${s.primary} 0 50%, ${s.accent} 50% 75%, ${s.background} 75% 100%)`

const previewText = computed(() => previewTextFor(props.appDescription))

// The note box stays folded until asked for, or while it holds a note.
const notesOpen = ref(Boolean(props.modelValue.notes.trim()))
const notesField = ref<HTMLTextAreaElement | null>(null)
const openNotes = async () => {
  notesOpen.value = true
  await nextTick()
  notesField.value?.focus()
}

// The styles' own fonts, loaded only on the page that shows them. Imagi's
// faces (Hanken, Instrument, Bricolage, Fraunces) are already on every page.
const FONTS_ID = 'starter-design-fonts'
const FONTS_HREF =
  'https://fonts.googleapis.com/css2?family=Nunito:wght@500..900&family=Fredoka:wght@500..700&family=DM+Serif+Display&family=Space+Mono:wght@400;700&family=Sora:wght@400..700&family=JetBrains+Mono:wght@500&display=swap'
onMounted(() => {
  if (typeof document === 'undefined' || document.getElementById(FONTS_ID)) return
  const link = document.createElement('link')
  link.id = FONTS_ID
  link.rel = 'stylesheet'
  link.href = FONTS_HREF
  document.head.appendChild(link)
})
</script>
