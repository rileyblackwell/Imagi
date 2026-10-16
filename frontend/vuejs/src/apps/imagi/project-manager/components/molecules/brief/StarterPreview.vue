<!--
  StarterPreview.vue — a small home page of the founder's app, drawn in a
  starter style and colour scheme (utils/projectBrief.ts).

  It is laid out at a fixed 760 × 480 and scaled to its box, so the same
  drawing serves as a style tile's thumbnail and as the large preview under
  step 4. The colours are the founder's app colours, not Imagi's, which is why
  they are inline values rather than Spotlight tokens.
-->
<template>
  <div class="frame" :class="{ 'frame--tile': tile }" role="img" :aria-label="label">
    <div v-if="!tile" class="chrome" aria-hidden="true"><i></i><i></i><i></i><span>/</span></div>
    <div ref="holder" class="holder">
      <div class="pv" :data-style="style.id" :style="vars" aria-hidden="true">
        <div class="pv-nav">
          <span class="pv-brand">{{ name }}</span>
          <span class="pv-links"><span>Features</span><span>Pricing</span><span>About</span></span>
          <span class="pv-btn pv-btn--sm">Sign up</span>
        </div>
        <div class="pv-hero" :class="{ 'pv-hero--center': look.hero === 'center' }">
          <template v-if="style.id === 'playful'">
            <span class="pv-blob" style="width: 120px; height: 120px; left: -30px; top: 30px; background: var(--a-blob-1)"></span>
            <span class="pv-blob" style="width: 70px; height: 70px; right: 60px; top: 20px; background: var(--a-blob-2)"></span>
            <span class="pv-blob" style="width: 44px; height: 44px; right: 150px; bottom: 30px; background: var(--a-blob-3)"></span>
          </template>
          <div class="pv-copy">
            <span v-if="look.eyebrow" class="pv-eyebrow">{{ look.eyebrow }}</span>
            <p class="pv-title">{{ name }}</p>
            <p class="pv-text">{{ text }}</p>
            <div class="pv-ctas"><span class="pv-btn">Get started</span><span class="pv-btn pv-btn--ghost">Learn more</span></div>
          </div>
          <div v-if="look.hero === 'left'" class="pv-art">
            <div class="pv-art__head"><b></b><i></i></div>
            <div class="pv-bars"><i v-for="h in BARS" :key="h" :style="{ height: `${h}%` }"></i></div>
          </div>
        </div>
        <div class="pv-cards">
          <div v-for="t in CARDS" :key="t" class="pv-card"><i class="pv-ico"></i><b>{{ t }}</b><span></span><span></span></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { STYLES, inkOn, luminance, type ColourScheme, type DesignStyle } from '../../../utils/projectBrief'

const props = defineProps<{
  styleId: string | null
  scheme: ColourScheme | null
  appName?: string
  appText?: string
  /** A thumbnail: no browser bar, no outer shadow. */
  tile?: boolean
}>()

const BARS = [46, 70, 58, 88, 64, 96, 78]
const CARDS = ['Get set up fast', 'Made for you', 'Works anywhere']

// Used before anything is picked: a quiet grey app in the plainest style.
const NEUTRAL: ColourScheme = {
  id: 'neutral', label: 'Neutral', background: '#F6F6F7', surface: '#FFFFFF', text: '#18181B', primary: '#3F3F46', accent: '#A1A1AA',
}

const style = computed<DesignStyle>(() => STYLES.find((s) => s.id === props.styleId) ?? STYLES[0]!)
const look = computed(() => style.value.preview)
const colours = computed(() => props.scheme ?? NEUTRAL)
const name = computed(() => props.appName || 'Your app')
const text = computed(() => props.appText || 'What your app is shows up here.')
const label = computed(() => `${name.value} in the ${style.value.label} style${props.scheme ? ` with ${props.scheme.label} colours` : ''}`)

const vars = computed(() => {
  const c = colours.value
  const p = look.value
  const dark = Boolean(c.dark)
  const line = `1px solid color-mix(in srgb, ${c.text} 11%, transparent)`
  const shadow = dark
    ? '0 10px 30px -14px rgba(0, 0, 0, 0.7)'
    : '0 1px 2px rgba(0, 0, 0, 0.04), 0 12px 28px -16px rgba(0, 0, 0, 0.22)'
  const raised = p.card === 'shadow' || p.card === 'fill'
  // A pale accent disappears as text on a light page, so the primary stands in.
  const accentInk = luminance(c.accent) > 0.45 && !dark ? c.primary : c.accent
  const brandInk = style.value.id === 'bold' || style.value.id === 'colourful' || c.primary === c.text ? c.text : c.primary
  return {
    '--a-bg': c.background,
    '--a-surface': p.card === 'none' ? 'transparent' : c.surface,
    '--a-text': c.text,
    '--a-muted': `color-mix(in srgb, ${c.text} 62%, ${c.background})`,
    '--a-primary': c.primary,
    '--a-accent': c.accent,
    '--a-on': inkOn(c.primary),
    '--a-brand': brandInk,
    '--a-accent-ink': accentInk,
    '--a-head': p.head,
    '--a-body': p.body,
    '--a-weight': String(p.weight),
    '--a-tracking': p.tracking,
    '--a-radius': `${p.radius}px`,
    '--a-button-radius': `${p.buttonRadius}px`,
    '--a-title': `${p.titleSize}px`,
    '--a-card-border': p.card === 'line' ? line : '0',
    '--a-card-shadow': p.card === 'shadow' ? shadow : 'none',
    '--a-art-border': raised ? '0' : line,
    '--a-art-shadow': raised ? shadow : 'none',
    '--a-blob-1': `color-mix(in srgb, ${c.accent} 45%, transparent)`,
    '--a-blob-2': `color-mix(in srgb, ${c.primary} 30%, transparent)`,
    '--a-blob-3': `color-mix(in srgb, ${c.accent} 60%, transparent)`,
    '--k': String(scale.value),
  }
})

// Scale the 760px drawing to whatever width the box has.
const holder = ref<HTMLElement | null>(null)
const scale = ref(1)
let observer: ResizeObserver | null = null
onMounted(() => {
  if (!holder.value) return
  scale.value = holder.value.clientWidth / 760 || 1
  if (typeof ResizeObserver === 'undefined') return
  observer = new ResizeObserver((entries) => {
    const width = entries[0]?.contentRect.width
    if (width) scale.value = width / 760
  })
  observer.observe(holder.value)
})
onBeforeUnmount(() => observer?.disconnect())
</script>

<style scoped>
.frame {
  overflow: hidden;
  width: 100%;
  border: 1px solid var(--sl-line-strong);
  border-radius: 0.9rem;
  background: var(--sl-surface);
  box-shadow: var(--sl-card-shadow);
}

.frame--tile {
  border: 0;
  border-radius: 0.55rem;
  box-shadow: 0 0 0 1px var(--sl-line);
}

.chrome {
  display: flex;
  align-items: center;
  gap: 6px;
  height: 26px;
  padding: 0 12px;
  border-bottom: 1px solid var(--sl-line);
  background: var(--sl-chrome-bg);
}

.chrome i {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: var(--sl-chrome-dot);
}

.chrome span {
  margin-left: 10px;
  font-size: 11px;
  color: var(--sl-faint);
}

.holder {
  position: relative;
  width: 100%;
  aspect-ratio: 760 / 480;
  overflow: hidden;
}

/* The app's home page, laid out at 760 × 480 and scaled to fit */
.pv {
  position: absolute;
  top: 0;
  left: 0;
  width: 760px;
  height: 480px;
  overflow: hidden;
  transform: scale(var(--k));
  transform-origin: 0 0;
  background: var(--a-bg);
  color: var(--a-text);
  font-family: var(--a-body);
  text-align: left;
  transition: background 0.3s ease;
}

.pv-nav {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 22px;
  padding: 18px 34px;
  border-bottom: 1px solid color-mix(in srgb, var(--a-text) 9%, transparent);
}

.pv-brand {
  max-width: 260px;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  font-family: var(--a-head);
  font-size: 18px;
  font-weight: var(--a-weight);
  letter-spacing: var(--a-tracking);
  color: var(--a-brand);
}

.pv-links {
  display: flex;
  gap: 20px;
  margin-left: auto;
  font-size: 13px;
  color: var(--a-muted);
}

.pv-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 11px 20px;
  border-radius: var(--a-button-radius);
  background: var(--a-primary);
  color: var(--a-on);
  font-family: var(--a-body);
  font-size: 14px;
  font-weight: 700;
  white-space: nowrap;
}

.pv-btn--sm {
  padding: 8px 15px;
  font-size: 12.5px;
}

.pv-btn--ghost {
  background: transparent;
  color: var(--a-text);
  box-shadow: inset 0 0 0 1.5px color-mix(in srgb, var(--a-text) 22%, transparent);
}

.pv-hero {
  position: relative;
  display: grid;
  grid-template-columns: 1.15fr 1fr;
  gap: 30px;
  align-items: center;
  height: 236px;
  padding: 30px 34px 24px;
}

.pv-hero--center {
  grid-template-columns: 1fr;
  justify-items: center;
  text-align: center;
}

.pv-copy {
  position: relative;
  z-index: 2;
  min-width: 0;
}

.pv-eyebrow {
  display: inline-block;
  margin-bottom: 12px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--a-accent-ink);
}

.pv-title {
  display: -webkit-box;
  overflow: hidden;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  font-family: var(--a-head);
  font-size: var(--a-title);
  font-weight: var(--a-weight);
  line-height: 1.02;
  letter-spacing: var(--a-tracking);
  text-wrap: balance;
}

.pv-text {
  display: -webkit-box;
  overflow: hidden;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  max-width: 40ch;
  margin-top: 14px;
  font-size: 14.5px;
  line-height: 1.55;
  color: var(--a-muted);
}

.pv-hero--center .pv-text {
  margin-inline: auto;
}

.pv-ctas {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.pv-hero--center .pv-ctas {
  justify-content: center;
}

.pv-art {
  position: relative;
  z-index: 2;
  display: grid;
  grid-template-rows: auto 1fr;
  gap: 14px;
  height: 180px;
  padding: 18px;
  border: var(--a-art-border);
  border-radius: var(--a-radius);
  background: var(--a-surface);
  box-shadow: var(--a-art-shadow);
}

.pv-art__head {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pv-art__head b {
  width: 34%;
  height: 9px;
  border-radius: 9px;
  background: color-mix(in srgb, var(--a-text) 18%, transparent);
}

.pv-art__head i {
  width: 40px;
  height: 18px;
  margin-left: auto;
  border-radius: var(--a-button-radius);
  background: color-mix(in srgb, var(--a-accent) 35%, transparent);
}

.pv-bars {
  display: flex;
  align-items: flex-end;
  gap: 10px;
}

.pv-bars i {
  flex: 1;
  border-radius: calc(var(--a-radius) / 2) calc(var(--a-radius) / 2) 2px 2px;
  background: var(--a-primary);
}

.pv-bars i:nth-child(even) {
  background: var(--a-accent);
}

.pv-cards {
  position: relative;
  z-index: 2;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  padding: 0 34px;
}

.pv-card {
  display: grid;
  gap: 9px;
  padding: 16px;
  border: var(--a-card-border);
  border-radius: var(--a-radius);
  background: var(--a-surface);
  box-shadow: var(--a-card-shadow);
}

.pv-card b {
  font-family: var(--a-head);
  font-size: 15px;
  font-weight: var(--a-weight);
  letter-spacing: var(--a-tracking);
}

.pv-card span {
  display: block;
  height: 7px;
  border-radius: 7px;
  background: color-mix(in srgb, var(--a-text) 12%, transparent);
}

.pv-card span + span {
  width: 70%;
}

.pv-ico {
  width: 28px;
  height: 28px;
  border-radius: calc(var(--a-radius) * 0.6);
  background: color-mix(in srgb, var(--a-accent) 32%, transparent);
}

.pv-blob {
  position: absolute;
  z-index: 1;
  border-radius: 999px;
}

/* What each style adds beyond fonts and corners */
.pv[data-style='minimal'] .pv-nav {
  border-bottom-color: transparent;
}

.pv[data-style='minimal'] .pv-card {
  padding: 14px 0 0;
  border-top: 1px solid color-mix(in srgb, var(--a-text) 15%, transparent);
}

.pv[data-style='bold'] .pv-card:first-child {
  background: var(--a-primary);
  color: var(--a-on);
}

.pv[data-style='bold'] .pv-card:first-child span,
.pv[data-style='bold'] .pv-card:first-child .pv-ico {
  background: color-mix(in srgb, var(--a-on) 28%, transparent);
}

.pv[data-style='elegant'] .pv-eyebrow {
  font-weight: 500;
  letter-spacing: 0.32em;
}

.pv[data-style='elegant'] .pv-btn {
  font-size: 11.5px;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.pv[data-style='playful'] .pv-card:nth-child(1) {
  background: color-mix(in srgb, var(--a-primary) 16%, var(--a-surface));
}

.pv[data-style='playful'] .pv-card:nth-child(2) {
  background: color-mix(in srgb, var(--a-accent) 24%, var(--a-surface));
  transform: rotate(-1.5deg);
}

.pv[data-style='playful'] .pv-card:nth-child(3) {
  background: color-mix(in srgb, var(--a-accent) 14%, var(--a-surface));
  transform: rotate(1.2deg);
}

.pv[data-style='colourful'] .pv-hero {
  height: 226px;
  margin: 12px 18px 0;
  border-radius: var(--a-radius);
  background: linear-gradient(120deg, var(--a-primary), color-mix(in srgb, var(--a-accent) 85%, var(--a-primary)));
  color: var(--a-on);
}

.pv[data-style='colourful'] .pv-text {
  color: color-mix(in srgb, var(--a-on) 80%, transparent);
}

.pv[data-style='colourful'] .pv-hero .pv-btn {
  background: var(--a-on);
  color: var(--a-primary);
}

.pv[data-style='colourful'] .pv-hero .pv-btn--ghost {
  background: transparent;
  color: var(--a-on);
  box-shadow: inset 0 0 0 1.5px color-mix(in srgb, var(--a-on) 55%, transparent);
}

.pv[data-style='colourful'] .pv-cards {
  margin-top: 14px;
}

.pv[data-style='retro'] .pv-nav {
  border-bottom: 2px solid var(--a-text);
}

.pv[data-style='retro'] .pv-card,
.pv[data-style='retro'] .pv-art {
  border: 2px solid var(--a-text);
  box-shadow: 4px 4px 0 var(--a-text);
}

.pv[data-style='retro'] .pv-btn {
  border: 2px solid var(--a-text);
  box-shadow: 3px 3px 0 var(--a-text);
}

.pv[data-style='retro'] .pv-btn--ghost {
  background: var(--a-surface);
}

.pv[data-style='techy'] {
  background-image:
    linear-gradient(color-mix(in srgb, var(--a-text) 5%, transparent) 1px, transparent 1px),
    linear-gradient(90deg, color-mix(in srgb, var(--a-text) 5%, transparent) 1px, transparent 1px);
  background-size: 28px 28px;
}

.pv[data-style='techy'] .pv-eyebrow {
  font-family: 'JetBrains Mono', ui-monospace, monospace;
  letter-spacing: 0.04em;
  text-transform: none;
}

.pv[data-style='techy'] .pv-eyebrow::before {
  content: '● ';
}

@media (prefers-reduced-motion: reduce) {
  .pv {
    transition: none;
  }
}
</style>
