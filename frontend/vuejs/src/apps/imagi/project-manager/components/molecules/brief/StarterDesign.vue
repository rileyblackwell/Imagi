<!--
  StarterDesign.vue — step 4 of the projects page's brief: the app's first
  design system.

  Four one-tap choices (style, colours, fonts, light or dark), each optional
  and each undone by tapping it again, then a free-text box for anything the
  presets don't cover. A small preview underneath shows the choices applied
  to a sample screen, so a non-technical founder sees what "Forest, classic
  type" means before the build does. The colours in the preview are the
  founder's app colours, not Imagi's, which is why they are inline values
  rather than Spotlight tokens.

  The parent turns the value into text for the build with
  composeDesignPreferences (utils/projectBrief.ts).
-->
<template>
  <div class="design">
    <div class="design__group" role="group" aria-labelledby="design-style-label">
      <p id="design-style-label" class="design__label">Style</p>
      <div class="design__chips">
        <button
          v-for="style in STYLES"
          :key="style.id"
          type="button"
          class="chip"
          :class="{ 'is-on': modelValue.style === style.id }"
          :aria-pressed="modelValue.style === style.id"
          :disabled="disabled"
          @click="toggle('style', style.id)"
        >
          {{ style.label }}
        </button>
      </div>
    </div>

    <div class="design__group" role="group" aria-labelledby="design-colour-label">
      <p id="design-colour-label" class="design__label">Colours</p>
      <div class="design__chips">
        <button
          v-for="palette in PALETTES"
          :key="palette.id"
          type="button"
          class="chip chip--palette"
          :class="{ 'is-on': modelValue.palette === palette.id }"
          :aria-pressed="modelValue.palette === palette.id"
          :disabled="disabled"
          @click="toggle('palette', palette.id)"
        >
          <span class="swatches" aria-hidden="true">
            <span :style="{ background: palette.primary }"></span>
            <span :style="{ background: palette.accent }"></span>
            <span :style="{ background: palette.background }"></span>
          </span>
          {{ palette.label }}
        </button>
        <button
          type="button"
          class="chip chip--palette"
          :class="{ 'is-on': isCustom }"
          :aria-pressed="isCustom"
          :disabled="disabled"
          @click="toggle('palette', CUSTOM_PALETTE_ID)"
        >
          <span class="swatches" aria-hidden="true">
            <span :style="{ background: modelValue.brandColor }"></span>
          </span>
          My brand colour
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
        <span>Pick your brand colour and Imagi builds the palette around it.</span>
      </label>
    </div>

    <div class="design__row">
      <div class="design__group" role="group" aria-labelledby="design-font-label">
        <p id="design-font-label" class="design__label">Fonts</p>
        <div class="design__chips">
          <button
            v-for="font in FONTS"
            :key="font.id"
            type="button"
            class="chip chip--font"
            :class="{ 'is-on': modelValue.font === font.id }"
            :aria-pressed="modelValue.font === font.id"
            :disabled="disabled"
            @click="toggle('font', font.id)"
          >
            <span class="chip__sample" :style="{ fontFamily: font.sample }" aria-hidden="true">Aa</span>
            {{ font.label }}
          </button>
        </div>
      </div>

      <div class="design__group" role="group" aria-labelledby="design-theme-label">
        <p id="design-theme-label" class="design__label">Light or dark</p>
        <div class="design__chips">
          <button
            v-for="theme in THEMES"
            :key="theme.id"
            type="button"
            class="chip"
            :class="{ 'is-on': modelValue.theme === theme.id }"
            :aria-pressed="modelValue.theme === theme.id"
            :disabled="disabled"
            @click="toggle('theme', theme.id)"
          >
            {{ theme.label }}
          </button>
        </div>
      </div>
    </div>

    <!-- The choices on a sample screen -->
    <figure class="preview" aria-label="Preview of the starter design">
      <div class="preview__screen" :style="previewVars">
        <div class="preview__bar">
          <span class="preview__brand">{{ appName || 'Your app' }}</span>
          <span class="preview__links" aria-hidden="true"><i></i><i></i><i></i></span>
        </div>
        <div class="preview__body">
          <p class="preview__title">A headline for your home page</p>
          <p class="preview__text">Body text sits here, in the font your app will use.</p>
          <span class="preview__button">Get started</span>
          <span class="preview__accent" aria-hidden="true"></span>
        </div>
      </div>
      <figcaption class="preview__caption">
        {{ designIsSet(modelValue) ? 'A rough preview. The build refines it into the full design.' : 'Pick nothing and Imagi chooses a look that fits your app.' }}
      </figcaption>
    </figure>

    <div class="design__group">
      <label class="design__label" for="project-design">Anything else?</label>
      <textarea
        id="project-design"
        :value="modelValue.notes"
        rows="2"
        class="field__input resize-none disabled:opacity-50 disabled:cursor-not-allowed"
        placeholder="Your logo’s colours, a font you love, or a site whose look you like."
        :disabled="disabled"
        @input="set('notes', ($event.target as HTMLTextAreaElement).value)"
        @focus="$emit('focus')"
        @blur="$emit('blur')"
      ></textarea>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  STYLES,
  PALETTES,
  FONTS,
  THEMES,
  CUSTOM_PALETTE_ID,
  designIsSet,
  type StarterDesign,
} from '../../../utils/projectBrief'

const props = defineProps<{
  modelValue: StarterDesign
  appName?: string
  disabled?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: StarterDesign): void
  (e: 'focus'): void
  (e: 'blur'): void
}>()

type Choice = 'style' | 'palette' | 'font' | 'theme'

const set = <K extends keyof StarterDesign>(key: K, value: StarterDesign[K]) =>
  emit('update:modelValue', { ...props.modelValue, [key]: value })

// Each preset is one tap to choose and one tap to undo, so "none" never needs
// its own button.
const toggle = (key: Choice, id: string) =>
  set(key, props.modelValue[key] === id ? null : id)

const isCustom = computed(() => props.modelValue.palette === CUSTOM_PALETTE_ID)

// How each style shapes the sample: corners and heading weight.
const STYLE_SHAPE: Record<string, { radius: string; button: string; weight: number; tracking: string }> = {
  minimal: { radius: '6px', button: '6px', weight: 600, tracking: '-0.01em' },
  friendly: { radius: '14px', button: '999px', weight: 700, tracking: '-0.01em' },
  bold: { radius: '4px', button: '4px', weight: 800, tracking: '-0.03em' },
  premium: { radius: '2px', button: '2px', weight: 500, tracking: '0.01em' },
  playful: { radius: '18px', button: '999px', weight: 800, tracking: '0' },
  professional: { radius: '8px', button: '6px', weight: 650, tracking: '-0.005em' },
}
const DEFAULT_SHAPE = { radius: '10px', button: '8px', weight: 700, tracking: '-0.01em' }

const previewVars = computed(() => {
  const d = props.modelValue
  const palette = PALETTES.find(p => p.id === d.palette)
  const primary = isCustom.value ? d.brandColor : palette?.primary ?? '#3F3F46'
  const accent = isCustom.value
    ? `color-mix(in srgb, ${d.brandColor} 45%, #ffffff)`
    : palette?.accent ?? '#A1A1AA'
  const dark = d.theme === 'dark'
  const background = dark
    ? `color-mix(in srgb, ${primary} 12%, #0e0f13)`
    : palette?.background ?? '#F7F7F8'
  const shape = STYLE_SHAPE[d.style ?? ''] ?? DEFAULT_SHAPE
  const font = FONTS.find(f => f.id === d.font)?.sample ?? "ui-sans-serif, system-ui, sans-serif"
  return {
    '--p-primary': primary,
    '--p-accent': accent,
    '--p-bg': background,
    '--p-text': dark ? '#F4F4F5' : '#18181B',
    '--p-muted': dark ? 'rgba(244, 244, 245, 0.62)' : 'rgba(24, 24, 27, 0.6)',
    // On a dark screen the deep primary sinks into the background, so the
    // lighter accent carries the brand and the button instead.
    '--p-brand': dark ? accent : primary,
    '--p-button': dark ? accent : primary,
    '--p-on-button': dark ? '#0e0f13' : '#ffffff',
    '--p-radius': shape.radius,
    '--p-button-radius': shape.button,
    '--p-weight': String(shape.weight),
    '--p-tracking': shape.tracking,
    '--p-font': font,
  }
})
</script>

<style scoped>
.design {
  display: grid;
  gap: 1.25rem;
}

.design__row {
  display: grid;
  gap: 1.25rem;
}

@media (min-width: 640px) {
  .design__row {
    grid-template-columns: 1fr auto;
    align-items: start;
  }
}

.design__group {
  display: grid;
  gap: 0.55rem;
  min-width: 0;
}

.design__label {
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--sl-muted);
}

.design__chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

/* Same pill as the sentence starters on the steps above. */
.chip {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.35rem 0.8rem;
  border: 1px solid var(--sl-line);
  border-radius: 999px;
  background: var(--sl-chip-bg);
  font-size: 0.8125rem;
  color: var(--sl-muted);
  transition: background 0.18s ease, border-color 0.18s ease, color 0.18s ease;
}

.chip:hover:not(:disabled) {
  background: var(--sl-chip-bg-hover);
  border-color: var(--sl-line-strong);
  color: var(--sl-text);
}

.chip:focus-visible {
  outline: 2px solid var(--sl-focus);
  outline-offset: 2px;
}

.chip.is-on,
.chip.is-on:hover:not(:disabled) {
  border-color: transparent;
  background: var(--sl-grad);
  color: var(--sl-on-accent);
  font-weight: 600;
}

.chip:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.chip--palette {
  padding-left: 0.4rem;
}

.swatches {
  display: inline-flex;
}

.swatches span {
  width: 16px;
  height: 16px;
  border-radius: 999px;
  border: 1.5px solid var(--sl-surface);
  box-shadow: 0 0 0 1px var(--sl-line);
}

.swatches span + span {
  margin-left: -5px;
}

.chip__sample {
  font-size: 0.95rem;
  font-weight: 700;
  line-height: 1;
  color: var(--sl-text);
}

.chip.is-on .chip__sample {
  color: inherit;
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

/* The sample screen, drawn in the founder's colours. */
.preview {
  margin: 0;
}

.preview__screen {
  overflow: hidden;
  border: 1px solid var(--sl-line);
  border-radius: 0.9rem;
  background: var(--p-bg);
  font-family: var(--p-font);
  color: var(--p-text);
  transition: background 0.25s ease;
}

.preview__bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.65rem 1rem;
  border-bottom: 1px solid color-mix(in srgb, var(--p-text) 10%, transparent);
}

.preview__brand {
  font-size: 0.85rem;
  font-weight: var(--p-weight);
  letter-spacing: var(--p-tracking);
  color: var(--p-brand);
}

.preview__links {
  display: inline-flex;
  gap: 0.45rem;
}

.preview__links i {
  width: 1.6rem;
  height: 0.3rem;
  border-radius: 999px;
  background: color-mix(in srgb, var(--p-text) 18%, transparent);
}

.preview__body {
  position: relative;
  padding: 1.1rem 1rem 1.2rem;
}

@media (min-width: 480px) {
  .preview__body {
    padding-right: 6.5rem;
  }
}

.preview__title {
  max-width: 22ch;
  font-size: 1.2rem;
  line-height: 1.15;
  font-weight: var(--p-weight);
  letter-spacing: var(--p-tracking);
}

.preview__text {
  margin-top: 0.4rem;
  font-size: 0.8rem;
  color: var(--p-muted);
}

.preview__button {
  display: inline-block;
  margin-top: 0.85rem;
  padding: 0.45rem 0.95rem;
  border-radius: var(--p-button-radius);
  background: var(--p-button);
  color: var(--p-on-button);
  font-size: 0.78rem;
  font-weight: 600;
}

.preview__accent {
  position: absolute;
  right: 1rem;
  bottom: 1.2rem;
  width: 4.5rem;
  height: 4.5rem;
  border-radius: var(--p-radius);
  background: var(--p-accent);
  opacity: 0.85;
}

/* No room for the accent tile beside the text on a phone. */
@media (max-width: 479px) {
  .preview__accent {
    display: none;
  }
}

.preview__caption {
  margin-top: 0.5rem;
  font-size: 0.8rem;
  color: var(--sl-muted);
}

@media (prefers-reduced-motion: reduce) {
  .chip,
  .preview__screen {
    transition: none;
  }
}
</style>
