<template>
  <section
    class="relative flex flex-col shrink-0 min-h-[7rem] border-t border-t-sl-line-strong bg-sl-surface dark:bg-sl-surface-2 text-sl-text text-[0.75rem]"
    :style="{ height: `${height}px` }"
    aria-label="Preview tools"
  >
    <!-- Drag the top edge to resize. -->
    <div
      class="absolute -top-1 left-0 right-0 h-2 cursor-ns-resize z-[2] focus-visible:!outline-offset-[-3px]"
      role="separator"
      aria-orientation="horizontal"
      aria-label="Resize the tools panel"
      tabindex="0"
      @pointerdown="onGripDown"
      @keydown.up.prevent="emit('update:height', height + 24)"
      @keydown.down.prevent="emit('update:height', height - 24)"
    ></div>

    <header class="flex items-center gap-1.5 h-9 px-2 border-b border-b-sl-line">
      <div class="flex gap-0.5 mr-auto" role="tablist">
        <button
          v-for="t in tabs"
          :key="t.key"
          type="button"
          role="tab"
          :aria-selected="tab === t.key"
          class="inline-flex items-center gap-1.5 h-[1.625rem] px-2.5 rounded-full font-semibold
            [transition:background-color_0.2s_cubic-bezier(0.22,1,0.36,1),color_0.2s_cubic-bezier(0.22,1,0.36,1)] motion-reduce:[transition:none]
            focus-visible:!outline-offset-2"
          :class="tab === t.key
            ? 'text-sl-text bg-sl-chip-bg-hover'
            : 'text-sl-muted hover:text-sl-text hover:bg-sl-chip-bg'"
          @click="emit('update:tab', t.key)"
        >
          {{ t.label }}
          <span
            v-if="t.count"
            class="min-w-[1.125rem] px-[0.3125rem] rounded-full text-[0.625rem] tabular-nums text-center"
            :class="t.key === 'console' && errorCount ? 'bg-sl-bad text-white' : 'bg-sl-chip-bg-hover text-sl-muted'"
          >{{ t.count }}</span>
        </button>
      </div>
      <!-- No ! on the outline: `.spotlight :focus-visible` has always won
           here, so the field takes the Spotlight ring when focused. -->
      <input
        v-model="filter"
        type="search"
        class="w-36 h-[1.625rem] px-2.5 rounded-full border border-sl-line bg-transparent text-sl-text text-[0.75rem] [outline:none]
          transition-[border-color] duration-200 ease-[cubic-bezier(0.22,1,0.36,1)] motion-reduce:[transition:none]
          hover:border-sl-line-strong focus:border-sl-line-strong placeholder:text-sl-faint"
        :placeholder="tab === 'network' ? 'Filter requests' : 'Filter'"
        aria-label="Filter"
      />
      <button type="button" :class="ICON_BTN" title="Clear" aria-label="Clear" @click="emit('clear', tab)">
        <i class="fas fa-ban"></i>
      </button>
      <button type="button" :class="ICON_BTN" title="Close (Ctrl+J)" aria-label="Close the tools panel" @click="emit('close')">
        <i class="fas fa-xmark"></i>
      </button>
    </header>

    <div
      ref="bodyRef"
      class="flex-1 min-h-0 overflow-auto [font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace]"
      role="tabpanel"
    >
      <!-- Console: errors pinned on top, then everything in order. -->
      <template v-if="tab === 'console'">
        <div
          v-if="pinnedErrors.length"
          class="sticky top-0 z-[1] border-b border-b-sl-line-strong bg-sl-surface dark:bg-sl-surface-2"
        >
          <div v-for="err in pinnedErrors" :key="err.text" :class="[ROW, ROW_TONE.error]">
            <i :class="['fas fa-circle-exclamation', LVL]"></i>
            <span :class="TEXT">{{ err.text }}</span>
            <span v-if="err.count > 1" class="shrink-0 text-sl-faint">×{{ err.count }}</span>
          </div>
        </div>
        <p v-if="!filteredConsole.length" :class="EMPTY">Nothing logged yet. Your app's console messages show up here.</p>
        <div v-for="(entry, i) in filteredConsole" :key="i" :class="[ROW, ROW_TONE[entry.level]]">
          <span class="shrink-0 text-sl-faint tabular-nums">{{ clock(entry.ts) }}</span>
          <i :class="['fas', levelIcon(entry.level), LVL]"></i>
          <span :class="TEXT">{{ entry.text }}</span>
        </div>
      </template>

      <!-- Network: the app's own fetch/XHR calls; failures stand out. -->
      <template v-else-if="tab === 'network'">
        <p v-if="!filteredNetwork.length" :class="EMPTY">No requests yet. Calls your app makes to its backend show up here.</p>
        <table v-else class="w-full border-collapse">
          <thead>
            <!-- Time stays left-aligned like the other headings. -->
            <tr><th :class="TH">Method</th><th :class="TH">Path</th><th :class="TH">Status</th><th :class="[TH, 'tabular-nums']">Time</th></tr>
          </thead>
          <tbody>
            <tr v-for="req in filteredNetwork" :key="req.id" :class="failed(req) && '[&>td]:text-sl-bad'">
              <td :class="TD">{{ req.method }}</td>
              <td :class="[TD, 'max-w-0 w-[60%] truncate']" :title="req.url">{{ req.url }}</td>
              <td :class="TD">{{ req.status || 'failed' }}</td>
              <td :class="[TD, 'text-right tabular-nums']">{{ req.ms }} ms</td>
            </tr>
          </tbody>
        </table>
      </template>

      <!-- Server logs: Django and Vite as they write them. -->
      <template v-else>
        <div class="flex gap-1 px-3 py-1.5 border-b border-b-sl-line font-sl-body" role="group" aria-label="Which server">
          <button
            v-for="s in sources"
            :key="s.key"
            type="button"
            :aria-pressed="source === s.key"
            class="h-[1.375rem] px-2.5 rounded-full border text-[0.6875rem] focus-visible:!outline-offset-2"
            :class="source === s.key
              ? 'text-sl-text border-sl-line-strong bg-sl-chip-bg-hover'
              : 'text-sl-muted border-sl-line'"
            @click="source = s.key"
          >{{ s.label }}</button>
        </div>
        <p v-if="!filteredLogs.length" :class="EMPTY">No server output yet.</p>
        <div
          v-for="(line, i) in filteredLogs"
          :key="i"
          :class="[ROW, isErrorLine(line.text) && ROW_TONE.error]"
        >
          <span class="shrink-0 w-[4.25rem] text-sl-faint tabular-nums">{{ line.source === 'backend' ? 'Backend' : 'Frontend' }}</span>
          <span :class="TEXT">{{ line.text }}</span>
        </div>
      </template>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import type { ConsoleEntry, NetworkEntry } from '../../../services/livePreviewService'

export type DrawerTab = 'console' | 'network' | 'logs'
export interface LogLine {
  source: 'backend' | 'frontend'
  text: string
}

const props = defineProps<{
  tab: DrawerTab
  height: number
  console: ConsoleEntry[]
  network: NetworkEntry[]
  logs: LogLine[]
}>()

const emit = defineEmits<{
  (e: 'update:tab', tab: DrawerTab): void
  (e: 'update:height', height: number): void
  (e: 'clear', tab: DrawerTab): void
  (e: 'close'): void
}>()

// Shared class lists. The focus ring is the Spotlight one (2px --sl-focus);
// the ! offsets beat `.spotlight :focus-visible`, which sets 3px.
const ICON_BTN =
  'inline-grid place-items-center w-[1.625rem] h-[1.625rem] rounded-full text-sl-muted text-[0.6875rem] hover:text-sl-text hover:bg-sl-chip-bg-hover focus-visible:!outline-offset-2'
const ROW = 'flex items-start gap-2 px-3 py-1 border-b border-b-sl-line leading-[1.45]'
const ROW_TONE: Record<ConsoleEntry['level'], string> = {
  error: 'text-sl-bad bg-[color:color-mix(in_srgb,var(--sl-bad)_6%,transparent)]',
  warn: 'text-sl-wait bg-[color:color-mix(in_srgb,var(--sl-wait)_6%,transparent)]',
  info: '',
  log: '',
}
const LVL = 'shrink-0 w-3 mt-[0.2rem] text-[0.625rem] opacity-80'
const TEXT = 'flex-1 min-w-0 whitespace-pre-wrap [word-break:break-word]'
const EMPTY = 'px-3 py-4 font-sl-body text-sl-muted'
const TH =
  'sticky top-0 px-3 py-[0.3125rem] border-b border-b-sl-line-strong bg-sl-surface dark:bg-sl-surface-2 font-sl-body text-[0.6875rem] font-semibold tracking-[0.14em] text-left uppercase text-sl-muted'
const TD = 'px-3 py-1 border-b border-b-sl-line'

const filter = ref('')
const source = ref<'all' | 'backend' | 'frontend'>('all')
const bodyRef = ref<HTMLElement | null>(null)

const sources = [
  { key: 'all' as const, label: 'Both' },
  { key: 'backend' as const, label: 'Backend' },
  { key: 'frontend' as const, label: 'Frontend' },
]

const errorCount = computed(() => props.console.filter((e) => e.level === 'error').length)
const failedCount = computed(() => props.network.filter(failed).length)

const tabs = computed(() => [
  { key: 'console' as const, label: 'Console', count: errorCount.value || 0 },
  { key: 'network' as const, label: 'Network', count: failedCount.value || 0 },
  { key: 'logs' as const, label: 'Server logs', count: 0 },
])

function matches(text: string): boolean {
  const q = filter.value.trim().toLowerCase()
  return !q || text.toLowerCase().includes(q)
}

const filteredConsole = computed(() => props.console.filter((e) => matches(e.text)))
const filteredNetwork = computed(() =>
  props.network.filter((r) => matches(`${r.method} ${r.url} ${r.status}`)).slice().reverse()
)
const filteredLogs = computed(() =>
  props.logs.filter((l) => (source.value === 'all' || l.source === source.value) && matches(l.text))
)

/** Distinct errors, newest first, with how often each happened. */
const pinnedErrors = computed(() => {
  const seen = new Map<string, { text: string; count: number; ts: number }>()
  for (const e of props.console) {
    if (e.level !== 'error') continue
    const hit = seen.get(e.text)
    if (hit) {
      hit.count += 1
      hit.ts = Math.max(hit.ts, e.ts)
    } else {
      seen.set(e.text, { text: e.text, count: 1, ts: e.ts })
    }
  }
  return [...seen.values()].sort((a, b) => b.ts - a.ts).slice(0, 5)
})

function failed(req: NetworkEntry): boolean {
  return !req.status || req.status >= 400
}

const ERROR_LINE = /\b(error|traceback|exception|failed)\b/i
function isErrorLine(text: string): boolean {
  return ERROR_LINE.test(text)
}

function levelIcon(level: ConsoleEntry['level']): string {
  return level === 'error'
    ? 'fa-circle-exclamation'
    : level === 'warn'
      ? 'fa-triangle-exclamation'
      : level === 'info'
        ? 'fa-circle-info'
        : 'fa-angle-right'
}

function clock(ts: number): string {
  const d = new Date(ts)
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}:${String(d.getSeconds()).padStart(2, '0')}`
}

// Follow the newest line, unless the reader scrolled up to look at older ones.
function stickToBottom() {
  const el = bodyRef.value
  if (!el) return
  const atBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 40
  if (atBottom) void nextTick(() => { el.scrollTop = el.scrollHeight })
}
watch(() => [props.console.length, props.logs.length, props.tab], stickToBottom)

function onGripDown(e: PointerEvent) {
  const startY = e.clientY
  const startH = props.height
  const target = e.currentTarget as HTMLElement
  target.setPointerCapture?.(e.pointerId)
  const move = (ev: PointerEvent) => emit('update:height', startH + (startY - ev.clientY))
  const up = () => {
    target.removeEventListener('pointermove', move)
    target.removeEventListener('pointerup', up)
    target.removeEventListener('pointercancel', up)
  }
  target.addEventListener('pointermove', move)
  target.addEventListener('pointerup', up)
  target.addEventListener('pointercancel', up)
}
</script>
