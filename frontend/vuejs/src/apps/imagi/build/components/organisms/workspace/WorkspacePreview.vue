<template>
  <div class="relative w-full h-full flex flex-col bg-white dark:bg-[#0a0a0a]">
    <!-- Toolbar -->
    <div class="flex items-center gap-1 px-2.5 py-2 border-b border-blue-950/[0.07] dark:border-white/[0.10] bg-[#fdf9f2]/50 dark:bg-white/[0.015]">
      <!-- Navigation controls — quiet ghost buttons, grouped as one cluster -->
      <div class="flex items-center gap-0.5 shrink-0">
        <button
          type="button"
          @click="goBack"
          :disabled="!canGoBack || phase !== 'ready'"
          title="Back"
          class="inline-flex items-center justify-center w-8 h-8 rounded-full text-blue-950/55 hover:text-blue-950 dark:text-blue-100/55 dark:hover:text-white hover:bg-blue-950/[0.06] dark:hover:bg-white/[0.07] active:scale-95 transition-[color,background-color,transform] duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0a0a0a] disabled:opacity-30 disabled:hover:bg-transparent disabled:hover:text-blue-950/55 disabled:cursor-not-allowed disabled:active:scale-100"
        >
          <i class="fas fa-arrow-left text-xs"></i>
        </button>

        <button
          type="button"
          @click="goForward"
          :disabled="!canGoForward || phase !== 'ready'"
          title="Forward"
          class="inline-flex items-center justify-center w-8 h-8 rounded-full text-blue-950/55 hover:text-blue-950 dark:text-blue-100/55 dark:hover:text-white hover:bg-blue-950/[0.06] dark:hover:bg-white/[0.07] active:scale-95 transition-[color,background-color,transform] duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0a0a0a] disabled:opacity-30 disabled:hover:bg-transparent disabled:hover:text-blue-950/55 disabled:cursor-not-allowed disabled:active:scale-100"
        >
          <i class="fas fa-arrow-right text-xs"></i>
        </button>

        <button
          type="button"
          @click="reload"
          title="Refresh page"
          class="inline-flex items-center justify-center w-8 h-8 rounded-full text-blue-950/55 hover:text-blue-950 dark:text-blue-100/55 dark:hover:text-white hover:bg-blue-950/[0.06] dark:hover:bg-white/[0.07] active:scale-95 transition-[color,background-color,transform] duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0a0a0a]"
        >
          <i class="fas fa-sync-alt text-xs" :class="{ 'fa-spin': phase === 'starting' }"></i>
        </button>

        <button
          type="button"
          @click="goHome"
          title="Go to home page"
          class="inline-flex items-center justify-center w-8 h-8 rounded-full text-blue-950/55 hover:text-blue-950 dark:text-blue-100/55 dark:hover:text-white hover:bg-blue-950/[0.06] dark:hover:bg-white/[0.07] active:scale-95 transition-[color,background-color,transform] duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0a0a0a]"
        >
          <i class="fas fa-home text-xs"></i>
        </button>
      </div>

      <!-- Hairline divider: separates controls from the address field -->
      <div class="w-px h-5 mx-1 shrink-0 bg-blue-950/[0.09] dark:bg-white/[0.12]"></div>

      <!-- Combined App / Page selector — the address bar -->
      <div class="relative flex-1 min-w-0" ref="menuRoot">
        <button
          type="button"
          @click="onMenuToggle"
          :disabled="apps.length === 0"
          class="group w-full flex items-center gap-2 h-9 rounded-full border border-blue-950/[0.10] dark:border-white/[0.14] bg-white dark:bg-white/[0.04] hover:border-blue-950/[0.22] dark:hover:border-white/[0.26] hover:shadow-[0_1px_2px_rgba(23,37,84,0.05)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0a0a0a] pl-3.5 pr-9 text-[13px] transition-[border-color,box-shadow] duration-150 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:shadow-none"
        >
          <i class="fas fa-globe text-[11px] shrink-0 text-blue-950/30 dark:text-blue-100/35 group-hover:text-blue-950/45 dark:group-hover:text-blue-100/50 transition-colors"></i>
          <span class="flex-1 truncate text-left font-medium text-blue-950 dark:text-white">{{ triggerLabel }}</span>
          <i class="fas fa-chevron-down absolute right-3.5 top-1/2 -translate-y-1/2 text-[10px] text-blue-950/35 dark:text-blue-100/40 pointer-events-none transition-transform duration-200" :class="{ 'rotate-180': menuOpen }"></i>
        </button>

        <!-- Directory tree: apps are folders, their pages are the files inside -->
        <div
          v-if="menuOpen && apps.length > 0"
          class="absolute z-20 mt-2 left-0 max-md:left-auto max-md:right-0 min-w-[17rem] max-md:max-w-[calc(100vw-1.5rem)] max-h-[60vh] overflow-y-auto rounded-2xl border border-blue-950/[0.08] dark:border-white/[0.12] bg-white dark:bg-[#0f0f0f] shadow-[0_16px_44px_-12px_rgba(23,37,84,0.22)] dark:shadow-[0_16px_44px_-12px_rgba(0,0,0,0.7)] p-1.5"
        >
          <div v-for="app in apps" :key="app.name">
            <!-- Folder row -->
            <button
              type="button"
              @click="toggleApp(app.name)"
              class="group/folder w-full flex items-center gap-2 px-2 py-1.5 rounded-lg text-[13px] font-medium text-blue-950 dark:text-white hover:bg-blue-950/[0.05] dark:hover:bg-white/[0.06] transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50"
            >
              <i
                class="fas fa-chevron-right text-[9px] w-3 shrink-0 text-blue-950/30 dark:text-blue-100/35 group-hover/folder:text-blue-950/50 dark:group-hover/folder:text-blue-100/55 transition-[transform,color] duration-200"
                :class="{ 'rotate-90': isExpanded(app.name) }"
              ></i>
              <i
                class="fas text-[12px] shrink-0 text-blue-950/40 dark:text-blue-100/45"
                :class="isExpanded(app.name) ? 'fa-folder-open' : 'fa-folder'"
              ></i>
              <span class="truncate">{{ app.title }}</span>
            </button>

            <!-- Files (pages) nested under the folder, with a tree guide line -->
            <div v-if="isExpanded(app.name)" class="ml-[1.05rem] pl-2 border-l border-blue-950/[0.08] dark:border-white/[0.10]">
              <p v-if="!app.pages.length" class="px-2 py-1.5 text-[12px] text-blue-950/35 dark:text-blue-100/35 italic">No pages</p>
              <button
                v-for="page in app.pages"
                :key="page.path"
                type="button"
                @click="onSelectPage(page.path)"
                :class="['group/file w-full flex items-center gap-2 px-2 py-1.5 rounded-lg text-[13px] text-left transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50',
                         page.path === currentPath
                           ? 'bg-blue-50 dark:bg-white/[0.08] font-medium text-blue-950 dark:text-white'
                           : 'text-blue-950/70 dark:text-blue-100/80 hover:bg-blue-950/[0.05] dark:hover:bg-white/[0.06]']"
              >
                <i
                  class="fas text-[11px] w-3.5 shrink-0"
                  :class="page.path === currentPath ? 'fa-circle-dot text-blue-600 dark:text-blue-300' : 'fa-file text-blue-950/30 dark:text-blue-100/35'"
                ></i>
                <span class="truncate flex-1">{{ page.title }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Screen: frames from the remote browser, input forwarded back -->
    <div
      ref="screenRef"
      tabindex="0"
      class="relative flex-1 min-h-0 bg-white dark:bg-[#0a0a0a] outline-none overflow-hidden touch-none"
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
        class="absolute bottom-3 left-3 right-3 z-10 flex items-center gap-2.5 rounded-xl border border-blue-100 dark:border-white/[0.08] bg-white/95 dark:bg-[#0f0f0f]/95 backdrop-blur px-3 py-2 shadow-lg"
        @pointerdown.stop
        @pointermove.stop
        @pointerup.stop
        @wheel.stop
      >
        <div class="w-7 h-7 shrink-0 rounded-full bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800/30 flex items-center justify-center">
          <i class="fas fa-exclamation-triangle text-red-600 dark:text-red-400 text-[10px]"></i>
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-[13px] font-medium text-blue-950 dark:text-white/90 leading-tight">Something broke in your app</p>
          <p class="text-[11px] text-blue-950/50 dark:text-white/45 truncate">{{ latestConsoleError.text }}</p>
        </div>
        <button
          type="button"
          @click="onFixConsoleError"
          class="shrink-0 inline-flex items-center gap-1.5 h-7 px-3 rounded-full text-[12px] font-medium bg-blue-950 text-[#fdf9f2] hover:bg-blue-900 dark:bg-[#f3ede2] dark:text-blue-950 dark:hover:bg-white transition-colors"
        >
          <i class="fas fa-wand-magic-sparkles text-[10px]"></i>
          Fix it
        </button>
        <button
          type="button"
          @click="dismissConsoleBanner"
          title="Dismiss"
          class="shrink-0 inline-flex items-center justify-center w-7 h-7 rounded-full text-blue-950/40 dark:text-white/40 hover:bg-blue-50 dark:hover:bg-white/[0.06] hover:text-blue-950/70 dark:hover:text-white/70 transition-colors"
        >
          <i class="fas fa-times text-[11px]"></i>
        </button>
      </div>

      <!-- Starting overlay -->
      <div
        v-if="phase === 'starting'"
        class="absolute inset-0 flex flex-col items-center justify-center gap-3 bg-white/90 dark:bg-[#0a0a0a]/90 text-blue-950/60 dark:text-blue-100/65"
      >
        <i class="fas fa-spinner fa-spin text-2xl"></i>
        <span class="text-sm font-medium">Starting preview…</span>
        <span class="text-xs text-blue-950/40 dark:text-blue-100/45 max-w-xs text-center">
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
        <p class="text-sm text-blue-950/70 dark:text-blue-100/70 max-w-md break-words">{{ error }}</p>
        <button
          @click="startPreview"
          class="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-blue-950/[0.14] dark:border-white/[0.16] bg-white dark:bg-white/[0.03] hover:bg-blue-950/[0.03] dark:hover:bg-white/[0.06] hover:border-blue-950/30 dark:hover:border-white/30 text-sm font-medium text-blue-950/80 hover:text-blue-950 dark:text-blue-100/80 dark:hover:text-white transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0a0a0a]"
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
        <div class="w-12 h-12 bg-blue-50 dark:bg-white/[0.05] border border-blue-950/[0.08] dark:border-white/[0.14] rounded-xl flex items-center justify-center">
          <i class="fas fa-pause text-blue-600 dark:text-blue-300"></i>
        </div>
        <p class="text-sm text-blue-950/70 dark:text-blue-100/70 max-w-md">The preview session has stopped.</p>
        <button
          @click="startPreview"
          class="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-blue-950/[0.14] dark:border-white/[0.16] bg-white dark:bg-white/[0.03] hover:bg-blue-950/[0.03] dark:hover:bg-white/[0.06] hover:border-blue-950/30 dark:hover:border-white/30 text-sm font-medium text-blue-950/80 hover:text-blue-950 dark:text-blue-100/80 dark:hover:text-white transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0a0a0a]"
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
  type PreviewConsoleError,
  type PreviewFrame,
  type PreviewInputEvent,
} from '../../../services/previewService'

const props = defineProps<{
  projectId: string
  /** Pane is hidden/backgrounded: keep the session warm but stop active work. */
  paused?: boolean
}>()

const emit = defineEmits<{
  /** "Fix it" pressed on the console-error banner; text is the raw error. */
  (e: 'fix-error', text: string): void
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

const menuOpen = ref(false)
// Folders (apps) start collapsed; this holds the ones currently open. When the
// menu opens we seed it with the folder holding the current page (see
// onMenuToggle) so you land on where you are without the whole tree unfurling.
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
        Math.hypot(x - touchDrag.startX, y - touchDrag.startY) > TOUCH_TAP_SLOP) {
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
  // Any scroll offset (optimistic or gliding) belongs to the page being left.
  stopInertia()
  resetLocalScroll()
  // Hard navigation clears the page's error buffer, so the same error text
  // on the fresh document should notify again.
  dismissedErrorKey.value = null
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
    // Open only the folder holding the current page, so you land on where you
    // are rather than the whole tree.
    const active = apps.value.find(a => a.pages.some(p => p.path === currentPath.value))
    expandedApps.value = active ? [active.name] : []
    // Routes may have changed since the last fetch (the agent edits routers);
    // refresh in the background whenever the menu opens.
    void refreshPages()
  }
}

// Folders start collapsed; expandedApps tracks the ones currently open.
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

// The collapsed address bar shows just the page you're on (e.g. "About").
const triggerLabel = computed(() => {
  if (apps.value.length === 0) return 'No pages yet'
  for (const app of apps.value) {
    const page = app.pages.find(p => p.path === currentPath.value)
    if (page) return page.title
  }
  return currentPath.value || 'Select page'
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

// Kept for existing callers of this component's public API.
const loadPreview = startPreview
defineExpose({ reload, loadPreview, navigateTo })
</script>
