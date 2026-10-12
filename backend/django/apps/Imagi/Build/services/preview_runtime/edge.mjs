// Imagi preview edge: the one public door to every live preview.
//
// Each open preview is a project's own Vite dev server (with its Django
// backend behind it) running on a loopback port in the Workspace container.
// The workspace shows it in an iframe on this origin, so the user's own
// browser renders the app natively; nothing is screenshotted.
//
// Routing is by path, because previews share one host (a Railway domain;
// see docs/preview-browser/DECISIONS.md):
//
//   /s/<token>/...            -> that session's Vite server, path unchanged
//                                (Vite runs with base "/s/<token>/").
//   /api/..., /media/..., ... -> the session's Django, picked from the
//                                Referer, since apps call "/api" absolutely.
//   other GETs with a Referer -> 307 back under /s/<token>/.
//   anything else             -> 404.
//
// <token> is 32 random bytes the Imagi backend mints per server start and
// hands only to the project's owner. A route file named after it
// (PREVIEW_ROUTES_DIR/<token>.json) says which ports it reaches; deleting the
// file (stop, idle shutdown, restart) revokes it.
//
// No dependencies beyond Node's standard library, so the container needs
// nothing installed for it.

import http from 'node:http'
import net from 'node:net'
import fs from 'node:fs'
import path from 'node:path'

const PORT = Number(process.env.PREVIEW_EDGE_PORT || 8790)
const BIND = process.env.PREVIEW_EDGE_BIND || '::'
const ROUTES_DIR = process.env.PREVIEW_ROUTES_DIR || ''
const FRAME_ANCESTORS = (process.env.PREVIEW_FRAME_ANCESTORS || "'none'").trim()
const SCHEME = process.env.PREVIEW_PUBLIC_SCHEME === 'https' ? 'https' : 'http'

// How long a backend request waits out a Django restart (runserver reloads
// on every Python edit) before it is answered with a 503.
const BACKEND_RETRY_MS = Number(process.env.PREVIEW_EDGE_BACKEND_RETRY_MS || 8000)
const RETRY_STEP_MS = 200
// Request bodies are buffered so a retry can replay them.
const MAX_REPLAY_BODY = 10 * 1024 * 1024

export const TOKEN_RE = /^[A-Za-z0-9_-]{32,64}$/
const PREFIX_RE = /^\/s\/([A-Za-z0-9_-]{32,64})(\/.*)?$/
// Paths the app's Django serves directly (Vite's own /api proxy is bypassed
// so the edge can hold requests through a backend reload).
const BACKEND_PREFIXES = ['/api/', '/media/', '/admin/', '/static/']

// --- routes -----------------------------------------------------------------

const routeCache = new Map()
const ROUTE_TTL_MS = 1000

export function loadRoute(token, routesDir = ROUTES_DIR) {
  if (!routesDir || !TOKEN_RE.test(token)) return null
  const now = Date.now()
  const hit = routeCache.get(token)
  if (hit && now - hit.at < ROUTE_TTL_MS) return hit.route
  let route = null
  try {
    const raw = JSON.parse(fs.readFileSync(path.join(routesDir, `${token}.json`), 'utf8'))
    if (raw && Number.isInteger(raw.frontend_port) && raw.frontend_port > 0) {
      route = {
        frontend: raw.frontend_port,
        backend: Number.isInteger(raw.backend_port) ? raw.backend_port : null,
      }
    }
  } catch {
    route = null
  }
  routeCache.set(token, { at: now, route })
  return route
}

/** Where a request goes: {kind, token, port?, location?} or null (404). */
export function resolve(method, url, referer, routesDir = ROUTES_DIR) {
  let pathname
  try {
    pathname = new URL(url, 'http://edge').pathname
  } catch {
    return null
  }
  const own = PREFIX_RE.exec(pathname)
  if (own) {
    const token = own[1]
    const route = loadRoute(token, routesDir)
    if (!route) return null
    if (own[2] === undefined) {
      return { kind: 'redirect', token, location: `/s/${token}/` }
    }
    return { kind: 'frontend', token, port: route.frontend }
  }
  // A request outside the prefix belongs to whichever preview page made it.
  let refPath = ''
  try {
    refPath = referer ? new URL(referer).pathname : ''
  } catch {
    refPath = ''
  }
  const from = PREFIX_RE.exec(refPath)
  if (!from) return null
  const token = from[1]
  const route = loadRoute(token, routesDir)
  if (!route) return null
  if (route.backend && BACKEND_PREFIXES.some((p) => pathname === p.slice(0, -1) || pathname.startsWith(p))) {
    return { kind: 'backend', token, port: route.backend }
  }
  if (method === 'GET' || method === 'HEAD') {
    const search = url.includes('?') ? url.slice(url.indexOf('?')) : ''
    return { kind: 'redirect', token, location: `/s/${token}${pathname}${search}` }
  }
  return null
}

// --- headers ----------------------------------------------------------------

const HOP_BY_HOP = new Set([
  'connection', 'keep-alive', 'proxy-authenticate', 'proxy-authorization',
  'te', 'trailer', 'transfer-encoding', 'upgrade',
])

function forwardHeaders(req) {
  const headers = {}
  for (const [key, value] of Object.entries(req.headers)) {
    if (!HOP_BY_HOP.has(key)) headers[key] = value
  }
  const prior = req.headers['x-forwarded-for']
  const addr = req.socket.remoteAddress || ''
  headers['x-forwarded-for'] = prior ? `${prior}, ${addr}` : addr
  // The edge knows the public scheme; never trust a client's claim to it.
  headers['x-forwarded-proto'] = SCHEME
  return headers
}

/** Cookies the app sets stay on the preview host: anything scoped to a
 *  wider Domain is dropped, so a preview can never plant a cookie on a
 *  parent domain. */
export function filterSetCookie(values) {
  if (!values) return values
  const list = Array.isArray(values) ? values : [values]
  return list.filter((c) => !/;\s*domain\s*=/i.test(c))
}

function securityHeaders(headers) {
  const out = { ...headers }
  for (const key of Object.keys(out)) {
    if (HOP_BY_HOP.has(key)) delete out[key]
  }
  if (out['set-cookie']) out['set-cookie'] = filterSetCookie(out['set-cookie'])
  // Only the Imagi workspace may frame a preview. An app's own CSP, if any,
  // still applies alongside this one.
  const csp = `frame-ancestors ${FRAME_ANCESTORS}`
  out['content-security-policy'] = out['content-security-policy']
    ? [].concat(out['content-security-policy'], csp)
    : csp
  // Same-origin only: the token in the path never leaks to other sites.
  out['referrer-policy'] = 'same-origin'
  out['x-robots-tag'] = 'noindex, nofollow'
  delete out['x-frame-options']
  return out
}

function notFound(res) {
  res.writeHead(404, {
    'content-type': 'text/plain; charset=utf-8',
    'cache-control': 'no-store',
    'referrer-policy': 'same-origin',
  })
  res.end('This preview has ended. Reopen it from your Imagi workspace.\n')
}

// --- proxying ---------------------------------------------------------------

function readBody(req) {
  return new Promise((resolveBody, reject) => {
    const chunks = []
    let size = 0
    req.on('data', (chunk) => {
      size += chunk.length
      if (size > MAX_REPLAY_BODY) {
        reject(new Error('body too large'))
        req.destroy()
        return
      }
      chunks.push(chunk)
    })
    req.on('end', () => resolveBody(Buffer.concat(chunks)))
    req.on('error', reject)
  })
}

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms))
}

function upstream(req, res, port, body) {
  return new Promise((done) => {
    const headers = forwardHeaders(req)
    if (body) headers['content-length'] = String(body.length)
    const proxyReq = http.request(
      { host: '127.0.0.1', port, method: req.method, path: req.url, headers },
      (proxyRes) => {
        res.writeHead(proxyRes.statusCode || 502, securityHeaders(proxyRes.headers))
        proxyRes.pipe(res)
        proxyRes.on('end', () => done('ok'))
        proxyRes.on('error', () => done('ok'))
      },
    )
    proxyReq.on('error', (err) => {
      done(res.headersSent ? 'ok' : err.code || 'error')
    })
    if (body) proxyReq.end(body)
    else req.pipe(proxyReq)
  })
}

async function proxyBackend(req, res, port) {
  let body
  try {
    body = await readBody(req)
  } catch {
    res.writeHead(413, { 'content-type': 'application/json' })
    res.end('{"error":"Request too large"}')
    return
  }
  const deadline = Date.now() + BACKEND_RETRY_MS
  for (;;) {
    const outcome = await upstream(req, res, port, body)
    if (outcome === 'ok') return
    const retryable = outcome === 'ECONNREFUSED' || outcome === 'ECONNRESET'
    if (!retryable || Date.now() >= deadline) {
      if (!res.headersSent) {
        res.writeHead(503, { 'content-type': 'application/json', 'retry-after': '1' })
        res.end('{"error":"Your app\'s backend is restarting. Try again in a moment."}')
      }
      return
    }
    await sleep(RETRY_STEP_MS)
  }
}

async function proxyFrontend(req, res, port) {
  const outcome = await upstream(req, res, port, null)
  if (outcome !== 'ok' && !res.headersSent) {
    res.writeHead(502, { 'content-type': 'text/plain; charset=utf-8' })
    res.end('Your app\'s frontend server is not answering. Imagi is restarting it.\n')
  }
}

export function handle(req, res) {
  if (req.url === '/__imagi/health') {
    res.writeHead(200, { 'content-type': 'text/plain' })
    res.end('ok')
    return
  }
  const target = resolve(req.method || 'GET', req.url || '/', req.headers.referer)
  if (!target) return notFound(res)
  if (target.kind === 'redirect') {
    res.writeHead(307, { location: target.location, 'cache-control': 'no-store', 'referrer-policy': 'same-origin' })
    res.end()
    return
  }
  if (target.kind === 'backend') return void proxyBackend(req, res, target.port)
  return void proxyFrontend(req, res, target.port)
}

/** WebSocket upgrades (Vite HMR, an app's own sockets): raw TCP pipe. */
export function handleUpgrade(req, socket, head) {
  const target = resolve('GET', req.url || '/', req.headers.referer)
  if (!target || target.kind === 'redirect') {
    socket.end('HTTP/1.1 404 Not Found\r\nConnection: close\r\n\r\n')
    return
  }
  const upstreamSocket = net.connect(target.port, '127.0.0.1', () => {
    const headers = forwardHeaders(req)
    headers.connection = 'Upgrade'
    headers.upgrade = req.headers.upgrade || 'websocket'
    let head0 = `${req.method} ${req.url} HTTP/1.1\r\n`
    for (const [k, v] of Object.entries(headers)) {
      for (const one of [].concat(v)) head0 += `${k}: ${one}\r\n`
    }
    upstreamSocket.write(head0 + '\r\n')
    if (head && head.length) upstreamSocket.write(head)
    upstreamSocket.pipe(socket)
    socket.pipe(upstreamSocket)
  })
  const close = () => {
    socket.destroy()
    upstreamSocket.destroy()
  }
  upstreamSocket.on('error', close)
  socket.on('error', close)
}

export function createEdge() {
  const server = http.createServer(handle)
  server.on('upgrade', handleUpgrade)
  server.keepAliveTimeout = 65_000
  server.headersTimeout = 66_000
  return server
}

if (import.meta.url === `file://${process.argv[1]}`) {
  if (!ROUTES_DIR) {
    console.error('PREVIEW_ROUTES_DIR is not set')
    process.exit(1)
  }
  const server = createEdge()
  let bind = BIND
  server.on('error', (err) => {
    // Another worker already holds the port: that edge serves everyone.
    if (err.code === 'EADDRINUSE') process.exit(0)
    // No IPv6 on this host: fall back to IPv4.
    if (err.code === 'EAFNOSUPPORT' && bind === '::') {
      bind = '0.0.0.0'
      server.listen(PORT, bind)
      return
    }
    console.error(err)
    process.exit(1)
  })
  server.on('listening', () => {
    console.log(`[preview-edge] listening on ${bind}:${PORT}`)
  })
  server.listen(PORT, bind)
}
