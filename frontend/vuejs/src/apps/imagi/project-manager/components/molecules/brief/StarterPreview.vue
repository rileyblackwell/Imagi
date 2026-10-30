<!--
  StarterPreview.vue — a small home page of the founder's app, drawn in a
  starter style and colour scheme (utils/projectBrief.ts).

  It is laid out at a fixed 760 × 480 and scaled to its box, so the same
  drawing serves as a style tile's thumbnail and as the large preview pinned
  beside the create page's steps. The colours are the founder's app colours, not Imagi's, which is why
  they are inline values rather than Spotlight tokens.
-->
<template>
  <div
    class="w-full overflow-hidden bg-sl-surface"
    :class="tile
      ? 'rounded-[0.55rem] [border:0] shadow-[0_0_0_1px_var(--sl-line)]'
      : 'rounded-[0.9rem] border border-sl-line-strong shadow-sl-card'"
    role="img"
    :aria-label="label"
  >
    <!-- A tile is a thumbnail: no browser bar, a hairline ring for an edge. -->
    <div v-if="!tile" class="flex h-[26px] items-center gap-[6px] border-b border-b-sl-line bg-sl-chrome-bg px-[12px]" aria-hidden="true">
      <i class="h-[8px] w-[8px] rounded-[999px] bg-sl-chrome-dot"></i>
      <i class="h-[8px] w-[8px] rounded-[999px] bg-sl-chrome-dot"></i>
      <i class="h-[8px] w-[8px] rounded-[999px] bg-sl-chrome-dot"></i>
      <span class="ml-[10px] text-[11px] text-sl-faint">/</span>
    </div>
    <div ref="holder" class="relative aspect-[760/480] w-full overflow-hidden">
      <!-- The app's home page, laid out at 760 × 480 and scaled to fit -->
      <div
        class="pv absolute left-0 top-0 h-[480px] w-[760px] overflow-hidden text-left text-[color:var(--a-text)] font-[family-name:var(--a-body)]
          [transform:scale(var(--k))] origin-[0_0] bg-[color:var(--a-bg)] [transition:background_0.3s_ease] motion-reduce:[transition:none]"
        :class="s === 'techy' && 'bg-[image:linear-gradient(color-mix(in_srgb,var(--a-text)_5%,transparent)_1px,transparent_1px),linear-gradient(90deg,color-mix(in_srgb,var(--a-text)_5%,transparent)_1px,transparent_1px)] bg-[length:28px_28px]'"
        :data-style="style.id"
        :style="vars"
        aria-hidden="true"
      >
        <div
          class="relative z-[2] flex items-center gap-[22px] px-[34px] py-[18px]"
          :class="s === 'retro'
            ? 'border-b-2 border-b-[color:var(--a-text)]'
            : s === 'minimal'
              ? 'border-b border-b-transparent'
              : 'border-b border-b-[color:color-mix(in_srgb,var(--a-text)_9%,transparent)]'"
        >
          <span class="pv-brand max-w-[260px] overflow-hidden text-ellipsis whitespace-nowrap font-[family-name:var(--a-head)] text-[18px] [font-weight:var(--a-weight)] tracking-[var(--a-tracking)] text-[color:var(--a-brand)]">{{ name }}</span>
          <span class="ml-auto flex gap-[20px] text-[13px] text-[color:var(--a-muted)]"><span>Features</span><span>Pricing</span><span>About</span></span>
          <span :class="btnClass(false, false, true)">Sign up</span>
        </div>
        <div
          class="relative grid items-center gap-[30px] px-[34px] pb-[24px] pt-[30px]"
          :class="[
            center ? 'grid-cols-[1fr] justify-items-center text-center' : 'grid-cols-[1.15fr_1fr]',
            s === 'colourful'
              ? 'mx-[18px] mb-0 mt-[12px] h-[226px] rounded-[var(--a-radius)] bg-[image:linear-gradient(120deg,var(--a-primary),color-mix(in_srgb,var(--a-accent)_85%,var(--a-primary)))] text-[color:var(--a-on)]'
              : 'h-[236px]',
          ]"
        >
          <template v-if="s === 'playful'">
            <span class="absolute z-[1] rounded-[999px]" style="width: 120px; height: 120px; left: -30px; top: 30px; background: var(--a-blob-1)"></span>
            <span class="absolute z-[1] rounded-[999px]" style="width: 70px; height: 70px; right: 60px; top: 20px; background: var(--a-blob-2)"></span>
            <span class="absolute z-[1] rounded-[999px]" style="width: 44px; height: 44px; right: 150px; bottom: 30px; background: var(--a-blob-3)"></span>
          </template>
          <div class="relative z-[2] min-w-0">
            <span
              v-if="look.eyebrow"
              class="mb-[12px] inline-block text-[11px] text-[color:var(--a-accent-ink)]"
              :class="eyebrowClass"
            >{{ look.eyebrow }}</span>
            <p class="pv-title line-clamp-2 text-balance font-[family-name:var(--a-head)] text-[length:var(--a-title)] [font-weight:var(--a-weight)] leading-[1.02] tracking-[var(--a-tracking)]">{{ name }}</p>
            <p
              class="pv-text mt-[14px] line-clamp-2 max-w-[40ch] text-[14.5px] leading-[1.55]"
              :class="[
                center && 'mx-auto',
                s === 'colourful' ? 'text-[color:color-mix(in_srgb,var(--a-on)_80%,transparent)]' : 'text-[color:var(--a-muted)]',
              ]"
            >{{ text }}</p>
            <div class="mt-[20px] flex gap-[10px]" :class="center && 'justify-center'">
              <span :class="btnClass(true, false, false)">Get started</span>
              <span :class="btnClass(true, true, false)">Learn more</span>
            </div>
          </div>
          <div
            v-if="look.hero === 'left'"
            class="relative z-[2] grid h-[180px] grid-rows-[auto_1fr] gap-[14px] rounded-[var(--a-radius)] bg-[color:var(--a-surface)] p-[18px]"
            :class="s === 'retro'
              ? '[border:2px_solid_var(--a-text)] [box-shadow:4px_4px_0_var(--a-text)]'
              : '[border:var(--a-art-border)] [box-shadow:var(--a-art-shadow)]'"
          >
            <div class="flex items-center gap-[8px]">
              <b class="h-[9px] w-[34%] rounded-[9px] bg-[color:color-mix(in_srgb,var(--a-text)_18%,transparent)]"></b>
              <i class="ml-auto h-[18px] w-[40px] rounded-[var(--a-button-radius)] bg-[color:color-mix(in_srgb,var(--a-accent)_35%,transparent)]"></i>
            </div>
            <div class="flex items-end gap-[10px]">
              <i
                v-for="h in BARS"
                :key="h"
                class="flex-1 rounded-[calc(var(--a-radius)/2)_calc(var(--a-radius)/2)_2px_2px] bg-[color:var(--a-primary)] even:bg-[color:var(--a-accent)]"
                :style="{ height: `${h}%` }"
              ></i>
            </div>
          </div>
        </div>
        <div
          class="relative z-[2] grid grid-cols-[repeat(3,1fr)] gap-[16px] px-[34px]"
          :class="s === 'colourful' && 'mt-[14px]'"
        >
          <div v-for="(t, i) in CARDS" :key="t" :class="cardClass(i)">
            <i
              class="h-[28px] w-[28px] rounded-[calc(var(--a-radius)*0.6)]"
              :class="s === 'bold' && i === 0
                ? 'bg-[color:color-mix(in_srgb,var(--a-on)_28%,transparent)]'
                : 'bg-[color:color-mix(in_srgb,var(--a-accent)_32%,transparent)]'"
            ></i>
            <b class="font-[family-name:var(--a-head)] text-[15px] [font-weight:var(--a-weight)] tracking-[var(--a-tracking)]">{{ t }}</b>
            <span class="block h-[7px] rounded-[7px]" :class="cardLine(i)"></span>
            <span class="block h-[7px] w-[70%] rounded-[7px]" :class="cardLine(i)"></span>
          </div>
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
const s = computed(() => style.value.id)
const center = computed(() => look.value.hero === 'center')
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

// What each style adds beyond fonts and corners, as utility classes: a
// button (nav or hero, solid or ghost), a feature card, and a card's lines.
const btnClass = (inHero: boolean, ghost: boolean, small: boolean) => [
  'inline-flex items-center justify-center whitespace-nowrap rounded-[var(--a-button-radius)] font-[family-name:var(--a-body)]',
  small ? 'px-[15px] py-[8px]' : 'px-[20px] py-[11px]',
  s.value === 'elegant'
    ? 'text-[11.5px] font-semibold uppercase tracking-[0.1em]'
    : small ? 'text-[12.5px] font-bold' : 'text-[14px] font-bold',
  s.value === 'retro'
    ? ghost
      ? '[border:2px_solid_var(--a-text)] [box-shadow:3px_3px_0_var(--a-text)] bg-[color:var(--a-surface)] text-[color:var(--a-text)]'
      : '[border:2px_solid_var(--a-text)] [box-shadow:3px_3px_0_var(--a-text)] bg-[color:var(--a-primary)] text-[color:var(--a-on)]'
    : s.value === 'colourful' && inHero
      ? ghost
        ? 'bg-transparent text-[color:var(--a-on)] [box-shadow:inset_0_0_0_1.5px_color-mix(in_srgb,var(--a-on)_55%,transparent)]'
        : 'bg-[color:var(--a-on)] text-[color:var(--a-primary)]'
      : ghost
        ? 'bg-transparent text-[color:var(--a-text)] [box-shadow:inset_0_0_0_1.5px_color-mix(in_srgb,var(--a-text)_22%,transparent)]'
        : 'bg-[color:var(--a-primary)] text-[color:var(--a-on)]',
]

const eyebrowClass = computed(() =>
  s.value === 'elegant'
    ? 'font-medium uppercase tracking-[0.32em]'
    : s.value === 'techy'
      ? "font-bold normal-case tracking-[0.04em] font-['JetBrains_Mono',ui-monospace,monospace] before:content-['●_']"
      : 'font-bold uppercase tracking-[0.16em]'
)

const cardClass = (i: number) => [
  'grid gap-[9px] rounded-[var(--a-radius)]',
  s.value === 'minimal'
    ? 'px-0 pb-0 pt-[14px] [border-width:1px_0_0] [border-style:solid_none_none] [border-color:color-mix(in_srgb,var(--a-text)_15%,transparent)_currentcolor_currentcolor]'
    : 'p-[16px]',
  s.value === 'retro'
    ? '[border:2px_solid_var(--a-text)] [box-shadow:4px_4px_0_var(--a-text)]'
    : s.value === 'minimal' ? '[box-shadow:var(--a-card-shadow)]' : '[border:var(--a-card-border)] [box-shadow:var(--a-card-shadow)]',
  s.value === 'bold' && i === 0
    ? 'bg-[color:var(--a-primary)] text-[color:var(--a-on)]'
    : s.value === 'playful' && i === 0
      ? 'bg-[color:color-mix(in_srgb,var(--a-primary)_16%,var(--a-surface))]'
      : s.value === 'playful' && i === 1
        ? 'bg-[color:color-mix(in_srgb,var(--a-accent)_24%,var(--a-surface))] [transform:rotate(-1.5deg)]'
        : s.value === 'playful' && i === 2
          ? 'bg-[color:color-mix(in_srgb,var(--a-accent)_14%,var(--a-surface))] [transform:rotate(1.2deg)]'
          : 'bg-[color:var(--a-surface)]',
]

const cardLine = (i: number) =>
  s.value === 'bold' && i === 0
    ? 'bg-[color:color-mix(in_srgb,var(--a-on)_28%,transparent)]'
    : 'bg-[color:color-mix(in_srgb,var(--a-text)_12%,transparent)]'

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
