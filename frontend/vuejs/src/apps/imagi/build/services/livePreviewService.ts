import api from '@/shared/services/api'

/**
 * Client for the live preview (backend: live_preview_service.py).
 *
 * The project's own Vite dev server is shown in an iframe on a separate
 * preview origin, so the user's browser renders the app natively. These
 * endpoints start it, report the dev servers' health and start progress,
 * stream their logs and run server actions. Everything the page itself does
 * (where it is, what it logs, its requests) arrives from the bridge script
 * inside the iframe over postMessage; see parseBridgeMessage below.
 */

export type PreviewMode = 'live' | 'stream'

export interface LiveStartResult {
  running: boolean
  mode: 'live'
  /** Full URL of the app's root, e.g. https://preview.host/s/<token>/ */
  url: string
  /** Origin the iframe runs on; the only one its messages are taken from. */
  origin: string
  /** The session's path prefix on that origin, "/s/<token>/". */
  base: string
  cold?: boolean
  error?: string
}

export type ServerState = 'ready' | 'reloading' | 'crashed' | 'stopped' | 'starting'

export interface ServerStatus {
  state: ServerState
  port?: number | null
  log_changed_at?: number | null
}

export interface StartStage {
  key: string
  label: string
  state: 'pending' | 'running' | 'done' | 'failed'
  ms?: number
  detail?: string
}

export interface LiveStatus {
  running: boolean
  backend?: ServerStatus
  frontend?: ServerStatus
  progress?: { started_at: number; stages: StartStage[] } | null
  started_at?: number
  /** Console errors the server accepted from this poll. */
  console_errors?: ConsoleEntry[]
  error_routing?: { to: 'thread' | 'coordinator'; conversation_id: number; new?: boolean } | null
  /** The latest action an agent took in its own browser on this app, while
   *  recent: the page it is on, the toolset member, and who it is. */
  agent?: AgentActivity | null
}

export interface AgentActivity {
  path: string
  action: string
  label: string
  at: number
}

/** What an agent's browser action looks like to the person watching. */
export function describeAgentAction(action: string): string {
  if (action === 'navigate') return 'opening a page'
  if (/click|mouse|hover|drag/.test(action)) return 'clicking'
  if (action === 'type' || action === 'key' || action === 'form_input') return 'typing'
  if (action === 'scroll' || action === 'scroll_to') return 'scrolling'
  if (action === 'read_console') return 'checking for errors'
  if (action === 'wait') return 'waiting'
  return 'looking'
}

export interface LogChunk {
  offset: number
  lines: string[]
  reset: boolean
}

export interface LiveLogs {
  backend: LogChunk
  frontend: LogChunk
}

export type ServerAction =
  | 'restart_backend'
  | 'restart_frontend'
  | 'restart'
  | 'migrate'
  | 'reset_database'

export interface ConsoleEntry {
  level: 'log' | 'info' | 'warn' | 'error'
  text: string
  ts: number
}

export interface NetworkEntry {
  id: number
  method: string
  url: string
  status: number
  ms: number
}

export interface PickedElement {
  tag: string
  id: string
  classes: string
  text: string
  component: string
  chain: string[]
  file: string
}

/** A message from the bridge, after validation. */
export type BridgeMessage =
  | { type: 'ready'; path: string; title: string }
  | { type: 'loading'; path: string }
  | { type: 'nav'; path: string; title: string; canGoBack: boolean; canGoForward: boolean }
  | ({ type: 'console' } & ConsoleEntry)
  | ({ type: 'net' } & NetworkEntry)
  | { type: 'hmr'; files: string[] }
  | { type: 'full-reload' }
  | { type: 'picked'; element: PickedElement | null; path?: string }
  | { type: 'shortcut'; key: string; shift: boolean }

const LEVELS = new Set(['log', 'info', 'warn', 'error'])
const MAX_TEXT = 4000

function str(v: unknown, max = MAX_TEXT): string {
  return typeof v === 'string' ? v.slice(0, max) : ''
}

function num(v: unknown): number {
  return typeof v === 'number' && Number.isFinite(v) ? v : 0
}

/**
 * Validate one postMessage payload from the preview iframe. Returns null for
 * anything that isn't a well-formed bridge message. The caller checks the
 * sender (origin and window) before this; this checks the shape, because the
 * page is the user's own code and can post anything.
 */
export function parseBridgeMessage(data: unknown): BridgeMessage | null {
  if (!data || typeof data !== 'object') return null
  const d = data as Record<string, unknown>
  if (d.source !== 'imagi-preview' || typeof d.type !== 'string') return null
  switch (d.type) {
    case 'ready':
      return { type: 'ready', path: str(d.path, 2000) || '/', title: str(d.title, 300) }
    case 'loading':
      return { type: 'loading', path: str(d.path, 2000) || '/' }
    case 'nav':
      return {
        type: 'nav',
        path: str(d.path, 2000) || '/',
        title: str(d.title, 300),
        canGoBack: d.canGoBack === true,
        canGoForward: d.canGoForward === true,
      }
    case 'console': {
      const level = typeof d.level === 'string' && LEVELS.has(d.level) ? (d.level as ConsoleEntry['level']) : 'log'
      return { type: 'console', level, text: str(d.text), ts: num(d.ts) || Date.now() }
    }
    case 'net':
      return {
        type: 'net',
        id: num(d.id),
        method: str(d.method, 12).toUpperCase() || 'GET',
        url: str(d.url, 2000),
        status: num(d.status),
        ms: num(d.ms),
      }
    case 'hmr':
      return {
        type: 'hmr',
        files: Array.isArray(d.files) ? d.files.filter((f) => typeof f === 'string').slice(0, 50).map((f) => (f as string).slice(0, 300)) : [],
      }
    case 'full-reload':
      return { type: 'full-reload' }
    case 'picked': {
      const e = d.element as Record<string, unknown> | null
      if (!e || typeof e !== 'object') return { type: 'picked', element: null }
      return {
        type: 'picked',
        path: str(d.path, 2000),
        element: {
          tag: str(e.tag, 40),
          id: str(e.id, 100),
          classes: str(e.classes, 200),
          text: str(e.text, 200),
          component: str(e.component, 100),
          chain: Array.isArray(e.chain) ? e.chain.filter((c) => typeof c === 'string').slice(0, 6).map((c) => (c as string).slice(0, 100)) : [],
          file: str(e.file, 300),
        },
      }
    }
    case 'shortcut':
      return { type: 'shortcut', key: str(d.key, 4).toLowerCase(), shift: d.shift === true }
    default:
      return null
  }
}

/** A command for the bridge. */
export type BridgeCommand =
  | { cmd: 'hello' }
  | { cmd: 'back' }
  | { cmd: 'forward' }
  | { cmd: 'reload' }
  | { cmd: 'navigate'; path: string }
  | { cmd: 'pick' }
  | { cmd: 'cancel-pick' }

/** Normalise what was typed in the address bar to an in-app path. */
export function normalizeAddress(input: string): string {
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
  const path = trimmed.startsWith('/') ? trimmed : '/' + trimmed
  // Never let a typed path leave the app (//host, backslash tricks).
  return path.startsWith('//') || path.includes('\\') ? '/' : path
}

export const LivePreviewService = {
  /** Which preview this deployment serves. */
  async mode(): Promise<PreviewMode> {
    const response = await api.get('/v1/builder/preview/config/')
    return response.data?.mode === 'live' ? 'live' : 'stream'
  },

  /** Ensure the dev servers run in live mode. Idempotent and fast when warm;
   *  progress of a cold start comes from status() meanwhile. */
  async start(projectId: string): Promise<LiveStartResult> {
    try {
      const response = await api.post(`/v1/builder/${projectId}/preview/`, {}, { timeout: 600_000 })
      return response.data
    } catch (error: any) {
      const message = error?.response?.data?.error || (error instanceof Error ? error.message : 'Preview failed to start.')
      throw new Error(message)
    }
  },

  /** Health poll (and viewer heartbeat), carrying new console errors. */
  async status(projectId: string, consoleErrors: ConsoleEntry[], visible: boolean): Promise<LiveStatus> {
    const response = await api.post(`/v1/builder/${projectId}/preview/status/`, {
      console_errors: consoleErrors,
      visible,
    })
    return response.data
  },

  async logs(projectId: string, offsets: { backend?: number; frontend?: number }): Promise<LiveLogs> {
    const params: Record<string, number> = {}
    if (offsets.backend !== undefined) params.backend = offsets.backend
    if (offsets.frontend !== undefined) params.frontend = offsets.frontend
    const response = await api.get(`/v1/builder/${projectId}/preview/logs/`, { params })
    return response.data
  },

  async action(projectId: string, action: ServerAction): Promise<{ ok?: boolean; error?: string | null; url?: string }> {
    const response = await api.post(
      `/v1/builder/${projectId}/preview/action/`,
      { action },
      { timeout: 120_000 }
    )
    return response.data
  },
}
