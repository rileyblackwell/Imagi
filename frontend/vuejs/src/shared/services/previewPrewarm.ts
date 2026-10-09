import api from '@/shared/services/api'

/**
 * Ask the workspace tier to start previews for the signed-in owner's most
 * recently opened projects, so opening one finds its preview already running.
 *
 * Fire and forget: the server answers at once, bounds the work itself (how
 * many projects, a host-wide cap, a short idle limit for sessions nobody
 * opens) and throttles repeats, and a failure only means the workspace boots
 * the preview on demand as before. Called once per sign-in per page load.
 */
let prewarmedToken: string | null = null

export function prewarmRecentPreviews(token: string | null): void {
  if (!token || token === prewarmedToken) return
  prewarmedToken = token
  Promise.resolve()
    .then(() => api.post('/v1/builder/preview/prewarm/'))
    .catch(() => {
      // Best-effort; the workspace starts the preview itself when it opens.
    })
}
