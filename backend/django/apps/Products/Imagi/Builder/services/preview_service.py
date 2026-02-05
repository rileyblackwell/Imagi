"""
Service for project preview operations in the Builder app.
"""

import subprocess
import os
import psutil
import time
import logging
import json
from django.conf import settings

logger = logging.getLogger(__name__)

class PreviewService:
    """Service for project preview operations with dual-stack support."""
    
    def __init__(self, project):
        self.project = project
        self.frontend_port = 5173  # Vite dev server - use 5173 to avoid conflict with main project on 5174
        self.backend_port = 8080   # Django dev server - use 8080 to avoid conflict with main project on 8000
        
        # Ensure the PID file directory exists
        pid_dir = os.path.join(settings.PROJECTS_ROOT, str(project.user.id))
        os.makedirs(pid_dir, exist_ok=True)
        
        self.frontend_pid_file = os.path.join(pid_dir, f"{project.name}_frontend.pid")
        self.backend_pid_file = os.path.join(pid_dir, f"{project.name}_backend.pid")
    
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

    def _start_dual_stack_preview(self, frontend_path, backend_path):
        """Start both VueJS frontend and Django backend servers."""
        logger.info("Starting dual-stack preview (VueJS + Django)")
        
        # Start Django backend first
        backend_success = self._start_django_backend(backend_path)
        if not backend_success:
            raise Exception("Failed to start Django backend")
        
        # Wait a moment for backend to start
        time.sleep(3)
        
        # Start VueJS frontend
        frontend_success = self._start_vuejs_frontend(frontend_path)
        if not frontend_success:
            # If frontend fails, stop the backend
            self._stop_django_backend()
            raise Exception("Failed to start VueJS frontend")
        
        # Wait for frontend to start
        time.sleep(5)
        
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
        """Start Django backend server."""
        try:
            logger.info(f"Attempting to start Django backend in: {backend_path}")
            
            # Find manage.py
            manage_py = os.path.join(backend_path, 'manage.py')
            if not os.path.exists(manage_py):
                logger.error(f"manage.py not found in {backend_path}")
                return False
            
            logger.info(f"Found manage.py at: {manage_py}")
            
            # Get project name for Django settings
            project_dirs = [d for d in os.listdir(backend_path) 
                          if os.path.isdir(os.path.join(backend_path, d)) 
                          and os.path.exists(os.path.join(backend_path, d, 'settings.py'))]
            
            logger.info(f"Found project directories with settings.py: {project_dirs}")
            
            if not project_dirs:
                logger.error("No Django project directory found")
                return False
            
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
            
            # Start Django development server
            process = subprocess.Popen(
                ['python', 'manage.py', 'runserver', f'127.0.0.1:{self.backend_port}'],
                cwd=backend_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                env=env
            )
            
            # Save the PID
            with open(self.backend_pid_file, 'w') as f:
                f.write(str(process.pid))
            
            logger.info(f"Django backend started with PID {process.pid}")
            
            # Wait a moment and check if process is still running
            time.sleep(1)
            if process.poll() is not None:
                # Process has terminated
                stdout, stderr = process.communicate()
                logger.error(f"Django backend process terminated unexpectedly")
                logger.error(f"Return code: {process.returncode}")
                logger.error(f"STDOUT: {stdout}")
                logger.error(f"STDERR: {stderr}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error starting Django backend: {e}")
            import traceback
            logger.error(f"Stack trace: {traceback.format_exc()}")
            return False

    def _start_vuejs_frontend(self, frontend_path):
        """Start VueJS frontend server."""
        try:
            logger.info(f"Attempting to start VueJS frontend in: {frontend_path}")
            
            # Check if package.json exists
            package_json = os.path.join(frontend_path, 'package.json')
            if not os.path.exists(package_json):
                logger.error(f"package.json not found in {frontend_path}")
                return False
            
            logger.info(f"Found package.json at: {package_json}")
            
            # Check if node_modules exists
            node_modules = os.path.join(frontend_path, 'node_modules')
            if not os.path.exists(node_modules):
                logger.warning(f"node_modules not found in {frontend_path}, npm dependencies may not be installed")
            
            # Find available port for frontend (avoiding conflict with main project on 5174)
            self.frontend_port = self._find_available_port_excluding(5173, 5200, exclude_ports=[5174])
            logger.info(f"Starting VueJS frontend on port {self.frontend_port}")
            
            # Set up environment for Vite
            env = os.environ.copy()
            env['PORT'] = str(self.frontend_port)
            
            # Ensure PID file directory exists
            os.makedirs(os.path.dirname(self.frontend_pid_file), exist_ok=True)
            
            # Start Vite development server
            process = subprocess.Popen(
                ['npm', 'run', 'dev', '--', '--port', str(self.frontend_port), '--host'],
                cwd=frontend_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                env=env
            )
            
            # Save the PID
            with open(self.frontend_pid_file, 'w') as f:
                f.write(str(process.pid))
            
            logger.info(f"VueJS frontend started with PID {process.pid}")
            
            # Wait a moment and check if process is still running
            time.sleep(2)
            if process.poll() is not None:
                # Process has terminated
                stdout, stderr = process.communicate()
                logger.error(f"VueJS frontend process terminated unexpectedly")
                logger.error(f"Return code: {process.returncode}")
                logger.error(f"STDOUT: {stdout}")
                logger.error(f"STDERR: {stderr}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error starting VueJS frontend: {e}")
            import traceback
            logger.error(f"Stack trace: {traceback.format_exc()}")
            return False

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
        process = subprocess.Popen(
            ['python', 'manage.py', 'runserver', f'127.0.0.1:{port}'],
            cwd=self.project.project_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            env=env
        )
        
        # Save the PID (use backend_pid_file for legacy projects)
        with open(self.backend_pid_file, 'w') as f:
            f.write(str(process.pid))
        
        # Wait for server to start
        time.sleep(2)
        
        # Check if the server started successfully
        if process.poll() is not None:
            error_output = process.stderr.read()
            raise Exception(f"Server failed to start: {error_output}")
        
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
        port = start_port
        
        while port <= max_port:
            try:
                # Check if port is in use
                in_use = False
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        for conn in proc.connections():
                            if hasattr(conn, 'laddr') and conn.laddr.port == port:
                                in_use = True
                                break
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.Error):
                        continue
                
                if not in_use:
                    return port
            except:
                pass
                
            port += 1
            
        # If we reach here, return start_port and hope for the best
        return start_port
    
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
                
            try:
                # Check if port is in use
                in_use = False
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        for conn in proc.connections():
                            if hasattr(conn, 'laddr') and conn.laddr.port == port:
                                in_use = True
                                break
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.Error):
                        continue
                
                if not in_use:
                    return port
            except:
                pass
                
            port += 1
            
        # If we reach here, return start_port and hope for the best (excluding excluded ports)
        if start_port not in exclude_ports:
            return start_port
        else:
            return start_port + 1
    
    def stop_preview(self):
        """Stop both frontend and backend development servers."""
        try:
            success_messages = []
            
            # Stop frontend server
            if self._stop_vuejs_frontend():
                success_messages.append("Frontend server stopped")
            
            # Stop backend server
            if self._stop_django_backend():
                success_messages.append("Backend server stopped")
            
            message = ', '.join(success_messages) if success_messages else 'No servers were running'
            
            return {
                'success': True,
                'message': f'Development servers stopped successfully: {message}'
            }
        except Exception as e:
            logger.error(f"Error stopping preview servers: {str(e)}")
            raise

    def _stop_vuejs_frontend(self):
        """Stop VueJS frontend server."""
        try:
            stopped = False
            
            # Stop using PID file
            if os.path.exists(self.frontend_pid_file):
                with open(self.frontend_pid_file, 'r') as f:
                    pid = int(f.read().strip())
                try:
                    process = psutil.Process(pid)
                    # Kill all child processes first
                    children = process.children(recursive=True)
                    for child in children:
                        child.kill()
                    process.kill()
                    stopped = True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                os.remove(self.frontend_pid_file)
            
            # Also check for processes on frontend port
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    for conn in proc.connections():
                        if hasattr(conn, 'laddr') and conn.laddr.port == self.frontend_port:
                            proc.kill()
                            stopped = True
                            break
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.Error):
                    continue
            
            return stopped
        except Exception as e:
            logger.error(f"Error stopping frontend server: {e}")
            return False

    def _stop_django_backend(self):
        """Stop Django backend server."""
        try:
            stopped = False
            
            # Stop using PID file
            if os.path.exists(self.backend_pid_file):
                with open(self.backend_pid_file, 'r') as f:
                    pid = int(f.read().strip())
                try:
                    process = psutil.Process(pid)
                    # Kill all child processes first
                    children = process.children(recursive=True)
                    for child in children:
                        child.kill()
                    process.kill()
                    stopped = True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                os.remove(self.backend_pid_file)
            
            # Also check for processes on backend port
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    for conn in proc.connections():
                        if hasattr(conn, 'laddr') and conn.laddr.port == self.backend_port:
                            proc.kill()
                            stopped = True
                            break
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.Error):
                    continue
            
            return stopped
        except Exception as e:
            logger.error(f"Error stopping backend server: {e}")
            return False 