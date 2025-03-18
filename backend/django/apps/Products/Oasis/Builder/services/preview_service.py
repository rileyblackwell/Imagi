"""
Service for project preview operations in the Builder app.
"""

import subprocess
import os
import psutil
import time
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class PreviewService:
    """Service for project preview operations."""
    
    def __init__(self, project):
        self.project = project
        self.port = 8080
        self.pid_file = os.path.join(settings.PROJECTS_ROOT, 
                                   str(project.user.id), 
                                   f"{project.name}_server.pid")
    
    def start_preview(self):
        """Start a development server for the project."""
        try:
            # Stop any existing server for this project
            self.stop_preview()
            
            # Get the project's manage.py path
            manage_py = os.path.join(self.project.project_path, 'manage.py')
            
            if not os.path.exists(manage_py):
                raise FileNotFoundError(f"manage.py not found in {self.project.project_path}")
            
            logger.info(f"Starting server with manage.py at: {manage_py}")
            
            # Get the project name from the path (use full unique name)
            project_name = os.path.basename(self.project.project_path)
            
            # Add the project directory to Python path
            project_dir = self.project.project_path
            env = os.environ.copy()
            env['PYTHONPATH'] = project_dir
            env['DJANGO_SETTINGS_MODULE'] = f"{project_name}.settings"
            
            # Start the development server using pipenv run
            process = subprocess.Popen(
                ['pipenv', 'run', 'python', 'manage.py', 'runserver', f'127.0.0.1:{self.port}'],
                cwd=self.project.project_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                env=env
            )
            
            # Save the PID
            with open(self.pid_file, 'w') as f:
                f.write(str(process.pid))
            
            # Wait a moment for the server to start
            time.sleep(2)
            
            # Check if the server started successfully
            if process.poll() is not None:
                error_output = process.stderr.read()
                raise Exception(f"Server failed to start: {error_output}")
            
            server_url = f"http://localhost:{self.port}"
            
            return {
                'success': True,
                'preview_url': server_url,
                'message': 'Development server started successfully'
            }
        except Exception as e:
            logger.error(f"Error starting preview server: {str(e)}")
            raise
    
    def stop_preview(self):
        """Stop the development server."""
        try:
            if os.path.exists(self.pid_file):
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())
                try:
                    process = psutil.Process(pid)
                    # Kill all child processes first
                    children = process.children(recursive=True)
                    for child in children:
                        child.kill()
                    process.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                os.remove(self.pid_file)
                
            # Also check if port 8080 is in use and kill that process
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    for conn in proc.connections():
                        if hasattr(conn, 'laddr') and conn.laddr.port == self.port:
                            proc.kill()
                            break
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.Error):
                    continue
            
            return {
                'success': True,
                'message': 'Development server stopped successfully'
            }
        except Exception as e:
            logger.error(f"Error stopping preview server: {str(e)}")
            raise 