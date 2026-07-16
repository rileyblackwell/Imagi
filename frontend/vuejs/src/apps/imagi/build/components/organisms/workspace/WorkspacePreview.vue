<template>
  <div class="relative w-full h-full flex flex-col bg-white dark:bg-[#0a0a0a]">
    <!-- Toolbar -->
    <div class="flex flex-col gap-2 px-3 py-1.5 border-b border-blue-200/60 dark:border-white/[0.08] bg-blue-50/50 dark:bg-white/[0.02]">
      <div class="flex items-center gap-1.5 flex-wrap">
        <button
          type="button"
          @click="goBack"
          :disabled="!canGoBack || phase !== 'ready'"
          title="Back"
          class="inline-flex items-center justify-center w-8 h-8 shrink-0 rounded-full border border-blue-200/60 dark:border-white/[0.08] bg-white dark:bg-white/[0.03] hover:bg-blue-50 dark:hover:bg-white/[0.06] text-blue-950/60 dark:text-white/60 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <i class="fas fa-arrow-left text-xs"></i>
        </button>

        <button
          type="button"
          @click="goForward"
          :disabled="!canGoForward || phase !== 'ready'"
          title="Forward"
          class="inline-flex items-center justify-center w-8 h-8 shrink-0 rounded-full border border-blue-200/60 dark:border-white/[0.08] bg-white dark:bg-white/[0.03] hover:bg-blue-50 dark:hover:bg-white/[0.06] text-blue-950/60 dark:text-white/60 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <i class="fas fa-arrow-right text-xs"></i>
        </button>

        <button
          type="button"
          @click="reload"
          title="Refresh page"
          class="inline-flex items-center justify-center w-8 h-8 shrink-0 rounded-full border border-blue-200/60 dark:border-white/[0.08] bg-white dark:bg-white/[0.03] hover:bg-blue-50 dark:hover:bg-white/[0.06] text-blue-950/60 dark:text-white/60 transition-colors"
        >
          <i class="fas fa-sync-alt text-xs" :class="{ 'fa-spin': phase === 'starting' }"></i>
        </button>

        <button
          type="button"
          @click="goHome"
          title="Go to home page"
          class="inline-flex items-center justify-center w-8 h-8 shrink-0 rounded-full border border-blue-200/60 dark:border-white/[0.08] bg-white dark:bg-white/[0.03] hover:bg-blue-50 dark:hover:bg-white/[0.06] text-blue-950/60 dark:text-white/60 transition-colors"
        >
          <i class="fas fa-home text-xs"></i>
        </button>

        <!-- Combined App / Page selector — slender address bar -->
        <div class="relative flex-1 min-w-[8rem]" ref="menuRoot">
          <button
            type="button"
            @click="onMenuToggle"
            :disabled="apps.length === 0"
            class="group w-full flex items-center gap-2 h-8 rounded-full border border-blue-200/60 dark:border-white/[0.08] bg-white/80 dark:bg-white/[0.04] hover:bg-blue-50 dark:hover:bg-white/[0.07] focus:border-blue-400 dark:focus:border-blue-300/40 focus:ring-2 focus:ring-blue-400/15 outline-none pl-3 pr-8 text-[13px] font-medium text-blue-950 dark:text-white/90 transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <i class="fas fa-cube text-[10px] text-blue-950/40 dark:text-white/40 shrink-0"></i>
            <span class="truncate flex-1 text-left">{{ triggerLabel }}</span>
            <span class="truncate max-w-[10rem] text-[11px] text-blue-950/35 dark:text-white/35 font-normal hidden sm:block">{{ currentPath }}</span>
            <i class="fas fa-chevron-down absolute right-3 top-1/2 -translate-y-1/2 text-[10px] text-blue-950/40 dark:text-white/35 pointer-events-none transition-transform duration-200" :class="{ 'rotate-180': menuOpen }"></i>
          </button>

          <div
            v-if="menuOpen && apps.length > 0"
            class="absolute z-20 mt-1.5 left-0 max-md:left-auto max-md:right-0 min-w-[14rem] max-md:max-w-[calc(100vw-1.5rem)] rounded-xl border border-blue-200/60 dark:border-white/[0.08] bg-white dark:bg-[#0f0f0f] shadow-xl py-1"
          >
            <div
              v-for="app in apps"
              :key="app.name"
              class="relative"
              @mouseenter="onAppEnter(app.name)"
              @mouseleave="onAppLeave(app.name)"
            >
              <button
                type="button"
                @click="hoveredApp = hoveredApp === app.name ? '' : app.name"
                class="w-full flex items-center justify-between gap-2 px-3 py-2 text-sm text-blue-950 dark:text-white/90 hover:bg-blue-50 dark:hover:bg-white/[0.05]"
              >
                <span class="flex items-center gap-2 truncate">
                  <i class="fas fa-cube text-xs text-blue-950/50 dark:text-white/50"></i>
                  {{ app.title }}
                </span>
                <i
                  class="fas fa-chevron-right text-[10px] text-blue-950/40 dark:text-white/40 transition-transform duration-200"
                  :class="{ 'max-md:rotate-90': hoveredApp === app.name }"
                ></i>
              </button>

              <div
                v-if="hoveredApp === app.name && app.pages.length"
                class="py-1 md:absolute md:top-0 md:left-full md:ml-1 md:min-w-[14rem] md:rounded-lg md:border md:border-blue-200/60 md:dark:border-white/[0.08] md:bg-white md:dark:bg-[#0f0f0f] md:shadow-lg max-md:ml-4 max-md:mt-0.5 max-md:mb-1 max-md:border-l max-md:border-blue-100 max-md:dark:border-white/[0.08]"
                @mouseenter="onAppEnter(app.name)"
                @mouseleave="onAppLeave(app.name)"
              >
                <button
                  v-for="page in app.pages"
                  :key="page.path"
                  type="button"
                  @click="onSelectPage(page.path)"
                  :class="['w-full flex items-center gap-2 px-3 py-2 text-sm text-left',
                           page.path === currentPath
                             ? 'bg-blue-50 dark:bg-white/[0.08] text-blue-950 dark:text-white'
                             : 'text-blue-950/70 dark:text-white/80 hover:bg-blue-50 dark:hover:bg-white/[0.05]']"
                >
                  <i class="fas fa-file-alt text-xs text-blue-950/50 dark:text-white/50"></i>
                  <span class="truncate">{{ page.title }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- Screen: frames from the remote browser, input forwarded back -->
    <div
      ref="screenRef"
      tabindex="0"
      class="relative flex-1 min-h-0 bg-white outline-none overflow-hidden touch-none"
      @pointerdown="onPointerDown"
      @pointermove="onPointerMove"
      @pointerup="onPointerUp"
      @pointercancel="onPointerCancel"
      @wheel.prevent="onWheel"
      @keydown="onKeyDown"
      @keyup="onKeyUp"
      @contextmenu.prevent
    >
      <img
        v-if="frameSrc"
        :src="frameSrc"
        alt=""
        draggable="false"
        class="w-full h-full select-none pointer-events-none"
        style="object-fit: fill;"
      />

      <!-- Starting overlay -->
      <div
        v-if="phase === 'starting'"
        class="absolute inset-0 flex flex-col items-center justify-center gap-3 bg-white/90 dark:bg-[#0a0a0a]/90 text-blue-950/60 dark:text-white/60"
      >
        <i class="fas fa-spinner fa-spin text-2xl"></i>
        <span class="text-sm font-medium">Starting preview…</span>
        <span class="text-xs text-blue-950/40 dark:text-white/40 max-w-xs text-center">
          The first start can take a few minutes while your project's dependencies install.
        </span>
      </div>

      <!-- Error overlay -->
      <div
        v-else-if="phase === 'error'"
        class="absolute inset-0 flex flex-col items-center justify-center gap-4 px-8 text-center bg-white dark:bg-[#0a0a0a]"
      >
        <div class="w-12 h-12 bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800/30 rounded-xl flex items-center justify-center">
          <i class="fas fa-exclamation-triangle text-red-600 dark:text-red-400"></i>
        </div>
        <p class="text-sm text-blue-950/70 dark:text-white/70 max-w-md break-words">{{ error }}</p>
        <button
          @click="startPreview"
          class="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-blue-200/60 dark:border-white/[0.08] bg-white dark:bg-white/[0.03] hover:bg-blue-50 dark:hover:bg-white/[0.06] text-sm font-medium text-blue-950/70 dark:text-white/70 transition-colors"
        >
          <i class="fas fa-sync-alt text-xs"></i>
          Retry
        </button>
      </div>

      <!-- Stopped overlay (session ended, e.g. idle shutdown or restart) -->
      <div
        v-else-if="phase === 'stopped'"
        class="absolute inset-0 flex flex-col items-center justify-center gap-4 px-8 text-center bg-white/95 dark:bg-[#0a0a0a]/95"
      >
        <div class="w-12 h-12 bg-blue-50 dark:bg-white/[0.05] border border-blue-200/60 dark:border-white/[0.08] rounded-xl flex items-center justify-center">
          <i class="fas fa-pause text-blue-600 dark:text-blue-300"></i>
        </div>
        <p class="text-sm text-blue-950/70 dark:text-white/70 max-w-md">The preview session has stopped.</p>
        <button
          @click="startPreview"
          class="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-blue-200/60 dark:border-white/[0.08] bg-white dark:bg-white/[0.03] hover:bg-blue-50 dark:hover:bg-white/[0.06] text-sm font-medium text-blue-950/70 dark:text-white/70 transition-colors"
        >
          <i class="fas fa-play text-xs"></i>
          Start preview
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed, onMounted, onBeforeUnmount } from 'vue'
import {
  PreviewService,
  PreviewNotRunningError,
  type PreviewApp,
  type PreviewFrame,
  type PreviewInputEvent,
} from '../../../services/previewService'

const props = defineProps<{
  projectId: string
}>()

type Phase = 'idle' | 'starting' | 'ready' | 'stopped' | 'error'

const phase = ref<Phase>('idle')
const error = ref<string | null>(null)
const frameSrc = ref<string | null>(null)
const etag = ref<string | undefined>(undefined)
const currentPath = ref('/')
const canGoBack = ref(false)
const canGoForward = ref(false)
// Size of the remote browser viewport in CSS pixels; kept in sync with the
// pane so client coordinates map 1:1 onto page coordinates.
const viewport = ref<[number, number]>([1280, 800])

const selectedApp = ref('')
const menuOpen = ref(false)
const hoveredApp = ref('')
const menuRoot = ref<HTMLElement | null>(null)
const screenRef = ref<HTMLElement | null>(null)
let leaveTimer: number | null = null

// ---------------------------------------------------------------------------
// Session lifecycle + frame polling
// ---------------------------------------------------------------------------

let pollTimer: number | null = null
let resizeTimer: number | null = null
let observer: ResizeObserver | null = null
let lastActivityAt = 0
let disposed = false

const deviceScaleFactor = Math.min(window.devicePixelRatio || 1, 2)

function paneSize(): { width: number; height: number } {
  const rect = screenRef.value?.getBoundingClientRect()
  return {
    width: Math.max(320, Math.round(rect?.width || 1280)),
    height: Math.max(320, Math.round(rect?.height || 800)),
  }
}

function applyFrame(f: PreviewFrame) {
  if (f.frame) {
    frameSrc.value = `data:image/jpeg;base64,${f.frame}`
  }
  if (f.etag) etag.value = f.etag
  if (typeof f.path === 'string') currentPath.value = f.path
  canGoBack.value = !!f.can_go_back
  canGoForward.value = !!f.can_go_forward
  if (f.viewport) viewport.value = f.viewport
  syncSelectionFromCurrent()
}

async function startPreview() {
  if (!props.projectId || phase.value === 'starting') return
  phase.value = 'starting'
  error.value = null
  try {
    const result = await PreviewService.start(props.projectId, paneSize(), deviceScaleFactor)
    if (disposed) return
    applyFrame(result)
    phase.value = 'ready'
    schedulePoll(200)
    // The size passed to start() can be stale — measured before the pane was
    // laid out, which falls back to a desktop width and makes the app render
    // its desktop layout squished into a phone. The ResizeObserver won't fix
    // it because the pane size never actually changes, so re-assert the
    // viewport against the now-laid-out pane once we're ready.
    requestAnimationFrame(() => void ensureViewportMatchesPane())
    // Starting may have scaffolded/hydrated the working copy the pages
    // menu reads from, so fetch it (again) now.
    void refreshPages()
  } catch (e) {
    if (disposed) return
    // Keep the failure local to this component — never call store.setError, or
    // the workspace-level error path can navigate the user back to /projects.
    phase.value = 'error'
    error.value = e instanceof Error ? e.message : 'Preview failed to start.'
  }
}

function markSessionStopped() {
  phase.value = 'stopped'
}

function schedulePoll(delay?: number) {
  if (pollTimer) window.clearTimeout(pollTimer)
  if (disposed) return
  const active = Date.now() - lastActivityAt < 4000
  pollTimer = window.setTimeout(pollFrame, delay ?? (active ? 350 : 1500))
}

async function pollFrame() {
  if (disposed || phase.value !== 'ready') return
  if (document.hidden || inputInFlight) {
    schedulePoll(1000)
    return
  }
  try {
    const f = await PreviewService.frame(props.projectId, etag.value)
    applyFrame(f)
  } catch (e) {
    if (e instanceof PreviewNotRunningError) {
      markSessionStopped()
      return
    }
    // Transient failure (network hiccup): keep polling.
  }
  schedulePoll()
}

// ---------------------------------------------------------------------------
// Input forwarding
// ---------------------------------------------------------------------------

let inputQueue: PreviewInputEvent[] = []
let inputInFlight = false
let flushTimer: number | null = null

function modifiersFrom(e: MouseEvent | KeyboardEvent): number {
  return (e.altKey ? 1 : 0) | (e.ctrlKey ? 2 : 0) | (e.metaKey ? 4 : 0) | (e.shiftKey ? 8 : 0)
}

function pageCoords(e: PointerEvent | WheelEvent): { x: number; y: number } {
  const rect = screenRef.value?.getBoundingClientRect()
  if (!rect || rect.width === 0 || rect.height === 0) return { x: 0, y: 0 }
  const [vw, vh] = viewport.value
  return {
    x: Math.round(((e.clientX - rect.left) / rect.width) * vw * 100) / 100,
    y: Math.round(((e.clientY - rect.top) / rect.height) * vh * 100) / 100,
  }
}

function enqueue(event: PreviewInputEvent, immediate = false) {
  if (phase.value !== 'ready') return
  lastActivityAt = Date.now()
  // Coalesce consecutive mouse moves so dragging doesn't flood the queue.
  const last = inputQueue[inputQueue.length - 1]
  if (event.type === 'mouseMoved' && last?.type === 'mouseMoved') {
    inputQueue[inputQueue.length - 1] = event
  } else if (event.kind === 'wheel' && last?.kind === 'wheel') {
    last.deltaX = (last.deltaX || 0) + (event.deltaX || 0)
    last.deltaY = (last.deltaY || 0) + (event.deltaY || 0)
  } else {
    inputQueue.push(event)
  }
  if (inputQueue.length > 64) inputQueue = inputQueue.slice(-64)
  scheduleFlush(immediate ? 0 : 24)
}

function scheduleFlush(delay: number) {
  if (flushTimer) return
  flushTimer = window.setTimeout(flushInput, delay)
}

async function flushInput() {
  flushTimer = null
  if (inputInFlight || inputQueue.length === 0 || phase.value !== 'ready') return
  const batch = inputQueue
  inputQueue = []
  inputInFlight = true
  try {
    const f = await PreviewService.sendInput(props.projectId, batch, etag.value)
    applyFrame(f)
  } catch (e) {
    if (e instanceof PreviewNotRunningError) {
      markSessionStopped()
      return
    }
    // Drop the batch on transient failure; interaction continues from live state.
  } finally {
    inputInFlight = false
  }
  if (inputQueue.length > 0) scheduleFlush(0)
  schedulePoll(250)
}

const BUTTON_NAMES: Array<'left' | 'middle' | 'right'> = ['left', 'middle', 'right']

// A touch drag scrolls the previewed app (forwarded as wheel deltas) the way a
// finger scrolls a native page, instead of being sent as a mouse drag. A touch
// that barely moves is treated as a tap and forwarded as a click so buttons and
// links still work. When the finger lifts we keep emitting decaying wheel
// deltas (momentum) so the page glides to a stop instead of stopping dead —
// the streamed preview has no native inertial scrolling of its own.
const TOUCH_TAP_SLOP = 8       // page px of travel before a touch becomes a scroll
const INERTIA_FRICTION = 0.94  // fraction of velocity kept each animation frame
const INERTIA_MIN_SPEED = 0.03 // px/ms; the glide ends below this
const INERTIA_MAX_SPEED = 4     // px/ms; caps a hard flick so it stays controllable
let touchDrag: {
  pointerId: number
  startX: number
  startY: number
  lastX: number
  lastY: number
  lastT: number
  vx: number
  vy: number
  scrolling: boolean
  stoppedInertia: boolean
} | null = null

let inertiaRaf: number | null = null
let inertiaX = 0
let inertiaY = 0
let inertiaVx = 0
let inertiaVy = 0
let inertiaLastT = 0

function stopInertia() {
  if (inertiaRaf !== null) {
    cancelAnimationFrame(inertiaRaf)
    inertiaRaf = null
  }
}

function startInertia(x: number, y: number, vx: number, vy: number) {
  stopInertia()
  inertiaX = x
  inertiaY = y
  inertiaVx = Math.max(-INERTIA_MAX_SPEED, Math.min(vx, INERTIA_MAX_SPEED))
  inertiaVy = Math.max(-INERTIA_MAX_SPEED, Math.min(vy, INERTIA_MAX_SPEED))
  if (Math.hypot(inertiaVx, inertiaVy) < INERTIA_MIN_SPEED) return
  inertiaLastT = performance.now()
  const step = () => {
    inertiaRaf = null
    if (disposed || phase.value !== 'ready') return
    const now = performance.now()
    const dt = Math.min(32, now - inertiaLastT)
    inertiaLastT = now
    inertiaVx *= INERTIA_FRICTION
    inertiaVy *= INERTIA_FRICTION
    if (Math.hypot(inertiaVx, inertiaVy) < INERTIA_MIN_SPEED) return
    // Same convention as a drag: wheel delta is opposite the finger travel.
    enqueue({ kind: 'wheel', x: inertiaX, y: inertiaY, deltaX: -inertiaVx * dt, deltaY: -inertiaVy * dt, modifiers: 0 })
    inertiaRaf = requestAnimationFrame(step)
  }
  inertiaRaf = requestAnimationFrame(step)
}

function onPointerDown(e: PointerEvent) {
  screenRef.value?.focus()
  if (phase.value !== 'ready') return
  const { x, y } = pageCoords(e)
  if (e.pointerType === 'touch') {
    const stoppedInertia = inertiaRaf !== null
    stopInertia()
    touchDrag = {
      pointerId: e.pointerId,
      startX: x, startY: y,
      lastX: x, lastY: y,
      lastT: e.timeStamp,
      vx: 0, vy: 0,
      scrolling: false,
      stoppedInertia,
    }
    try { screenRef.value?.setPointerCapture(e.pointerId) } catch {}
    return
  }
  enqueue({
    kind: 'mouse',
    type: 'mousePressed',
    x, y,
    button: BUTTON_NAMES[e.button] || 'left',
    buttons: e.buttons,
    clickCount: Math.max(1, e.detail),
    modifiers: modifiersFrom(e),
  }, true)
}

function onPointerMove(e: PointerEvent) {
  if (phase.value !== 'ready') return
  const { x, y } = pageCoords(e)
  if (touchDrag && e.pointerId === touchDrag.pointerId) {
    const dx = x - touchDrag.lastX
    const dy = y - touchDrag.lastY
    if (!touchDrag.scrolling &&
        Math.hypot(x - touchDrag.startX, y - touchDrag.startY) > TOUCH_TAP_SLOP) {
      touchDrag.scrolling = true
    }
    if (touchDrag.scrolling && (dx !== 0 || dy !== 0)) {
      // Wheel delta is opposite the finger travel: drag up -> scroll down.
      enqueue({ kind: 'wheel', x, y, deltaX: -dx, deltaY: -dy, modifiers: 0 })
      // Track a smoothed finger velocity (px/ms) to seed the release glide.
      const dt = Math.max(1, e.timeStamp - touchDrag.lastT)
      touchDrag.vx = touchDrag.vx * 0.7 + (dx / dt) * 0.3
      touchDrag.vy = touchDrag.vy * 0.7 + (dy / dt) * 0.3
    }
    touchDrag.lastX = x
    touchDrag.lastY = y
    touchDrag.lastT = e.timeStamp
    return
  }
  enqueue({
    kind: 'mouse',
    type: 'mouseMoved',
    x, y,
    button: 'none',
    buttons: e.buttons,
    modifiers: modifiersFrom(e),
  })
}

function onPointerUp(e: PointerEvent) {
  if (phase.value !== 'ready') return
  const { x, y } = pageCoords(e)
  if (touchDrag && e.pointerId === touchDrag.pointerId) {
    const drag = touchDrag
    touchDrag = null
    try { screenRef.value?.releasePointerCapture(e.pointerId) } catch {}
    if (drag.scrolling) {
      // Let the page keep gliding from the finger's release velocity.
      startInertia(drag.lastX, drag.lastY, drag.vx, drag.vy)
    } else if (!drag.stoppedInertia) {
      // A genuine tap (not a tap that just halted a glide) becomes a click.
      enqueue({ kind: 'mouse', type: 'mousePressed', x, y, button: 'left', buttons: 1, clickCount: 1, modifiers: modifiersFrom(e) }, true)
      enqueue({ kind: 'mouse', type: 'mouseReleased', x, y, button: 'left', buttons: 0, clickCount: 1, modifiers: modifiersFrom(e) }, true)
    }
    return
  }
  enqueue({
    kind: 'mouse',
    type: 'mouseReleased',
    x, y,
    button: BUTTON_NAMES[e.button] || 'left',
    buttons: e.buttons,
    clickCount: Math.max(1, e.detail),
    modifiers: modifiersFrom(e),
  }, true)
}

function onPointerCancel(e: PointerEvent) {
  if (touchDrag && e.pointerId === touchDrag.pointerId) {
    touchDrag = null
    try { screenRef.value?.releasePointerCapture(e.pointerId) } catch {}
  }
}

function onWheel(e: WheelEvent) {
  if (phase.value !== 'ready') return
  const { x, y } = pageCoords(e)
  enqueue({
    kind: 'wheel',
    x, y,
    deltaX: e.deltaX,
    deltaY: e.deltaY,
    modifiers: modifiersFrom(e),
  })
}

function keyEvent(e: KeyboardEvent, type: 'keyDown' | 'keyUp'): PreviewInputEvent {
  return {
    kind: 'key',
    type,
    key: e.key,
    code: e.code,
    text: e.key.length === 1 ? e.key : e.key === 'Enter' ? '\r' : '',
    keyCode: e.keyCode,
    modifiers: modifiersFrom(e),
  }
}

function onKeyDown(e: KeyboardEvent) {
  if (phase.value !== 'ready') return
  e.preventDefault()
  e.stopPropagation()
  enqueue(keyEvent(e, 'keyDown'), true)
}

function onKeyUp(e: KeyboardEvent) {
  if (phase.value !== 'ready') return
  e.preventDefault()
  e.stopPropagation()
  enqueue(keyEvent(e, 'keyUp'), true)
}

// ---------------------------------------------------------------------------
// Navigation
// ---------------------------------------------------------------------------

async function doNavigate(action: 'goto' | 'back' | 'forward' | 'reload', path?: string) {
  if (phase.value !== 'ready') return
  lastActivityAt = Date.now()
  try {
    const f = await PreviewService.navigate(props.projectId, action, path)
    applyFrame(f)
    schedulePoll(300)
  } catch (e) {
    if (e instanceof PreviewNotRunningError) markSessionStopped()
  }
}

function navigateTo(path: string) {
  void doNavigate('goto', normalizePath(path))
}

function goBack() {
  void doNavigate('back')
}

function goForward() {
  void doNavigate('forward')
}

function goHome() {
  navigateTo('/')
}

function reload() {
  if (phase.value === 'ready') {
    void doNavigate('reload')
  } else if (phase.value !== 'starting') {
    void startPreview()
  }
}

// ---------------------------------------------------------------------------
// Pane size -> remote viewport
// ---------------------------------------------------------------------------

// Resize the remote browser to match the pane's current CSS size, so the
// previewed app renders (and fills) at the real display width. No-op when it
// already matches.
async function ensureViewportMatchesPane() {
  if (disposed || phase.value !== 'ready') return
  const { width, height } = paneSize()
  const [vw, vh] = viewport.value
  if (Math.abs(width - vw) < 4 && Math.abs(height - vh) < 4) return
  try {
    await PreviewService.resize(props.projectId, width, height, deviceScaleFactor)
    viewport.value = [width, height]
    etag.value = undefined // force a fresh frame at the new size
    schedulePoll(100)
  } catch (e) {
    if (e instanceof PreviewNotRunningError) markSessionStopped()
  }
}

function onPaneResized() {
  if (resizeTimer) window.clearTimeout(resizeTimer)
  resizeTimer = window.setTimeout(() => void ensureViewportMatchesPane(), 350)
}

// ---------------------------------------------------------------------------
// App / page selector (read from the project's actual Vue routers)
// ---------------------------------------------------------------------------

const apps = ref<PreviewApp[]>([])

async function refreshPages() {
  if (!props.projectId) return
  try {
    apps.value = await PreviewService.pages(props.projectId)
    syncSelectionFromCurrent()
  } catch {
    // Keep whatever menu we had; the preview itself is unaffected.
  }
}

function onMenuToggle() {
  menuOpen.value = !menuOpen.value
  // Routes may have changed since the last fetch (the agent edits routers);
  // refresh in the background whenever the menu opens.
  if (menuOpen.value) void refreshPages()
}

const pagesForSelectedApp = computed(() => {
  const app = apps.value.find(a => a.name === selectedApp.value)
  return app ? app.pages : []
})

function appNameFromPath(path: string): string | null {
  if (path === '/' || path === '') return apps.value.some(a => a.name === 'home') ? 'home' : null
  const m = path.match(/^\/([^/]+)/)
  return m ? m[1]! : null
}

function normalizePath(input: string): string {
  const trimmed = (input || '').trim()
  if (!trimmed) return '/'
  if (/^https?:\/\//i.test(trimmed)) {
    try {
      const u = new URL(trimmed)
      return u.pathname + u.search + u.hash
    } catch {
      return '/'
    }
  }
  return trimmed.startsWith('/') ? trimmed : '/' + trimmed
}

function onSelectPage(path: string) {
  navigateTo(path)
  menuOpen.value = false
  hoveredApp.value = ''
}

function onAppEnter(name: string) {
  if (leaveTimer) {
    window.clearTimeout(leaveTimer)
    leaveTimer = null
  }
  hoveredApp.value = name
}

function onAppLeave(name: string) {
  if (leaveTimer) window.clearTimeout(leaveTimer)
  leaveTimer = window.setTimeout(() => {
    if (hoveredApp.value === name) hoveredApp.value = ''
    leaveTimer = null
  }, 120)
}

function onDocClick(e: MouseEvent) {
  if (!menuOpen.value) return
  if (menuRoot.value && !menuRoot.value.contains(e.target as Node)) {
    menuOpen.value = false
    hoveredApp.value = ''
  }
}

const triggerLabel = computed(() => {
  const app = apps.value.find(a => a.name === selectedApp.value)
  const page = pagesForSelectedApp.value.find(p => p.path === currentPath.value)
  if (app && page) return `${app.title} / ${page.title}`
  if (app) return app.title
  if (apps.value.length === 0) return 'No apps yet'
  return 'Select page'
})

function syncSelectionFromCurrent() {
  const appFromPath = appNameFromPath(currentPath.value)
  if (appFromPath && apps.value.some(a => a.name === appFromPath)) {
    selectedApp.value = appFromPath
  } else if (!selectedApp.value && apps.value.length > 0) {
    selectedApp.value = apps.value[0]!.name
  }
}

// ---------------------------------------------------------------------------
// Lifecycle
// ---------------------------------------------------------------------------

onMounted(() => {
  document.addEventListener('mousedown', onDocClick)
  if (screenRef.value && typeof ResizeObserver !== 'undefined') {
    observer = new ResizeObserver(onPaneResized)
    observer.observe(screenRef.value)
  }
  void refreshPages()
  void startPreview()
})

onBeforeUnmount(() => {
  disposed = true
  document.removeEventListener('mousedown', onDocClick)
  if (leaveTimer) window.clearTimeout(leaveTimer)
  if (pollTimer) window.clearTimeout(pollTimer)
  if (resizeTimer) window.clearTimeout(resizeTimer)
  if (flushTimer) window.clearTimeout(flushTimer)
  stopInertia()
  observer?.disconnect()
})

watch(
  () => props.projectId,
  (next, prev) => {
    if (next && next !== prev) {
      frameSrc.value = null
      etag.value = undefined
      phase.value = 'idle'
      apps.value = []
      void refreshPages()
      void startPreview()
    }
  }
)

watch(apps, () => {
  if (!selectedApp.value && apps.value.length > 0) {
    syncSelectionFromCurrent()
  }
})

// Kept for existing callers of this component's public API.
const loadPreview = startPreview
defineExpose({ reload, loadPreview, navigateTo })
</script>
