import subprocess
import os
import signal
import psutil
from django.conf import settings

class DevServerManager:
    def __init__(self, project):
        self.project = project
        self.server_process = None
        self.pid_file = os.path.join(settings.PROJECTS_ROOT, str(project.user.id), 
                                    f"{project.get_url_safe_name()}_server.pid")

    def start_server(self):
        """Start the development server for the project"""
        try:
            # Kill any existing server for this project
            self.stop_server()
            
            # Get the project's manage.py path
            manage_py = os.path.join(self.project.project_path, 'manage.py')
            
            # Start the development server on a dynamic port
            process = subprocess.Popen(
                ['python', manage_py, 'runserver', '0:0'],  # Port 0 means use any available port
                cwd=self.project.project_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Save the PID
            with open(self.pid_file, 'w') as f:
                f.write(str(process.pid))
            
            # Read the first few lines to get the port number
            for line in process.stdout:
                if "Starting development server at" in line:
                    port = line.split(":")[-1].strip().rstrip('/')
                    return int(port)
            
            raise Exception("Could not determine server port")
            
        except Exception as e:
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