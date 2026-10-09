import api from '@/shared/services/api'

/**
 * Ask the workspace tier to start previews for the signed-in owner's most
 * recently opened projects, so opening one finds its preview already running.
 *
 * Fire and forget: the server answers at once, bounds the work itself (how
 * many projects, a host-wide cap, a short idle limit for sessions nobody
 * opens) and throttles repeats, and a failure only means the workspace boots
 * the preview on demand as before. Called once per sign-in per page load.
 *
 * The previews are rendered at the size the preview pane had last time, so
 * the workspace can show a prewarmed one the moment it opens instead of
 * waiting for a resize.
 */
let prewarmedToken: string | null = null

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

export function prewarmRecentPreviews(token: string | null): void {
  if (!token || token === prewarmedToken) return
  prewarmedToken = token
  Promise.resolve()
    .then(() => api.post('/v1/builder/preview/prewarm/', rememberedViewport() || {}))
    .catch(() => {
      // Best-effort; the workspace starts the preview itself when it opens.
    })
}
