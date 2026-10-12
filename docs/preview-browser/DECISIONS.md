# Decisions

Each entry: what was decided, why, and what it costs.

## 1. Show the real dev server in an iframe

**Decided:** the preview is the project's own Vite dev server in a sandboxed
iframe, not screenshots of a server-side browser.

**Why:** the screenshot stream could never feel like a browser: frames lag
input, fast scrolls show unloaded areas, text blurs between frames, and every
viewer costs a Chromium on the server. A native iframe is exact and costs the
server nothing per frame.

**Cost:** the app runs in the user's browser, so it needs a public origin
(decision 2) and an isolation story (SECURITY.md). The headless Chromium stays
for the agent's own preview tool only, and idles out after 120 s.

## 2. One Railway domain, a secret path per preview

**Decided (Riley, 2026-10-12):** previews are served from one Railway domain on
the Workspace service (e.g. `imagi-preview.up.railway.app`), each under
`/s/<token>/`, with the token as the only credential.

**Why:** no DNS or wildcard certificate to buy or manage, and it works today.
A per-preview subdomain would need a custom domain with a wildcard; a cookie
would not survive Safari's third-party cookie blocking (and iPad Safari is a
target), while a path token works everywhere.

**Cost:** all previews share one origin, so one user's previews share
`localStorage` and cookies in that user's browser (SECURITY.md, "Shared
origin"). Apps must work under a path prefix: Vite's `base` handles assets
and Vue Router already uses `createWebHistory(import.meta.env.BASE_URL)`;
absolute `/api` calls are routed by Referer.

## 3. Wrapper configs, never edits to the project

**Decided:** the preview's wiring lives in two generated files outside the
project (a Vite config that imports the project's, a settings module that
star-imports the project's), rewritten on every start.

**Why:** the project's configs belong to the user and the agent, who rewrite
them freely; anything Imagi wrote into them would be lost or, worse, shipped.
The bridge plugin is `apply: 'serve'`, so it never reaches the app's build.

## 4. Small Node edge, standard library only

**Decided:** a ~340-line Node proxy (`edge.mjs`) in the Workspace container in
front of every session.

**Why:** routing by token, holding API requests through Django reloads,
WebSocket upgrades for HMR, and security headers all needed one place. Node is
already in the image; no packages means nothing to install or patch. Vite's
own `/api` proxy is bypassed so the edge can retry during a reload.

## 5. Polling for status and logs, postMessage for the page

**Decided:** server health is polled every 2 s while visible (15 s when
hidden); logs every 1.5 s while the logs tab is open. Everything about the
page itself (navigation, console, network, edits, picks) comes from the bridge
over `postMessage`.

**Why:** the status poll doubles as the viewer heartbeat that keeps a session
alive and is cheap (file reads). SSE would hold a connection per viewer
through nginx for little gain. The page's own events are already in the
browser, so they never round-trip through the server; console errors are
batched onto the next poll so the agent can read them back.

## 6. Migrations run for the user

**Decided:** `migrate --noinput` runs before `runserver` (skipped when a stamp
of the migration files is unchanged), and again, debounced, when an agent
writes a migration file.

**Why:** runserver never migrates, so a new model meant a broken page with
"no such table". The stamp keeps it off a warm start.

## 7. Memory budget instead of a session count

**Decided:** sessions are capped by measured memory (`PREVIEW_MEMORY_BUDGET_MB`,
2 GB), evicting least recently used first and prewarmed-but-unopened first of
all; one viewed in the last 60 s is never evicted. While the user is signed in
with Imagi open, their 3 most recently opened projects stay running (Riley's
rule, as in the screenshot preview); idle sessions, and one that drops out of
those 3, stop after 10 minutes.

**Why:** a dev-server pair measured about 280 MB on a small app and grows with the app; a count cannot tell a small app
from a large one. Railway bills memory, and the brief caps spend at $20/month.

## 8. Cookies rewritten for a cross-site frame

**Decided:** the edge rewrites every `Set-Cookie` to `SameSite=None; Secure;
Partitioned` and drops any with a `Domain`.

**Why:** `railway.app` is a public suffix, so the preview is a different site
from the workspace and its cookies are third-party. Without this, the
generated sign-in and sign-up pages (Django CSRF cookie) failed inside the
frame. `Partitioned` keeps them in a jar that exists only under Imagi.

## Deferred

- **Device frames (P1).** Riley removed the phone/device toggle in PR #219 and
  wants the preview to read as a plain browser. The live preview follows the
  pane's width; narrow the pane to test small screens. Revisit only if asked.
- **Light/dark emulation (P2).** Needs the app to cooperate (a class or
  `prefers-color-scheme` override inside the frame); left out of this round.
- **Screenshot to chat (P2).** The picker covers "ask about this"; a pixel
  screenshot needs the server browser or a canvas capture. Left out.
- **Process isolation (cutover prerequisite).** Dev servers run as the
  container's user. Before PREVIEW_V2 is on for users other than Riley, run
  them as an unprivileged user with resource limits (SECURITY.md).
