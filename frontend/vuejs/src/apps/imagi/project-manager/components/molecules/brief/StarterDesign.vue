<!--
  StarterDesign.vue — step 4 of the projects page's brief: the app's first
  design system, as two choices.

  Style is a grid of tiles, each a small picture of the founder's own app in
  that style (StarterPreview), so nobody has to imagine what "Elegant" means.
  Colours are one row of dots, two of them dark schemes, plus the founder's
  own brand colour. Fonts, corners and light or dark come with the picks. A
  large preview below follows both, and a quiet "Add a note" opens a box for
  anything the presets don't cover. Each pick is undone by tapping it again,
  and "let Imagi choose" (in the step's hint, see Projects.vue) clears them.

  The parent turns the value into text for the build with
  composeDesignPreferences (utils/projectBrief.ts).
-->
<template>
  <div class="design">
    <div class="design__group">
      <p id="design-style-label" class="design__label">
        Style
        <span v-if="selectedStyle" class="design__label-note">{{ selectedStyle.line }}</span>
      </p>
      <div class="tiles" role="radiogroup" aria-labelledby="design-style-label">
        <button
          v-for="style in STYLES"
          :key="style.id"
          type="button"
          role="radio"
          class="tile"
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
          <span class="tile__name">{{ style.label }}</span>
          <span class="tile__line">{{ style.line }}</span>
        </button>
      </div>
    </div>

    <div class="design__group">
      <p id="design-colour-label" class="design__label">Colours</p>
      <div class="swatches" role="radiogroup" aria-labelledby="design-colour-label">
        <button
          v-for="option in schemeOptions"
          :key="option.id"
          type="button"
          role="radio"
          class="swatch"
          :aria-checked="modelValue.scheme === option.id"
          :title="option.dark ? `${option.label} (dark)` : option.label"
          :disabled="disabled"
          @click="toggle('scheme', option.id)"
        >
          <span
            v-if="option.id === CUSTOM_SCHEME_ID && modelValue.scheme !== CUSTOM_SCHEME_ID"
            class="swatch__plus"
            aria-hidden="true"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M12 5v14M5 12h14" /></svg>
          </span>
          <span v-else class="swatch__dot" :style="{ background: dotFill(option) }" aria-hidden="true"></span>
          <span class="swatch__name">{{ option.label }}</span>
        </button>
      </div>
      <label v-if="isCustom" class="brand">
        <input
          type="color"
          class="brand__picker"
          :value="modelValue.brandColor"
          :disabled="disabled"
          aria-label="Brand colour"
          @input="set('brandColor', ($event.target as HTMLInputElement).value)"
        >
        <span>Pick your brand colour and Imagi builds the scheme around it.</span>
      </label>
    </div>

    <figure v-if="modelValue.style || modelValue.scheme" class="design__group preview">
      <figcaption class="design__label">Your app</figcaption>
      <StarterPreview
        :style-id="modelValue.style"
        :scheme="scheme"
        :app-name="appName"
        :app-text="previewText"
      />
    </figure>
    <p v-else class="design__auto">Nothing picked yet. Imagi chooses a look that fits your app.</p>

    <div v-if="notesOpen" class="design__group">
      <label class="design__label" for="project-design">Anything else about the look?</label>
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
      <button type="button" class="note-btn" :disabled="disabled" @click="openNotes">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 20h4L19 9l-4-4L4 16v4z" /></svg>
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
  type StarterDesign,
} from '../../../utils/projectBrief'

const props = defineProps<{
  modelValue: StarterDesign
  appName?: string
  /** What the app is (step 2), shown as the sample screen's intro text. */
  appDescription?: string
  disabled?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: StarterDesign): void
  (e: 'focus'): void
  (e: 'blur'): void
}>()

const set = <K extends keyof StarterDesign>(key: K, value: StarterDesign[K]) =>
  emit('update:modelValue', { ...props.modelValue, [key]: value })

// One tap to choose, one tap to undo, so "none" never needs its own button.
const toggle = (key: 'style' | 'scheme', id: string) =>
  set(key, props.modelValue[key] === id ? null : id)

const selectedStyle = computed(() => STYLES.find((s) => s.id === props.modelValue.style) ?? null)
const scheme = computed(() => schemeFor(props.modelValue))
const isCustom = computed(() => props.modelValue.scheme === CUSTOM_SCHEME_ID)
const schemeOptions = computed<ColourScheme[]>(() => [...SCHEMES, customScheme(props.modelValue.brandColor)])

// A dot shows the scheme as primary, accent and background slices.
const dotFill = (s: ColourScheme) =>
  `conic-gradient(from 225deg, ${s.primary} 0 50%, ${s.accent} 50% 75%, ${s.background} 75% 100%)`

// The sample screen shows the founder's own words: the first sentence of what
// the app is, cut short so it stays a one-glance preview.
const PREVIEW_TEXT_MAX = 110
const previewText = computed(() => {
  const text = (props.appDescription ?? '').trim()
  if (!text) return ''
  const first = text.match(/^.*?[.!?](\s|$)/)?.[0].trim() ?? text
  return first.length > PREVIEW_TEXT_MAX ? `${first.slice(0, PREVIEW_TEXT_MAX - 1).trimEnd()}…` : first
})

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

<style scoped>
.design {
  display: grid;
  gap: 1.5rem;
}

.design__group {
  display: grid;
  gap: 0.65rem;
  min-width: 0;
  margin: 0;
}

.design__label {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--sl-muted);
}

.design__label-note {
  font-weight: 500;
  letter-spacing: 0;
  text-transform: none;
  color: var(--sl-faint);
}

.design__auto {
  font-size: 0.85rem;
  color: var(--sl-muted);
}

/* Style tiles: three across, two on a phone */
.tiles {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.75rem;
}

@media (max-width: 560px) {
  .tiles {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

.tile {
  display: grid;
  gap: 0.45rem;
  padding: 0.375rem 0.375rem 0.65rem;
  border: 1px solid var(--sl-line);
  border-radius: 0.9rem;
  background: var(--sl-surface);
  text-align: left;
  transition: border-color 0.2s cubic-bezier(0.22, 1, 0.36, 1), transform 0.2s cubic-bezier(0.22, 1, 0.36, 1), box-shadow 0.2s ease;
}

.tile:hover:not(:disabled) {
  border-color: var(--sl-line-strong);
  transform: translateY(-1px);
}

.tile[aria-checked='true'] {
  border-color: transparent;
  box-shadow: 0 0 0 2px var(--sl-amber), 0 10px 30px -14px var(--sl-glow);
}

.tile:focus-visible {
  outline: 2px solid var(--sl-focus);
  outline-offset: 3px;
}

.tile:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.tile__name {
  padding: 0 0.25rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--sl-text);
}

.tile__line {
  margin-top: -0.3rem;
  padding: 0 0.25rem;
  font-size: 0.75rem;
  line-height: 1.35;
  color: var(--sl-muted);
}

/* Colour dots */
.swatches {
  display: flex;
  flex-wrap: wrap;
  gap: 0.9rem 0.6rem;
}

.swatch {
  display: grid;
  justify-items: center;
  gap: 0.45rem;
  width: 3.6rem;
  padding: 0;
  border: 0;
  background: none;
  font-size: 0.75rem;
  line-height: 1.25;
  text-align: center;
  color: var(--sl-muted);
}

.swatch__dot,
.swatch__plus {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 999px;
  transition: transform 0.2s cubic-bezier(0.22, 1, 0.36, 1), box-shadow 0.2s ease;
}

.swatch__dot {
  box-shadow: 0 0 0 1px var(--sl-line-strong);
}

.swatch__plus {
  display: grid;
  place-items: center;
  border: 1.5px dashed var(--sl-line-strong);
}

.swatch__plus svg {
  width: 1rem;
  height: 1rem;
}

.swatch:hover:not(:disabled) .swatch__dot,
.swatch:hover:not(:disabled) .swatch__plus {
  transform: translateY(-1px);
}

.swatch[aria-checked='true'] {
  font-weight: 600;
  color: var(--sl-text);
}

.swatch[aria-checked='true'] .swatch__dot {
  box-shadow: 0 0 0 2px var(--sl-bg), 0 0 0 4px var(--sl-amber);
}

.swatch:focus-visible {
  outline: 2px solid var(--sl-focus);
  outline-offset: 3px;
  border-radius: 0.5rem;
}

.swatch:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.85rem;
  color: var(--sl-muted);
}

.brand__picker {
  width: 2.25rem;
  height: 2.25rem;
  padding: 0;
  border: 1px solid var(--sl-line-strong);
  border-radius: 0.6rem;
  background: none;
  cursor: pointer;
}

.brand__picker::-webkit-color-swatch-wrapper {
  padding: 3px;
}

.brand__picker::-webkit-color-swatch {
  border: 0;
  border-radius: 0.4rem;
}

/* The quiet way to add words about the look */
.note-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.45rem 0.85rem;
  border: 1px solid var(--sl-line);
  border-radius: 999px;
  background: var(--sl-chip-bg);
  font-size: 0.8125rem;
  color: var(--sl-muted);
  transition: background 0.2s ease, border-color 0.2s ease, color 0.2s ease;
}

.note-btn svg {
  width: 0.95rem;
  height: 0.95rem;
}

.note-btn:hover:not(:disabled) {
  border-color: var(--sl-line-strong);
  background: var(--sl-chip-bg-hover);
  color: var(--sl-text);
}

.note-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (prefers-reduced-motion: reduce) {
  .tile,
  .swatch__dot,
  .swatch__plus,
  .note-btn {
    transition: none;
  }
}
</style>
