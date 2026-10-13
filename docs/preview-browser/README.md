# Preview browser (live preview)

The workspace's preview shows the user's app itself: the project's own Vite
dev server, with its Django backend behind it, in a sandboxed iframe on a
separate preview origin. The user's browser renders it natively, so
scrolling, typing, video and animation behave exactly as they will for the
app's visitors. It replaces the screenshot-streaming preview
(`WorkspacePreview.vue`, a headless Chromium on the server) and is behind the
`PREVIEW_V2` flag until the cutover.

- [DECISIONS.md](DECISIONS.md): why it is built this way, and what was left out.
- [SECURITY.md](SECURITY.md): who can reach a preview and what a preview can reach.
- [PERF.md](PERF.md): start-up times, memory and the Railway budget.

## How a request flows

```
Imagi workspace (imagi.up.railway.app)
  └─ <iframe sandbox src="https://imagi-preview.up.railway.app/s/<token>/">
        │
        ▼
  preview edge (Node, port 8790, Workspace service)
    /s/<token>/...   → the session's Vite dev server (base "/s/<token>/")
    /api/, /media/,  → the session's Django, picked by the Referer
    /admin/, /static/
    other GETs       → 307 back under /s/<token>/
    anything else    → 404
```

The token is 32 random bytes, minted per server start and handed only to the
project's owner. A route file per token (`PREVIEW_ROUTES_DIR/<token>.json`)
names the ports; deleting it revokes the session.

Neither the project's `vite.config` nor its `settings.py` is touched. Each
start writes two wrappers next to the session's pid files
(`<pid_dir>/<id>_runtime/`): a Vite config that imports the project's and sets
`base`, the allowed host and a bridge plugin, and a settings module that does
`from <project>.settings import *` and trusts the preview origin.

## Pieces

| Where | What |
| --- | --- |
| `backend/django/apps/Imagi/Build/services/live_preview_service.py` | Sessions: start, status, logs, console errors, server actions, idle shutdown, memory budget, prewarm |
| `backend/django/apps/Imagi/Build/services/preview_runtime/edge.mjs` | The edge proxy (Node standard library only) |
| `backend/django/apps/Imagi/Build/services/preview_runtime/bridge.js` | Injected into the app's pages in dev only; reports navigation, console, network, edits and picked elements over `postMessage` |
| `backend/django/apps/Imagi/Build/services/preview_service.py` | Starts the dev servers; in live mode with the wrappers, and runs migrations first |
| `frontend/vuejs/src/apps/imagi/build/components/organisms/workspace/LivePreview.vue` | Toolbar, address bar, status pill, start/error states, picker |
| `frontend/vuejs/src/apps/imagi/build/components/organisms/workspace/PreviewDrawer.vue` | Console, network and server-log drawer |
| `frontend/vuejs/src/apps/imagi/build/services/livePreviewService.ts` | API client and bridge message validation |

API (all under `/api/v1/builder/`, owner only):

- `preview/config/` → `{mode: 'live' | 'stream'}`
- `<id>/preview/` POST starts (idempotent), DELETE stops
- `<id>/preview/status/` POST: server health and start progress; also the
  viewer heartbeat, and carries console errors the page reported
- `<id>/preview/logs/?backend=<offset>&frontend=<offset>`: new log lines
- `<id>/preview/action/` POST `{action}`: `restart_backend`,
  `restart_frontend`, `restart`, `migrate`, `reset_database`

## Using it

| Control | Shortcut |
| --- | --- |
| Address bar (type a path, or pick a page) | Cmd/Ctrl+L |
| Reload; Shift for a hard reload | Cmd/Ctrl+R |
| Console, network and server logs | Cmd/Ctrl+J |
| Pick an element to ask the agent about | Cmd/Ctrl+Shift+C |

Shortcuts work while focus is inside the app too (the bridge forwards them).

## Running it locally

Add `PREVIEW_V2=1` to `backend/django/.env`. The edge listens on
`127.0.0.1:8790` and the workspace frames it from the Vite dev server's
origin; nothing else is needed. The edge's log is `PROJECTS_ROOT/.preview-edge.log`.

## Turning it on in production

1. Workspace service → Settings → Networking → Generate Domain, target port
   **8790**. Railway gives something like `imagi-preview.up.railway.app`
   (the name can be edited before saving).
2. Workspace service variables:
   - `PREVIEW_PUBLIC_ORIGIN=https://<that domain>`
   - `PREVIEW_PARENT_ORIGINS=https://imagi.up.railway.app`
   - `PREVIEW_V2=1`
3. Redeploy the Workspace service and open a project. The status pill should
   read Live.

To turn it off, set `PREVIEW_V2=0`; the workspace goes back to the
screenshot preview on its next load. The domain can stay.

## Settings

| Setting | Default | Meaning |
| --- | --- | --- |
| `PREVIEW_V2` | off | Serve the live preview |
| `PREVIEW_PUBLIC_ORIGIN` | `http://127.0.0.1:8790` | Origin the iframe loads from |
| `PREVIEW_PARENT_ORIGINS` | `FRONTEND_URL` | Origins allowed to frame a preview and talk to its bridge |
| `PREVIEW_EDGE_PORT` | 8790 | Edge port |
| `PREVIEW_LIVE_IDLE_TIMEOUT` | 600 s | Stop a session nobody has viewed for this long |
| `PREVIEW_LIVE_PREWARM_IDLE_TIMEOUT` | 600 s | The same for a prewarmed session never opened |
| `PREVIEW_LIVE_PREWARM_RECENT` | 3 | Most recently opened projects kept running while the user is signed in |
| `PREVIEW_MEMORY_BUDGET_MB` | 2048 | Dev servers' measured memory, host-wide |
| `PREVIEW_BROWSER_IDLE_TIMEOUT` | 120 s | Headless Chromium idle limit (the agent's preview tool only) |

## Screenshots

| Before (screenshot stream) | After (live preview) |
| --- | --- |
| ![Before](screenshots/before-dark.webp) | ![After](screenshots/after-dark.webp) |

Pages in the address bar, an app error banner, the server-log drawer, the
element picker (light theme), and a phone:

![Address bar pages](screenshots/address-pages-dark.webp)
![Error banner](screenshots/error-banner-dark.webp)
![Server logs](screenshots/drawer-logs-dark.webp)
![Picker](screenshots/picker-light.webp)
![Phone](screenshots/phone-dark.webp)
