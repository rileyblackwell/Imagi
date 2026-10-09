"""
Headless-browser preview for generated projects.

The old preview handed the user's browser a ``http://localhost:<port>`` URL,
which only works when Imagi itself runs on the user's machine. This service
instead runs a real Chromium instance *next to* the project's dev servers,
inside whatever machine/container hosts the Django backend, and drives it
over the Chrome DevTools Protocol (CDP). The workspace UI receives JPEG
frames and sends input events through the normal authenticated API, so the
exact same setup works in local development and on Railway.

Process model (mirrors PreviewService's): Chromium is a plain subprocess
tracked by PID/state files beside the project directory. All page state
(current URL, history, session storage) lives in Chromium itself, so any
Django worker can serve any request. Workers keep one pooled CDP connection
per browser purely as a transport optimization — losing it costs nothing but
a reconnect.
"""

import contextlib
import glob
import hashlib
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

try:
    import fcntl
except ImportError:  # pragma: no cover - Windows dev machines
    fcntl = None

import psutil
import requests
from django.conf import settings
from django.db import close_old_connections
from websocket import create_connection, WebSocketException

from .preview_service import (
    BROWSER_PROFILE_SUFFIX,
    BROWSER_STATE_SUFFIX,
    PreviewService,
    preview_start_lock,
    sidecar_stem,
)

logger = logging.getLogger(__name__)
# One line per preview start with where its time went (see settings.LOGGING,
# which lets it through in production where INFO is otherwise dropped).
timing_logger = logging.getLogger('imagi.timing')

# Per-project files this service writes beside the dev-server PID files
# (cleanup-relevant suffixes live in preview_service so its sweeps cover them).
BROWSER_PID_SUFFIX = '_browser.pid'
BROWSER_LOG_SUFFIX = '_browser.log'
BACKDROP_CACHE_SUFFIX = '_backdrop.json'

# Defaults until the client reports its pane size.
DEFAULT_VIEWPORT = (1280, 800)
MIN_VIEWPORT, MAX_VIEWPORT = 320, 3840
MAX_EVENTS_PER_REQUEST = 64

# Frames of a page at rest are lossless PNG, so text and hairlines come
# through exactly as Chromium drew them (JPEG at any quality halves the colour
# resolution, which smears coloured text). Measured at 2x, an app view is
# ~150-400 KB as PNG, roughly JPEG 90's size and under 2x JPEG 70's, and a
# frame is only re-sent when the page changes.
# Photo-heavy views can run to megabytes as PNG, so a PNG over the budget is
# replaced by a high-quality JPEG, and the session skips PNG for a while.
FRAME_PNG_BUDGET_B64 = 900_000
FRAME_PNG_RETRY_S = 10
FRAME_JPEG_QUALITY = 90
# Frames produced while the user is scrolling or dragging trade fidelity for
# encode speed and payload size; the poll after the gesture re-delivers a
# crisp frame of the settled page.
MOTION_JPEG_QUALITY = 55

# How long to wait for the Vite dev server to answer HTTP before pointing
# Chromium at it. Vite itself is up in a couple of seconds; the generous
# ceiling covers first-run dependency optimization.
FRONTEND_READY_TIMEOUT = 90

# CDP modifier bitmask (Alt=1, Ctrl=2, Meta=4, Shift=8) — the client sends
# the mask directly; we only clamp it.
MODIFIER_MASK = 0xF

# Recent JS console errors surfaced in every frame/status payload so the
# workspace can offer one-click fixes. Small and bounded by design.
MAX_CONSOLE_ERRORS = 5
CONSOLE_ERROR_TEXT_LIMIT = 500

# Error collector injected into the previewed page. Why in-page state instead
# of CDP Runtime events: the pooled DevTools sockets are per worker process,
# so per-process event buffers would diverge between workers (a worker whose
# connection attached after the error never hears about it) and die with
# every pool reconnect, and events arriving between requests would sit unread
# until the next CDP call happens to drain the socket. Keeping the buffer in
# the page matches this module's process model — all page state lives in
# Chromium, so any worker serves any request — and a hard navigation clears
# it for free because the fresh document starts without it. (SPA route
# changes keep the same document, so errors survive those; they stay
# relevant to the running app either way.)
_CONSOLE_WATCH_JS = """
(function () {
  if (window.__imagiConsoleWatch) return;
  window.__imagiConsoleWatch = true;
  window.__imagiErrors = [];
  function push(text) {
    try {
      text = String(text == null ? '' : text).slice(0, %(text_limit)d);
      if (!text) return;
      var buf = window.__imagiErrors;
      for (var i = 0; i < buf.length; i++) {
        if (buf[i].text === text) { buf[i].ts = Date.now(); return; }
      }
      buf.push({ level: 'error', text: text, ts: Date.now() });
      if (buf.length > %(max_errors)d) buf.shift();
    } catch (e) {}
  }
  function fmt(value) {
    try {
      if (value instanceof Error) return value.stack || value.message || String(value);
      if (typeof value === 'object') return JSON.stringify(value);
      return String(value);
    } catch (e) { return '[unserializable]'; }
  }
  var original = console.error;
  console.error = function () {
    try { push(Array.prototype.map.call(arguments, fmt).join(' ')); } catch (e) {}
    return original.apply(console, arguments);
  };
  window.addEventListener('error', function (event) {
    // No capture phase: uncaught exceptions only, not resource-load noise.
    push(event.message
      ? event.message + (event.filename ? ' (' + event.filename + ':' + event.lineno + ')' : '')
      : 'Uncaught error');
  });
  window.addEventListener('unhandledrejection', function (event) {
    var reason = event.reason;
    push('Unhandled promise rejection: ' +
      ((reason && (reason.stack || reason.message)) || String(reason)));
  });
})();
""" % {'text_limit': CONSOLE_ERROR_TEXT_LIMIT, 'max_errors': MAX_CONSOLE_ERRORS}

# Evaluated on every frame/status poll: installs the collector if this
# document does not have it yet (covers documents that predate the
# on-new-document registration below) and returns the buffer WITHOUT
# clearing it — the payload carries the full current list each time, so a
# worker that didn't serve the previous poll still reports the same errors
# and an empty list genuinely means "none".
_CONSOLE_COLLECT_JS = (
    '(function () { %s; return window.__imagiErrors || []; })()' % _CONSOLE_WATCH_JS
)

# Where the page is scrolled to, how far it can scroll, and the colour behind
# it. Every frame carries this so the client can place the bitmap at the exact
# scroll offset it shows (instead of guessing from the deltas it sent), draw a
# scrollbar that tracks the page, and fill the strip that an optimistic scroll
# uncovers with the page's own background instead of a dark gap.
_SCROLL_METRICS_JS = r"""
(function () {
  var el = document.scrollingElement || document.documentElement;
  // The colour actually showing at the bottom of the view: the nearest
  // painted background behind the element there. A gradient counts by its
  // first colour; the body's own colour is often hidden under an app shell
  // painted another one (a dark body under a light page read as black).
  var bg = '';
  try {
    var node = document.elementFromPoint(window.innerWidth / 2, window.innerHeight - 2);
    for (; node && node.nodeType === 1; node = node.parentElement) {
      var cs = getComputedStyle(node);
      if (cs.backgroundColor && cs.backgroundColor !== 'transparent' &&
          cs.backgroundColor !== 'rgba(0, 0, 0, 0)') { bg = cs.backgroundColor; break; }
      var m = /gradient\(.*?(rgba?\([^)]*\))/.exec(cs.backgroundImage || '');
      if (m) { bg = m[1]; break; }
    }
  } catch (e) {}
  return {
    x: window.scrollX, y: window.scrollY,
    width: el ? el.scrollWidth : 0, height: el ? el.scrollHeight : 0,
    viewport_width: window.innerWidth, viewport_height: window.innerHeight,
    background: bg
  };
})()
"""

# Same metrics, read once the page has drawn its next frame. Chromium applies
# a dispatched wheel scroll on its next frame, not by the time the CDP call
# returns: read straight away, scrollY still holds the pre-scroll offset (the
# screenshot itself does wait for the frame). The timeout keeps a page that
# isn't producing frames from stalling the request.
_SETTLED_SCROLL_METRICS_JS = """
new Promise(function (resolve) {
  var done = false;
  function read() { if (!done) { done = true; resolve(%s); } }
  requestAnimationFrame(read);
  setTimeout(read, 120);
})
""" % _SCROLL_METRICS_JS.strip()

# ---------------------------------------------------------------------------
# Backdrop: the whole page, captured ahead of time
# ---------------------------------------------------------------------------
# Frames show only the viewport, so a scroll otherwise reveals nothing until
# the next frame comes back. The backdrop is the rest of the page, captured
# once per page in viewport-sized slices (Chromium only rasterizes what is in
# view: a clip beyond the viewport comes back blank, and captureBeyondViewport
# resizes the viewport, which fires resize events and moves the scroll). The
# client scrolls through the backdrop locally until the real frame arrives.
#
# Fixed elements would repeat in every slice, so they are hidden from the
# backdrop and captured once, on a transparent background, as an overlay the
# client keeps in place. Sticky elements are laid out as plain relative boxes
# for the slices (same space in the flow, so nothing reflows); one that is
# currently stuck goes in the overlay too.

BACKDROP_MAX_PX = 10000     # CSS px of page per backdrop, around the scroll
# Slices are captured at the session's full device scale, like a settled
# frame, so scrolling through them is as sharp as the page at rest and the
# frame that lands after the scroll swaps in without a visible change. They
# are lossless PNG while a slice stays under this budget, else JPEG 90 (photos,
# big gradients); after BACKDROP_PNG_MISSES slices in a row over it, the rest
# of the capture skips the wasted PNG encode.
# Measured at 2x on a 1280x800 view: a text-and-flat-colour slice is ~150-400
# KB as PNG; a gradient-heavy one 0.6-4 MB as PNG but 200-500 KB as JPEG 90.
BACKDROP_PNG_BUDGET_B64 = 450_000
BACKDROP_PNG_MISSES = 2
BACKDROP_JPEG_QUALITY = FRAME_JPEG_QUALITY
# After a document's first pass scrolls it through once (firing lazy-loading
# and scroll-reveal observers), give the images and transitions it started a
# moment before capturing.
BACKDROP_WARM_SETTLE_S = 0.6
# A warm-up captures the backdrop once the freshly loaded app has had this
# long to fetch its data and images.
BACKDROP_PREPARE_DELAY_S = 1.5
PAGE_LOCK_TIMEOUT_S = 5

_BACKDROP_MARK_JS = """
(function () {
  var marked = 0;
  var els = document.querySelectorAll('body *');
  for (var i = 0; i < els.length; i++) {
    var el = els[i];
    var cs = getComputedStyle(el);
    if (cs.position === 'fixed') {
      el.setAttribute('data-imagi-bd', 'fixed');
      marked++;
    } else if (cs.position === 'sticky') {
      var top = parseFloat(cs.top);
      // At or above its stick line: it stays put while the page scrolls
      // under it (true of a sticky header at the very top of the page too).
      var stuck = !isNaN(top) && el.getBoundingClientRect().top <= top + 1;
      el.setAttribute('data-imagi-bd', stuck ? 'stuck' : 'sticky');
      if (stuck) marked++;
    }
  }
  return marked;
})()
"""

_BACKDROP_CSS = {
    'slices': (
        'html{scroll-behavior:auto!important}'
        '[data-imagi-bd=fixed]{visibility:hidden!important}'
        '[data-imagi-bd=sticky],[data-imagi-bd=stuck]'
        '{position:relative!important;top:auto!important;bottom:auto!important}'
    ),
    'overlay': (
        'html,body{background:transparent!important}'
        'html{visibility:hidden!important}'
        '[data-imagi-bd=fixed],[data-imagi-bd=stuck]{visibility:visible!important}'
    ),
}

_BACKDROP_STYLE_JS = """
(function (css) {
  var el = document.getElementById('__imagi_backdrop');
  if (!css) {
    if (el) el.remove();
    var marks = document.querySelectorAll('[data-imagi-bd]');
    for (var i = 0; i < marks.length; i++) marks[i].removeAttribute('data-imagi-bd');
    return true;
  }
  if (!el) {
    el = document.createElement('style');
    el.id = '__imagi_backdrop';
    document.documentElement.appendChild(el);
  }
  el.textContent = css;
  return true;
})(%s)
"""

# Scroll instantly (whatever the page's scroll-behavior) and say where it
# landed: the last slice clamps at the bottom of the page.
_SCROLL_TO_JS = "(function () { window.scrollTo({left: %f, top: %f, behavior: 'instant'}); return [window.scrollX, window.scrollY]; })()"

# Identifies the document and how often its DOM has changed: a captured
# backdrop is reused (see _load_backdrop_cache) only while this still reads
# the same, i.e. same document, nothing added, removed or restyled since. The
# backdrop's own marks and stylesheet don't count.
_DOC_STAMP_JS = """
(function () {
  var s = window.__imagiDocStamp;
  if (!s) {
    s = window.__imagiDocStamp = { id: Math.random().toString(36).slice(2), n: 0 };
    function ours(node) { return node && node.id === '__imagi_backdrop'; }
    try {
      new MutationObserver(function (records) {
        for (var i = 0; i < records.length; i++) {
          var r = records[i];
          if (r.attributeName === 'data-imagi-bd' || ours(r.target) || ours(r.target.parentNode)) continue;
          if (r.type === 'childList' &&
              Array.prototype.every.call(r.addedNodes, ours) &&
              Array.prototype.every.call(r.removedNodes, ours)) continue;
          s.n++;
          return;
        }
      }).observe(document, { subtree: true, childList: true, attributes: true, characterData: true });
    } catch (e) {}
  }
  return location.href + '#' + s.id + ':' + s.n;
})()
"""

_NEXT_FRAME_JS = (
    "new Promise(function (r) { var d = false; function f() { if (!d) { d = true; r(true); } }"
    " requestAnimationFrame(f); setTimeout(f, 120); })"
)

_CSS_COLOR_RE = re.compile(r'^rgba?\([0-9.,%/ ]{1,60}\)$')

_MOUSE_EVENT_TYPES = {'mousePressed', 'mouseReleased', 'mouseMoved'}
_MOUSE_BUTTONS = {'none', 'left', 'middle', 'right', 'back', 'forward'}
_KEY_EVENT_TYPES = {'keyDown', 'keyUp'}


def _as_int(value):
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


class BrowserPreviewError(Exception):
    """Raised for user-reportable browser preview failures."""


class BrowserNotRunning(BrowserPreviewError):
    """The browser session is not (or no longer) running."""


class CdpError(BrowserPreviewError):
    """A DevTools command failed."""


class CdpConnection:
    """Minimal synchronous Chrome DevTools Protocol client for one target.

    Chromium supports multiple simultaneous CDP clients, so each worker
    process keeping its own pooled connection is safe even when several
    Django workers talk to the same page at once. One socket cannot serve
    two callers concurrently though — the pool serializes use per entry.
    """

    def __init__(self, ws_url, timeout=15):
        # suppress_origin: Chromium rejects DevTools websocket upgrades that
        # carry a non-localhost Origin header.
        self._ws = create_connection(ws_url, timeout=timeout, suppress_origin=True)
        self._next_id = 0
        # Device metrics this connection has applied via emulation override
        # (overrides live exactly as long as the CDP session that set them);
        # None until _apply_viewport sends the first one.
        self.applied_viewport = None
        # While a view's PNG frames run over budget, capture JPEG until this
        # time (see _capture_settled).
        self.png_skip_until = 0
        # Whether this connection has registered the console-error collector
        # for future documents (same session-scoped lifetime as emulation).
        self.console_watch_registered = False

    def call(self, method, params=None):
        self._next_id += 1
        msg_id = self._next_id
        self._ws.send(json.dumps({'id': msg_id, 'method': method, 'params': params or {}}))
        # Responses interleave with protocol events; skip events until our
        # reply arrives (the socket timeout bounds the wait).
        while True:
            payload = json.loads(self._ws.recv())
            if payload.get('id') == msg_id:
                if 'error' in payload:
                    err = payload['error']
                    raise CdpError(f"{method}: {err.get('message', 'unknown CDP error')}")
                return payload.get('result', {})

    def close(self):
        try:
            self._ws.close()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Per-process CDP connection pool
# ---------------------------------------------------------------------------
# One long-lived connection per browser (keyed by DevTools port). Reusing it
# saves two HTTP round-trips (/json/version, /json/list) plus a websocket
# handshake on every frame/input/navigate request. Entries also carry the
# resolved page target and a lock: the target so callers skip /json/list on
# the hot path, the lock because a single websocket cannot interleave two
# requests' send/recv cycles.

_cdp_pool = {}  # cdp_port -> {'ws_url', 'conn', 'page', 'lock'}
_cdp_pool_lock = threading.Lock()


def _resolve_page_target(port, state):
    """Find (or open) the app's page target via the DevTools HTTP endpoint."""
    try:
        targets = requests.get(f'http://127.0.0.1:{port}/json/list', timeout=5).json()
    except (requests.RequestException, ValueError) as e:
        raise BrowserNotRunning(f'Browser session is not reachable: {e}')

    page = next(
        (t for t in targets
         if t.get('type') == 'page' and not t.get('url', '').startswith('devtools://')),
        None,
    )
    if not page:
        # All tabs closed (e.g. the page crashed) — open a fresh one.
        try:
            page = requests.put(
                f'http://127.0.0.1:{port}/json/new?{state.get("app_url", "about:blank")}',
                timeout=5,
            ).json()
        except (requests.RequestException, ValueError) as e:
            raise BrowserNotRunning(f'Could not open a browser tab: {e}')
    return page


def _pool_checkout(port, state):
    """Return the pooled entry for a port, creating it on cache miss."""
    with _cdp_pool_lock:
        entry = _cdp_pool.get(port)
    if entry is not None:
        return entry

    page = _resolve_page_target(port, state)
    try:
        conn = CdpConnection(page['webSocketDebuggerUrl'])
    except (WebSocketException, OSError, KeyError) as e:
        raise BrowserNotRunning(f'Could not attach to browser page: {e}')

    entry = {
        'ws_url': page.get('webSocketDebuggerUrl'),
        'conn': conn,
        'page': page,
        'lock': threading.Lock(),
    }
    with _cdp_pool_lock:
        existing = _cdp_pool.get(port)
        if existing is not None:
            # Another thread connected while we did; keep theirs.
            conn.close()
            return existing
        _cdp_pool[port] = entry
    return entry


def _pool_invalidate(port, entry=None):
    """Drop (and close) a pooled connection.

    With ``entry``, only unmaps it if it is still the pooled one — a
    concurrent request may already have replaced it with a fresh connection
    that must not be torn down. The stale entry's socket is always closed.
    """
    current = None
    with _cdp_pool_lock:
        current = _cdp_pool.get(port)
        if entry is None or current is entry:
            _cdp_pool.pop(port, None)
    if entry is not None:
        entry['conn'].close()
    elif current is not None:
        current['conn'].close()


class BrowserPreviewService:
    """Drives a per-project headless Chromium for the workspace preview."""

    def __init__(self, project):
        self.project = project
        # Reuse the dev-server manager: it owns the project's Django + Vite
        # subprocesses and the pid-file conventions we extend here.
        self.servers = PreviewService(project)
        self.pid_dir = self.servers.pid_dir

        # Keyed on the project id, never project.name: the ownership check in
        # the views validates the Project row, not a path derived from it, so a
        # name spelling another user's directory would have made _load_state()
        # hand back that user's live CDP session.
        stem = sidecar_stem(project)
        self.pid_file = os.path.join(self.pid_dir, f"{stem}{BROWSER_PID_SUFFIX}")
        self.log_file = os.path.join(self.pid_dir, f"{stem}{BROWSER_LOG_SUFFIX}")
        self.state_file = os.path.join(self.pid_dir, f"{stem}{BROWSER_STATE_SUFFIX}")
        self.profile_dir = os.path.join(self.pid_dir, f"{stem}{BROWSER_PROFILE_SUFFIX}")

    # ------------------------------------------------------------------
    # Session lifecycle
    # ------------------------------------------------------------------

    def start(self, viewport=None, device_scale_factor=None, prewarm=False):
        """Ensure dev servers + Chromium are running and showing the app.

        Idempotent: an already-healthy session is reused, so the workspace
        can call this on every mount without restarting anything.

        The whole bring-up runs under a per-project lock. Two starters race
        routinely — the warm-up at project creation and the workspace opening
        moments later — and the second must wait and reattach to what the
        first brought up, not launch a duplicate session over it.

        ``prewarm`` marks a session started ahead of the owner asking for it
        (see prewarm_recent_previews), which the idle reaper shuts down
        sooner if nobody opens it.
        """
        with preview_start_lock(self.pid_dir, sidecar_stem(self.project)):
            return self._start_locked(viewport, device_scale_factor, prewarm)

    def _start_locked(self, viewport, device_scale_factor, prewarm=False):
        ensure_idle_reaper()
        reap_idle_sessions()
        started = time.monotonic()
        timings = {}

        state = self._load_state()
        if viewport:
            width, height = self._clamp_viewport(*viewport)
        elif state and state.get('viewport'):
            width, height = self._clamp_viewport(*state['viewport'])
        else:
            width, height = DEFAULT_VIEWPORT
        dsf = self._clamp_dsf(
            device_scale_factor
            or (state or {}).get('device_scale_factor')
            or 1
        )

        # start() is the one place worth a full health probe: a hung browser
        # should be relaunched here, not surfaced as a request error later.
        fresh = not (state and self._browser_alive(state, probe=True))
        if fresh and not prewarm:
            # Someone is opening this project: at the host's session cap,
            # the least recently used session makes way for it.
            make_room_for_session(exclude=self.state_file)

        # A cold start has three independent boots: Django, Vite and Chromium.
        # Chromium doesn't need the app to be up to launch, so it comes up on
        # a blank page alongside the dev servers and is pointed at the app
        # once Vite answers — the wait is the slowest boot, not all three.
        with ThreadPoolExecutor(max_workers=1, thread_name_prefix='preview-browser') as pool:
            launch = pool.submit(self._timed_launch, width, height, dsf) if fresh else None
            # A server failure propagates once the launch finishes (leaving
            # the block waits for it). That browser is recorded in the state
            # file, so a retry reattaches to it and the idle reaper collects
            # it otherwise.
            server_state = self.servers.ensure_preview()
            # The dev servers report a localhost preview URL; dual-stack
            # projects point it at Vite, legacy single-Django ones at runserver.
            app_url = (server_state.get('preview_url') or '').replace('localhost', '127.0.0.1').rstrip('/')
            if not app_url:
                app_url = f"http://127.0.0.1:{self.servers.frontend_port}"
            self._wait_for_frontend(app_url)
            timings['servers'] = time.monotonic() - started
            if launch is not None:
                state, timings['browser'] = launch.result()

        if not fresh:
            state['viewport'] = [width, height]
            # A reused browser (typically one a warm-up launched at 1x
            # before any client said otherwise) adopts the client's density,
            # or a Retina screen gets soft frames until the pane is resized.
            state['device_scale_factor'] = dsf

        state['app_url'] = app_url
        state['last_active'] = time.time()
        if not prewarm:
            state['last_used'] = state['last_active']
        # Opening the workspace claims a prewarmed session; a prewarm never
        # re-marks a session someone is already using.
        state['prewarmed'] = bool(prewarm and (fresh or state.get('prewarmed')))
        self._save_state(state)
        if fresh:
            self._open_app_tab(state['cdp_port'], app_url + '/')

        def body(conn, _page):
            self._apply_viewport(conn, state)
            if fresh:
                time.sleep(0.3)  # let the first paint land in the frame below
            else:
                # Ask the live page where it is — the pooled target info
                # records the URL from when the connection was first resolved.
                history = conn.call('Page.getNavigationHistory')
                entries = history.get('entries', [])
                index = history.get('currentIndex', 0)
                current = entries[index].get('url', '') if 0 <= index < len(entries) else ''
                # A reused browser may sit on a network error page from before
                # the dev servers were (re)started; bring it back to the app.
                if not current.startswith(app_url):
                    conn.call('Page.navigate', {'url': app_url + '/'})
                    time.sleep(0.3)  # let the first paint land in the frame below
            payload = self._status_payload(conn, state)
            self._attach_frame(conn, payload, None)
            return payload

        status = self._with_page(state, body)
        timings['total'] = time.monotonic() - started
        status['servers'] = server_state.get('message', '')
        status['timings'] = {k: round(v, 2) for k, v in timings.items()}
        timing_logger.info(
            "preview start project=%s cold=%s %s",
            self.project.pk, fresh,
            ' '.join(f"{k}={v:.2f}s" for k, v in timings.items()),
        )
        return status

    def stop(self):
        """Stop Chromium and the project's dev servers."""
        self._kill_browser()
        return self.servers.stop_preview()

    def keep_alive(self):
        """Mark a running session as in use, so the idle reaper leaves it be.

        Returns whether a session was running. Doesn't claim a prewarmed
        session (start() does that), so one kept warm for the owner still
        goes after the shorter prewarm idle limit once the heartbeats stop.
        """
        try:
            state = self._require_state()
        except BrowserNotRunning:
            return False
        # Only last_active: being kept warm isn't being used, so it doesn't
        # move the session up the eviction order.
        now = time.time()
        if now - state.get('last_active', 0) > 30:
            state['last_active'] = now
            self._save_state(state)
        return True

    def is_running(self):
        state = self._load_state()
        return bool(state and self._browser_alive(state))

    # ------------------------------------------------------------------
    # Interaction (served over the worker's pooled CDP connection)
    # ------------------------------------------------------------------

    def frame(self, etag=None):
        """Return the current screenshot (unless it matches ``etag``) + nav state."""
        state = self._require_state(touch=True)

        def body(conn, _page):
            self._apply_viewport(conn, state)
            payload = self._status_payload(conn, state)
            self._attach_frame(conn, payload, etag)
            return payload

        return self._with_page(state, body)

    def dispatch_input(self, events, etag=None, frame=True):
        """Forward a batch of mouse/keyboard/wheel events, then return a frame.

        ``frame=False`` skips the screenshot (``frame_skipped`` in the reply):
        a client scrolling through a backdrop it already holds only needs to
        know where the page landed, and the capture is most of the request.
        """
        if not isinstance(events, list) or len(events) > MAX_EVENTS_PER_REQUEST:
            raise BrowserPreviewError('Invalid input event batch.')

        state = self._require_state(touch=True)
        width, height = state.get('viewport', DEFAULT_VIEWPORT)
        # Scroll/drag batches arrive back-to-back while the user's gesture is
        # in progress, so their frames prioritize latency over fidelity. A
        # plain hover is not a gesture: the pointer rests over the page while
        # the user reads it, and a low-resolution frame per mouse move kept the
        # whole page blurry for as long as the mouse moved.
        motion = any(
            isinstance(e, dict) and (
                e.get('kind') == 'wheel'
                or (e.get('type') == 'mouseMoved' and _as_int(e.get('buttons')))
            )
            for e in events
        )
        scrolls = any(isinstance(e, dict) and e.get('kind') in ('wheel', 'scroll') for e in events)

        def body(conn, _page):
            self._apply_viewport(conn, state)
            for event in events:
                method, params = self._translate_event(event, width, height)
                conn.call(method, params)
            payload = self._status_payload(conn, state, settle_scroll=scrolls)
            if not frame:
                payload['frame'] = None
                payload['frame_skipped'] = True
            elif motion or scrolls:
                self._attach_frame(
                    conn, payload, etag,
                    quality=MOTION_JPEG_QUALITY, motion_state=state,
                )
            else:
                self._attach_frame(conn, payload, etag)
            return payload

        # Not idempotent: a retry would dispatch the whole event batch twice.
        return self._with_page(state, body, idempotent=False, preempt=True)

    def navigate(self, action, path=None):
        """goto/back/forward/reload, then return a frame."""
        state = self._require_state(touch=True)
        app_url = state.get('app_url', '')

        def body(conn, _page):
            self._apply_viewport(conn, state)
            if action == 'goto':
                # Only paths on the project's own frontend are addressable
                # from the URL bar; the preview is not a general browser.
                clean = self._normalize_path(path)
                conn.call('Page.navigate', {'url': app_url + clean})
            elif action in ('back', 'forward'):
                history = conn.call('Page.getNavigationHistory')
                index = history.get('currentIndex', 0) + (1 if action == 'forward' else -1)
                entries = history.get('entries', [])
                if 0 <= index < len(entries):
                    conn.call('Page.navigateToHistoryEntry', {'entryId': entries[index]['id']})
            elif action == 'reload':
                conn.call('Page.reload', {'ignoreCache': False})
            else:
                raise BrowserPreviewError(f"Unknown navigation action: {action}")

            # Give the navigation a beat to paint before the first frame.
            time.sleep(0.15)
            payload = self._status_payload(conn, state)
            self._attach_frame(conn, payload, None)
            return payload

        # Not idempotent: a retried 'back' navigates back twice, a retried
        # goto/reload re-fires the navigation.
        return self._with_page(state, body, idempotent=False, preempt=True)

    def resize(self, width, height, device_scale_factor=None):
        """Adopt the client pane's size (CSS pixels)."""
        state = self._require_state(touch=True)
        state['viewport'] = list(self._clamp_viewport(width, height))
        if device_scale_factor:
            state['device_scale_factor'] = self._clamp_dsf(device_scale_factor)
        self._save_state(state)
        self._with_page(state, lambda conn, _page: self._apply_viewport(conn, state))
        return {'viewport': state['viewport']}

    # ------------------------------------------------------------------
    # Chromium process management
    # ------------------------------------------------------------------

    def backdrop(self, cached_only=False, touch=True):
        """Capture the page around the current scroll as slices + an overlay.

        Runs under the project's exclusive page lock (see _page_lock): the
        page is scrolled through and restyled while this works, and no frame
        or input request may see it that way. The scroll is restored before
        the lock is released.

        A complete capture is kept on disk and handed back as-is while the
        page is unchanged (see _cached_backdrop), so one taken ahead of time
        (a prewarm, an earlier visit) is on the client the moment it asks.
        ``cached_only`` returns that or nothing, never capturing: for a client
        that wants the page mid-gesture, when a capture would get in the way.
        ``touch=False`` (a warm-up) doesn't count as the owner using it.
        """
        state = self._require_state(touch=touch)
        width, height = state.get('viewport', DEFAULT_VIEWPORT)
        dsf = float(state.get('device_scale_factor', 1))
        empty = {'path': None, 'viewport': [int(width), int(height)], 'scroll': None,
                 'slices': [], 'overlay': None}
        # User input that arrives mid-capture stops it (see _page_lock): a
        # scroll waiting behind a whole backdrop read as the preview freezing.
        started = time.time()

        cached = self._with_page(state, lambda conn, _page: self._cached_backdrop(conn, state))
        if cached or cached_only:
            return cached or empty

        def warm(conn, _page):
            # First backdrop for this page: scroll through it once so
            # lazy images start loading and scroll-reveal content reveals.
            self._apply_viewport(conn, state)
            # Keyed by URL: an in-app route change keeps the document.
            first = self._evaluate(
                conn,
                'window.__imagiBackdropWarm !== location.href && !!(window.__imagiBackdropWarm = location.href)',
            )
            if not first:
                return False
            start = self._scroll_metrics(conn)
            if not start:
                return False
            try:
                for y in self._backdrop_offsets(start):
                    if self._input_waiting(started):
                        # Warm it properly next time.
                        self._evaluate(conn, 'window.__imagiBackdropWarm = null')
                        return False
                    self._evaluate(conn, _SCROLL_TO_JS % (start['x'], y))
                    self._evaluate(conn, _NEXT_FRAME_JS, await_promise=True)
            finally:
                self._evaluate(conn, _SCROLL_TO_JS % (start['x'], start['y']))
            return True

        if self._with_page(state, warm, exclusive=True):
            time.sleep(BACKDROP_WARM_SETTLE_S)
        if self._input_waiting(started):
            # The user is busy with the page; the client asks again once idle.
            return empty

        def capture(conn, _page):
            self._apply_viewport(conn, state)
            # Watch the DOM from here on, so the stamp read at the end says
            # whether the page still looks like these slices.
            self._evaluate(conn, _DOC_STAMP_JS)
            payload = self._status_payload(conn, state)
            start = payload.get('scroll')
            if not start:
                raise BrowserPreviewError('The page did not report its size.')
            slices = []
            overlay = None
            offsets = self._nearest_first(self._backdrop_offsets(start), start)
            cut_short = False
            png_misses = 0
            try:
                marked = self._evaluate(conn, _BACKDROP_MARK_JS) or 0
                if marked:
                    overlay = self._capture_overlay(conn, start, width, height)
                self._evaluate(conn, _BACKDROP_STYLE_JS % json.dumps(_BACKDROP_CSS['slices']))
                seen = set()
                # Nearest first, so a capture cut short by input still holds
                # the screens either side of the view (the client needs the
                # slices to be one contiguous run, which this order keeps).
                for y in offsets:
                    if slices and self._input_waiting(started):
                        cut_short = True
                        break
                    landed = self._evaluate(conn, _SCROLL_TO_JS % (start['x'], y)) or [start['x'], y]
                    lx, ly = float(landed[0]), float(landed[1])
                    if ly in seen:
                        continue
                    seen.add(ly)
                    data, kind = self._capture_slice(conn, {
                        'x': lx, 'y': ly, 'width': int(width), 'height': int(height), 'scale': 1,
                    }, png_misses < BACKDROP_PNG_MISSES)
                    png_misses = 0 if kind == 'png' else png_misses + 1
                    slices.append({'y': ly, 'frame': data, 'type': kind})
            finally:
                self._evaluate(conn, _BACKDROP_STYLE_JS % 'null')
                self._evaluate(conn, _SCROLL_TO_JS % (start['x'], start['y']))
            result = {
                'path': payload.get('path'),
                'viewport': [int(width), int(height)],
                'scroll': start,
                'slices': sorted(slices, key=lambda sl: sl['y']),
                'overlay': overlay,
            }
            if not cut_short and slices:
                # The page reacts to the scroll being put back on its next
                # frame (a header that shrinks on scroll); count that in.
                self._evaluate(conn, _NEXT_FRAME_JS, await_promise=True)
                stamp = self._evaluate(conn, _DOC_STAMP_JS)
                if stamp:
                    self._save_backdrop_cache(state, stamp, result)
            return result

        return self._with_page(state, capture, exclusive=True)

    def prepare_backdrop(self):
        """Capture the backdrop ahead of the owner opening the workspace.

        Best-effort, for warm-ups: the stored capture is what the workspace's
        first backdrop request gets back, so the whole page is there to
        scroll through from the moment the preview appears.
        """
        if not self._load_state():
            return
        # The app's first paint is in; give its data and images a moment.
        time.sleep(BACKDROP_PREPARE_DELAY_S)
        try:
            self.backdrop(touch=False)
        except Exception as e:
            logger.info("Backdrop for project %s not prepared: %s", self.project.pk, e)

    def _capture_slice(self, conn, clip, png):
        """One backdrop slice at full resolution: (base64, 'png'|'jpeg')."""
        if png:
            data = self._capture_png(conn, clip).get('data', '')
            if len(data) <= BACKDROP_PNG_BUDGET_B64:
                return data, 'png'
        return self._capture_screenshot(conn, BACKDROP_JPEG_QUALITY, clip).get('data', ''), 'jpeg'

    @property
    def _backdrop_cache_file(self):
        return os.path.join(self.pid_dir, f"{sidecar_stem(self.project)}{BACKDROP_CACHE_SUFFIX}")

    def _backdrop_key(self, state, stamp):
        return {
            'stamp': stamp,
            'viewport': [int(v) for v in state.get('viewport', DEFAULT_VIEWPORT)],
            'device_scale_factor': float(state.get('device_scale_factor', 1)),
        }

    def _save_backdrop_cache(self, state, stamp, result):
        tmp = f"{self._backdrop_cache_file}.{os.getpid()}.tmp"
        try:
            with open(tmp, 'w') as fh:
                json.dump({'key': self._backdrop_key(state, stamp), 'backdrop': result}, fh)
            os.replace(tmp, self._backdrop_cache_file)
        except (OSError, TypeError, ValueError):
            try:
                os.remove(tmp)
            except OSError:
                pass

    def _cached_backdrop(self, conn, state):
        """The stored backdrop, if the page still matches it, else None.

        It matches while the same document is showing, its DOM hasn't changed
        since the capture, the viewport is the same, and the view is inside
        the stretch of page the slices cover.
        """
        try:
            with open(self._backdrop_cache_file) as fh:
                cached = json.load(fh)
            key, result = cached['key'], cached['backdrop']
        except (OSError, ValueError, KeyError, TypeError):
            return None
        stamp = self._evaluate(conn, _DOC_STAMP_JS)
        if not stamp or key != self._backdrop_key(state, stamp):
            return None
        scroll = self._scroll_metrics(conn)
        slices = result.get('slices') or []
        if not scroll or not slices or abs(scroll['height'] - result['scroll']['height']) > 1:
            return None
        top = slices[0]['y']
        bottom = slices[-1]['y'] + scroll['viewport_height']
        if scroll['y'] < top - 0.5 or scroll['y'] + scroll['viewport_height'] > bottom + 0.5:
            return None
        return dict(result, scroll=scroll, cached=True)

    @staticmethod
    def _backdrop_offsets(metrics):
        """Slice offsets: up to BACKDROP_MAX_PX of page, mostly below the scroll."""
        vh = max(1.0, metrics['viewport_height'])
        page = max(metrics['height'], vh)
        span = min(page, BACKDROP_MAX_PX)
        top = max(0.0, min(metrics['y'] - span / 3, page - span))
        offsets = []
        y = top
        while y < top + span:
            offsets.append(y)
            y += vh
        return offsets

    @staticmethod
    def _nearest_first(offsets, metrics):
        """offsets reordered outward from the view: here, below, above, ..."""
        if not offsets:
            return offsets
        here = max(i for i, y in enumerate(offsets) if y <= metrics['y'] or i == 0)
        order = [here]
        below, above = here + 1, here - 1
        while below < len(offsets) or above >= 0:
            if below < len(offsets):
                order.append(below)
                below += 1
            if above >= 0:
                order.append(above)
                above -= 1
        return [offsets[i] for i in order]

    def _input_waiting(self, since):
        """Whether user input has queued for the page lock since ``since``."""
        try:
            return os.path.getmtime(self._input_waiting_file) > since
        except OSError:
            return False

    @property
    def _input_waiting_file(self):
        return os.path.join(self.pid_dir, f"{sidecar_stem(self.project)}_input_waiting")

    def _capture_overlay(self, conn, scroll, width, height):
        """The fixed (and stuck) elements alone, on a transparent background."""
        self._evaluate(conn, _BACKDROP_STYLE_JS % json.dumps(_BACKDROP_CSS['overlay']))
        try:
            conn.call('Emulation.setDefaultBackgroundColorOverride', {'color': {'r': 0, 'g': 0, 'b': 0, 'a': 0}})
        except CdpError:
            return None
        try:
            shot = conn.call('Page.captureScreenshot', {
                'format': 'png',
                'clip': {'x': scroll['x'], 'y': scroll['y'], 'width': int(width), 'height': int(height), 'scale': 1},
            })
            return shot.get('data') or None
        finally:
            conn.call('Emulation.setDefaultBackgroundColorOverride', {})

    def _evaluate(self, conn, expression, await_promise=False):
        params = {'expression': expression, 'returnByValue': True}
        if await_promise:
            params['awaitPromise'] = True
        result = conn.call('Runtime.evaluate', params)
        if result.get('exceptionDetails'):
            return None
        return result.get('result', {}).get('value')

    @staticmethod
    def _open_app_tab(port, url):
        """Swap the blank tab the browser launched with for one on the app.

        A tab opened straight onto the app has only the app in its history,
        so "back" never leads outside it. Navigating the blank tab instead
        fails on Chromium builds that move the page to a new renderer on its
        first real navigation ("Not attached to an active page").
        """
        base = f'http://127.0.0.1:{port}'
        try:
            blank = [t for t in requests.get(f'{base}/json/list', timeout=5).json()
                     if t.get('type') == 'page']
            requests.put(f'{base}/json/new?{url}', timeout=5).raise_for_status()
            for target in blank:
                requests.get(f"{base}/json/close/{target['id']}", timeout=5)
        except (requests.RequestException, ValueError, KeyError) as e:
            raise BrowserNotRunning(f'Could not open the app in the preview browser: {e}')
        finally:
            # Any pooled connection was to the blank tab.
            _pool_invalidate(port)

    def _timed_launch(self, width, height, dsf):
        began = time.monotonic()
        state = self._launch_chromium(width, height, dsf)
        return state, time.monotonic() - began

    def _launch_chromium(self, width, height, dsf, initial_url='about:blank'):
        executable = find_chromium()
        if not executable:
            raise BrowserPreviewError(
                'No Chromium/Chrome executable found. Install Chromium or set '
                'BROWSER_PREVIEW_EXECUTABLE to a browser binary.'
            )

        self._kill_browser(keep_profile=True)

        cdp_port = self.servers._find_available_port_excluding(9300, 9400)
        # The port range recycles: drop any pooled connection to a previous
        # browser that happened to use this port.
        _pool_invalidate(cdp_port)
        os.makedirs(self.profile_dir, exist_ok=True)
        self._clear_singleton_locks()

        # --no-sandbox: the preview renders the user's own generated app, and
        # that same code already runs unsandboxed in this container via the
        # dev servers, so the browser sandbox (which cannot run as root in
        # containers) adds no isolation here.
        args = [
            executable,
            '--headless',
            f'--remote-debugging-port={cdp_port}',
            '--remote-debugging-address=127.0.0.1',
            f'--user-data-dir={self.profile_dir}',
            f'--window-size={width},{height}',
            f'--force-device-scale-factor={dsf}',
            '--no-first-run',
            '--no-default-browser-check',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--disable-background-networking',
            '--mute-audio',
            '--no-sandbox',
            initial_url,
        ]

        logger.info(f"Launching preview browser for {self.project.name} on CDP port {cdp_port}")
        with open(self.log_file, 'w') as log_fh:
            process = subprocess.Popen(args, stdout=log_fh, stderr=subprocess.STDOUT)

        with open(self.pid_file, 'w') as f:
            f.write(str(process.pid))

        state = {
            'cdp_port': cdp_port,
            'pid': process.pid,
            'viewport': [width, height],
            'device_scale_factor': dsf,
            'last_active': time.time(),
        }

        # Wait for the DevTools endpoint to accept connections.
        deadline = time.time() + 30
        while time.time() < deadline:
            if process.poll() is not None:
                tail = self.servers._read_log_tail(self.log_file)
                raise BrowserPreviewError(f"Browser exited on startup: {tail}")
            try:
                requests.get(f'http://127.0.0.1:{cdp_port}/json/version', timeout=2)
                self._save_state(state)
                return state
            except requests.RequestException:
                time.sleep(0.25)

        raise BrowserPreviewError('Browser did not expose its DevTools endpoint in time.')

    def _clear_singleton_locks(self):
        """Remove Chromium's profile lock files before (re)launching.

        Chromium writes ``SingletonLock`` (a symlink to ``<hostname>-<pid>``)
        into the user-data-dir to stop two instances sharing one profile. We
        keep the profile across relaunches (``keep_profile=True``), so on a
        Railway redeploy the new container inherits the previous container's
        lock. Because the hostname differs, Chromium can't confirm the old pid
        is dead and refuses to start ("in use by another Chromium process on
        another computer"). We've already killed any browser we own by the time
        this runs, so any lock still present is stale and safe to delete.
        """
        for name in ('SingletonLock', 'SingletonSocket', 'SingletonCookie'):
            try:
                os.unlink(os.path.join(self.profile_dir, name))
            except OSError:
                # Missing (the common case) or a directory we didn't create —
                # either way there's no lock of ours to clear.
                pass

    def _kill_browser(self, keep_profile=False):
        self.servers._kill_from_pid_file(self.pid_file)
        state = self._load_state()
        if state and state.get('cdp_port'):
            _pool_invalidate(state['cdp_port'])
            self.servers._kill_by_port(state['cdp_port'])
        for path in (self.state_file, self._backdrop_cache_file):
            try:
                os.remove(path)
            except OSError:
                pass
        if not keep_profile:
            shutil.rmtree(self.profile_dir, ignore_errors=True)

    def _browser_alive(self, state, probe=False):
        """Whether the recorded Chromium process is alive.

        The default is just the cheap PID check — hot-path requests run on
        every frame poll, and a dead DevTools endpoint surfaces as a
        connection failure there anyway. ``probe=True`` adds the HTTP
        round-trip for callers that act on the answer (start() relaunches
        a hung browser instead of erroring).
        """
        pid, port = state.get('pid'), state.get('cdp_port')
        if not pid or not port:
            return False
        try:
            proc = psutil.Process(pid)
            if not proc.is_running():
                return False
        except psutil.NoSuchProcess:
            return False
        if probe:
            try:
                requests.get(f'http://127.0.0.1:{port}/json/version', timeout=2)
            except requests.RequestException:
                return False
        return True

    def _wait_for_frontend(self, app_url):
        """Block until the Vite dev server answers HTTP."""
        deadline = time.time() + FRONTEND_READY_TIMEOUT
        last_error = None
        while time.time() < deadline:
            try:
                requests.get(app_url + '/', timeout=3)
                return
            except requests.RequestException as e:
                last_error = e
                time.sleep(0.5)
        raise BrowserPreviewError(
            f"The project's dev server did not become reachable: {last_error}"
        )

    # ------------------------------------------------------------------
    # CDP helpers
    # ------------------------------------------------------------------

    @contextlib.contextmanager
    def _page_lock(self, exclusive, preempt=False):
        """Cross-process lock on this project's page.

        Frame, input and navigation requests share it; a backdrop capture
        takes it exclusively, because it scrolls and restyles the page and
        each worker process has its own CDP connection, so the per-process
        pool lock alone wouldn't keep another worker's frame from catching
        the page mid-capture. Best effort: a lock not acquired in
        PAGE_LOCK_TIMEOUT_S is skipped rather than failing the request.

        ``preempt`` (user input) that finds the lock held says so by touching
        a stamp file the backdrop capture checks between slices, so it wraps
        up and lets the input through instead of making it wait.
        """
        if fcntl is None:
            yield
            return
        fh = None
        try:
            fh = open(os.path.join(self.pid_dir, f"{sidecar_stem(self.project)}_page.lock"), 'a')
        except OSError:
            yield
            return
        mode = fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH
        locked = False
        deadline = time.time() + PAGE_LOCK_TIMEOUT_S
        try:
            while True:
                try:
                    fcntl.flock(fh, mode | fcntl.LOCK_NB)
                    locked = True
                    break
                except OSError:
                    if preempt:
                        preempt = False
                        try:
                            with open(self._input_waiting_file, 'a'):
                                pass
                            os.utime(self._input_waiting_file)
                        except OSError:
                            pass
                    if time.time() >= deadline:
                        break
                    time.sleep(0.01)
            yield
        finally:
            if locked:
                fcntl.flock(fh, fcntl.LOCK_UN)
            fh.close()

    def _with_page(self, state, body, idempotent=True, exclusive=False, preempt=False):
        with self._page_lock(exclusive, preempt):
            return self._with_page_unlocked(state, body, idempotent)

    def _with_page_unlocked(self, state, body, idempotent=True):
        """Run ``body(conn, page)`` on the pooled CDP connection for this browser.

        The pooled connection is shared across requests and never closed by a
        request; a transport or CDP failure invalidates the pool entry, the
        page target is re-resolved and the body retried once (this covers a
        connection gone stale behind the cache, e.g. after a browser restart).
        A second failure propagates.

        ``idempotent=False`` disables the retry: input and navigation bodies
        perform their side effects before the trailing status/screenshot calls,
        so re-running the whole body after a late failure would replay clicks,
        keystrokes and history navigations against the live page.
        """
        port = state['cdp_port']
        last_error = None
        for attempt in (0, 1):
            entry = _pool_checkout(port, state)
            with entry['lock']:
                try:
                    return body(entry['conn'], entry['page'])
                except (WebSocketException, CdpError, ConnectionError, OSError) as e:
                    # Always drop the entry so the next request reconnects.
                    _pool_invalidate(port, entry)
                    last_error = e
                    if attempt or not idempotent:
                        raise
            logger.info(f"Pooled CDP connection failed ({last_error}); reconnecting once")

    def _apply_viewport(self, conn, state):
        width, height = state.get('viewport', DEFAULT_VIEWPORT)
        dsf = float(state.get('device_scale_factor', 1))
        requested = [int(width), int(height), dsf]
        # Emulation overrides live exactly as long as the CDP session that
        # set them, and the connection is pooled now — so once this
        # connection has applied the requested metrics there is nothing to
        # re-send. That matters because every override forces a relayout,
        # which makes frame streaming stutter. A fresh connection starts at
        # None, forcing one apply.
        if conn.applied_viewport == requested:
            return
        # The page's own scrollbar is drawn into the frame, where it slid
        # with the optimistic scroll and then snapped back. The client draws
        # its own scrollbar from the scroll metrics instead. Hiding it only
        # takes effect at the next layout, which the override below forces,
        # so it has to come first.
        try:
            conn.call('Emulation.setScrollbarsHidden', {'hidden': True})
        except CdpError:
            pass  # older Chromium: keep the native scrollbar
        conn.call('Emulation.setDeviceMetricsOverride', {
            'width': requested[0],
            'height': requested[1],
            'deviceScaleFactor': dsf,
            'mobile': False,
        })
        conn.applied_viewport = requested

    # Whether this Chromium accepts captureScreenshot's optimizeForSpeed
    # param (Chrome 104+); flipped off on the first rejection.
    _fast_screenshots = True

    def _capture_screenshot(self, conn, quality, clip=None):
        params = {'format': 'jpeg', 'quality': int(quality)}
        if clip:
            params['clip'] = clip
        if BrowserPreviewService._fast_screenshots:
            try:
                return conn.call('Page.captureScreenshot', {**params, 'optimizeForSpeed': True})
            except CdpError:
                BrowserPreviewService._fast_screenshots = False
        return conn.call('Page.captureScreenshot', params)

    def _motion_clip(self, conn, state, scroll=None):
        """Clip that captures the visible viewport at 1 CSS px per image px.

        On a HiDPI client the browser renders at deviceScaleFactor 2, so a
        full frame carries 4x the pixels the pane shows at 1x. Mid-gesture
        that costs more than it buys: measured locally on a 1000x800 pane at
        2x, a 1x motion frame is ~3x smaller (53 vs 163 KB of base64) and
        encodes ~40% faster, and the client stretches it to the same box. The
        idle poll after the gesture delivers the full-resolution frame.
        Returns None (capture the normal frame) at 1x or if metrics fail.
        """
        dsf = float(state.get('device_scale_factor', 1))
        if dsf <= 1:
            return None
        if scroll:
            # The settled offset the payload already read (see _scroll_metrics):
            # an offset read before the scroll lands would clip the region the
            # page just scrolled away from.
            metrics = {'pageX': scroll['x'], 'pageY': scroll['y']}
        else:
            try:
                metrics = conn.call('Page.getLayoutMetrics').get('cssVisualViewport') or {}
            except CdpError:
                return None
        width, height = state.get('viewport', DEFAULT_VIEWPORT)
        # Clip coordinates are document coordinates, so offset by the scroll
        # position or the capture shows the top of the page.
        return {
            'x': float(metrics.get('pageX') or 0),
            'y': float(metrics.get('pageY') or 0),
            'width': int(width),
            'height': int(height),
            'scale': 1 / dsf,
        }

    def _capture_png(self, conn, clip=None):
        params = {'format': 'png'}
        if clip:
            params['clip'] = clip
        if BrowserPreviewService._fast_screenshots:
            try:
                # optimizeForSpeed picks fast zlib: ~3x faster than the default
                # for a slightly larger file (measured 34 vs 92 ms at 2x).
                return conn.call('Page.captureScreenshot', {**params, 'optimizeForSpeed': True})
            except CdpError:
                BrowserPreviewService._fast_screenshots = False
        return conn.call('Page.captureScreenshot', params)

    def _capture_settled(self, conn):
        """A full-resolution frame of the page at rest: (base64, 'png'|'jpeg')."""
        if time.time() >= getattr(conn, 'png_skip_until', 0):
            data = self._capture_png(conn).get('data', '')
            if len(data) <= FRAME_PNG_BUDGET_B64:
                return data, 'png'
            conn.png_skip_until = time.time() + FRAME_PNG_RETRY_S
        return self._capture_screenshot(conn, FRAME_JPEG_QUALITY).get('data', ''), 'jpeg'

    def _attach_frame(self, conn, payload, etag, quality=None, motion_state=None):
        clip = (
            self._motion_clip(conn, motion_state, payload.get('scroll'))
            if motion_state else None
        )
        if quality is None and clip is None:
            data, frame_type = self._capture_settled(conn)
        else:
            shot = self._capture_screenshot(conn, quality or FRAME_JPEG_QUALITY, clip)
            data, frame_type = shot.get('data', ''), 'jpeg'
        payload['frame_type'] = frame_type
        # The etag only has to change when the frame does, so hash the base64
        # text as-is — decoding it first would just burn CPU per frame.
        digest = hashlib.sha1(data.encode('ascii')).hexdigest() if data else ''
        payload['etag'] = digest
        if etag and etag == digest:
            payload['frame'] = None  # unchanged since the client's last frame
        else:
            payload['frame'] = data

    def _status_payload(self, conn, state, settle_scroll=False):
        self._ensure_console_watch(conn)
        history = conn.call('Page.getNavigationHistory')
        entries = history.get('entries', [])
        index = history.get('currentIndex', 0)
        current = entries[index] if 0 <= index < len(entries) else {}
        url = current.get('url', '')
        return {
            'path': self._display_path(url, state.get('app_url', '')),
            'title': current.get('title', ''),
            'can_go_back': index > 0,
            'can_go_forward': index < len(entries) - 1,
            'viewport': state.get('viewport', list(DEFAULT_VIEWPORT)),
            'device_scale_factor': state.get('device_scale_factor', 1),
            'console_errors': self._collect_console_errors(conn),
            'scroll': self._scroll_metrics(conn, settle=settle_scroll),
        }

    def _scroll_metrics(self, conn, settle=False):
        """The page's scroll position/extent and background, or None.

        ``settle`` waits for the page's next frame first; pass it after
        dispatching wheel input so the offset matches the screenshot taken
        next. Like console errors, this is page-supplied data that never fails
        a frame, so it is re-validated and any failure reports None.
        """
        params = {
            'expression': _SETTLED_SCROLL_METRICS_JS if settle else _SCROLL_METRICS_JS,
            'returnByValue': True,
        }
        if settle:
            params['awaitPromise'] = True
        try:
            result = conn.call('Runtime.evaluate', params)
        except CdpError:
            return None
        raw = result.get('result', {}).get('value')
        if result.get('exceptionDetails') or not isinstance(raw, dict):
            return None
        metrics = {}
        for key in ('x', 'y', 'width', 'height', 'viewport_width', 'viewport_height'):
            try:
                value = float(raw.get(key) or 0)
            except (TypeError, ValueError):
                return None
            if value != value or value in (float('inf'), float('-inf')):
                return None
            metrics[key] = round(max(0.0, min(value, 1e7)), 2)
        background = raw.get('background')
        metrics['background'] = (
            background if isinstance(background, str) and _CSS_COLOR_RE.match(background) else ''
        )
        return metrics

    def _ensure_console_watch(self, conn):
        """Arm the console collector for documents the page navigates to next.

        Registered once per pooled connection (registrations live exactly as
        long as their CDP session, like emulation overrides), so errors
        raised during a new document's startup are captured too. The current
        document is covered by the lazy install in _CONSOLE_COLLECT_JS.
        """
        if conn.console_watch_registered:
            return
        try:
            # Verified against real Chrome: the registration is inert until
            # the Page domain is enabled. Enabling makes Chromium emit Page
            # events on this socket between requests; call()'s recv loop
            # already skips them, and they only fire on navigations.
            conn.call('Page.enable')
            conn.call('Page.addScriptToEvaluateOnNewDocument', {'source': _CONSOLE_WATCH_JS})
        except CdpError as e:
            # The collector still installs lazily on every poll; only errors
            # raised before a document's first poll would be missed.
            logger.info(f"Console watch pre-registration unavailable: {e}")
        conn.console_watch_registered = True

    def _collect_console_errors(self, conn):
        """Read (installing if needed) the page's recent console-error buffer."""
        try:
            result = conn.call('Runtime.evaluate', {
                'expression': _CONSOLE_COLLECT_JS,
                'returnByValue': True,
            })
        except CdpError:
            return []  # diagnostics must never fail a frame
        if result.get('exceptionDetails'):
            return []
        raw = result.get('result', {}).get('value')
        if not isinstance(raw, list):
            return []
        # Re-validate page-supplied data: the shape is enforced by injected
        # code, but the page can overwrite window.__imagiErrors with anything.
        errors = []
        for item in raw[-MAX_CONSOLE_ERRORS:]:
            if not (isinstance(item, dict) and item.get('text')):
                continue
            try:
                ts = int(item.get('ts') or 0)
            except (TypeError, ValueError):
                ts = 0
            errors.append({
                'level': 'error',
                'text': str(item['text'])[:CONSOLE_ERROR_TEXT_LIMIT],
                'ts': ts,
            })
        return errors

    def _translate_event(self, event, width, height):
        """Validate one client input event and map it onto a CDP command."""
        if not isinstance(event, dict):
            raise BrowserPreviewError('Malformed input event.')
        kind = event.get('kind')
        modifiers = int(event.get('modifiers') or 0) & MODIFIER_MASK

        if kind == 'mouse':
            etype = event.get('type')
            if etype not in _MOUSE_EVENT_TYPES:
                raise BrowserPreviewError(f'Unsupported mouse event: {etype}')
            button = event.get('button', 'none')
            if button not in _MOUSE_BUTTONS:
                button = 'none'
            return 'Input.dispatchMouseEvent', {
                'type': etype,
                'x': max(0, min(float(event.get('x') or 0), width)),
                'y': max(0, min(float(event.get('y') or 0), height)),
                'button': button,
                'buttons': int(event.get('buttons') or 0),
                'clickCount': max(0, min(int(event.get('clickCount') or 0), 3)),
                'modifiers': modifiers,
            }

        if kind == 'wheel':
            return 'Input.dispatchMouseEvent', {
                'type': 'mouseWheel',
                'x': max(0, min(float(event.get('x') or 0), width)),
                'y': max(0, min(float(event.get('y') or 0), height)),
                'deltaX': float(event.get('deltaX') or 0),
                'deltaY': float(event.get('deltaY') or 0),
                'modifiers': modifiers,
            }

        if kind == 'scroll':
            # Absolute scroll to a document offset: the client's scrollbar
            # thumb. Unlike a wheel event it doesn't depend on what sits under
            # the pointer, so dragging the thumb always moves the page itself.
            try:
                top = max(0.0, min(float(event.get('y') or 0), 1e7))
            except (TypeError, ValueError):
                raise BrowserPreviewError('Malformed scroll event.')
            return 'Runtime.evaluate', {
                'expression': f"window.scrollTo({{top: {top:.2f}, behavior: 'instant'}})",
            }

        if kind == 'key':
            etype = event.get('type')
            if etype not in _KEY_EVENT_TYPES:
                raise BrowserPreviewError(f'Unsupported key event: {etype}')
            text = event.get('text') or ''
            params = {
                # keyDown without text produces no character input; CDP calls
                # that variant rawKeyDown (this mirrors what Puppeteer sends).
                'type': etype if etype == 'keyUp' else ('keyDown' if text else 'rawKeyDown'),
                'key': str(event.get('key') or '')[:32],
                'code': str(event.get('code') or '')[:32],
                'modifiers': modifiers,
                'windowsVirtualKeyCode': int(event.get('keyCode') or 0),
                'nativeVirtualKeyCode': int(event.get('keyCode') or 0),
            }
            if text and etype == 'keyDown':
                params['text'] = text[:8]
            return 'Input.dispatchKeyEvent', params

        raise BrowserPreviewError(f'Unsupported input kind: {kind}')

    # ------------------------------------------------------------------
    # State files
    # ------------------------------------------------------------------

    def _require_state(self, touch=False):
        state = self._load_state()
        if not state or not self._browser_alive(state):
            raise BrowserNotRunning('The preview browser is not running.')
        if touch:
            # last_active drives idle reaping and last_used drives eviction
            # order (see make_room_for_session); throttle rewrites to one
            # per 30s.
            now = time.time()
            if now - min(state.get('last_active', 0), state.get('last_used', 0)) > 30:
                state['last_active'] = state['last_used'] = now
                self._save_state(state)
        return state

    def _load_state(self):
        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)
        except (OSError, ValueError):
            return None
        return state if isinstance(state, dict) else None

    def _save_state(self, state):
        try:
            with open(self.state_file, 'w') as f:
                json.dump(state, f)
        except OSError as e:
            logger.warning(f"Could not save browser preview state: {e}")

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _clamp_viewport(width, height):
        try:
            width, height = int(width), int(height)
        except (TypeError, ValueError):
            return DEFAULT_VIEWPORT
        return (
            max(MIN_VIEWPORT, min(width, MAX_VIEWPORT)),
            max(MIN_VIEWPORT, min(height, MAX_VIEWPORT)),
        )

    @staticmethod
    def _clamp_dsf(value):
        try:
            return max(1.0, min(float(value), 3.0))
        except (TypeError, ValueError):
            return 1.0

    @staticmethod
    def _normalize_path(path):
        if path is not None and not isinstance(path, str):
            raise BrowserPreviewError('Path must be a string.')
        clean = (path or '/').strip()
        if not clean.startswith('/'):
            clean = '/' + clean
        # Reject anything that could escape onto another origin
        # (protocol-relative //host, backslash tricks, embedded schemes).
        if clean.startswith('//') or '\\' in clean or '://' in clean:
            raise BrowserPreviewError('Only paths within the project can be opened.')
        return clean

    @staticmethod
    def _display_path(url, app_url):
        """Map the internal dev-server URL to the path shown in the UI."""
        if app_url and url.startswith(app_url):
            return url[len(app_url):] or '/'
        if not url or url == 'about:blank':
            return '/'
        return url  # off-origin (page-initiated) navigation: show it verbatim


def find_chromium():
    """Locate a Chromium/Chrome binary, preferring explicit configuration."""
    configured = getattr(settings, 'BROWSER_PREVIEW_EXECUTABLE', '') or ''
    if configured:
        return configured if os.path.exists(configured) else shutil.which(configured)

    for name in ('chromium', 'chromium-browser', 'google-chrome-stable', 'google-chrome'):
        found = shutil.which(name)
        if found:
            return found

    mac_paths = (
        '/Applications/Chromium.app/Contents/MacOS/Chromium',
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    )
    for path in mac_paths:
        if os.path.exists(path):
            return path

    # Playwright-managed browsers (present in some dev/CI environments).
    browsers_root = os.environ.get('PLAYWRIGHT_BROWSERS_PATH')
    if browsers_root:
        pattern = 'chrome.exe' if sys.platform == 'win32' else 'chrome'
        for candidate in sorted(glob.glob(os.path.join(browsers_root, 'chromium-*', '*', pattern)), reverse=True):
            if os.access(candidate, os.X_OK):
                return candidate

    return None


def start_preview_warmup(project):
    """Bring the project's preview session up in the background.

    Called when a project is created, so the dev servers and browser are
    already live — dependencies linked, Vite's dependency pre-bundle done —
    by the time the founder opens the workspace. Without it the first open
    pays the whole boot right after they have waited on the build.

    Best-effort: the workspace's own start() remains the call that reports
    failures to the user, and it simply reattaches when this got there
    first. Returns the thread, or None when warm-up is disabled.
    """
    if not getattr(settings, 'BROWSER_PREVIEW_PREWARM_ON_CREATE', True):
        return None

    def run():
        close_old_connections()
        try:
            service = BrowserPreviewService(project)
            service.start()
            service.prepare_backdrop()
            logger.info("Preview warmed up for project %s", project.pk)
        except Exception:
            logger.warning(
                "Preview warm-up for project %s did not complete; the workspace "
                "will start it on demand", project.pk, exc_info=True,
            )
        finally:
            close_old_connections()

    thread = threading.Thread(
        target=run, name=f"preview-warmup-{project.pk}", daemon=True
    )
    thread.start()
    return thread


def prewarm_recent_previews(user, viewport=None, device_scale_factor=None):
    """Bring up previews for the owner's most recently opened projects.

    Called at sign-in and then on a heartbeat for as long as the owner is
    signed in with Imagi open, on the bet that the projects someone opened
    last are the ones they open next: the workspace then reattaches to a
    running session (well under a second) instead of booting one. Each call
    starts whichever of those projects isn't running and keeps the running
    ones from idling out, so they stay warm while the owner browses the rest
    of the site and go cold once the heartbeats stop. Bounded three ways
    so it can never run up resources: at most
    BROWSER_PREVIEW_PREWARM_RECENT projects, none at all once the host has
    BROWSER_PREVIEW_MAX_SESSIONS live sessions, and an unopened prewarmed
    session is shut down after BROWSER_PREVIEW_PREWARM_IDLE_TIMEOUT. The
    owner's previews outside those few, the least recently used, are
    stopped first (see _projects_by_recent_use for what counts as use).

    The projects start one after another on one background thread, most
    recent first, so a sign-in never starts several boots at once. They
    render at ``viewport`` / ``device_scale_factor`` (the size the owner's
    preview pane had last time) so the workspace can show one the moment it
    opens. Returns the thread, or None when there is nothing to do.
    """
    limit = getattr(settings, 'BROWSER_PREVIEW_PREWARM_RECENT', 3)
    if not limit or not getattr(user, 'pk', None):
        return None

    ranked = _projects_by_recent_use(user)
    projects = ranked[:limit]
    if not projects:
        return None

    with _prewarm_lock:
        # A heartbeat that lands while the last one is still booting
        # previews has nothing to add.
        running = _prewarm_threads.get(user.pk)
        if running is not None and running.is_alive():
            return None

    def run():
        close_old_connections()
        try:
            from .project_files_service import ensure_working_copy
            # The owner's sessions beyond the most recent few make way first.
            _evict_sessions(ranked[limit:])
            for project in projects:
                if live_session_count() >= getattr(settings, 'BROWSER_PREVIEW_MAX_SESSIONS', 12):
                    logger.info("Preview prewarm stopped: the host is at its session cap")
                    return
                try:
                    service = BrowserPreviewService(project)
                    if service.keep_alive():
                        continue
                    ensure_working_copy(project)
                    service.start(
                        viewport=viewport,
                        device_scale_factor=device_scale_factor,
                        prewarm=True,
                    )
                    service.prepare_backdrop()
                    logger.info("Preview prewarmed for project %s", project.pk)
                except Exception:
                    logger.warning(
                        "Preview prewarm for project %s did not complete; the "
                        "workspace will start it on demand", project.pk, exc_info=True,
                    )
        finally:
            close_old_connections()

    thread = threading.Thread(
        target=run, name=f"preview-prewarm-user-{user.pk}", daemon=True
    )
    with _prewarm_lock:
        _prewarm_threads[user.pk] = thread
    thread.start()
    return thread


# A session used this recently is on someone's screen and is never evicted.
IN_USE_SECONDS = 60


def _session_last_used(service):
    """When the session was last opened or interacted with (0 if never)."""
    state = service._load_state() or {}
    return state.get('last_used') or 0


def _projects_by_recent_use(user):
    """The owner's projects, most recently used first.

    A project counts as used when its workspace was opened
    (Project.last_opened_at) and while its preview is being viewed or
    clicked (the session's last_used), whichever is later, so the project
    someone has been working in all afternoon outranks one they opened
    after it and left.
    """
    from apps.Imagi.ProjectManager.models import Project

    projects = list(
        Project.objects.filter(user=user, is_active=True)
        .exclude(project_dir='')
        .select_related('user')
    )

    def last_used(project):
        opened = project.last_opened_at.timestamp() if project.last_opened_at else 0
        try:
            viewed = _session_last_used(BrowserPreviewService(project))
        except Exception:
            viewed = 0
        return (max(opened, viewed), project.updated_at.timestamp() if project.updated_at else 0)

    return sorted(projects, key=last_used, reverse=True)


def _evict_sessions(projects):
    """Stop these projects' running previews, unless one is on screen now."""
    now = time.time()
    for project in projects:
        try:
            service = BrowserPreviewService(project)
            if not service.is_running():
                continue
            with preview_start_lock(service.pid_dir, sidecar_stem(project)):
                if now - _session_last_used(service) < IN_USE_SECONDS:
                    continue
                service.stop()
            logger.info("Preview for project %s evicted (least recently used)", project.pk)
        except Exception:
            logger.warning("Could not evict preview for project %s", project.pk, exc_info=True)


def evict_least_recent_previews(user):
    """Stop the owner's previews beyond their BROWSER_PREVIEW_PREWARM_RECENT
    most recently used projects, on a background thread.

    Runs when a workspace opens, so opening a fourth project shuts down the
    least recently used of the earlier ones right away rather than when it
    idles out.
    """
    limit = getattr(settings, 'BROWSER_PREVIEW_PREWARM_RECENT', 3)
    if not limit or not getattr(user, 'pk', None):
        return None

    def run():
        close_old_connections()
        try:
            _evict_sessions(_projects_by_recent_use(user)[limit:])
        finally:
            close_old_connections()

    thread = threading.Thread(target=run, name=f"preview-evict-user-{user.pk}", daemon=True)
    thread.start()
    return thread


# The prewarm thread per user in this process, so heartbeats never stack.
_prewarm_threads = {}
_prewarm_lock = threading.Lock()


def _live_sessions():
    """(state file, state) for every preview session on this host with a live browser."""
    root = getattr(settings, 'PROJECTS_ROOT', None)
    if not root or not os.path.isdir(root):
        return []
    sessions = []
    for state_file in glob.glob(os.path.join(root, '*', f'*{BROWSER_STATE_SUFFIX}')):
        try:
            with open(state_file, 'r') as f:
                state = json.load(f) or {}
            pid = state.get('pid')
            if pid and psutil.pid_exists(pid):
                sessions.append((state_file, state))
        except (OSError, ValueError, AttributeError):
            continue
    return sessions


def live_session_count():
    """How many preview sessions on this host have a live browser."""
    return len(_live_sessions())


def make_room_for_session(exclude=None):
    """Keep the host under BROWSER_PREVIEW_MAX_SESSIONS when a session starts.

    At the cap, the least recently used sessions shut down to make room:
    prewarmed ones nobody opened go first (they were never used), then the
    ones whose workspace was used longest ago. A session in use within the
    last IN_USE_SECONDS is left alone even then; starting over the cap beats
    closing a preview someone is looking at.
    """
    cap = getattr(settings, 'BROWSER_PREVIEW_MAX_SESSIONS', 12)
    if not cap:
        return
    sessions = [s for s in _live_sessions() if s[0] != exclude]
    excess = len(sessions) + 1 - cap
    if excess <= 0:
        return
    now = time.time()
    idle = sorted(
        (s for s in sessions if now - (s[1].get('last_used') or 0) >= IN_USE_SECONDS),
        key=lambda s: (s[1].get('last_used') or 0, s[1].get('last_active') or 0),
    )
    for state_file, _ in idle[:excess]:
        logger.info(f"Evicting least recently used preview: {os.path.basename(state_file)}")
        _shut_down_session(state_file)


_reaper_thread = None
_reaper_lock = threading.Lock()


def ensure_idle_reaper():
    """Run reap_idle_sessions on a timer in this process.

    Reaping used to happen only when some preview started, so a session
    nobody returned to could outlive its idle limit for as long as the host
    stayed quiet — and a prewarmed session nobody opens is exactly that. One
    daemon thread per process; reaping is idempotent, so several workers
    each running one is harmless.
    """
    global _reaper_thread
    interval = getattr(settings, 'BROWSER_PREVIEW_REAP_INTERVAL', 60)
    if not interval:
        return
    with _reaper_lock:
        if _reaper_thread is not None and _reaper_thread.is_alive():
            return

        def loop():
            while True:
                time.sleep(interval)
                try:
                    reap_idle_sessions()
                except Exception:
                    logger.warning("Idle preview reaping failed", exc_info=True)

        _reaper_thread = threading.Thread(target=loop, name='preview-idle-reaper', daemon=True)
        _reaper_thread.start()


def reap_idle_sessions():
    """Shut down preview sessions (browser + dev servers) idle past the limit.

    Runs when any preview starts and on ensure_idle_reaper's timer. Works purely from the
    per-project files on disk so it needs no database access and covers
    every user's projects.
    """
    timeout = getattr(settings, 'BROWSER_PREVIEW_IDLE_TIMEOUT', 1800)
    if not timeout:
        return
    # A session prewarmed at sign-in that the owner never opened goes sooner.
    prewarm_timeout = min(
        getattr(settings, 'BROWSER_PREVIEW_PREWARM_IDLE_TIMEOUT', 600) or timeout, timeout
    )

    root = getattr(settings, 'PROJECTS_ROOT', None)
    if not root or not os.path.isdir(root):
        return

    now = time.time()
    for state_file in glob.glob(os.path.join(root, '*', f'*{BROWSER_STATE_SUFFIX}')):
        try:
            with open(state_file, 'r') as f:
                state = json.load(f)
            if not isinstance(state, dict):
                continue
            limit = prewarm_timeout if state.get('prewarmed') else timeout
            if now - state.get('last_active', 0) < limit:
                continue

            logger.info(f"Reaping idle preview session: {os.path.basename(state_file)}")
            _shut_down_session(state_file)
        except Exception as e:
            logger.warning(f"Could not reap preview session {state_file}: {e}")


def _shut_down_session(state_file):
    """Stop a session (browser + dev servers) from its state file alone."""
    prefix = state_file[:-len(BROWSER_STATE_SUFFIX)]
    # Browser first, then the dev servers recorded by PreviewService.
    _kill_pid_file(prefix + BROWSER_PID_SUFFIX)
    _kill_pid_file(prefix + '_frontend.pid')
    _kill_pid_file(prefix + '_backend.pid')
    for leftover in (state_file, prefix + '_preview_ports.json', prefix + BACKDROP_CACHE_SUFFIX):
        try:
            os.remove(leftover)
        except OSError:
            pass
    shutil.rmtree(prefix + BROWSER_PROFILE_SUFFIX, ignore_errors=True)


def _kill_pid_file(pid_file):
    if not os.path.exists(pid_file):
        return
    try:
        with open(pid_file, 'r') as f:
            pid = int(f.read().strip())
        process = psutil.Process(pid)
        for proc in process.children(recursive=True) + [process]:
            PreviewService._stop_process(proc)
    except (OSError, ValueError, psutil.NoSuchProcess, psutil.AccessDenied):
        pass
    try:
        os.remove(pid_file)
    except OSError:
        pass
