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
Django worker can serve any request by opening a short-lived CDP connection —
nothing is held in worker memory.
"""

import base64
import glob
import hashlib
import json
import logging
import os
import shutil
import subprocess
import sys
import time

import psutil
import requests
from django.conf import settings
from websocket import create_connection, WebSocketException

from .preview_service import (
    BROWSER_PROFILE_SUFFIX,
    BROWSER_STATE_SUFFIX,
    PreviewService,
)

logger = logging.getLogger(__name__)

# Per-project files this service writes beside the dev-server PID files
# (cleanup-relevant suffixes live in preview_service so its sweeps cover them).
BROWSER_PID_SUFFIX = '_browser.pid'
BROWSER_LOG_SUFFIX = '_browser.log'

# Defaults until the client reports its pane size.
DEFAULT_VIEWPORT = (1280, 800)
MIN_VIEWPORT, MAX_VIEWPORT = 320, 3840
MAX_EVENTS_PER_REQUEST = 64

# How long to wait for the Vite dev server to answer HTTP before pointing
# Chromium at it. Vite itself is up in a couple of seconds; the generous
# ceiling covers first-run dependency optimization.
FRONTEND_READY_TIMEOUT = 90

# CDP modifier bitmask (Alt=1, Ctrl=2, Meta=4, Shift=8) — the client sends
# the mask directly; we only clamp it.
MODIFIER_MASK = 0xF

_MOUSE_EVENT_TYPES = {'mousePressed', 'mouseReleased', 'mouseMoved'}
_MOUSE_BUTTONS = {'none', 'left', 'middle', 'right', 'back', 'forward'}
_KEY_EVENT_TYPES = {'keyDown', 'keyUp'}


class BrowserPreviewError(Exception):
    """Raised for user-reportable browser preview failures."""


class BrowserNotRunning(BrowserPreviewError):
    """The browser session is not (or no longer) running."""


class CdpError(BrowserPreviewError):
    """A DevTools command failed."""


class CdpConnection:
    """Minimal synchronous Chrome DevTools Protocol client for one target.

    Chromium supports multiple simultaneous CDP clients, so short-lived
    per-request connections are safe even when several Django workers talk
    to the same page at once.
    """

    def __init__(self, ws_url, timeout=15):
        # suppress_origin: Chromium rejects DevTools websocket upgrades that
        # carry a non-localhost Origin header.
        self._ws = create_connection(ws_url, timeout=timeout, suppress_origin=True)
        self._next_id = 0

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

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


class BrowserPreviewService:
    """Drives a per-project headless Chromium for the workspace preview."""

    def __init__(self, project):
        self.project = project
        # Reuse the dev-server manager: it owns the project's Django + Vite
        # subprocesses and the pid-file conventions we extend here.
        self.servers = PreviewService(project)
        self.pid_dir = self.servers.pid_dir

        name = project.name
        self.pid_file = os.path.join(self.pid_dir, f"{name}{BROWSER_PID_SUFFIX}")
        self.log_file = os.path.join(self.pid_dir, f"{name}{BROWSER_LOG_SUFFIX}")
        self.state_file = os.path.join(self.pid_dir, f"{name}{BROWSER_STATE_SUFFIX}")
        self.profile_dir = os.path.join(self.pid_dir, f"{name}{BROWSER_PROFILE_SUFFIX}")

    # ------------------------------------------------------------------
    # Session lifecycle
    # ------------------------------------------------------------------

    def start(self, viewport=None, device_scale_factor=None):
        """Ensure dev servers + Chromium are running and showing the app.

        Idempotent: an already-healthy session is reused, so the workspace
        can call this on every mount without restarting anything.
        """
        reap_idle_sessions()

        server_state = self.servers.ensure_preview()
        # The dev servers report a localhost preview URL; dual-stack projects
        # point it at Vite, legacy single-Django projects at runserver.
        app_url = (server_state.get('preview_url') or '').replace('localhost', '127.0.0.1').rstrip('/')
        if not app_url:
            app_url = f"http://127.0.0.1:{self.servers.frontend_port}"
        self._wait_for_frontend(app_url)

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

        fresh = not (state and self._browser_alive(state))
        if fresh:
            # Opening the app URL directly keeps about:blank out of the
            # page's history, so "back" never leads outside the app.
            state = self._launch_chromium(width, height, dsf, app_url + '/')
        else:
            state['viewport'] = [width, height]

        state['app_url'] = app_url
        state['last_active'] = time.time()
        self._save_state(state)

        with self._page_connection(state) as (conn, target):
            self._apply_viewport(conn, state)
            current = target.get('url') or ''
            # A reused browser may sit on a network error page from before
            # the dev servers were (re)started; bring it back to the app.
            if not fresh and not current.startswith(app_url):
                conn.call('Page.navigate', {'url': app_url + '/'})
                time.sleep(0.3)  # let the first paint land in the frame below
            status = self._status_payload(conn, state)
            self._attach_frame(conn, status, None)

        status['servers'] = server_state.get('message', '')
        return status

    def stop(self):
        """Stop Chromium and the project's dev servers."""
        self._kill_browser()
        return self.servers.stop_preview()

    def is_running(self):
        state = self._load_state()
        return bool(state and self._browser_alive(state))

    # ------------------------------------------------------------------
    # Interaction (each call opens a short-lived CDP connection)
    # ------------------------------------------------------------------

    def frame(self, etag=None):
        """Return the current screenshot (unless it matches ``etag``) + nav state."""
        state = self._require_state(touch=True)
        with self._page_connection(state) as (conn, _target):
            self._apply_viewport(conn, state)
            payload = self._status_payload(conn, state)
            self._attach_frame(conn, payload, etag)
        return payload

    def dispatch_input(self, events, etag=None):
        """Forward a batch of mouse/keyboard/wheel events, then return a frame."""
        if not isinstance(events, list) or len(events) > MAX_EVENTS_PER_REQUEST:
            raise BrowserPreviewError('Invalid input event batch.')

        state = self._require_state(touch=True)
        width, height = state.get('viewport', DEFAULT_VIEWPORT)
        with self._page_connection(state) as (conn, _target):
            self._apply_viewport(conn, state)
            for event in events:
                method, params = self._translate_event(event, width, height)
                conn.call(method, params)
            payload = self._status_payload(conn, state)
            self._attach_frame(conn, payload, etag)
        return payload

    def navigate(self, action, path=None):
        """goto/back/forward/reload, then return a frame."""
        state = self._require_state(touch=True)
        app_url = state.get('app_url', '')
        with self._page_connection(state) as (conn, _target):
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

    def resize(self, width, height, device_scale_factor=None):
        """Adopt the client pane's size (CSS pixels)."""
        state = self._require_state(touch=True)
        state['viewport'] = list(self._clamp_viewport(width, height))
        if device_scale_factor:
            state['device_scale_factor'] = self._clamp_dsf(device_scale_factor)
        self._save_state(state)
        with self._page_connection(state) as (conn, _target):
            self._apply_viewport(conn, state)
        return {'viewport': state['viewport']}

    # ------------------------------------------------------------------
    # Chromium process management
    # ------------------------------------------------------------------

    def _launch_chromium(self, width, height, dsf, initial_url='about:blank'):
        executable = find_chromium()
        if not executable:
            raise BrowserPreviewError(
                'No Chromium/Chrome executable found. Install Chromium or set '
                'BROWSER_PREVIEW_EXECUTABLE to a browser binary.'
            )

        self._kill_browser(keep_profile=True)

        cdp_port = self.servers._find_available_port_excluding(9300, 9400)
        os.makedirs(self.profile_dir, exist_ok=True)

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

    def _kill_browser(self, keep_profile=False):
        self.servers._kill_from_pid_file(self.pid_file)
        state = self._load_state()
        if state and state.get('cdp_port'):
            self.servers._kill_by_port(state['cdp_port'])
        try:
            os.remove(self.state_file)
        except OSError:
            pass
        if not keep_profile:
            shutil.rmtree(self.profile_dir, ignore_errors=True)

    def _browser_alive(self, state):
        pid, port = state.get('pid'), state.get('cdp_port')
        if not pid or not port:
            return False
        try:
            proc = psutil.Process(pid)
            if not proc.is_running():
                return False
        except psutil.NoSuchProcess:
            return False
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

    def _page_connection(self, state):
        """Context manager yielding (CdpConnection, target-info) for the app page."""
        port = state['cdp_port']
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

        class _Ctx:
            def __enter__(ctx):
                try:
                    ctx.conn = CdpConnection(page['webSocketDebuggerUrl'])
                except (WebSocketException, OSError, KeyError) as e:
                    raise BrowserNotRunning(f'Could not attach to browser page: {e}')
                return ctx.conn, page

            def __exit__(ctx, *exc):
                ctx.conn.close()

        return _Ctx()

    def _apply_viewport(self, conn, state):
        # Emulation overrides can be tied to a DevTools session, and our
        # connections are per-request — re-applying is cheap and idempotent.
        width, height = state.get('viewport', DEFAULT_VIEWPORT)
        conn.call('Emulation.setDeviceMetricsOverride', {
            'width': int(width),
            'height': int(height),
            'deviceScaleFactor': float(state.get('device_scale_factor', 1)),
            'mobile': False,
        })

    def _attach_frame(self, conn, payload, etag):
        shot = conn.call('Page.captureScreenshot', {'format': 'jpeg', 'quality': 70})
        data = shot.get('data', '')
        digest = hashlib.sha1(base64.b64decode(data)).hexdigest() if data else ''
        payload['etag'] = digest
        if etag and etag == digest:
            payload['frame'] = None  # unchanged since the client's last frame
        else:
            payload['frame'] = data

    def _status_payload(self, conn, state):
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
        }

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
            # last_active drives idle reaping; throttle rewrites to one per 30s.
            now = time.time()
            if now - state.get('last_active', 0) > 30:
                state['last_active'] = now
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


def reap_idle_sessions():
    """Shut down preview sessions (browser + dev servers) idle past the limit.

    Runs opportunistically when any preview starts. Works purely from the
    per-project files on disk so it needs no database access and covers
    every user's projects.
    """
    timeout = getattr(settings, 'BROWSER_PREVIEW_IDLE_TIMEOUT', 1800)
    if not timeout:
        return

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
            if now - state.get('last_active', 0) < timeout:
                continue

            prefix = state_file[:-len(BROWSER_STATE_SUFFIX)]
            logger.info(f"Reaping idle preview session: {os.path.basename(prefix)}")
            # Browser first, then the dev servers recorded by PreviewService.
            _kill_pid_file(prefix + BROWSER_PID_SUFFIX)
            _kill_pid_file(prefix + '_frontend.pid')
            _kill_pid_file(prefix + '_backend.pid')
            for leftover in (state_file, prefix + '_preview_ports.json'):
                try:
                    os.remove(leftover)
                except OSError:
                    pass
            shutil.rmtree(prefix + BROWSER_PROFILE_SUFFIX, ignore_errors=True)
        except Exception as e:
            logger.warning(f"Could not reap preview session {state_file}: {e}")


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
