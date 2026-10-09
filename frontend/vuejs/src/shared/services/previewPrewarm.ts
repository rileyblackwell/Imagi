import api from '@/shared/services/api'

/**
 * Keep the signed-in owner's most recently opened projects' previews warm, so
 * opening one finds its preview already running wherever they come from.
 *
 * From sign-in (or a restored session) until sign-out, a heartbeat asks the
 * workspace tier to start whichever of those previews isn't running and keep
 * the rest from idling out. It beats only while the tab is visible: a hidden
 * tab lets them go cold after the server's idle limit, and coming back beats
 * at once. The server bounds the work itself (how many projects, a host-wide
 * cap, a short idle limit once the beats stop) and throttles repeats; a
 * failed beat only means the workspace boots the preview on demand.
 *
 * The previews are rendered at the size the preview pane had last time, so
 * the workspace can show a warm one the moment it opens instead of waiting
 * for a resize.
 */

// Well inside the server's 10-minute idle limit for previews nobody opened.
const HEARTBEAT_MS = 2 * 60_000
// Visibility flips can come in bursts; the server throttles at a minute too.
const MIN_GAP_MS = 60_000

let warmToken: string | null = null
let heartbeat: ReturnType<typeof setInterval> | null = null
let lastBeatAt = 0
let listening = false

const VIEWPORT_KEY = 'imagi_preview_viewport'

interface RememberedViewport {
  viewport: { width: number; height: number }
  device_scale_factor: number
}

/** Record the preview pane's size, for the next prewarm to render at. */
export function rememberPreviewViewport(
  viewport: { width: number; height: number },
  deviceScaleFactor: number
): void {
  try {
    const value: RememberedViewport = { viewport, device_scale_factor: deviceScaleFactor }
    localStorage.setItem(VIEWPORT_KEY, JSON.stringify(value))
  } catch {
    // Storage unavailable: prewarms fall back to the server's default size.
  }
}

function rememberedViewport(): RememberedViewport | undefined {
  try {
    const value = JSON.parse(localStorage.getItem(VIEWPORT_KEY) || 'null')
    const { width, height } = value?.viewport || {}
    if (Number.isFinite(width) && Number.isFinite(height) && Number.isFinite(value.device_scale_factor)) {
      return value
    }
  } catch {
    // Unreadable: same fallback.
  }
  return undefined
}

function beat(): void {
  if (!warmToken || (typeof document !== 'undefined' && document.hidden)) return
  const now = Date.now()
  if (now - lastBeatAt < MIN_GAP_MS) return
  lastBeatAt = now
  Promise.resolve()
    .then(() => api.post('/v1/builder/preview/prewarm/', rememberedViewport() || {}))
    .catch(() => {
      // Best-effort; the workspace starts the preview itself when it opens.
    })
}

function onVisibilityChange(): void {
  if (!document.hidden) beat()
}

/** Start keeping this signed-in owner's recent previews warm. */
export function keepRecentPreviewsWarm(token: string | null): void {
  if (!token || token === warmToken) return
  warmToken = token
  lastBeatAt = 0
  beat()
  if (heartbeat) clearInterval(heartbeat)
  heartbeat = setInterval(beat, HEARTBEAT_MS)
  if (!listening && typeof document !== 'undefined') {
    document.addEventListener('visibilitychange', onVisibilityChange)
    listening = true
  }
}

/** Signed out: stop the heartbeat, and the server lets the previews go cold. */
export function stopKeepingPreviewsWarm(): void {
  warmToken = null
  if (heartbeat) clearInterval(heartbeat)
  heartbeat = null
}
