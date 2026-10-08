<template>
  <div class="pv-root relative w-full h-full flex flex-col">
    <!-- The dock: one frosted pill floating on the stage above the app —
         navigation, and where you are (also the page menu). It sits in its own band rather than over the app,
         because anything laid over the frame would hide the app's own header. -->
    <div class="pv-dockbar">
      <div class="pv-dock">
        <div class="pv-rail shrink-0">
          <button
            type="button"
            @click="goBack"
            :disabled="!canGoBack || phase !== 'ready'"
            title="Back"
            aria-label="Back"
            class="pv-nav"
          >
            <i class="fas fa-arrow-left"></i>
          </button>

          <button
            type="button"
            @click="goForward"
            :disabled="!canGoForward || phase !== 'ready'"
            title="Forward"
            aria-label="Forward"
            class="pv-nav"
          >
            <i class="fas fa-arrow-right"></i>
          </button>

          <button
            type="button"
            @click="reload"
            title="Refresh page"
            aria-label="Refresh page"
            class="pv-nav"
          >
            <i class="fas fa-rotate-right" :class="{ 'fa-spin': busy }"></i>
          </button>

          <!-- Home has a second door (the home page is a row in the page
               menu), which is why it alone stands down on the narrowest phones. -->
          <button
            type="button"
            @click="goHome"
            title="Go to home page"
            aria-label="Go to home page"
            class="pv-nav pv-nav--home"
          >
            <i class="fas fa-house"></i>
          </button>
        </div>

        <span class="pv-dock-sep" aria-hidden="true"></span>

        <!-- The nameplate: the section of the app this page lives in, then the
             page itself ("home / About"). Also opens the page menu. -->
        <div class="relative flex-1 min-w-0" ref="menuRoot">
          <button
            type="button"
            @click="onMenuToggle"
            :disabled="apps.length === 0"
            :aria-expanded="menuOpen"
            aria-haspopup="true"
            class="pv-plate"
          >
            <span v-if="location.dir" class="pv-plate-dir">{{ location.dir }}</span>
            <span v-if="location.dir" class="pv-plate-sep" aria-hidden="true">/</span>
            <span class="pv-plate-page">{{ location.page }}</span>
            <i class="fas fa-chevron-down pv-plate-chevron" :class="{ 'rotate-180': menuOpen }"></i>
          </button>

          <!-- Every page in the project, grouped by the section it belongs to:
               folders, then the pages inside them. Names only — the menu is a
               map of the app, not of its source tree. -->
          <div v-if="menuOpen && apps.length > 0" class="pv-menu">
            <p class="pv-menu-head">
              Pages in your app
              <span class="pv-menu-count">{{ pageCount }}</span>
            </p>
            <div v-for="(app, i) in apps" :key="app.name" class="pv-row" :style="{ '--pv-i': i }">
              <button
                type="button"
                @click="toggleApp(app.name)"
                :aria-expanded="isExpanded(app.name)"
                class="pv-folder"
              >
                <i
                  class="fas fa-chevron-right pv-folder-chevron"
                  :class="{ 'rotate-90': isExpanded(app.name) }"
                ></i>
                <i
                  class="fas pv-folder-icon"
                  :class="isExpanded(app.name) ? 'fa-folder-open' : 'fa-folder'"
                ></i>
                <span class="truncate flex-1 text-left">{{ app.name }}</span>
                <span class="pv-folder-count">{{ app.pages.length }}</span>
              </button>

              <div v-if="isExpanded(app.name)" class="pv-files">
                <p v-if="!app.pages.length" class="pv-files-empty">No pages yet</p>
                <button
                  v-for="page in app.pages"
                  :key="page.path"
                  type="button"
                  @click="onSelectPage(page.path)"
                  :aria-current="page.path === currentPath ? 'page' : undefined"
                  :class="['pv-file', page.path === currentPath && 'pv-file--current']"
                >
                  <i class="fas fa-file-lines pv-file-icon"></i>
                  <span class="truncate flex-1">{{ page.title }}</span>
                  <span v-if="page.path === currentPath" class="pv-file-here">Viewing</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Back to the main agent: phones only, where the preview has
             replaced the chat (see canReturnToChat). -->
        <button
          v-if="canReturnToChat"
          type="button"
          @click="emit('return-to-chat')"
          class="pv-switch shrink-0"
          aria-label="Back to the coordinator"
        >
          <i class="fas fa-chevron-left pv-switch-chevron"></i>
          <i class="fas fa-comments pv-switch-icon"></i>
          <span class="pv-switch-label">Coordinator</span>
          <span v-if="returnCount" class="pv-switch-count">{{ returnCount }}</span>
        </button>

        <!-- Loading ribbon along the dock's lower edge while the session is
             starting or a navigation is in flight. -->
        <div v-if="busy" class="pv-progress" aria-hidden="true"></div>
      </div>
    </div>

    <!-- The frame: the app as a lit card on the stage. -->
    <div class="pv-stagewrap">
      <div class="pv-frame">

        <!-- Screen: frames from the remote browser, input forwarded back.
             NOTE for future edits: this element's box IS the remote viewport —
             paneSize() measures it and pageCoords() maps client coords through it
              1:1. Never give it padding, a border, or anything else that makes its
             rect disagree with the <img> inside; decoration goes on the background
             or in pointer-events-none overlays. -->
        <div
          ref="screenRef"
          tabindex="0"
          class="pv-stage relative flex-1 min-h-0 outline-none overflow-hidden touch-none"
          @pointerdown="onPointerDown"
          @pointermove="onPointerMove"
          @pointerup="onPointerUp"
          @pointercancel="onPointerCancel"
          @wheel.prevent="onWheel"
          @keydown="onKeyDown"
          @keyup="onKeyUp"
          @contextmenu.prevent
        >
          <!-- contain, not fill: pane and remote viewport can briefly disagree
               (resizes are debounced), and letterboxing against the container's
               background reads better than stretched text. The translate3d carries
               the optimistic local scroll (compositor-only, always present so the
               img keeps its own layer); gaps it opens show the container bg. -->
          <img
            v-if="frameSrc"
            :src="frameSrc"
            alt=""
            draggable="false"
            decoding="async"
            class="w-full h-full select-none pointer-events-none"
            :style="frameStyle"
          />

          <!-- Console-error banner: recent JS errors reported by the previewed
               page itself. Pointer events must not leak through to the screen's
               input forwarding underneath. -->
          <div
            v-if="consoleBannerVisible && latestConsoleError"
            class="pv-alert"
            @pointerdown.stop
            @pointermove.stop
            @pointerup.stop
            @wheel.stop
          >
            <span class="pv-alert-edge" aria-hidden="true"></span>
            <div class="pv-alert-mark">
              <i class="fas fa-exclamation"></i>
            </div>
            <div class="flex-1 min-w-0">
              <p class="pv-alert-title">Something broke in your app</p>
              <p class="pv-alert-detail">{{ latestConsoleError.text }}</p>
            </div>
            <button type="button" @click="onFixConsoleError" class="pv-btn pv-btn--ink shrink-0">
              <i class="fas fa-wand-magic-sparkles"></i>
              Fix it
            </button>
            <button
              type="button"
              @click="dismissConsoleBanner"
              title="Dismiss"
              aria-label="Dismiss"
              class="pv-alert-dismiss"
            >
              <i class="fas fa-times"></i>
            </button>
          </div>

          <!-- Starting: the wait is long enough (first start installs the whole
               dependency tree) that it gets a real progress story — an elapsed
               clock and copy that tracks which stage the wait is in. -->
          <div v-if="phase === 'starting'" class="pv-veil">
            <div class="pv-notice">
              <div class="pv-orbit" aria-hidden="true"><span class="pv-orbit-core"></span></div>
              <h3 class="pv-notice-title">Bringing your app to life</h3>
              <p class="pv-notice-body" aria-live="polite">{{ startingStage }}</p>
              <p class="pv-clock">{{ elapsedLabel }}</p>
            </div>
          </div>

          <!-- Error overlay -->
          <div v-else-if="phase === 'error'" class="pv-veil pv-veil--solid">
            <div class="pv-notice">
              <div class="pv-mark pv-mark--alert" aria-hidden="true">
                <i class="fas fa-triangle-exclamation"></i>
              </div>
              <h3 class="pv-notice-title">The preview couldn't start</h3>
              <p class="pv-notice-body">This is the preview server, not your app's code — a retry usually clears it.</p>
              <pre class="pv-code">{{ error }}</pre>
              <button @click="startPreview" class="pv-btn pv-btn--ink pv-btn--lg">
                <i class="fas fa-sync-alt"></i>
                Try again
              </button>
            </div>
          </div>

          <!-- Stopped overlay (session ended, e.g. idle shutdown or restart) -->
          <div v-else-if="phase === 'stopped'" class="pv-veil">
            <div class="pv-notice">
              <div class="pv-mark" aria-hidden="true">
                <i class="fas fa-moon"></i>
              </div>
              <h3 class="pv-notice-title">Your preview dozed off</h3>
              <p class="pv-notice-body">The session shuts down after a quiet spell to save you money. Everything you built is safe.</p>
              <button @click="startPreview" class="pv-btn pv-btn--ink pv-btn--lg">
                <i class="fas fa-play"></i>
                Wake it up
              </button>
            </div>
          </div>
        </div>
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
  type PreviewConsoleError,
  type PreviewFrame,
  type PreviewInputEvent,
} from '../../../services/previewService'

const props = defineProps<{
  projectId: string
  /** Pane is hidden/backgrounded: keep the session warm but stop active work. */
  paused?: boolean
  /**
   * The preview has replaced the panes rather than sitting beside them, and
   * nothing else on screen brings them back. True only on a phone showing the
   * preview: desktop collapses the sidebar from the top bar's toggle, which
   * stays put and is the way back there, so a second control would be a second
   * way to do one thing.
   */
  canReturnToChat?: boolean
  /** Badge on that return: how much has come back from the subagents and is
   *  sitting in the thread — questions to answer and work that just landed. */
  returnCount?: number
}>()

const emit = defineEmits<{
  /** "Fix it" pressed on the console-error banner; text is the raw error. */
  (e: 'fix-error', text: string): void
  /** Take me back to the main agent (the toolbar's return pill). */
  (e: 'return-to-chat'): void
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

// A navigation (goto/back/forward/reload) is waiting on the server. Purely
// presentational: it drives the loading ribbon and the refresh icon's spin.
const navigating = ref(false)
const busy = computed(() => phase.value === 'starting' || navigating.value)

const menuOpen = ref(false)
// The folders (apps) currently open in the page menu. Opening the menu opens
// all of them (see onMenuToggle); a folder can still be folded away by hand.
const expandedApps = ref<string[]>([])
const menuRoot = ref<HTMLElement | null>(null)
const screenRef = ref<HTMLElement | null>(null)

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

// Frames are decoded off-screen before being shown, so the JPEG decode never
// blocks the paint that displays it (decoding on the visible <img> stutters
// scrolling). The sequence numbers keep a slow decode from replacing a newer
// frame with an older one.
let frameSeq = 0
let shownFrameSeq = 0

function showFrame(src: string, onShown?: () => void) {
  const seq = ++frameSeq
  const img = new Image()
  img.src = src
  const show = () => {
    if (disposed) return
    if (seq > shownFrameSeq) {
      shownFrameSeq = seq
      frameSrc.value = src
    }
    // Fires even when a newer frame superseded this one: the pixels on screen
    // are at least as fresh as this frame, which is what callers care about.
    onShown?.()
  }
  img.decode().then(show, show)
}

// onShown fires once this frame's content is on screen (or immediately when
// the payload carried no bitmap — the pixels already shown are up to date).
function applyFrame(f: PreviewFrame, onShown?: () => void) {
  if (f.frame) {
    showFrame(`data:image/jpeg;base64,${f.frame}`, onShown)
  } else {
    onShown?.()
  }
  if (f.etag) etag.value = f.etag
  if (typeof f.path === 'string') currentPath.value = f.path
  canGoBack.value = !!f.can_go_back
  canGoForward.value = !!f.can_go_forward
  if (f.viewport) viewport.value = f.viewport
  // A full replacement list on every payload (empty array clears); guarded so
  // a payload from an older backend without the field keeps the current list.
  if (Array.isArray(f.console_errors)) consoleErrors.value = f.console_errors
}

// ---------------------------------------------------------------------------
// Console errors from the previewed page (backend contract: frame/status
// payloads carry the last ~5 uncaught errors, deduped, cleared on navigation)
// ---------------------------------------------------------------------------

const consoleErrors = ref<PreviewConsoleError[]>([])
// Key of the error the user dismissed; the banner stays hidden until a
// different error shows up.
const dismissedErrorKey = ref<string | null>(null)

function consoleErrorKey(err: PreviewConsoleError): string {
  // Text alone, no ts: the in-page collector bumps ts on every repeat of the
  // same error, so a ts-based key would resurrect a dismissed banner on the
  // next poll for any recurring error (the most common failure mode).
  return err.text
}

const latestConsoleError = computed<PreviewConsoleError | null>(() => {
  let latest: PreviewConsoleError | null = null
  for (const err of consoleErrors.value) {
    if (err?.text && (!latest || err.ts >= latest.ts)) latest = err
  }
  return latest
})

const consoleBannerVisible = computed(() =>
  phase.value === 'ready' &&
  latestConsoleError.value !== null &&
  consoleErrorKey(latestConsoleError.value) !== dismissedErrorKey.value
)

function dismissConsoleBanner() {
  if (latestConsoleError.value) dismissedErrorKey.value = consoleErrorKey(latestConsoleError.value)
}

function onFixConsoleError() {
  const err = latestConsoleError.value
  if (!err) return
  emit('fix-error', err.text)
  // The agent is on it; don't keep nagging about this same error.
  dismissConsoleBanner()
}

async function startPreview() {
  if (!props.projectId || phase.value === 'starting') return
  phase.value = 'starting'
  error.value = null
  try {
    const result = await PreviewService.start(props.projectId, paneSize(), deviceScaleFactor)
    if (disposed) return
    resetLocalScroll()
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
  stopInertia()
  resetLocalScroll()
}

// While paused the frames aren't visible, so polling drops to a slow
// keep-alive that stops the session from idling out — never the active
// cadence, even when a caller asks for a short delay.
const PAUSED_KEEPALIVE_MS = 20000

function schedulePoll(delay?: number) {
  if (pollTimer) window.clearTimeout(pollTimer)
  if (disposed) return
  if (props.paused) {
    pollTimer = window.setTimeout(pollFrame, PAUSED_KEEPALIVE_MS)
    return
  }
  const active = Date.now() - lastActivityAt < 4000
  pollTimer = window.setTimeout(pollFrame, delay ?? (active ? 120 : 1500))
}

async function pollFrame() {
  if (disposed || phase.value !== 'ready') return
  if (document.hidden) {
    schedulePoll(1000)
    return
  }
  if (inputInFlight) {
    // Input responses carry frames themselves; just check back in shortly.
    schedulePoll(300)
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
// Optimistic local scrolling
//
// A touch drag otherwise gives zero visual feedback until a server round trip
// returns a frame (150–500ms on mobile). So while a drag or its inertia glide
// is scrolling, the frame <img> is translated (compositor-only translate3d)
// by the deltas the server hasn't shown yet.
//
// Reconciliation: the offset is kept as two buckets of client-px deltas —
// `unsent` (wheel events still in inputQueue) and `inflight` (sent, response
// pending). When an input batch's response frame is actually on screen, that
// batch's share leaves the transform in the same paint that the bitmap takes
// it over, so fast networks show mostly bitmap motion and slow networks show
// mostly transform motion, without double-scroll in either. Known trade-offs,
// accepted: (a) a poll frame racing an input batch can briefly double-count
// that batch (rare — polling skips while input is in flight — and the input
// response corrects it); (b) over-scroll past the page edge translates pixels
// the server won't, then snaps back on ack — reads as a rubber-band.
//
// Vertical only: most previewed pages don't scroll horizontally, and a false
// horizontal shift on a slightly-diagonal swipe looks worse than no feedback.
// Horizontal wheel deltas still go to the server unchanged.
// ---------------------------------------------------------------------------

const localScrollY = ref(0)
let unsentLocalY = 0
let inflightLocalY = 0
// Bumped on reset so in-flight reconciliation closures from before the reset
// can't drive the buckets negative afterwards.
let localScrollGen = 0

const frameStyle = computed(() => ({
  objectFit: 'contain' as const,
  transform: `translate3d(0, ${localScrollY.value}px, 0)`,
}))

function updateLocalScroll() {
  // Beyond a screenful the content has fully left the pane, so cap there
  // (viewport height ≈ pane height; the two are kept in sync).
  const limit = viewport.value[1]
  localScrollY.value = Math.max(-limit, Math.min(unsentLocalY + inflightLocalY, limit))
}

function resetLocalScroll() {
  localScrollGen++
  wheelEdgeDir = 0
  unsentLocalY = 0
  inflightLocalY = 0
  localScrollY.value = 0
}

// Inertia deltas are produced in remote-page px; the transform wants client
// px. Same axis convention as pageCoords, inverted.
function pageToClientScaleY(): number {
  const rect = screenRef.value?.getBoundingClientRect()
  const vh = viewport.value[1]
  return rect && rect.height > 0 && vh > 0 ? rect.height / vh : 1
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
    // Sum the deltas but take the newest coordinates/modifiers — the merged
    // event must land where the pointer is now, or a scroll that crosses into
    // a nested scroll container keeps scrolling the old one.
    last.deltaX = (last.deltaX || 0) + (event.deltaX || 0)
    last.deltaY = (last.deltaY || 0) + (event.deltaY || 0)
    last.x = event.x
    last.y = event.y
    last.modifiers = event.modifiers
  } else {
    inputQueue.push(event)
  }
  if (inputQueue.length > 64) inputQueue = inputQueue.slice(-64)
  // Wheel events flush immediately: anything arriving while a batch is in
  // flight coalesces into the next one anyway, so pre-batching them only adds
  // latency between the gesture and the frame that shows it.
  scheduleFlush(immediate || event.kind === 'wheel' ? 0 : 24)
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
  // This batch's optimistic scroll stops being "unsent" now. `carried` (not a
  // blanket zeroing) keeps the accounting right when this response's decode
  // overlaps the next batch's flight.
  const carried = unsentLocalY
  const gen = localScrollGen
  const wheelDy = batch.reduce((sum, ev) => sum + (ev.kind === 'wheel' ? ev.deltaY || 0 : 0), 0)
  inflightLocalY += carried
  unsentLocalY = 0
  const settleCarried = () => {
    if (gen !== localScrollGen) return
    inflightLocalY -= carried
    updateLocalScroll()
  }
  try {
    const f = await PreviewService.sendInput(props.projectId, batch, etag.value)
    // The response reflects the whole batch (even as frame:null when pixels
    // didn't change, e.g. scrolled at the page edge): retire this batch's
    // share of the transform in the paint where the bitmap takes over.
    if (wheelDy !== 0 && gen === localScrollGen) wheelEdgeDir = f.frame ? 0 : Math.sign(wheelDy)
    applyFrame(f, settleCarried)
  } catch (e) {
    // Batch never applied server-side; its optimistic scroll must not persist.
    settleCarried()
    if (e instanceof PreviewNotRunningError) {
      markSessionStopped()
      return
    }
    // Drop the batch on transient failure; interaction continues from live state.
  } finally {
    inputInFlight = false
  }
  if (inputQueue.length > 0) scheduleFlush(0)
  schedulePoll() // activity-based: quick while the user is interacting
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
  // Client-px position, tracked separately from the page coords above: the
  // optimistic transform must follow the finger in screen pixels exactly.
  lastClientY: number
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
    // The glide moves the content optimistically too, same as the drag did.
    unsentLocalY += inertiaVy * dt * pageToClientScaleY()
    updateLocalScroll()
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
      lastClientY: e.clientY,
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
        Math.hypot(x - touchDrag.startX, y - touchDrag.startY)> TOUCH_TAP_SLOP) {
      touchDrag.scrolling = true
    }
    if (touchDrag.scrolling && (dx !== 0 || dy !== 0)) {
      // Wheel delta is opposite the finger travel: drag up -> scroll down.
      enqueue({ kind: 'wheel', x, y, deltaX: -dx, deltaY: -dy, modifiers: 0 })
      // Optimistic feedback: the content follows the finger immediately.
      unsentLocalY += e.clientY - touchDrag.lastClientY
      updateLocalScroll()
      // Track a smoothed finger velocity (px/ms) to seed the release glide.
      const dt = Math.max(1, e.timeStamp - touchDrag.lastT)
      touchDrag.vx = touchDrag.vx * 0.7 + (dx / dt) * 0.3
      touchDrag.vy = touchDrag.vy * 0.7 + (dy / dt) * 0.3
    }
    touchDrag.lastX = x
    touchDrag.lastY = y
    touchDrag.lastClientY = e.clientY
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
    // The gesture is void; snap the optimistic offset back to server truth.
    resetLocalScroll()
  }
}

// CDP's mouseWheel takes pixels; some browsers (Firefox with a mouse wheel)
// report lines or pages instead, which would scroll a few pixels per notch.
// Chromium's own line height for wheel scrolling is 40px.
const WHEEL_LINE_PX = 40

// Direction (1 down, -1 up) the page last refused to scroll in: a wheel batch
// whose response came back with unchanged pixels hit the page's edge (or a
// spot with nothing to scroll). Further wheel in that direction skips the
// optimistic shift, so a mouse wheel spun at the bottom of a page doesn't
// bounce the frame on every notch. Any batch that does move clears it.
let wheelEdgeDir = 0

function onWheel(e: WheelEvent) {
  if (phase.value !== 'ready') return
  const { x, y } = pageCoords(e)
  // Read the deltas before deltaMode: Firefox only reports line deltas to
  // pages that check deltaMode first.
  let deltaX = e.deltaX
  let deltaY = e.deltaY
  if (e.deltaMode === 1) {
    deltaX *= WHEEL_LINE_PX
    deltaY *= WHEEL_LINE_PX
  } else if (e.deltaMode === 2) {
    deltaX *= viewport.value[0]
    deltaY *= viewport.value[1]
  }
  enqueue({ kind: 'wheel', x, y, deltaX, deltaY, modifiers: modifiersFrom(e) })
  // Optimistic feedback, as for a touch drag: the frame moves now instead of
  // a round trip later. Ctrl+wheel is a zoom gesture, not a scroll.
  if (!e.ctrlKey && deltaY !== 0 && Math.sign(deltaY) !== wheelEdgeDir) {
    stopInertia()
    unsentLocalY -= deltaY * pageToClientScaleY()
    updateLocalScroll()
  }
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
  // Any scroll offset (optimistic or gliding) belongs to the page being left.
  stopInertia()
  resetLocalScroll()
  // Hard navigation clears the page's error buffer, so the same error text
  // on the fresh document should notify again.
  dismissedErrorKey.value = null
  navigating.value = true
  try {
    const f = await PreviewService.navigate(props.projectId, action, path)
    applyFrame(f)
    schedulePoll(300)
  } catch (e) {
    if (e instanceof PreviewNotRunningError) markSessionStopped()
  } finally {
    navigating.value = false
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

// Pane resizes that arrive while paused are remembered, not acted on — the
// pane is often mid-layout-change (e.g. another pane going fullscreen) and
// resizing the remote browser for sizes nobody sees is wasted work. The
// single viewport check on unpause applies whatever size the pane settled at.
let paneResizedWhilePaused = false

function onPaneResized() {
  if (props.paused) {
    paneResizedWhilePaused = true
    return
  }
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
  } catch {
    // Keep whatever menu we had; the preview itself is unaffected.
  }
}

function onMenuToggle() {
  menuOpen.value = !menuOpen.value
  if (menuOpen.value) {
    // Every section open: the menu's job is to show all the pages there are.
    expandedApps.value = apps.value.map(a => a.name)
    // Routes may have changed since the last fetch (the agent edits routers);
    // refresh in the background whenever the menu opens.
    void refreshPages()
  }
}

function isExpanded(name: string): boolean {
  return expandedApps.value.includes(name)
}

function toggleApp(name: string) {
  const i = expandedApps.value.indexOf(name)
  if (i >= 0) expandedApps.value.splice(i, 1)
  else expandedApps.value.push(name)
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

const pageCount = computed(() => apps.value.reduce((n, a) => n + a.pages.length, 0))

function onSelectPage(path: string) {
  navigateTo(path)
  menuOpen.value = false
}

function onDocClick(e: MouseEvent) {
  if (!menuOpen.value) return
  if (menuRoot.value && !menuRoot.value.contains(e.target as Node)) {
    menuOpen.value = false
  }
}

// What the collapsed plate says: the section of the app holding the current
// page, then the page by name, as the menu lists it — "home / About".
const location = computed(() => {
  for (const app of apps.value) {
    const page = app.pages.find(p => p.path === currentPath.value)
    if (page) return { dir: app.name, page: page.title }
  }
  // No router claims this path — a 404, or a route the agent added since the
  // last fetch. There is no folder to name, so show the address itself.
  if (apps.value.length === 0) return { dir: '', page: 'No pages yet' }
  return { dir: '', page: currentPath.value || '/' }
})

// ---------------------------------------------------------------------------
// Start-up progress
//
// A cold start installs the project's whole dependency tree, so the wait runs
// to minutes. A bare spinner reads as "hung" at that length; an elapsed clock
// and copy that names the current stage read as "working".
// ---------------------------------------------------------------------------

const elapsed = ref(0)
let elapsedTimer: number | null = null

function stopElapsed() {
  if (elapsedTimer) {
    window.clearInterval(elapsedTimer)
    elapsedTimer = null
  }
}

watch(phase, (p) => {
  stopElapsed()
  if (p !== 'starting') return
  elapsed.value = 0
  const startedAt = Date.now()
  elapsedTimer = window.setInterval(() => {
    elapsed.value = Math.floor((Date.now() - startedAt) / 1000)
  }, 1000)
})

const elapsedLabel = computed(() => {
  const s = elapsed.value
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`
})

// Thresholds are the shape of a real cold start, not a promise about it — the
// copy stays true even if a stage runs long, because none of it claims to be
// nearly done until the wait is genuinely unusual. Dependencies are never
// installed here: every project links to a store installed once per machine
// at creation, and the servers start in a second or two — so a wait past a
// few seconds is the app compiling, and only a wait past that on a fresh
// machine (empty store) is an install.
const startingStage = computed(() => {
  const s = elapsed.value
  if (s < 5) return 'Waking the preview server…'
  if (s < 30) return 'Compiling your app…'
  if (s < 90) return 'Still going — a first start on a new machine installs dependencies, which can take a few minutes.'
  return 'Still going — a first start can take a few minutes.'
})

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
  if (pollTimer) window.clearTimeout(pollTimer)
  if (resizeTimer) window.clearTimeout(resizeTimer)
  if (flushTimer) window.clearTimeout(flushTimer)
  stopElapsed()
  stopInertia()
  observer?.disconnect()
})

watch(
  () => props.projectId,
  (next, prev) => {
    if (next && next !== prev) {
      shownFrameSeq = ++frameSeq // drop any frame still decoding for the old project
      frameSrc.value = null
      etag.value = undefined
      phase.value = 'idle'
      apps.value = []
      stopInertia()
      resetLocalScroll()
      consoleErrors.value = []
      dismissedErrorKey.value = null
      void refreshPages()
      void startPreview()
    }
  }
)

watch(
  () => props.paused,
  (paused) => {
    if (disposed) return
    if (paused) {
      // A resize debounce armed just before pausing must not resize the
      // remote browser mid-pause; fold it into the deferred-resize marker.
      if (resizeTimer) {
        window.clearTimeout(resizeTimer)
        resizeTimer = null
        paneResizedWhilePaused = true
      }
      // Nobody can see the pane; a glide or half-reconciled optimistic offset
      // must not keep running (or linger) into the background.
      stopInertia()
      resetLocalScroll()
      // Likewise a poll timer set moments ago could still fire at the active
      // cadence; rescheduling drops it to the keep-alive interval right away.
      schedulePoll()
      return
    }
    // Unpaused: fetch a frame immediately — the one on screen may be minutes
    // old.
    void pollFrame()
    if (paneResizedWhilePaused) {
      paneResizedWhilePaused = false
      // The pane's geometry was in flux while paused (that's what set the
      // flag), so measure after layout settles — the same reason startPreview
      // re-asserts its first measurement in a rAF.
      requestAnimationFrame(() => void ensureViewportMatchesPane())
    } else {
      // Nothing was deferred, but re-check anyway; it no-ops when in sync.
      void ensureViewportMatchesPane()
    }
  }
)

defineExpose({ reload })
</script>

<style scoped>
/* ---------------------------------------------------------------------------
   Glass Dock. The preview pane is a Spotlight stage: the user's app sits on it
   as a lit card, and the controls float above it in one
   frosted pill. The chrome stays quiet so the app is the brightest thing here.
   Colours come from the --sl-* tokens (shared/styles/spotlight.css), so the
   light and dark themes differ only there.
   --------------------------------------------------------------------------- */

.pv-root {
  background-color: var(--sl-bg, #f8f7f4);
  background-image: radial-gradient(70% 320px at 50% -80px, var(--sl-spot-core, rgba(255, 170, 110, 0.3)), transparent 70%);
}

/* --- The dock ------------------------------------------------------------ */

.pv-dockbar {
  position: relative;
  z-index: 3;
  display: flex;
  flex-shrink: 0;
  justify-content: center;
  padding: 0.75rem 1rem 0.625rem;
}

.pv-dock {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  width: 100%;
  max-width: 44rem;
  padding: 0.25rem;
  border-radius: 9999px;
  border: 1px solid var(--sl-line-strong, rgba(20, 21, 30, 0.15));
  background: color-mix(in srgb, var(--sl-surface, #ffffff) 72%, transparent);
  backdrop-filter: blur(16px) saturate(1.4);
  -webkit-backdrop-filter: blur(16px) saturate(1.4);
  box-shadow: var(--sl-card-shadow, 0 14px 34px -20px rgba(20, 21, 30, 0.2));
}

.pv-dock-sep {
  flex-shrink: 0;
  width: 1px;
  height: 1.125rem;
  margin: 0 0.125rem;
  background: var(--sl-line-strong, rgba(20, 21, 30, 0.15));
}

.pv-rail {
  display: flex;
  align-items: center;
  gap: 0.0625rem;
}

.pv-nav {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  color: var(--sl-muted, #5c6172);
  cursor: pointer;
  transition: color 0.15s ease, background-color 0.15s ease, transform 0.15s ease;
}

.pv-nav:hover:not(:disabled) {
  color: var(--sl-text, #14151c);
  background: var(--sl-chip-bg-hover, rgba(20, 21, 30, 0.065));
}

.pv-nav:active:not(:disabled) { transform: scale(0.92); }

.pv-nav:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.pv-nav:focus-visible,
.pv-plate:focus-visible,
.pv-switch:focus-visible {
  outline: none;
  box-shadow: 0 0 0 2px var(--sl-focus, #d9730d);
}

/* --- The nameplate ------------------------------------------------------- */

.pv-plate {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.375rem;
  width: 100%;
  height: 2rem;
  padding: 0 2rem 0 0.875rem;
  border-radius: 9999px;
  text-align: left;
  background: var(--sl-chip-bg, rgba(20, 21, 30, 0.035));
  cursor: pointer;
  transition: background-color 0.16s ease;
}

.pv-plate:hover:not(:disabled) { background: var(--sl-chip-bg-hover, rgba(20, 21, 30, 0.065)); }

.pv-plate:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.pv-plate-dir {
  flex-shrink: 0;
  max-width: 10rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.8125rem;
  color: var(--sl-faint, #8a8fa0);
}

.pv-plate-sep {
  flex-shrink: 0;
  font-size: 0.8125rem;
  color: var(--sl-faint, #8a8fa0);
  opacity: 0.6;
}

.pv-plate-page {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-family: var(--sl-font-display);
  font-size: 0.875rem;
  font-weight: 600;
  letter-spacing: -0.01em;
  color: var(--sl-text, #14151c);
}

/* Narrow panes drop the section before the page name ever truncates. */
@media (max-width: 640px) {
  .pv-plate-dir,
  .pv-plate-sep { display: none; }
}

.pv-plate-chevron {
  position: absolute;
  right: 0.875rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.5625rem;
  color: var(--sl-faint, #8a8fa0);
  pointer-events: none;
  transition: transform 0.2s ease;
}

.pv-plate-chevron.rotate-180 { transform: translateY(-50%) rotate(180deg); }

/* --- Back to the main agent (phones) ------------------------------------- */

.pv-switch {
  display: inline-flex;
  align-items: center;
  gap: 0.3125rem;
  height: 2rem;
  padding: 0 0.75rem;
  border-radius: 9999px;
  background: var(--sl-chip-bg, rgba(20, 21, 30, 0.035));
  color: var(--sl-muted, #5c6172);
  font-size: 0.75rem;
  font-weight: 500;
  white-space: nowrap;
  cursor: pointer;
  transition: background-color 0.16s ease, color 0.16s ease;
}

.pv-switch:hover {
  background: var(--sl-chip-bg-hover, rgba(20, 21, 30, 0.065));
  color: var(--sl-text, #14151c);
}

.pv-switch-chevron { font-size: 0.5rem; opacity: 0.55; }
.pv-switch-icon { font-size: 0.625rem; opacity: 0.75; }

.pv-switch-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 1.0625rem;
  height: 1.0625rem;
  padding: 0 0.25rem;
  border-radius: 9999px;
  background: var(--sl-grad);
  color: var(--sl-on-accent, #1a0e08);
  font-size: 0.625rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  line-height: 1;
}

/* Loading ribbon: a travelling sliver of the coral-to-amber light along the
   dock's lower edge. */
.pv-progress {
  position: absolute;
  left: 1.25rem;
  right: 1.25rem;
  bottom: -1px;
  height: 2px;
  overflow: hidden;
  border-radius: 2px;
  pointer-events: none;
}

.pv-progress::after {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  width: 34%;
  border-radius: 2px;
  background: var(--sl-grad);
  animation: pv-slide 1.2s ease-in-out infinite;
}

@keyframes pv-slide {
  0% { transform: translateX(-110%); }
  100% { transform: translateX(400%); }
}

/* --- The page menu ------------------------------------------------------- */

.pv-menu {
  position: absolute;
  z-index: 20;
  left: 50%;
  margin-top: 0.625rem;
  width: 20rem;
  max-width: calc(100vw - 1.5rem);
  max-height: 60vh;
  overflow-y: auto;
  padding: 0.375rem;
  border-radius: 1rem;
  border: 1px solid var(--sl-line-strong, rgba(20, 21, 30, 0.15));
  background: var(--sl-surface, #ffffff);
  box-shadow: var(--sl-card-shadow), 0 24px 60px -24px rgba(0, 0, 0, 0.35);
  transform: translateX(-50%);
  transform-origin: top center;
  animation: pv-menu-in 0.16s cubic-bezier(0.2, 0.9, 0.3, 1) both;
}

.dark .pv-menu {
  background: var(--sl-surface-2, #1a1d28);
  box-shadow: 0 24px 60px -20px rgba(0, 0, 0, 0.85);
}

@keyframes pv-menu-in {
  from { opacity: 0; transform: translate(-50%, -4px) scale(0.98); }
  to { opacity: 1; transform: translateX(-50%); }
}

.pv-menu-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.375rem 0.625rem 0.5rem;
  margin-bottom: 0.25rem;
  border-bottom: 1px solid var(--sl-line, rgba(20, 21, 30, 0.09));
  font-size: 0.6875rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--sl-faint, #8a8fa0);
}

.pv-menu-count,
.pv-folder-count {
  font-size: 0.6875rem;
  font-weight: 500;
  font-variant-numeric: tabular-nums;
  letter-spacing: 0;
  color: var(--sl-faint, #8a8fa0);
}

.pv-row {
  animation: pv-row-in 0.22s ease both;
  animation-delay: calc(var(--pv-i, 0) * 28ms);
}

@keyframes pv-row-in {
  from { opacity: 0; transform: translateY(-3px); }
  to { opacity: 1; transform: none; }
}

.pv-folder {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.4375rem 0.625rem;
  border-radius: 0.625rem;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--sl-text, #14151c);
  cursor: pointer;
  transition: background-color 0.14s ease;
}

.pv-folder:hover { background: var(--sl-chip-bg, rgba(20, 21, 30, 0.035)); }

.pv-folder:focus-visible,
.pv-file:focus-visible {
  outline: none;
  box-shadow: inset 0 0 0 2px var(--sl-focus, #d9730d);
}

.pv-folder-chevron {
  width: 0.625rem;
  flex-shrink: 0;
  font-size: 0.5rem;
  color: var(--sl-faint, #8a8fa0);
  transition: transform 0.2s ease;
}

.pv-folder-chevron.rotate-90 { transform: rotate(90deg); }

.pv-folder-icon {
  flex-shrink: 0;
  width: 0.875rem;
  font-size: 0.75rem;
  color: var(--sl-amber, #ee8c10);
}

.pv-files {
  margin: 0.0625rem 0 0.25rem 1.3125rem;
  padding-left: 0.5rem;
  border-left: 1px solid var(--sl-line, rgba(20, 21, 30, 0.09));
}

.pv-files-empty {
  padding: 0.375rem 0.625rem;
  font-size: 0.75rem;
  font-style: italic;
  color: var(--sl-faint, #8a8fa0);
}

.pv-file {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.4375rem 0.625rem;
  border-radius: 0.625rem;
  font-size: 0.8125rem;
  text-align: left;
  color: var(--sl-muted, #5c6172);
  cursor: pointer;
  transition: background-color 0.14s ease, color 0.14s ease;
}

.pv-file:hover {
  background: var(--sl-chip-bg, rgba(20, 21, 30, 0.035));
  color: var(--sl-text, #14151c);
}

.pv-file--current {
  background: var(--sl-chip-bg-hover, rgba(20, 21, 30, 0.065));
  font-weight: 600;
  color: var(--sl-text, #14151c);
}

.pv-file-icon {
  width: 0.875rem;
  flex-shrink: 0;
  font-size: 0.6875rem;
  color: var(--sl-faint, #8a8fa0);
}

.pv-file--current .pv-file-icon { color: var(--sl-coral, #ec4a33); }

.pv-file-here {
  flex-shrink: 0;
  font-size: 0.6875rem;
  font-weight: 500;
  color: var(--sl-coral, #ec4a33);
}

/* --- The stage and the frame --------------------------------------------- */

.pv-stagewrap {
  position: relative;
  display: flex;
  flex: 1;
  min-height: 0;
  justify-content: center;
  padding: 0 1rem 1rem;
}

/* The app as a lit card: rounded, edged with a hairline, and set on the
   stage's light. Decoration lives here, never on .pv-stage (see the note on
   the screen element in the template). */
.pv-frame {
  position: relative;
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
  min-height: 0;
  overflow: hidden;
  border-radius: 1rem;
  border: 1px solid var(--sl-line-strong, rgba(20, 21, 30, 0.15));
  box-shadow: var(--sl-win-shadow, 0 40px 90px -40px rgba(20, 21, 30, 0.45));
}

/* What shows through when the frame and remote viewport briefly disagree, or
   an optimistic scroll opens a gap: a quiet matte, not a glitch. */
.pv-stage {
  background-color: var(--sl-bg-deep, #f0eee9);
}

/* Phones: the preview already fills a phone, so no stage margins and no
   card. */
@media (max-width: 767px) {
  .pv-dockbar { padding: 0.5rem; }

  .pv-dock { gap: 0.125rem; }

  .pv-nav {
    width: 1.75rem;
    height: 1.75rem;
  }

  .pv-stagewrap {
    padding: 0;
    background-image: none;
  }

  .pv-frame {
    border: 0;
    border-top: 1px solid var(--sl-line, rgba(20, 21, 30, 0.09));
    border-radius: 0;
    box-shadow: none;
  }

  .pv-switch {
    height: 1.75rem;
    gap: 0.25rem;
    padding: 0 0.5rem;
  }
}

/* The narrowest phones (320px): Home goes (the page menu has it) and the
   switch drops its chevron, so the page name keeps a readable share. */
@media (max-width: 359px) {
  .pv-switch-chevron,
  .pv-nav--home,
  .pv-dock-sep { display: none; }
}

/* --- Notices (starting / stopped / error) -------------------------------- */

.pv-veil {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  background: color-mix(in srgb, var(--sl-bg-deep, #f5f0e7) 86%, transparent);
  backdrop-filter: blur(6px);
}

.pv-veil--solid { background: var(--sl-bg-deep, #f5f0e7); }

.dark .pv-veil { background: color-mix(in srgb, var(--sl-bg-deep, #0b0b0d) 88%, transparent); }
.dark .pv-veil--solid { background: var(--sl-bg-deep, #0b0b0d); }

.pv-notice {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  max-width: 23rem;
  padding: 1.75rem 1.5rem 1.5rem;
  border-radius: 1.25rem;
  border: 1px solid rgba(19, 26, 44, 0.08);
  background: #fbfaf7;
  text-align: center;
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.8),
    0 24px 60px -24px rgba(19, 26, 44, 0.3);
  animation: pv-notice-in 0.3s cubic-bezier(0.2, 0.9, 0.3, 1) both;
}

.dark .pv-notice {
  border-color: rgba(255, 255, 255, 0.1);
  background: #121214;
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.04),
    0 24px 60px -24px rgba(0, 0, 0, 0.9);
}

@keyframes pv-notice-in {
  from { opacity: 0; transform: translateY(8px) scale(0.985); }
  to { opacity: 1; transform: none; }
}

.pv-notice-title {
  font-family: var(--sl-font-display, theme('fontFamily.display'));
  font-variation-settings: 'opsz' 24, 'SOFT' 30, 'WONK' 1;
  font-size: 1.0625rem;
  font-weight: 600;
  letter-spacing: -0.012em;
  color: theme('colors.blue.950');
}

.dark .pv-notice-title { color: rgba(255, 255, 255, 0.94); }

.pv-notice-body {
  max-width: 19rem;
  font-size: 0.8125rem;
  line-height: 1.5;
  color: rgba(19, 26, 44, 0.55);
}

.dark .pv-notice-body { color: rgba(219, 234, 254, 0.55); }

/* Elapsed clock: proof of life while a cold start installs a dependency tree */
.pv-clock {
  margin-top: 0.125rem;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 0.6875rem;
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.04em;
  color: rgba(19, 26, 44, 0.35);
}

.dark .pv-clock { color: rgba(219, 234, 254, 0.35); }

/* A ring of ink drawn once around, with a heartbeat at the centre. */
.pv-orbit {
  position: relative;
  display: grid;
  place-items: center;
  width: 3.25rem;
  height: 3.25rem;
  margin-bottom: 0.375rem;
}

.pv-orbit::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 9999px;
  background: conic-gradient(
    from 0deg,
    rgba(19, 26, 44, 0) 0deg,
    rgba(19, 26, 44, 0.1) 150deg,
    rgba(19, 26, 44, 0.85) 355deg
  );
  -webkit-mask: radial-gradient(farthest-side, transparent calc(100% - 2.5px), #000 calc(100% - 2.5px));
  mask: radial-gradient(farthest-side, transparent calc(100% - 2.5px), #000 calc(100% - 2.5px));
  animation: pv-rotate 1.1s linear infinite;
}

.dark .pv-orbit::before {
  background: conic-gradient(
    from 0deg,
    rgba(243, 237, 226, 0) 0deg,
    rgba(243, 237, 226, 0.12) 150deg,
    rgba(243, 237, 226, 0.9) 355deg
  );
}

.pv-orbit-core {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 9999px;
  background: theme('colors.blue.950');
  animation: pv-breathe 1.8s ease-in-out infinite;
}

.dark .pv-orbit-core { background: #f3ede2; }

@keyframes pv-rotate {
  to { transform: rotate(360deg); }
}

/* Notice marks: the same rounded plaque as the pane header's mark */
.pv-mark {
  display: grid;
  place-items: center;
  width: 2.75rem;
  height: 2.75rem;
  margin-bottom: 0.5rem;
  border-radius: 0.875rem;
  background: rgba(19, 26, 44, 0.06);
  color: rgba(19, 26, 44, 0.6);
  font-size: 0.9375rem;
  box-shadow: inset 0 0 0 1px rgba(19, 26, 44, 0.06);
}

.pv-mark--alert {
  background: rgba(239, 68, 68, 0.08);
  color: #dc2626;
  box-shadow: inset 0 0 0 1px rgba(239, 68, 68, 0.18);
}

.dark .pv-mark {
  background: rgba(243, 237, 226, 0.09);
  color: rgba(243, 237, 226, 0.75);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.07);
}

.dark .pv-mark--alert {
  background: rgba(239, 68, 68, 0.12);
  color: #f87171;
  box-shadow: inset 0 0 0 1px rgba(239, 68, 68, 0.25);
}

/* Raw server text stays raw — mono, boxed, and scrollable rather than
   dressed up as prose. */
.pv-code {
  width: 100%;
  max-height: 7rem;
  overflow: auto;
  margin: 0.375rem 0 0.25rem;
  padding: 0.5rem 0.625rem;
  border-radius: 0.625rem;
  border: 1px solid rgba(19, 26, 44, 0.08);
  background: rgba(19, 26, 44, 0.035);
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 0.6875rem;
  line-height: 1.5;
  text-align: left;
  white-space: pre-wrap;
  word-break: break-word;
  color: rgba(19, 26, 44, 0.65);
}

.dark .pv-code {
  border-color: rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
  color: rgba(219, 234, 254, 0.65);
}

/* --- Buttons (navy ink) --------------------------------------------------- */

.pv-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  height: 1.75rem;
  padding: 0 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.18s ease, box-shadow 0.18s ease, transform 0.18s ease;
}

.pv-btn i { font-size: 0.625rem; }

.pv-btn--lg {
  height: 2.125rem;
  margin-top: 0.625rem;
  padding: 0 1.125rem;
  font-size: 0.8125rem;
}

.pv-btn--ink {
  background: theme('colors.blue.950');
  color: #fbfaf7;
  box-shadow:
    0 1px 2px rgba(19, 26, 44, 0.2),
    0 3px 8px -2px rgba(19, 26, 44, 0.25);
}

.pv-btn--ink:hover {
  background: theme('colors.blue.900');
  transform: translateY(-1px);
  box-shadow:
    0 2px 3px rgba(19, 26, 44, 0.2),
    0 6px 14px -4px rgba(19, 26, 44, 0.3);
}

.pv-btn--ink:active { transform: translateY(0); }

.pv-btn:focus-visible {
  outline: none;
  box-shadow: 0 0 0 2px #fbfaf7, 0 0 0 4px rgba(194, 65, 12, 0.4);
}

.dark .pv-btn--ink {
  background: #f3ede2;
  color: theme('colors.blue.950');
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.4),
    0 3px 8px -2px rgba(0, 0, 0, 0.45);
}

.dark .pv-btn--ink:hover { background: #ffffff; }

.dark .pv-btn:focus-visible {
  box-shadow: 0 0 0 2px #121214, 0 0 0 4px rgba(251, 191, 36, 0.5);
}

/* --- Console-error banner ------------------------------------------------- */

.pv-alert {
  position: absolute;
  z-index: 10;
  left: 0.75rem;
  right: 0.75rem;
  bottom: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.625rem;
  overflow: hidden;
  padding: 0.5rem 0.625rem 0.5rem 0.875rem;
  border-radius: 0.875rem;
  border: 1px solid rgba(19, 26, 44, 0.08);
  background: rgba(253, 249, 242, 0.96);
  backdrop-filter: blur(8px);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.8),
    0 16px 36px -16px rgba(19, 26, 44, 0.4);
  animation: pv-alert-in 0.26s cubic-bezier(0.2, 0.9, 0.3, 1) both;
}

.dark .pv-alert {
  border-color: rgba(255, 255, 255, 0.1);
  background: rgba(18, 18, 20, 0.96);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.04),
    0 16px 36px -16px rgba(0, 0, 0, 0.9);
}

@keyframes pv-alert-in {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: none; }
}

/* A stripe of alarm down the edge — enough to read as "wrong" from the corner
   of the eye without turning the whole card red. */
.pv-alert-edge {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: linear-gradient(180deg, #f87171, #dc2626);
}

.pv-alert-mark {
  display: grid;
  place-items: center;
  flex-shrink: 0;
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 9999px;
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
  font-size: 0.625rem;
  box-shadow: inset 0 0 0 1px rgba(239, 68, 68, 0.2);
}

.dark .pv-alert-mark {
  background: rgba(239, 68, 68, 0.14);
  color: #f87171;
}

.pv-alert-title {
  font-size: 0.8125rem;
  font-weight: 500;
  line-height: 1.25;
  color: theme('colors.blue.950');
}

.dark .pv-alert-title { color: rgba(255, 255, 255, 0.92); }

.pv-alert-detail {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 0.6875rem;
  color: rgba(19, 26, 44, 0.5);
}

.dark .pv-alert-detail { color: rgba(219, 234, 254, 0.45); }

.pv-alert-dismiss {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 1.75rem;
  height: 1.75rem;
  border-radius: 9999px;
  font-size: 0.6875rem;
  color: rgba(19, 26, 44, 0.4);
  cursor: pointer;
  transition: background-color 0.14s ease, color 0.14s ease;
}

.pv-alert-dismiss:hover {
  background: rgba(19, 26, 44, 0.06);
  color: rgba(19, 26, 44, 0.7);
}

.pv-alert-dismiss:focus-visible {
  outline: none;
  box-shadow: 0 0 0 2px #fbfaf7, 0 0 0 4px rgba(194, 65, 12, 0.4);
}

.dark .pv-alert-dismiss { color: rgba(255, 255, 255, 0.4); }

.dark .pv-alert-dismiss:hover {
  background: rgba(255, 255, 255, 0.07);
  color: rgba(255, 255, 255, 0.75);
}

@media (prefers-reduced-motion: reduce) {
  .pv-progress::after,
  .pv-orbit::before,
  .pv-orbit-core {
    animation: none;
  }

  .pv-menu,
  .pv-row,
  .pv-notice,
  .pv-alert {
    animation-duration: 0.01ms;
  }

  .pv-btn--ink:hover { transform: none; }
}
</style>
