import subprocess
import os
import psutil
import time
from django.conf import settings

class DevServerManager:
    def __init__(self, user_project):
        self.user_project = user_project
        self.server_process = None
        self.port = 8080
        self.pid_file = os.path.join(settings.PROJECTS_ROOT, 
                                    str(user_project.user.id), 
                                    f"{user_project.name}_server.pid")

    def start_server(self):
        """Start the development server for the project"""
        try:
            # Kill any existing server for this project
            self.stop_server()
            
            # Get the project's manage.py path
            manage_py = os.path.join(self.user_project.project_path, 'manage.py')
            
            if not os.path.exists(manage_py):
                raise FileNotFoundError(f"manage.py not found in {self.user_project.project_path}")
            
            print(f"Starting server with manage.py at: {manage_py}")
            
            # Start the development server on port 8080
            process = subprocess.Popen(
                ['python3', manage_py, 'runserver', '127.0.0.1:8080'],
                cwd=self.user_project.project_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
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
            
            return 8080
            
        except Exception as e:
            print(f"Error starting server: {str(e)}")
            raise Exception(f"Failed to start development server: {str(e)}")

    def stop_server(self):
        """Stop the development server if it's running"""
        try:
            if os.path.exists(self.pid_file):
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())
                try:
                    process = psutil.Process(pid)
                    for child in process.children(recursive=True):
                        child.kill()
                    process.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                os.remove(self.pid_file)
                
            # Also check if port 8080 is in use and kill that process
            for proc in psutil.process_iter(['pid', 'name', 'connections']):
                try:
                    for conn in proc.connections():
                        if conn.laddr.port == self.port:
                            proc.kill()
                            break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except Exception as e:
            print(f"Error stopping server: {str(e)}")

    def get_server_url(self):
        """Get the URL of the running development server"""
        try:
            # Start server if not running
            port = self.start_server()
            return f"http://localhost:{port}"
        except Exception as e:
            raise Exception(f"Failed to get server URL: {str(e)}") 