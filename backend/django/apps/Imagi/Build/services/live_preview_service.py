"""
Live preview (PREVIEW_V2): the user's own browser renders their app.

The screenshot preview (BrowserPreviewService) runs a headless Chromium next
to the project's dev servers and streams pictures of it. This one serves the
project's real Vite dev server, through the preview edge
(preview_runtime/edge.mjs), into a sandboxed iframe on a separate origin, so
scrolling, typing and animation are native and input has no extra hop.

A live session is the project's two dev servers plus a **token**: 32 random
bytes minted when the servers start and handed only to the project's owner.
The app is served under ``/s/<token>/`` on the preview origin (Vite's
``base``), and the edge finds the session's ports from a route file named
after the token. Stopping the servers deletes the file, which revokes the
URL. See docs/preview-browser/ for the design, the threat model and the
decisions behind both.

Lifecycle mirrors the screenshot preview's, keyed on its own state file
(``<id>_live.json``): a viewer heartbeat (the status poll) keeps a session
alive, sessions idle past PREVIEW_LIVE_IDLE_TIMEOUT stop, and starting one
when the host is over PREVIEW_MEMORY_BUDGET_MB stops the least recently used
first, never one somebody looked at in the last minute.
"""

import glob
import json
import logging
import os
import re
import secrets
import shutil
import subprocess
import threading
import time
from dataclasses import dataclass
from typing import Dict, List, Optional
from urllib.parse import urlsplit

import psutil
from django.conf import settings
from django.db import close_old_connections

from .preview_service import (
    PreviewService,
    port_accepting,
    preview_start_lock,
    sidecar_stem,
)

logger = logging.getLogger(__name__)
timing_logger = logging.getLogger('imagi.timing')

RUNTIME_DIR = os.path.join(os.path.dirname(__file__), 'preview_runtime')
EDGE_SCRIPT = os.path.join(RUNTIME_DIR, 'edge.mjs')
BRIDGE_SCRIPT = os.path.join(RUNTIME_DIR, 'bridge.js')

LIVE_STATE_SUFFIX = '_live.json'
CONSOLE_SUFFIX = '_console.json'
PROGRESS_SUFFIX = '_progress.json'

TOKEN_RE = re.compile(r'^[A-Za-z0-9_-]{32,64}$')
# A session someone viewed this recently is never evicted.
IN_USE_SECONDS = 60
# What a session is assumed to need before it has been measured.
DEFAULT_SESSION_MB = 400
MAX_CONSOLE_ENTRIES = 50
LOG_TAIL_BYTES = 64 * 1024
MAX_LOG_LINES = 400


def enabled() -> bool:
    return bool(getattr(settings, 'PREVIEW_V2', False))


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LiveConfig:
    """How one live session is reached from the outside."""
    token: str
    public_origin: str  # e.g. https://imagi-preview.up.railway.app

    @property
    def base(self) -> str:
        """Vite's base: the session's path prefix, with both slashes."""
        return f'/s/{self.token}/'

    @property
    def url(self) -> str:
        return f'{self.public_origin}{self.base}'

    @property
    def host(self) -> str:
        """The preview host as the dev servers see it (no port)."""
        return urlsplit(self.public_origin).hostname or ''

    @property
    def secure(self) -> bool:
        return urlsplit(self.public_origin).scheme == 'https'


def mint_token() -> str:
    return secrets.token_urlsafe(32)


def public_origin() -> str:
    origin = (getattr(settings, 'PREVIEW_PUBLIC_ORIGIN', '') or '').rstrip('/')
    if origin:
        return origin
    return f"http://127.0.0.1:{edge_port()}"


def edge_port() -> int:
    return int(getattr(settings, 'PREVIEW_EDGE_PORT', 8790))


def config_for(token: str) -> LiveConfig:
    return LiveConfig(token=token, public_origin=public_origin())


def parent_origin_pattern() -> str:
    """Regex for the Imagi origins allowed to frame and talk to a preview."""
    explicit = getattr(settings, 'PREVIEW_PARENT_ORIGIN_RE', '')
    if explicit:
        return explicit
    origins = parent_origins()
    return '^(' + '|'.join(re.escape(o) for o in origins) + ')$' if origins else '^$'


def parent_origins() -> List[str]:
    return [o.rstrip('/') for o in getattr(settings, 'PREVIEW_PARENT_ORIGINS', []) if o]


def frame_ancestors() -> str:
    """CSP frame-ancestors sources for the edge."""
    explicit = getattr(settings, 'PREVIEW_FRAME_ANCESTORS', '')
    if explicit:
        return explicit
    return ' '.join(parent_origins()) or "'none'"


def routes_dir() -> str:
    path = getattr(settings, 'PREVIEW_ROUTES_DIR', '') or os.path.join(
        settings.PROJECTS_ROOT, '.preview-routes'
    )
    os.makedirs(path, mode=0o700, exist_ok=True)
    return path


def write_route(token: str, frontend_port: int, backend_port: Optional[int]) -> None:
    """Point the edge at a session's servers (atomic: the edge never reads
    half a file)."""
    if not TOKEN_RE.match(token or ''):
        raise ValueError('bad preview token')
    path = os.path.join(routes_dir(), f'{token}.json')
    tmp = f'{path}.tmp'
    with open(tmp, 'w') as f:
        json.dump({'frontend_port': frontend_port, 'backend_port': backend_port}, f)
    os.replace(tmp, path)


def remove_route(token: Optional[str]) -> None:
    if not token or not TOKEN_RE.match(token):
        return
    try:
        os.remove(os.path.join(routes_dir(), f'{token}.json'))
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Generated runtime files: wrappers around the project's own configs
# ---------------------------------------------------------------------------
#
# The project's vite.config and settings.py belong to the user and the agent,
# who may rewrite them at any time. The preview's wiring therefore lives in
# two small wrapper files outside the project, regenerated on every start,
# that import the project's config and add to it. Nothing preview-specific is
# written into the project, and the app's own production build never sees
# any of it.

_HMR_MODULE = """
const post = (m) => window.__imagiBridge && window.__imagiBridge.post(m)
if (import.meta.hot) {
  import.meta.hot.on('vite:afterUpdate', (p) => post({ type: 'hmr', files: (p.updates || []).map((u) => u.path) }))
  import.meta.hot.on('vite:beforeFullReload', () => post({ type: 'full-reload' }))
  import.meta.hot.on('vite:error', (p) => post({ type: 'console', level: 'error', text: String((p && p.err && p.err.message) || 'Build error'), ts: Date.now() }))
}
"""


def bridge_source(config: LiveConfig) -> str:
    with open(BRIDGE_SCRIPT, 'r') as f:
        source = f.read()
    return (
        source
        .replace('__IMAGI_PARENT_RE__', json.dumps(parent_origin_pattern()))
        .replace('__IMAGI_BASE__', json.dumps(config.base.rstrip('/')))
    )


def vite_wrapper_source(user_config_path: str, config: LiveConfig) -> str:
    imagi = {
        'base': config.base,
        'host': config.host,
        'bridge': bridge_source(config),
        'hmrModule': _HMR_MODULE,
    }
    return f"""// Generated by Imagi for the live preview; rewritten on every start.
// Wraps the project's own vite.config without changing it.
import userConfig from {json.dumps(user_config_path)}

const IMAGI = {json.dumps(imagi)}
const HMR_ID = '\\0imagi-preview-hmr'

function imagiPreview() {{
  return {{
    name: 'imagi-preview',
    apply: 'serve',
    enforce: 'post',
    resolveId(id) {{
      if (id === '/__imagi_hmr.js') return HMR_ID
    }},
    load(id) {{
      if (id === HMR_ID) return IMAGI.hmrModule
    }},
    transformIndexHtml() {{
      return [
        {{ tag: 'script', children: IMAGI.bridge, injectTo: 'head-prepend' }},
        {{ tag: 'script', attrs: {{ type: 'module', src: IMAGI.base + '__imagi_hmr.js' }}, injectTo: 'head' }},
      ]
    }},
  }}
}}

export default async (env) => {{
  const loaded = typeof userConfig === 'function' ? await userConfig(env) : await userConfig
  const cfg = {{ ...(loaded || {{}}) }}
  const server = {{ ...(cfg.server || {{}}) }}
  const hmr = server.hmr && typeof server.hmr === 'object' ? {{ ...server.hmr }} : {{}}
  // The HMR socket follows the page: same host, port and scheme, under the
  // session's base path, so it works both through the edge and direct.
  delete hmr.host
  delete hmr.port
  delete hmr.clientPort
  delete hmr.protocol
  delete hmr.path
  server.hmr = hmr
  server.allowedHosts = [IMAGI.host]
  server.strictPort = true
  server.open = false
  cfg.server = server
  cfg.base = IMAGI.base
  cfg.plugins = [...(cfg.plugins || []), imagiPreview()]
  return cfg
}}
"""


def django_wrapper_source(settings_module: str, config: LiveConfig) -> str:
    origin = config.public_origin
    lines = [
        '# Generated by Imagi for the live preview; rewritten on every start.',
        "# Wraps the project's own settings without changing them.",
        f'from {settings_module} import *  # noqa: F401,F403',
        '',
        "_LOCAL = ['localhost', '127.0.0.1', '[::1]', '.localhost']",
        "ALLOWED_HOSTS = list(globals().get('ALLOWED_HOSTS') or _LOCAL)",
        f'ALLOWED_HOSTS += [h for h in {[config.host]!r} + _LOCAL if h not in ALLOWED_HOSTS]',
        f"CSRF_TRUSTED_ORIGINS = list(globals().get('CSRF_TRUSTED_ORIGINS') or []) + [{origin!r}]",
    ]
    if config.secure:
        lines += [
            '# The app is framed by Imagi, another site: its cookies must say so.',
            "SESSION_COOKIE_SAMESITE = 'None'",
            "CSRF_COOKIE_SAMESITE = 'None'",
            'SESSION_COOKIE_SECURE = True',
            'CSRF_COOKIE_SECURE = True',
            "SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')",
        ]
    return '\n'.join(lines) + '\n'


# ---------------------------------------------------------------------------
# The edge process
# ---------------------------------------------------------------------------

_edge_lock = threading.Lock()


def ensure_edge(wait: float = 5.0) -> bool:
    """Make sure the preview edge is listening; start it if not.

    One edge serves every session on the host. It is a plain Node process
    with no access to Imagi's secrets (its environment is built from
    scratch). Several workers may race to start it; the losers exit on
    EADDRINUSE and the winner serves.
    """
    port = edge_port()
    if port_accepting(port):
        return True
    node = shutil.which('node')
    if not node:
        logger.error('Cannot start the preview edge: node is not installed')
        return False
    with _edge_lock:
        if port_accepting(port):
            return True
        env = {
            'PATH': os.environ.get('PATH', os.defpath),
            'PREVIEW_EDGE_PORT': str(port),
            'PREVIEW_EDGE_BIND': getattr(settings, 'PREVIEW_EDGE_BIND', '::'),
            'PREVIEW_ROUTES_DIR': routes_dir(),
            'PREVIEW_FRAME_ANCESTORS': frame_ancestors(),
            'PREVIEW_PUBLIC_SCHEME': urlsplit(public_origin()).scheme,
        }
        log_path = os.path.join(settings.PROJECTS_ROOT, '.preview-edge.log')
        with open(log_path, 'a') as log:
            subprocess.Popen(
                [node, EDGE_SCRIPT], env=env, stdout=log, stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL, start_new_session=True,
            )
        deadline = time.monotonic() + wait
        while time.monotonic() < deadline:
            if port_accepting(port):
                logger.info('Preview edge listening on %s', port)
                return True
            time.sleep(0.05)
    logger.error('The preview edge did not start; see %s', log_path)
    return False


# ---------------------------------------------------------------------------
# Start progress
# ---------------------------------------------------------------------------

STAGES = [
    ('files', 'Preparing your project'),
    ('migrate', 'Updating the database'),
    ('django', 'Starting the backend'),
    ('vite', 'Starting the frontend'),
    ('app', 'Loading your app'),
]


class Progress:
    """Start stages with timings, written where the status poll reads them."""

    def __init__(self, path: str):
        self.path = path
        self.started = time.time()
        self.lock = threading.Lock()
        self.stages = {key: {'key': key, 'label': label, 'state': 'pending'} for key, label in STAGES}
        self._begun = {}
        self._write()

    def __call__(self, key: str, state: str, detail: str = '') -> None:
        with self.lock:
            stage = self.stages.get(key)
            if not stage:
                return
            now = time.time()
            if state == 'running':
                self._begun[key] = now
            elif key in self._begun:
                stage['ms'] = int((now - self._begun[key]) * 1000)
            stage['state'] = state
            if detail:
                stage['detail'] = detail[-2000:]
            self._write()

    def _write(self):
        payload = {
            'started_at': self.started,
            'stages': [self.stages[key] for key, _ in STAGES],
        }
        try:
            tmp = f'{self.path}.tmp'
            with open(tmp, 'w') as f:
                json.dump(payload, f)
            os.replace(tmp, self.path)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# The service
# ---------------------------------------------------------------------------

class LivePreviewService:
    """One project's live preview session."""

    def __init__(self, project):
        self.project = project
        self.servers = PreviewService(project)
        self.pid_dir = self.servers.pid_dir
        stem = sidecar_stem(project)
        self.state_file = os.path.join(self.pid_dir, f'{stem}{LIVE_STATE_SUFFIX}')
        self.console_file = os.path.join(self.pid_dir, f'{stem}{CONSOLE_SUFFIX}')
        self.progress_file = os.path.join(self.pid_dir, f'{stem}{PROGRESS_SUFFIX}')

    # -- lifecycle -----------------------------------------------------------

    def start(self, prewarm: bool = False) -> Dict:
        """Ensure the servers run in live mode and return how to reach them.

        Idempotent and cheap when the session is already up: the workspace
        calls it on every open.
        """
        from .browser_preview_service import ensure_idle_reaper

        ensure_idle_reaper()
        started = time.monotonic()
        if not ensure_edge():
            raise RuntimeError('The preview server could not start. Try again in a moment.')
        with preview_start_lock(self.pid_dir, sidecar_stem(self.project)):
            reap_idle_live_sessions()
            ports = self.servers._load_port_state() or {}
            token = ports.get('live_token')
            if not (token and TOKEN_RE.match(token)):
                token = mint_token()
            config = config_for(token)
            cold = not self._servers_healthy(ports, token)
            if cold and not prewarm:
                make_room(exclude=self.project.pk)
            progress = Progress(self.progress_file) if cold else None
            result = self.servers.ensure_preview(live=config, progress=progress)
            # ensure_preview restarts servers that weren't in live mode,
            # minting nothing itself: the token it used is ours.
            write_route(token, self.servers.frontend_port, self.servers.backend_port)
            if progress:
                progress('app', 'running')
            state = self._load_state() or {}
            now = time.time()
            if state.get('token') != token:
                state = {'token': token, 'started_at': now}
            state['last_active'] = now
            if not prewarm:
                state['last_used'] = now
            state['prewarmed'] = bool(prewarm and (cold or state.get('prewarmed')))
            self._save_state(state)
        elapsed = time.monotonic() - started
        timing_logger.info(
            'live preview start project=%s cold=%s total=%.2fs', self.project.pk, cold, elapsed,
        )
        return {
            'running': True,
            'mode': 'live',
            'url': config.url,
            'origin': config.public_origin,
            'base': config.base,
            'cold': cold,
            'servers': result.get('message', ''),
            'timings': {'total': round(elapsed, 2)},
        }

    def stop(self) -> Dict:
        state = self._load_state() or {}
        ports = self.servers._load_port_state() or {}
        remove_route(state.get('token'))
        remove_route(ports.get('live_token'))
        result = self.servers.stop_preview()
        for path in (self.state_file, self.progress_file):
            try:
                os.remove(path)
            except OSError:
                pass
        return result

    def is_running(self) -> bool:
        state = self._load_state()
        ports = self.servers._load_port_state() or {}
        return bool(state and self._servers_healthy(ports, state.get('token')))

    def _servers_healthy(self, ports: Dict, token: Optional[str]) -> bool:
        if not ports or not token or ports.get('live_token') != token:
            return False
        frontend = ports.get('frontend_port')
        backend = ports.get('backend_port')
        return bool(frontend and backend and port_accepting(frontend) and port_accepting(backend))

    # -- status, logs, console -------------------------------------------------

    def status(self, touch: bool = True) -> Dict:
        """Server health for the status pill, plus start progress."""
        state = self._load_state()
        ports = self.servers._load_port_state() or {}
        progress = self._read_json(self.progress_file)
        if not state:
            return {'running': False, 'progress': progress}
        if touch:
            now = time.time()
            if now - min(state.get('last_active', 0), state.get('last_used', 0)) > 30:
                state['last_active'] = state['last_used'] = now
                state['prewarmed'] = False
                self._save_state(state)
        token = state.get('token')
        if ports.get('live_token') != token:
            return {'running': False, 'progress': progress}
        backend = self._server_state(
            ports.get('backend_port'), self.servers.backend_pid_file, self.servers.backend_log_file,
            reload_marker=re.compile(r'changed, reloading|Performing system checks'),
            ready_marker=re.compile(r'Starting development server|Quit the server'),
        )
        frontend = self._server_state(
            ports.get('frontend_port'), self.servers.frontend_pid_file, self.servers.frontend_log_file,
            reload_marker=re.compile(r'server restarted|restarting server', re.I),
            ready_marker=re.compile(r'ready in|Local:', re.I),
        )
        return {
            'running': backend['state'] != 'stopped' or frontend['state'] != 'stopped',
            'backend': backend,
            'frontend': frontend,
            'progress': progress,
            'started_at': state.get('started_at'),
        }

    def _server_state(self, port, pid_file, log_file, reload_marker, ready_marker) -> Dict:
        alive = self._pid_alive(pid_file)
        listening = bool(port) and port_accepting(port)
        try:
            changed = os.path.getmtime(log_file)
        except OSError:
            changed = None
        if listening:
            state = 'ready'
        elif not alive:
            state = 'stopped'
        else:
            # Running but not answering: reloading, unless the log's last
            # word since the reload is an error (a crash runserver waits out
            # until the next edit).
            tail = self._tail(log_file, 4096)
            last_reload = max((m.end() for m in reload_marker.finditer(tail)), default=0)
            after = tail[last_reload:]
            state = 'crashed' if re.search(r'Error|Traceback|Exception', after) else 'reloading'
        return {'state': state, 'port': port, 'log_changed_at': changed}

    @staticmethod
    def _pid_alive(pid_file) -> bool:
        try:
            with open(pid_file) as f:
                pid = int(f.read().strip())
            proc = psutil.Process(pid)
            return proc.status() != psutil.STATUS_ZOMBIE
        except (OSError, ValueError, psutil.Error):
            return False

    @staticmethod
    def _tail(path, size) -> str:
        try:
            with open(path, 'rb') as f:
                f.seek(0, os.SEEK_END)
                end = f.tell()
                f.seek(max(0, end - size))
                return f.read().decode('utf-8', errors='replace')
        except OSError:
            return ''

    def logs(self, offsets: Optional[Dict[str, int]] = None) -> Dict:
        """New dev-server log lines since the given byte offsets.

        Without an offset, the last LOG_TAIL_BYTES of each log. A log that
        shrank (the server restarted and truncated it) starts over.
        """
        offsets = offsets or {}
        out = {}
        for name, path in (
            ('backend', self.servers.backend_log_file),
            ('frontend', self.servers.frontend_log_file),
        ):
            try:
                size = os.path.getsize(path)
            except OSError:
                out[name] = {'offset': 0, 'lines': [], 'reset': True}
                continue
            offset = offsets.get(name)
            reset = offset is None or offset > size
            start = max(0, size - LOG_TAIL_BYTES) if reset else offset
            try:
                with open(path, 'rb') as f:
                    f.seek(start)
                    chunk = f.read(size - start)
            except OSError:
                chunk = b''
            text = chunk.decode('utf-8', errors='replace')
            # Only whole lines; a partial last line waits for the next poll.
            if text and not text.endswith('\n'):
                cut = text.rfind('\n') + 1
                consumed = len(text[:cut].encode('utf-8'))
                text = text[:cut]
            else:
                consumed = len(chunk)
            lines = [_strip_ansi(line) for line in text.splitlines()]
            if reset and start > 0 and lines:
                lines = lines[1:]  # the first is probably cut in half
            out[name] = {
                'offset': start + consumed,
                'lines': lines[-MAX_LOG_LINES:],
                'reset': reset,
            }
        return out

    def record_console(self, entries: List[Dict]) -> List[Dict]:
        """Keep the latest console errors the page reported, so an agent's
        live edit can read back what broke (live_apply), as it does from
        the screenshot preview's browser."""
        clean = []
        for entry in entries or []:
            if not isinstance(entry, dict) or entry.get('level') != 'error':
                continue
            text = str(entry.get('text') or '').strip()[:500]
            try:
                ts = int(entry.get('ts') or 0)
            except (TypeError, ValueError):
                ts = 0
            if text:
                clean.append({'level': 'error', 'text': text, 'ts': ts or int(time.time() * 1000)})
        if not clean:
            return []
        current = self._read_json(self.console_file) or []
        if not isinstance(current, list):
            current = []
        merged = (current + clean)[-MAX_CONSOLE_ENTRIES:]
        try:
            with open(self.console_file, 'w') as f:
                json.dump(merged, f)
        except OSError:
            pass
        return clean

    def console_errors_since(self, since_ms: int) -> List[str]:
        entries = self._read_json(self.console_file) or []
        return [e['text'] for e in entries if isinstance(e, dict) and int(e.get('ts') or 0) >= since_ms]

    # -- server actions --------------------------------------------------------

    ACTIONS = ('restart_backend', 'restart_frontend', 'restart', 'migrate', 'reset_database')

    def action(self, name: str) -> Dict:
        if name not in self.ACTIONS:
            raise ValueError('Unknown action')
        ports = self.servers._load_port_state() or {}
        token = ports.get('live_token')
        if name == 'restart' or not token:
            self.stop()
            return self.start()
        config = config_for(token)
        backend_path, frontend_path = self.servers.stack_paths()
        if name == 'migrate':
            output = self.servers.run_migrations(backend_path, force=True)
            return {'ok': output is None, 'error': output}
        if name == 'reset_database':
            with preview_start_lock(self.pid_dir, sidecar_stem(self.project)):
                self.servers._stop_django_backend(port=ports.get('backend_port'))
                for db in glob.glob(os.path.join(backend_path, '*.sqlite3')):
                    os.remove(db)
                error = self.servers.start_backend(backend_path, config, port=ports.get('backend_port'))
            return {'ok': error is None, 'error': error}
        with preview_start_lock(self.pid_dir, sidecar_stem(self.project)):
            if name == 'restart_backend':
                self.servers._stop_django_backend(port=ports.get('backend_port'))
                error = self.servers.start_backend(backend_path, config, port=ports.get('backend_port'))
            else:
                self.servers._stop_vuejs_frontend(port=ports.get('frontend_port'))
                error = self.servers.start_frontend(frontend_path, config)
                write_route(token, self.servers.frontend_port, self.servers.backend_port)
            self.servers._save_port_state()
        return {'ok': error is None, 'error': error}

    # -- files -----------------------------------------------------------------

    def _load_state(self) -> Optional[Dict]:
        data = self._read_json(self.state_file)
        return data if isinstance(data, dict) else None

    def _save_state(self, state: Dict) -> None:
        try:
            with open(self.state_file, 'w') as f:
                json.dump(state, f)
        except OSError as e:
            logger.warning('Could not save live preview state: %s', e)

    @staticmethod
    def _read_json(path):
        try:
            with open(path) as f:
                return json.load(f)
        except (OSError, ValueError):
            return None


_ANSI_RE = re.compile(r'\x1b\[[0-9;?]*[A-Za-z]')


def _strip_ansi(text: str) -> str:
    return _ANSI_RE.sub('', text)


# ---------------------------------------------------------------------------
# Host-wide policy: idle shutdown, memory budget, prewarm
# ---------------------------------------------------------------------------

def _live_states():
    """(prefix, state) for every live session state file on this host."""
    root = getattr(settings, 'PROJECTS_ROOT', None)
    if not root or not os.path.isdir(root):
        return []
    out = []
    for path in glob.glob(os.path.join(root, '*', f'*{LIVE_STATE_SUFFIX}')):
        try:
            with open(path) as f:
                state = json.load(f)
        except (OSError, ValueError):
            continue
        if isinstance(state, dict):
            out.append((path[:-len(LIVE_STATE_SUFFIX)], state))
    return out


def _tree_rss_mb(pid_file: str) -> float:
    try:
        with open(pid_file) as f:
            pid = int(f.read().strip())
        proc = psutil.Process(pid)
        procs = [proc] + proc.children(recursive=True)
        return sum(p.memory_info().rss for p in procs if p.is_running()) / (1024 * 1024)
    except (OSError, ValueError, psutil.Error):
        return 0.0


def session_rss_mb(prefix: str) -> float:
    """Measured memory of one session's Django + Vite process trees."""
    return _tree_rss_mb(prefix + '_backend.pid') + _tree_rss_mb(prefix + '_frontend.pid')


def shut_down_live(prefix: str) -> None:
    """Stop a live session from its files alone (no DB access)."""
    from .browser_preview_service import BROWSER_PID_SUFFIX, _kill_pid_file

    state_file = prefix + LIVE_STATE_SUFFIX
    try:
        with open(prefix + '_preview_ports.json') as f:
            remove_route((json.load(f) or {}).get('live_token'))
    except (OSError, ValueError, AttributeError):
        pass
    try:
        with open(state_file) as f:
            remove_route((json.load(f) or {}).get('token'))
    except (OSError, ValueError, AttributeError):
        pass
    _kill_pid_file(prefix + BROWSER_PID_SUFFIX)
    _kill_pid_file(prefix + '_frontend.pid')
    _kill_pid_file(prefix + '_backend.pid')
    for leftover in (state_file, prefix + '_preview_ports.json', prefix + PROGRESS_SUFFIX):
        try:
            os.remove(leftover)
        except OSError:
            pass


def live_session_active(prefix: str, within: Optional[float] = None) -> bool:
    """Whether a live session at this prefix was viewed recently. The
    screenshot preview's reaper asks before taking dev servers down with an
    agent's idle browser."""
    try:
        with open(prefix + LIVE_STATE_SUFFIX) as f:
            state = json.load(f)
    except (OSError, ValueError):
        return False
    limit = within if within is not None else getattr(settings, 'PREVIEW_LIVE_IDLE_TIMEOUT', 600)
    return time.time() - (state.get('last_active') or 0) < limit


def reap_idle_live_sessions() -> None:
    timeout = getattr(settings, 'PREVIEW_LIVE_IDLE_TIMEOUT', 600)
    if not timeout:
        return
    prewarm_timeout = min(getattr(settings, 'PREVIEW_LIVE_PREWARM_IDLE_TIMEOUT', 600) or timeout, timeout)
    now = time.time()
    for prefix, state in _live_states():
        limit = prewarm_timeout if state.get('prewarmed') else timeout
        if now - (state.get('last_active') or 0) >= limit:
            logger.info('Stopping idle live preview %s', os.path.basename(prefix))
            shut_down_live(prefix)


def make_room(exclude=None) -> None:
    """Keep live sessions within PREVIEW_MEMORY_BUDGET_MB.

    Measures what the running sessions actually use, adds what a new one
    needs, and stops the least recently used sessions until that fits. One
    used in the last IN_USE_SECONDS is never stopped: going over the budget
    beats closing a preview someone is looking at.
    """
    budget = getattr(settings, 'PREVIEW_MEMORY_BUDGET_MB', 2048)
    if not budget:
        return
    sessions = [
        (prefix, state, session_rss_mb(prefix))
        for prefix, state in _live_states()
        if not (exclude is not None and os.path.basename(prefix) == str(exclude))
    ]
    measured = [mb for _, _, mb in sessions if mb]
    need = max(measured) if measured else DEFAULT_SESSION_MB
    total = sum(mb for _, _, mb in sessions)
    if total + need <= budget:
        return
    now = time.time()
    candidates = sorted(
        (s for s in sessions if now - (s[1].get('last_used') or 0) >= IN_USE_SECONDS),
        key=lambda s: (not s[1].get('prewarmed'), s[1].get('last_used') or 0),
    )
    for prefix, _, mb in candidates:
        if total + need <= budget:
            break
        logger.info('Stopping live preview %s to stay within the memory budget', os.path.basename(prefix))
        shut_down_live(prefix)
        total -= mb


_prewarm_threads: Dict[int, threading.Thread] = {}
_prewarm_lock = threading.Lock()


def prewarm_recent(user) -> Optional[threading.Thread]:
    """Keep the owner's most recently opened projects running while an Imagi
    tab is open (the client's heartbeat): start the ones that are down, and
    mark the running ones active so the idle reaper leaves them alone."""
    from apps.Imagi.ProjectManager.models import Project

    limit = getattr(settings, 'PREVIEW_LIVE_PREWARM_RECENT', 3)
    if not limit or not getattr(user, 'pk', None):
        return None
    projects = list(
        Project.objects.filter(user=user, is_active=True, last_opened_at__isnull=False)
        .exclude(project_dir='')
        .select_related('user')
        .order_by('-last_opened_at')[:limit]
    )
    if not projects:
        return None
    with _prewarm_lock:
        running = _prewarm_threads.get(user.pk)
        if running is not None and running.is_alive():
            return None

    def run():
        close_old_connections()
        try:
            from .project_files_service import ensure_working_copy
            for project in projects:
                try:
                    service = LivePreviewService(project)
                    if service.is_running():
                        state = service._load_state() or {}
                        state['last_active'] = time.time()
                        service._save_state(state)
                        continue
                    ensure_working_copy(project)
                    service.start(prewarm=True)
                except Exception:
                    logger.warning('Live preview prewarm failed for project %s', project.pk, exc_info=True)
        finally:
            close_old_connections()

    thread = threading.Thread(target=run, name=f'live-prewarm-{user.pk}', daemon=True)
    with _prewarm_lock:
        _prewarm_threads[user.pk] = thread
    thread.start()
    return thread


def warm_up_new_project(project) -> Optional[threading.Thread]:
    """Live-mode counterpart of start_preview_warmup (project creation)."""
    def run():
        close_old_connections()
        try:
            LivePreviewService(project).start(prewarm=True)
        except Exception:
            logger.warning('Live preview warm-up failed for project %s', project.pk, exc_info=True)
        finally:
            close_old_connections()

    thread = threading.Thread(target=run, name=f'live-warmup-{project.pk}', daemon=True)
    thread.start()
    return thread


# ---------------------------------------------------------------------------
# Migrations written by an agent
# ---------------------------------------------------------------------------

_MIGRATION_RE = re.compile(r'(^|/)migrations/\d{4}_[^/]+\.py$')
_migrate_timers: Dict[int, threading.Timer] = {}
_migrate_lock = threading.Lock()


def is_migration_file(path: str) -> bool:
    return bool(_MIGRATION_RE.search((path or '').replace('\\', '/')))


def schedule_migrate(project_id, delay: float = 1.5) -> None:
    """Apply migrations shortly after an agent writes one, if the project's
    servers are running. Debounced: a burst of migration files runs once."""
    if not project_id:
        return

    def run():
        close_old_connections()
        try:
            from apps.Imagi.ProjectManager.models import Project
            project = Project.objects.select_related('user').get(pk=project_id)
            servers = PreviewService(project)
            ports = servers._load_port_state()
            if not ports or not port_accepting(ports.get('backend_port') or 0):
                return
            backend_path, _ = servers.stack_paths()
            servers.run_migrations(backend_path, force=True)
        except Exception:
            logger.warning('Migrating project %s after an edit failed', project_id, exc_info=True)
        finally:
            close_old_connections()
            with _migrate_lock:
                _migrate_timers.pop(project_id, None)

    with _migrate_lock:
        existing = _migrate_timers.get(project_id)
        if existing is not None:
            existing.cancel()
        timer = threading.Timer(delay, run)
        timer.daemon = True
        _migrate_timers[project_id] = timer
        timer.start()
