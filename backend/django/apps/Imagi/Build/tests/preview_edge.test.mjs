// Tests for the preview edge (services/preview_runtime/edge.mjs).
// Run by test_live_preview.py through `node --test`, or directly:
//   node --test apps/Imagi/Build/tests/preview_edge.test.mjs
import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import http from 'node:http'
import os from 'node:os'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const here = path.dirname(fileURLToPath(import.meta.url))
const routesDir = fs.mkdtempSync(path.join(os.tmpdir(), 'edge-routes-'))
process.env.PREVIEW_ROUTES_DIR = routesDir
process.env.PREVIEW_FRAME_ANCESTORS = 'https://imagi.example'
process.env.PREVIEW_EDGE_BACKEND_RETRY_MS = '300'
const edge = await import(path.join(here, '../services/preview_runtime/edge.mjs'))

const TOKEN = 'a'.repeat(43)
const OTHER = 'b'.repeat(43)
// Each server test uses its own token: routes are cached for a second.
const SERVED = 'c'.repeat(43)
const DOWN = 'd'.repeat(43)

function listen(server) {
  return new Promise((resolve) => server.listen(0, '127.0.0.1', () => resolve(server.address().port)))
}

function get(port, urlPath, headers = {}, method = 'GET') {
  return new Promise((resolve, reject) => {
    const req = http.request({ host: '127.0.0.1', port, path: urlPath, method, headers }, (res) => {
      let body = ''
      res.on('data', (c) => (body += c))
      res.on('end', () => resolve({ status: res.statusCode, headers: res.headers, body }))
    })
    req.on('error', reject)
    req.end()
  })
}

function writeRoute(token, frontend, backend) {
  fs.writeFileSync(path.join(routesDir, `${token}.json`), JSON.stringify({ frontend_port: frontend, backend_port: backend }))
}

test('routes the prefix to the frontend and API calls by Referer', () => {
  writeRoute(TOKEN, 5101, 8101)
  assert.deepEqual(edge.resolve('GET', `/s/${TOKEN}/about`, undefined, routesDir), { kind: 'frontend', token: TOKEN, port: 5101 })
  assert.equal(edge.resolve('GET', `/s/${TOKEN}`, undefined, routesDir).kind, 'redirect')
  const api = edge.resolve('POST', '/api/v1/auth/register/', `https://p.example/s/${TOKEN}/auth/register`, routesDir)
  assert.deepEqual(api, { kind: 'backend', token: TOKEN, port: 8101 })
  const stray = edge.resolve('GET', '/about?x=1', `https://p.example/s/${TOKEN}/`, routesDir)
  assert.deepEqual(stray, { kind: 'redirect', token: TOKEN, location: `/s/${TOKEN}/about?x=1` })
})

test('refuses unknown tokens, missing referers and stray writes', () => {
  assert.equal(edge.resolve('GET', `/s/${OTHER}/`, undefined, routesDir), null)
  assert.equal(edge.resolve('GET', '/api/v1/', undefined, routesDir), null)
  assert.equal(edge.resolve('GET', '/api/v1/', `https://p.example/s/${OTHER}/`, routesDir), null)
  assert.equal(edge.resolve('POST', '/about', `https://p.example/s/${TOKEN}/`, routesDir), null)
  assert.equal(edge.resolve('GET', '/s/short/', undefined, routesDir), null)
  assert.equal(edge.loadRoute('../../etc/passwd', routesDir), null)
})

test('drops Domain cookies and makes the rest work in a cross-site frame', () => {
  const out = edge.filterSetCookie([
    'csrftoken=x; Path=/; SameSite=Lax',
    'evil=1; Domain=up.railway.app; Path=/',
    'sessionid=y; HttpOnly; Secure; SameSite=Strict; Path=/',
  ])
  assert.equal(out.length, 2)
  assert.equal(out[0], 'csrftoken=x; Path=/; SameSite=None; Secure; Partitioned')
  assert.equal(out[1], 'sessionid=y; HttpOnly; Path=/; SameSite=None; Secure; Partitioned')
})

test('serves through the edge with frame and referrer headers', async (t) => {
  const app = http.createServer((req, res) => {
    res.writeHead(200, { 'content-type': 'text/html', 'x-frame-options': 'DENY', 'set-cookie': 'a=1; Path=/' })
    res.end(`app ${req.url}`)
  })
  const appPort = await listen(app)
  writeRoute(SERVED, appPort, null)
  const server = edge.createEdge()
  const port = await listen(server)
  t.after(() => {
    app.close()
    server.close()
  })

  const ok = await get(port, `/s/${SERVED}/about`)
  assert.equal(ok.status, 200)
  assert.equal(ok.body, `app /s/${SERVED}/about`)
  assert.equal(ok.headers['content-security-policy'], 'frame-ancestors https://imagi.example')
  assert.equal(ok.headers['referrer-policy'], 'same-origin')
  assert.equal(ok.headers['x-frame-options'], undefined)
  assert.match(ok.headers['x-robots-tag'], /noindex/)
  assert.deepEqual(ok.headers['set-cookie'], ['a=1; Path=/; SameSite=None; Secure; Partitioned'])

  const gone = await get(port, `/s/${OTHER}/`)
  assert.equal(gone.status, 404)
  assert.equal((await get(port, '/__imagi/health')).body, 'ok')
})

test('answers 503 when the backend stays down past the retry window', async (t) => {
  const closed = http.createServer()
  const deadPort = await listen(closed)
  closed.close()
  writeRoute(DOWN, 5101, deadPort)
  const server = edge.createEdge()
  const port = await listen(server)
  t.after(() => server.close())
  const res = await get(port, '/api/v1/ping/', { referer: `http://127.0.0.1/s/${DOWN}/` })
  assert.equal(res.status, 503)
})
