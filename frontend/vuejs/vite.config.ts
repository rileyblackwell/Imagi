import { defineConfig, type ProxyOptions } from 'vite'
import vue from '@vitejs/plugin-vue'
import fs from 'node:fs'
import path from 'path'

// ---------------------------------------------------------------------------
// Backend discovery (multiple Claude Code instances / worktrees at once)
//
// Each instance's dev servers get whatever ports were free when they launched —
// 5173/8000 for the first one, arbitrary high ports for the rest. The frontend
// therefore cannot assume its Django is on 8000: that used to send /api into
// *another* instance's backend, which silently answered with another database's
// data. So the backend publishes the port it actually bound to (see
// .claude/hooks/dev-setup.sh serve-backend) and we read it back here.
//
// Resolution happens per request, not once at startup, so it does not matter
// which of the two servers boots first.
// ---------------------------------------------------------------------------

const DEV_PORTS_FILE = path.resolve(__dirname, '../../.claude/.dev-ports.json')
const FALLBACK_BACKEND_URL = 'http://127.0.0.1:8000'

interface BackendRecord {
  port?: number
  pid?: number
}

let portsCache: { mtimeMs: number; backend: BackendRecord | null } = { mtimeMs: -1, backend: null }

function readPublishedBackend(): BackendRecord | null {
  let mtimeMs: number
  try {
    mtimeMs = fs.statSync(DEV_PORTS_FILE).mtimeMs
  } catch {
    portsCache = { mtimeMs: -1, backend: null }
    return null
  }
  // Re-parse only when the file actually changed; this runs on every request.
  if (mtimeMs !== portsCache.mtimeMs) {
    let backend: BackendRecord | null = null
    try {
      backend = JSON.parse(fs.readFileSync(DEV_PORTS_FILE, 'utf8'))?.backend ?? null
    } catch {
      backend = null
    }
    portsCache = { mtimeMs, backend }
  }
  return portsCache.backend
}

// A crashed backend leaves its file behind, and the OS may hand that port to a
// different instance later — so check liveness every time rather than trusting
// the file's presence.
function isAlive(pid: number | undefined): boolean {
  if (!pid) return false
  try {
    process.kill(pid, 0)
    return true
  } catch (err) {
    // EPERM means the process exists but belongs to someone else.
    return (err as NodeJS.ErrnoException).code === 'EPERM'
  }
}

let lastLogged = ''

function resolveBackendUrl(): string {
  // Explicit env wins: production/CI and anyone pointing at a remote backend.
  if (process.env.VITE_BACKEND_URL) return process.env.VITE_BACKEND_URL

  const backend = readPublishedBackend()
  const live = !!backend?.port && isAlive(backend.pid)
  const url = live ? `http://127.0.0.1:${backend!.port}` : FALLBACK_BACKEND_URL

  // Announce every change of target. Silence here is what made the old
  // cross-instance bug so hard to spot — the app just quietly served another
  // worktree's data.
  if (url !== lastLogged) {
    lastLogged = url
    if (live) {
      console.log(`[api proxy] -> ${url} (this worktree's backend)`)
    } else {
      console.warn(
        `[api proxy] -> ${url} (fallback: no backend published for this worktree). ` +
          `If another Claude Code instance owns that port you will be talking to its ` +
          `Django. Start this worktree's backend to fix.`,
      )
    }
  }
  return url
}

const apiProxy = {
  changeOrigin: true,
  ws: true,
  rewriteWsOrigin: true,
  configure: (proxy) => {
    proxy.on('proxyReq', (proxyReq, _req, _res, options) => {
      // Django's CSRF check requires Origin to match the host the request
      // arrived on, and only waives that for origins listed in
      // CSRF_TRUSTED_ORIGINS — which hardcodes :5173. Production keeps the two
      // in agreement by forwarding the original Host (`proxy_set_header Host
      // $host` in nginx.conf), but this dev proxy runs with changeOrigin, which
      // rewrites Host to the backend and leaves Origin as the browser sent it.
      // On the canonical 5173/8000 pair the CSRF_TRUSTED_ORIGINS entry papered
      // over the mismatch; on any other port every session-authenticated write
      // came back 403 "Origin checking failed" — the "CORS problem" that
      // appeared as soon as the ports moved.
      //
      // So bring Origin back in line with the Host we're sending. Dev-only, and
      // it weakens nothing: the SPA still has to present a matching csrftoken
      // cookie + header, which is what actually stops cross-site writes.
      const { target } = options // http-proxy has already normalized this to a URL

      if (!(target instanceof URL) || !proxyReq.getHeader('origin')) return
      proxyReq.setHeader('origin', `${target.protocol}//${target.host}`)
    })
  },
} satisfies ProxyOptions

// A getter, not a value: http-proxy re-reads `target` for each request, which is
// what makes late-starting backends work without restarting Vite.
Object.defineProperty(apiProxy, 'target', {
  enumerable: true,
  get: resolveBackendUrl,
})

export default defineConfig({
  plugins: [
    vue(),
  ],
  server: {
    // Honor a harness/CI-assigned PORT, else default to 5173.
    // strictPort is false so Vite auto-increments (5174, 5175, …) when the
    // port is taken — lets multiple dev servers run side by side.
    port: Number(process.env.PORT) || 5173,
    strictPort: false,
    hmr: {
      overlay: false,
    },
    proxy: {
      '/api': apiProxy,
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
    extensions: ['.ts', '.js', '.vue', '.json'],
  },
  optimizeDeps: {
    // Pre-bundle these at server startup instead of letting Vite discover them
    // mid-load. The vee-validate rule/i18n packages are pulled in by the
    // validation plugin but aren't reliably caught by Vite's dep scanner, so on
    // a cold optimize cache they were discovered on the first page load —
    // triggering a re-optimize + full reload that intermittently rendered a
    // blank page (fixed only by a manual refresh). Listing them here removes the
    // mid-load reload entirely.
    include: [
      'vee-validate',
      '@vee-validate/rules',
      '@vee-validate/i18n',
    ],
  },
})
