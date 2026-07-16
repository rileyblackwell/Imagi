import api from '@/shared/services/api'

/**
 * Client for the browser-based project preview.
 *
 * The backend runs the project's dev servers plus a headless Chromium on its
 * own host and exposes it through these endpoints: the workspace polls JPEG
 * frames and forwards input events, so the preview works the same whether
 * Imagi runs locally or in production.
 */

/** One user-input event forwarded to the remote browser page. */
export interface PreviewInputEvent {
  kind: 'mouse' | 'wheel' | 'key'
  type?: 'mousePressed' | 'mouseReleased' | 'mouseMoved' | 'keyDown' | 'keyUp'
  x?: number
  y?: number
  button?: 'none' | 'left' | 'middle' | 'right'
  buttons?: number
  clickCount?: number
  deltaX?: number
  deltaY?: number
  key?: string
  code?: string
  text?: string
  keyCode?: number
  modifiers?: number
}

/** Snapshot of the remote page: navigation state plus (optionally) a frame. */
export interface PreviewFrame {
  running?: boolean
  /** Base64 JPEG. Null when it matched the etag we already have. */
  frame?: string | null
  etag?: string
  path?: string
  title?: string
  can_go_back?: boolean
  can_go_forward?: boolean
  viewport?: [number, number]
  device_scale_factor?: number
  error?: string
}

/** One navigable page of the previewed app, read from its actual router. */
export interface PreviewPage {
  title: string
  path: string
}

/** One app of the previewed project with its navigable pages. */
export interface PreviewApp {
  name: string
  title: string
  pages: PreviewPage[]
}

/** Thrown when the backend reports the session is gone (HTTP 409). */
export class PreviewNotRunningError extends Error {
  constructor(message = 'The preview session is not running.') {
    super(message)
    this.name = 'PreviewNotRunningError'
  }
}

// Starting can scaffold + npm-install a fresh project, which takes minutes.
const START_TIMEOUT_MS = 600_000

function rethrow(error: any): never {
  if (error?.response?.status === 409) {
    throw new PreviewNotRunningError(error.response?.data?.error)
  }
  const data = error?.response?.data
  const message =
    (typeof data?.error === 'string' && data.error) ||
    (typeof data?.detail === 'string' && data.detail) ||
    (error instanceof Error ? error.message : 'Preview request failed')
  throw new Error(message)
}

export const PreviewService = {
  /** Ensure dev servers + browser are running; idempotent. */
  async start(
    projectId: string,
    viewport?: { width: number; height: number },
    deviceScaleFactor?: number
  ): Promise<PreviewFrame> {
    try {
      const response = await api.post(
        `/v1/builder/${projectId}/preview/`,
        { viewport, device_scale_factor: deviceScaleFactor },
        { timeout: START_TIMEOUT_MS }
      )
      return response.data
    } catch (error) {
      rethrow(error)
    }
  },

  /** Current session state; running=false when nothing is up (never throws 409). */
  async status(projectId: string): Promise<PreviewFrame> {
    try {
      const response = await api.get(`/v1/builder/${projectId}/preview/`)
      return response.data
    } catch (error) {
      rethrow(error)
    }
  },

  async stop(projectId: string): Promise<void> {
    await api.delete(`/v1/builder/${projectId}/preview/`)
  },

  /** The project's apps and pages, derived from its real Vue routers. */
  async pages(projectId: string): Promise<PreviewApp[]> {
    try {
      const response = await api.get(`/v1/builder/${projectId}/pages/`)
      return response.data?.apps || []
    } catch (error) {
      rethrow(error)
    }
  },

  /** Poll the latest frame; pass the previous etag to skip unchanged frames. */
  async frame(projectId: string, etag?: string): Promise<PreviewFrame> {
    try {
      const response = await api.get(`/v1/builder/${projectId}/preview/frame/`, {
        params: etag ? { etag } : undefined,
      })
      return response.data
    } catch (error) {
      rethrow(error)
    }
  },

  /** Forward a batch of input events; the response includes a fresh frame. */
  async sendInput(
    projectId: string,
    events: PreviewInputEvent[],
    etag?: string
  ): Promise<PreviewFrame> {
    try {
      const response = await api.post(`/v1/builder/${projectId}/preview/input/`, {
        events,
        etag,
      })
      return response.data
    } catch (error) {
      rethrow(error)
    }
  },

  async navigate(
    projectId: string,
    action: 'goto' | 'back' | 'forward' | 'reload',
    path?: string
  ): Promise<PreviewFrame> {
    try {
      const response = await api.post(`/v1/builder/${projectId}/preview/navigate/`, {
        action,
        path,
      })
      return response.data
    } catch (error) {
      rethrow(error)
    }
  },

  /** Keep the remote viewport in sync with the preview pane's CSS size. */
  async resize(
    projectId: string,
    width: number,
    height: number,
    deviceScaleFactor?: number
  ): Promise<void> {
    try {
      await api.post(`/v1/builder/${projectId}/preview/resize/`, {
        width,
        height,
        device_scale_factor: deviceScaleFactor,
      })
    } catch (error) {
      rethrow(error)
    }
  },
}
