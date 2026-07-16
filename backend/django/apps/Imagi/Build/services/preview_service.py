"""
Service for project preview operations in the Builder app.
"""

import contextlib
import subprocess
import os
import sys
import shutil
import psutil
import time
import logging
import json
from django.conf import settings

logger = logging.getLogger(__name__)

# npm install for a freshly scaffolded frontend can legitimately take minutes
NPM_INSTALL_TIMEOUT = 600

# Lock directory created inside a generated frontend while npm install runs
# there, so concurrent installers (the background install kicked off at
# project creation and a preview start that finds node_modules missing)
# serialize instead of corrupting node_modules under each other.
NPM_INSTALL_LOCK_DIRNAME = '.imagi_npm_install.lock'


@contextlib.contextmanager
def npm_install_lock(frontend_path, timeout=NPM_INSTALL_TIMEOUT):
    """Serialize npm installs for one frontend across processes and threads.

    Uses an atomic mkdir as the lock. Locks whose directory looks older than
    a full install could take are treated as leftovers from a crashed
    installer and stolen. If the lock cannot be acquired within ``timeout``,
    we proceed anyway — attempting the install beats failing outright.
    """
    lock_dir = os.path.join(frontend_path, NPM_INSTALL_LOCK_DIRNAME)
    deadline = time.time() + timeout
    acquired = False
    while time.time() < deadline:
        try:
            os.mkdir(lock_dir)
            acquired = True
            break
        except FileExistsError:
            try:
                if time.time() - os.path.getmtime(lock_dir) > timeout + 300:
                    os.rmdir(lock_dir)
                    continue
            except OSError:
                pass
            time.sleep(1)
        except OSError:
            break
    if not acquired:
        logger.warning(f"Proceeding without npm install lock for {frontend_path}")
    try:
        yield
    finally:
        if acquired:
            try:
                os.rmdir(lock_dir)
            except OSError:
                pass

# The per-project files this service keeps beside the project directory, by
# filename suffix. They are named after project.name, not the timestamped
# directory, so deleting the directory does not remove them. The _browser.*
# files belong to BrowserPreviewService (which imports these constants);
# they are listed here so cleanup sweeps the whole preview session.
PID_SUFFIXES = ('_frontend.pid', '_backend.pid', '_server.pid', '_browser.pid')  # _server.pid predates dual-stack
LOG_SUFFIXES = ('_frontend.log', '_backend.log', '_browser.log')
PORTS_SUFFIX = '_preview_ports.json'
BROWSER_STATE_SUFFIX = '_browser.json'
BROWSER_PROFILE_SUFFIX = '_browser_profile'


class PreviewService:
    """Service for project preview operations with dual-stack support."""

    def __init__(self, project):
        self.project = project
        self.frontend_port = 5174  # Vite dev server - use 5174 to avoid conflict with Imagi itself on 5173
        self.backend_port = 8080   # Django dev server - use 8080 to avoid conflict with main project on 8000

        # Ensure the PID file directory exists
        self.pid_dir = os.path.join(settings.PROJECTS_ROOT, str(project.user.id))
        os.makedirs(self.pid_dir, exist_ok=True)

        self.frontend_pid_file = os.path.join(self.pid_dir, f"{project.name}_frontend.pid")
        self.backend_pid_file = os.path.join(self.pid_dir, f"{project.name}_backend.pid")
        # Records the ports the servers were actually started on, so stopping
        # only ever touches those ports (never someone else's dev server).
        self.ports_file = os.path.join(self.pid_dir, f"{project.name}{PORTS_SUFFIX}")
        # Dev server output goes to log files: piping to subprocess.PIPE without
        # draining would freeze the servers once the pipe buffer fills.
        self.frontend_log_file = os.path.join(self.pid_dir, f"{project.name}_frontend.log")
        self.backend_log_file = os.path.join(self.pid_dir, f"{project.name}_backend.log")

    def ensure_preview(self):
        """Start the dev servers only if a healthy preview is not already up.

        start_preview() always tears down and relaunches; this variant lets
        callers (the browser preview, a workspace re-mount) reattach to a
        running session instead of paying the restart cost.
        """
        state = self._load_port_state()
        if state:
            backend_port = state.get('backend_port')
            frontend_port = state.get('frontend_port')
            backend_ok = bool(backend_port) and self._port_in_use(backend_port)
            # Legacy single-Django projects have no frontend server.
            frontend_ok = not frontend_port or self._port_in_use(frontend_port)
            if backend_ok and frontend_ok:
                self.backend_port = backend_port
                if frontend_port:
                    self.frontend_port = frontend_port
                port = frontend_port or backend_port
                return {
                    'success': True,
                    'preview_url': f"http://localhost:{port}",
                    'message': 'Development servers already running',
                }
        return self.start_preview()

    def start_preview(self):
        """Start both frontend and backend development servers."""
        try:
            logger.info(f"Starting preview for project: {self.project.name} (ID: {self.project.id})")
            logger.info(f"Project path: {self.project.project_path}")

            # Validate project path
            if not self.project.project_path:
                raise ValueError("Project path is not set")

            if not os.path.exists(self.project.project_path):
                raise FileNotFoundError(f"Project path does not exist: {self.project.project_path}")

            # Repair the project skeleton if it went missing (generated projects
            # aren't tracked by Imagi's git repo, so a clean checkout can lose
            # everything but the DB record and the per-app files).
            self._ensure_scaffold()

            # Stop any existing servers for this project
            self.stop_preview()

            # Check if project has the new dual-stack structure
            frontend_path = os.path.join(self.project.project_path, 'frontend', 'vuejs')
            backend_path = os.path.join(self.project.project_path, 'backend', 'django')

            logger.info(f"Frontend path: {frontend_path} (exists: {os.path.exists(frontend_path)})")
            logger.info(f"Backend path: {backend_path} (exists: {os.path.exists(backend_path)})")

            if os.path.exists(frontend_path) and os.path.exists(backend_path):
                # New dual-stack structure
                logger.info("Detected dual-stack project structure")
                return self._start_dual_stack_preview(frontend_path, backend_path)
            else:
                # Legacy single Django project
                logger.info("Detected legacy Django project structure")
                return self._start_legacy_preview()

        except Exception as e:
            logger.error(f"Error starting preview server: {str(e)}")
            import traceback
            logger.error(f"Stack trace: {traceback.format_exc()}")
            raise

    def _ensure_scaffold(self):
        """Recreate any missing scaffold files before trying to boot servers."""
        from apps.Imagi.ProjectManager.services.project_creation_service import ProjectCreationService

        try:
            creation_service = ProjectCreationService(self.project.user)
            repaired = creation_service.ensure_scaffold(self.project)
            if repaired:
                logger.info(
                    f"Repaired missing scaffold for project {self.project.name}: {', '.join(repaired)}"
                )
        except Exception as e:
            raise Exception(f"Project scaffold repair failed: {e}")

    def _start_dual_stack_preview(self, frontend_path, backend_path):
        """Start both VueJS frontend and Django backend servers."""
        logger.info("Starting dual-stack preview (VueJS + Django)")

        # Start Django backend first
        backend_error = self._start_django_backend(backend_path)
        if backend_error:
            raise Exception(f"Django backend failed to start: {backend_error}")

        # Wait a moment for backend to start
        time.sleep(3)

        # Start VueJS frontend
        frontend_error = self._start_vuejs_frontend(frontend_path)
        if frontend_error:
            # If frontend fails, stop the backend
            self._stop_django_backend(port=self.backend_port)
            raise Exception(f"VueJS frontend failed to start: {frontend_error}")

        # Wait for frontend to start
        time.sleep(5)

        self._save_port_state()

        frontend_url = f"http://localhost:{self.frontend_port}"

        # Note: Browser opening is handled by the frontend client via window.open()
        # Do not use webbrowser.open() here to avoid opening duplicate tabs

        return {
            'success': True,
            'preview_url': frontend_url,
            'frontend_url': frontend_url,
            'backend_url': f"http://localhost:{self.backend_port}",
            'message': 'Full-stack development servers started successfully'
        }

    def _start_django_backend(self, backend_path):
        """Start Django backend server. Returns None on success, error text on failure."""
        try:
            logger.info(f"Attempting to start Django backend in: {backend_path}")

            # Find manage.py
            manage_py = os.path.join(backend_path, 'manage.py')
            if not os.path.exists(manage_py):
                logger.error(f"manage.py not found in {backend_path}")
                return f"manage.py not found in {backend_path}"

            logger.info(f"Found manage.py at: {manage_py}")

            # Get project name for Django settings
            project_dirs = [d for d in os.listdir(backend_path)
                          if os.path.isdir(os.path.join(backend_path, d))
                          and os.path.exists(os.path.join(backend_path, d, 'settings.py'))]

            logger.info(f"Found project directories with settings.py: {project_dirs}")

            if not project_dirs:
                logger.error("No Django project directory found")
                return f"no Django settings module found under {backend_path}"

            project_name = project_dirs[0]
            logger.info(f"Using Django project: {project_name}")

            # Set up environment
            env = os.environ.copy()
            env['DJANGO_SETTINGS_MODULE'] = f"{project_name}.settings"

            # Find available port for backend (avoiding conflict with main project on 8000)
            self.backend_port = self._find_available_port_excluding(8080, 8100, exclude_ports=[8000])
            logger.info(f"Starting Django backend on port {self.backend_port}")

            # Ensure PID file directory exists
            os.makedirs(os.path.dirname(self.backend_pid_file), exist_ok=True)

            # Start Django development server. sys.executable is the
            # interpreter running Imagi itself, which is guaranteed to exist
            # and to have Django/DRF installed (a bare 'python' may be neither).
            with open(self.backend_log_file, 'w') as log_fh:
                process = subprocess.Popen(
                    [sys.executable, 'manage.py', 'runserver', f'127.0.0.1:{self.backend_port}'],
                    cwd=backend_path,
                    stdout=log_fh,
                    stderr=subprocess.STDOUT,
                    env=env
                )

            # Save the PID
            with open(self.backend_pid_file, 'w') as f:
                f.write(str(process.pid))

            logger.info(f"Django backend started with PID {process.pid}")

            # Wait a moment and check if process is still running
            time.sleep(1)
            if process.poll() is not None:
                output = self._read_log_tail(self.backend_log_file)
                logger.error(f"Django backend process terminated unexpectedly")
                logger.error(f"Return code: {process.returncode}")
                logger.error(f"Output: {output}")
                return f"process exited with code {process.returncode}: {output}"

            return None

        except Exception as e:
            logger.error(f"Error starting Django backend: {e}")
            import traceback
            logger.error(f"Stack trace: {traceback.format_exc()}")
            return str(e)

    def _start_vuejs_frontend(self, frontend_path):
        """Start VueJS frontend server. Returns None on success, error text on failure."""
        try:
            logger.info(f"Attempting to start VueJS frontend in: {frontend_path}")

            # Check if package.json exists
            package_json = os.path.join(frontend_path, 'package.json')
            if not os.path.exists(package_json):
                logger.error(f"package.json not found in {frontend_path}")
                return f"package.json not found in {frontend_path}"

            logger.info(f"Found package.json at: {package_json}")

            npm = shutil.which('npm')
            if not npm:
                logger.error("npm command not found on PATH")
                return "npm is not installed or not on PATH"

            # Install dependencies if they are missing (e.g. after a scaffold
            # repair, or when the original background install never finished).
            deps_error = self._ensure_frontend_dependencies(frontend_path, npm)
            if deps_error:
                return deps_error

            # Find available port for frontend (avoiding conflict with Imagi itself on 5173)
            self.frontend_port = self._find_available_port_excluding(5174, 5200, exclude_ports=[5173])
            logger.info(f"Starting VueJS frontend on port {self.frontend_port}")

            # Set up environment for Vite. VITE_BACKEND_URL points the generated
            # app's /api proxy at its own Django backend rather than the default.
            env = os.environ.copy()
            env['PORT'] = str(self.frontend_port)
            env['VITE_BACKEND_URL'] = f"http://localhost:{self.backend_port}"

            # Ensure PID file directory exists
            os.makedirs(os.path.dirname(self.frontend_pid_file), exist_ok=True)

            # Start Vite development server
            with open(self.frontend_log_file, 'w') as log_fh:
                process = subprocess.Popen(
                    # Bind to loopback only: the preview is consumed by the
                    # headless browser running on this same host, never
                    # directly by the user's machine.
                    [npm, 'run', 'dev', '--', '--port', str(self.frontend_port), '--host', '127.0.0.1'],
                    cwd=frontend_path,
                    stdout=log_fh,
                    stderr=subprocess.STDOUT,
                    env=env
                )

            # Save the PID
            with open(self.frontend_pid_file, 'w') as f:
                f.write(str(process.pid))

            logger.info(f"VueJS frontend started with PID {process.pid}")

            # Wait a moment and check if process is still running
            time.sleep(2)
            if process.poll() is not None:
                output = self._read_log_tail(self.frontend_log_file)
                logger.error(f"VueJS frontend process terminated unexpectedly")
                logger.error(f"Return code: {process.returncode}")
                logger.error(f"Output: {output}")
                return f"process exited with code {process.returncode}: {output}"

            return None

        except Exception as e:
            logger.error(f"Error starting VueJS frontend: {e}")
            import traceback
            logger.error(f"Stack trace: {traceback.format_exc()}")
            return str(e)

    def _ensure_frontend_dependencies(self, frontend_path, npm):
        """Run npm install when node_modules is missing.

        Returns None on success, error text on failure. Blocking on purpose:
        the preview cannot start without dependencies, and the caller reports
        progress/failure to the user.
        """
        node_modules = os.path.join(frontend_path, 'node_modules')
        installing = os.path.isdir(os.path.join(frontend_path, NPM_INSTALL_LOCK_DIRNAME))
        # An existing node_modules is only trustworthy when no install is in
        # flight; otherwise fall through and wait on the lock.
        if os.path.isdir(node_modules) and not installing:
            return None

        logger.info(f"node_modules missing or being installed - ensuring npm install in {frontend_path}")
        try:
            with npm_install_lock(frontend_path):
                # Even if the install we waited on finished, run npm install
                # ourselves: it is a fast no-op on a complete node_modules and
                # repairs a partial one left by a failed/killed installer.
                result = subprocess.run(
                    [npm, 'install'],
                    cwd=frontend_path,
                    capture_output=True,
                    text=True,
                    timeout=NPM_INSTALL_TIMEOUT,
                )
        except subprocess.TimeoutExpired:
            return f"npm install timed out after {NPM_INSTALL_TIMEOUT} seconds"

        if result.returncode != 0:
            tail = (result.stderr or result.stdout or '').strip()[-2000:]
            logger.error(f"npm install failed in {frontend_path}: {tail}")
            return f"npm install failed: {tail}"

        logger.info(f"npm install completed in {frontend_path}")
        return None

    def _read_log_tail(self, log_path, max_chars=2000):
        """Return the tail of a server log file for error reporting."""
        try:
            with open(log_path, 'r') as f:
                return f.read()[-max_chars:].strip()
        except OSError:
            return ''

    def _save_port_state(self):
        """Persist the ports the servers were started on for a targeted stop."""
        try:
            with open(self.ports_file, 'w') as f:
                json.dump({
                    'frontend_port': self.frontend_port,
                    'backend_port': self.backend_port,
                }, f)
        except OSError as e:
            logger.warning(f"Could not save preview port state: {e}")

    def _load_port_state(self):
        """Return the recorded ports of a running preview, or None.

        The file can be stale or truncated from an earlier crash, so anything
        that is not a well-formed mapping is treated as absent.
        """
        try:
            with open(self.ports_file, 'r') as f:
                state = json.load(f)
        except (OSError, ValueError):
            return None
        return state if isinstance(state, dict) else None

    def _start_legacy_preview(self):
        """Start preview for legacy single Django projects."""
        logger.info("Starting legacy Django preview")

        # Get the project's manage.py path
        manage_py = os.path.join(self.project.project_path, 'manage.py')

        if not os.path.exists(manage_py):
            raise FileNotFoundError(f"manage.py not found in {self.project.project_path}")

        # Get an available port
        port = self._find_available_port(8080, 8100)

        # Get the project name from the path
        project_name = os.path.basename(self.project.project_path)

        # Set up environment
        env = os.environ.copy()
        env['PYTHONPATH'] = self.project.project_path
        env['DJANGO_SETTINGS_MODULE'] = f"{project_name}.settings"

        # Start the development server
        with open(self.backend_log_file, 'w') as log_fh:
            process = subprocess.Popen(
                [sys.executable, 'manage.py', 'runserver', f'127.0.0.1:{port}'],
                cwd=self.project.project_path,
                stdout=log_fh,
                stderr=subprocess.STDOUT,
                env=env
            )

        # Save the PID (use backend_pid_file for legacy projects)
        with open(self.backend_pid_file, 'w') as f:
            f.write(str(process.pid))

        # Wait for server to start
        time.sleep(2)

        # Check if the server started successfully
        if process.poll() is not None:
            error_output = self._read_log_tail(self.backend_log_file)
            raise Exception(f"Server failed to start: {error_output}")

        self.backend_port = port
        self._save_port_state()

        server_url = f"http://localhost:{port}"

        # Note: Browser opening is handled by the frontend client via window.open()
        # Do not use webbrowser.open() here to avoid opening duplicate tabs

        return {
            'success': True,
            'preview_url': server_url,
            'message': 'Development server started successfully'
        }

    def _find_available_port(self, start_port, max_port):
        """Find an available port starting from the start_port."""
        return self._find_available_port_excluding(start_port, max_port)

    def _find_available_port_excluding(self, start_port, max_port, exclude_ports=None):
        """Find an available port starting from the start_port, excluding specified ports."""
        if exclude_ports is None:
            exclude_ports = []

        port = start_port

        while port <= max_port:
            # Skip excluded ports
            if port in exclude_ports:
                port += 1
                continue

            if not self._port_in_use(port):
                return port

            port += 1

        # If we reach here, return start_port and hope for the best (excluding excluded ports)
        if start_port not in exclude_ports:
            return start_port
        else:
            return start_port + 1

    @staticmethod
    def _process_connections(proc):
        """Process connections across psutil versions (connections() was
        renamed to net_connections() in psutil 6)."""
        if hasattr(proc, 'net_connections'):
            return proc.net_connections()
        return proc.connections()

    def _port_in_use(self, port):
        """Check whether any process is listening on the given port."""
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    for conn in self._process_connections(proc):
                        if hasattr(conn, 'laddr') and conn.laddr and conn.laddr.port == port:
                            return True
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.Error):
                    continue
        except Exception:
            pass
        return False

    def stop_preview(self):
        """Stop both frontend and backend development servers."""
        try:
            success_messages = []

            # Only sweep the ports this preview actually recorded; killing by
            # default port numbers could take down unrelated dev servers.
            port_state = self._load_port_state() or {}

            # Stop frontend server
            if self._stop_vuejs_frontend(port=port_state.get('frontend_port')):
                success_messages.append("Frontend server stopped")

            # Stop backend server
            if self._stop_django_backend(port=port_state.get('backend_port')):
                success_messages.append("Backend server stopped")

            if os.path.exists(self.ports_file):
                os.remove(self.ports_file)

            message = ', '.join(success_messages) if success_messages else 'No servers were running'

            return {
                'success': True,
                'message': f'Development servers stopped successfully: {message}'
            }
        except Exception as e:
            logger.error(f"Error stopping preview servers: {str(e)}")
            raise

    def cleanup_project_files(self, name_variants=None):
        """Stop the servers and remove every file this service wrote for the project.

        For deleting a project, where stop_preview() is not enough: it leaves the
        logs behind (deliberately, so a stopped server's output stays readable)
        and only knows the project's current name. Older releases wrote these
        files under sanitized spellings of the name, so callers can pass
        name_variants to sweep those too.
        """
        try:
            self.stop_preview()
        except Exception as e:
            # Best effort: a project must still be deletable when its dev
            # servers are already gone or unkillable.
            logger.warning(f"Error stopping preview while cleaning up {self.project.name}: {e}")

        for name in name_variants or [self.project.name]:
            for suffix in PID_SUFFIXES:
                # stop_preview already cleared the current-name PID files; this
                # catches legacy and renamed leftovers, killing what they name.
                try:
                    self._kill_from_pid_file(os.path.join(self.pid_dir, f"{name}{suffix}"))
                except Exception as e:
                    logger.warning(f"Error stopping process from {name}{suffix}: {e}")

            for suffix in LOG_SUFFIXES + (PORTS_SUFFIX, BROWSER_STATE_SUFFIX):
                path = os.path.join(self.pid_dir, f"{name}{suffix}")
                if not os.path.exists(path):
                    continue
                try:
                    os.remove(path)
                    logger.info(f"Deleted project file: {path}")
                except OSError as e:
                    logger.warning(f"Failed to delete project file {path}: {e}")

            shutil.rmtree(os.path.join(self.pid_dir, f"{name}{BROWSER_PROFILE_SUFFIX}"), ignore_errors=True)

    def _stop_vuejs_frontend(self, port=None):
        """Stop VueJS frontend server."""
        try:
            stopped = self._kill_from_pid_file(self.frontend_pid_file)
            if port:
                stopped = self._kill_by_port(port) or stopped
            return stopped
        except Exception as e:
            logger.error(f"Error stopping frontend server: {e}")
            return False

    def _stop_django_backend(self, port=None):
        """Stop Django backend server."""
        try:
            stopped = self._kill_from_pid_file(self.backend_pid_file)
            if port:
                stopped = self._kill_by_port(port) or stopped
            return stopped
        except Exception as e:
            logger.error(f"Error stopping backend server: {e}")
            return False

    def _kill_from_pid_file(self, pid_file):
        """Stop the recorded process (and its children), removing the PID file."""
        if not os.path.exists(pid_file):
            return False

        stopped = False
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
        except (OSError, ValueError):
            pid = None

        if pid:
            try:
                process = psutil.Process(pid)
                # Children first, so a dying parent cannot orphan them.
                for proc in process.children(recursive=True) + [process]:
                    self._stop_process(proc)
                stopped = True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        try:
            os.remove(pid_file)
        except OSError as e:
            logger.warning(f"Failed to delete PID file {pid_file}: {e}")
        return stopped

    @staticmethod
    def _stop_process(proc):
        """Ask a process to exit, escalating to SIGKILL if it ignores that."""
        try:
            proc.terminate()
            proc.wait(timeout=3)
        except psutil.TimeoutExpired:
            try:
                proc.kill()
            except psutil.NoSuchProcess:
                pass
        except psutil.NoSuchProcess:
            pass
        except psutil.AccessDenied:
            logger.warning(f"Access denied stopping process {proc.pid}")

    def _kill_by_port(self, port):
        """Kill any process still listening on the given port."""
        stopped = False
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                for conn in self._process_connections(proc):
                    if hasattr(conn, 'laddr') and conn.laddr and conn.laddr.port == port:
                        proc.kill()
                        stopped = True
                        break
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.Error):
                continue
        return stopped
