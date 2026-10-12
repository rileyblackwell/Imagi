<template>
  <section class="pd-root" :style="{ height: `${height}px` }" aria-label="Preview tools">
    <!-- Drag the top edge to resize. -->
    <div
      class="pd-grip"
      role="separator"
      aria-orientation="horizontal"
      aria-label="Resize the tools panel"
      tabindex="0"
      @pointerdown="onGripDown"
      @keydown.up.prevent="emit('update:height', height + 24)"
      @keydown.down.prevent="emit('update:height', height - 24)"
    ></div>

    <header class="pd-head">
      <div class="pd-tabs" role="tablist">
        <button
          v-for="t in tabs"
          :key="t.key"
          type="button"
          role="tab"
          :aria-selected="tab === t.key"
          :class="['pd-tab', tab === t.key && 'is-on']"
          @click="emit('update:tab', t.key)"
        >
          {{ t.label }}
          <span v-if="t.count" :class="['pd-count', t.key === 'console' && errorCount && 'is-bad']">{{ t.count }}</span>
        </button>
      </div>
      <input
        v-model="filter"
        type="search"
        class="pd-filter"
        :placeholder="tab === 'network' ? 'Filter requests' : 'Filter'"
        aria-label="Filter"
      />
      <button type="button" class="pd-icon" title="Clear" aria-label="Clear" @click="emit('clear', tab)">
        <i class="fas fa-ban"></i>
      </button>
      <button type="button" class="pd-icon" title="Close (Ctrl+J)" aria-label="Close the tools panel" @click="emit('close')">
        <i class="fas fa-xmark"></i>
      </button>
    </header>

    <div ref="bodyRef" class="pd-body" role="tabpanel">
      <!-- Console: errors pinned on top, then everything in order. -->
      <template v-if="tab === 'console'">
        <div v-if="pinnedErrors.length" class="pd-pinned">
          <div v-for="err in pinnedErrors" :key="err.text" class="pd-row pd-row--error">
            <i class="fas fa-circle-exclamation pd-lvl"></i>
            <span class="pd-text">{{ err.text }}</span>
            <span v-if="err.count > 1" class="pd-times">×{{ err.count }}</span>
            <button type="button" class="pd-fix" @click="emit('fix', err.text)">Fix it</button>
          </div>
        </div>
        <p v-if="!filteredConsole.length" class="pd-empty">Nothing logged yet. Your app's console messages show up here.</p>
        <div v-for="(entry, i) in filteredConsole" :key="i" :class="['pd-row', `pd-row--${entry.level}`]">
          <span class="pd-time">{{ clock(entry.ts) }}</span>
          <i :class="['fas', levelIcon(entry.level), 'pd-lvl']"></i>
          <span class="pd-text">{{ entry.text }}</span>
        </div>
      </template>

      <!-- Network: the app's own fetch/XHR calls; failures stand out. -->
      <template v-else-if="tab === 'network'">
        <p v-if="!filteredNetwork.length" class="pd-empty">No requests yet. Calls your app makes to its backend show up here.</p>
        <table v-else class="pd-table">
          <thead>
            <tr><th>Method</th><th>Path</th><th>Status</th><th class="pd-num">Time</th></tr>
          </thead>
          <tbody>
            <tr v-for="req in filteredNetwork" :key="req.id" :class="{ 'is-failed': failed(req) }">
              <td class="pd-mono">{{ req.method }}</td>
              <td class="pd-mono pd-path" :title="req.url">{{ req.url }}</td>
              <td class="pd-mono">{{ req.status || 'failed' }}</td>
              <td class="pd-mono pd-num">{{ req.ms }} ms</td>
            </tr>
          </tbody>
        </table>
      </template>

      <!-- Server logs: Django and Vite as they write them. -->
      <template v-else>
        <div class="pd-sources" role="group" aria-label="Which server">
          <button
            v-for="s in sources"
            :key="s.key"
            type="button"
            :aria-pressed="source === s.key"
            :class="['pd-chip', source === s.key && 'is-on']"
            @click="source = s.key"
          >{{ s.label }}</button>
        </div>
        <p v-if="!filteredLogs.length" class="pd-empty">No server output yet.</p>
        <div
          v-for="(line, i) in filteredLogs"
          :key="i"
          :class="['pd-row', 'pd-log', isErrorLine(line.text) && 'pd-row--error']"
        >
          <span class="pd-src">{{ line.source === 'backend' ? 'Backend' : 'Frontend' }}</span>
          <span class="pd-text">{{ line.text }}</span>
          <button v-if="isErrorLine(line.text)" type="button" class="pd-fix" @click="emit('fix', line.text)">Fix it</button>
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
  /** "Fix it" on one error: its text goes to the agent. */
  (e: 'fix', text: string): void
}>()

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

<style scoped>
.pd-root {
  position: relative;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  min-height: 7rem;
  border-top: 1px solid var(--sl-line-strong, rgba(20, 21, 30, 0.15));
  background: var(--sl-surface, #ffffff);
  color: var(--sl-text, #14151c);
  font-size: 0.75rem;
}
.dark .pd-root { background: var(--sl-surface-2, #1a1d28); }

.pd-grip {
  position: absolute;
  top: -4px;
  left: 0;
  right: 0;
  height: 8px;
  cursor: ns-resize;
  z-index: 2;
}
.pd-grip:focus-visible {
  outline: 2px solid var(--sl-focus, #d9730d);
  outline-offset: -3px;
}

.pd-head {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  height: 2.25rem;
  padding: 0 0.5rem;
  border-bottom: 1px solid var(--sl-line, rgba(20, 21, 30, 0.09));
}

.pd-tabs {
  display: flex;
  gap: 0.125rem;
  margin-right: auto;
}

.pd-tab {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  height: 1.625rem;
  padding: 0 0.625rem;
  border-radius: 9999px;
  font-weight: 600;
  color: var(--sl-muted, #5c6172);
  transition: background-color 0.2s cubic-bezier(0.22, 1, 0.36, 1), color 0.2s cubic-bezier(0.22, 1, 0.36, 1);
}
.pd-tab:hover { color: var(--sl-text, #14151c); background: var(--sl-chip-bg, rgba(20, 21, 30, 0.035)); }
.pd-tab.is-on { color: var(--sl-text, #14151c); background: var(--sl-chip-bg-hover, rgba(20, 21, 30, 0.065)); }

.pd-count {
  min-width: 1.125rem;
  padding: 0 0.3125rem;
  border-radius: 9999px;
  background: var(--sl-chip-bg-hover, rgba(20, 21, 30, 0.065));
  font-size: 0.625rem;
  font-variant-numeric: tabular-nums;
  text-align: center;
  color: var(--sl-muted, #5c6172);
}
.pd-count.is-bad { background: var(--sl-bad, #d7334a); color: #fff; }

.pd-filter {
  width: 9rem;
  height: 1.625rem;
  padding: 0 0.625rem;
  border-radius: 9999px;
  border: 1px solid var(--sl-line, rgba(20, 21, 30, 0.09));
  background: transparent;
  color: var(--sl-text, #14151c);
  font-size: 0.75rem;
  outline: none;
  transition: border-color 0.2s cubic-bezier(0.22, 1, 0.36, 1);
}
.pd-filter:hover,
.pd-filter:focus { border-color: var(--sl-line-strong, rgba(20, 21, 30, 0.15)); }
.pd-filter::placeholder { color: var(--sl-faint, #8a8fa0); }

.pd-icon {
  display: inline-grid;
  place-items: center;
  width: 1.625rem;
  height: 1.625rem;
  border-radius: 9999px;
  color: var(--sl-muted, #5c6172);
  font-size: 0.6875rem;
}
.pd-icon:hover { color: var(--sl-text, #14151c); background: var(--sl-chip-bg-hover, rgba(20, 21, 30, 0.065)); }

.pd-tab:focus-visible,
.pd-icon:focus-visible,
.pd-chip:focus-visible,
.pd-fix:focus-visible {
  outline: 2px solid var(--sl-focus, #d9730d);
  outline-offset: 2px;
}

.pd-body {
  flex: 1;
  min-height: 0;
  overflow: auto;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}

.pd-pinned {
  position: sticky;
  top: 0;
  z-index: 1;
  border-bottom: 1px solid var(--sl-line-strong, rgba(20, 21, 30, 0.15));
  background: inherit;
  background: var(--sl-surface, #ffffff);
}
.dark .pd-pinned { background: var(--sl-surface-2, #1a1d28); }

.pd-row {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  border-bottom: 1px solid var(--sl-line, rgba(20, 21, 30, 0.09));
  line-height: 1.45;
}
.pd-row--error { color: var(--sl-bad, #d7334a); background: color-mix(in srgb, var(--sl-bad, #d7334a) 6%, transparent); }
.pd-row--warn { color: var(--sl-wait, #c46f00); background: color-mix(in srgb, var(--sl-wait, #c46f00) 6%, transparent); }

.pd-time,
.pd-src {
  flex-shrink: 0;
  color: var(--sl-faint, #8a8fa0);
  font-variant-numeric: tabular-nums;
}
.pd-src { width: 4.25rem; }
.pd-lvl { flex-shrink: 0; width: 0.75rem; margin-top: 0.2rem; font-size: 0.625rem; opacity: 0.8; }
.pd-text { flex: 1; min-width: 0; white-space: pre-wrap; word-break: break-word; }
.pd-times { flex-shrink: 0; color: var(--sl-faint, #8a8fa0); }

.pd-fix {
  flex-shrink: 0;
  height: 1.375rem;
  padding: 0 0.625rem;
  border-radius: 9999px;
  border: 1px solid currentColor;
  font-family: var(--sl-font-body, inherit);
  font-size: 0.6875rem;
  font-weight: 600;
  transition: background-color 0.2s cubic-bezier(0.22, 1, 0.36, 1);
}
.pd-fix:hover { background: color-mix(in srgb, currentColor 10%, transparent); }

.pd-empty {
  padding: 1rem 0.75rem;
  font-family: var(--sl-font-body, inherit);
  color: var(--sl-muted, #5c6172);
}

.pd-sources {
  display: flex;
  gap: 0.25rem;
  padding: 0.375rem 0.75rem;
  border-bottom: 1px solid var(--sl-line, rgba(20, 21, 30, 0.09));
  font-family: var(--sl-font-body, inherit);
}
.pd-chip {
  height: 1.375rem;
  padding: 0 0.625rem;
  border-radius: 9999px;
  border: 1px solid var(--sl-line, rgba(20, 21, 30, 0.09));
  color: var(--sl-muted, #5c6172);
  font-size: 0.6875rem;
}
.pd-chip.is-on { color: var(--sl-text, #14151c); border-color: var(--sl-line-strong, rgba(20, 21, 30, 0.15)); background: var(--sl-chip-bg-hover, rgba(20, 21, 30, 0.065)); }

.pd-table { width: 100%; border-collapse: collapse; }
.pd-table th {
  position: sticky;
  top: 0;
  padding: 0.3125rem 0.75rem;
  border-bottom: 1px solid var(--sl-line-strong, rgba(20, 21, 30, 0.15));
  background: var(--sl-surface, #ffffff);
  font-family: var(--sl-font-body, inherit);
  font-size: 0.6875rem;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-align: left;
  text-transform: uppercase;
  color: var(--sl-muted, #5c6172);
}
.dark .pd-table th { background: var(--sl-surface-2, #1a1d28); }
.pd-table td { padding: 0.25rem 0.75rem; border-bottom: 1px solid var(--sl-line, rgba(20, 21, 30, 0.09)); }
.pd-table tr.is-failed td { color: var(--sl-bad, #d7334a); }
.pd-path { max-width: 0; width: 60%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.pd-num { text-align: right; font-variant-numeric: tabular-nums; }

@media (prefers-reduced-motion: reduce) {
  .pd-tab, .pd-filter, .pd-fix { transition: none; }
}
</style>
