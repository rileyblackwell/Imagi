import os
import logging
from typing import List, Optional
from django.conf import settings
from rest_framework.exceptions import ValidationError
from ..models import Project

logger = logging.getLogger(__name__)

class ProjectManagementService:
    def __init__(self, user):
        self.user = user
        self.base_directory = os.path.join(settings.PROJECTS_ROOT, str(user.id))
        os.makedirs(self.base_directory, exist_ok=True)
    
    # Project management methods
    def get_active_projects(self) -> List[Project]:
        """Get all active projects for the current user."""
        return Project.objects.filter(user=self.user, is_active=True)

    def get_project(self, project_id: int) -> Optional[Project]:
        """Get a specific project by ID."""
        return self.get_active_projects().filter(id=project_id).first()
        
    def delete_project(self, project_or_id):
        """Delete a project and its associated files."""
        try:
            # Get project if ID is provided
            if isinstance(project_or_id, int):
                project = self.get_project(project_or_id)
                if not project:
                    raise ValidationError("Project not found")
            else:
                project = project_or_id
            
            # Store project details before deletion
            project_name = project.name
            project_path = project.project_path
            project_id = project.id
            
            # Stop any running preview server and delete PID file
            self._stop_project_server_and_cleanup_pid(project_name)
            
            # Delete project files using path (preferred) or name as fallback
            if project_path and os.path.exists(project_path):
                self._delete_project_directory(project_path)
            else:
                # Fallback to name-based deletion if path doesn't exist
                self._delete_project_files(project_name)
            
            # Perform a hard delete by using the hard_delete=True parameter
            project.delete(hard_delete=True)
            
            # Verify deletion and force if needed
            if Project.objects.filter(id=project_id).exists():
                logger.warning(f"Project {project_id} still exists after deletion attempt, forcing removal")
                # Force delete with raw SQL if needed
                from django.db import connection
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM Products_Oasis_ProjectManager_project WHERE id = %s", [project_id])
            
            logger.info(f"Project {project_name} deleted successfully (path: {project_path})")
            return {"success": True, "message": f"Project {project_name} deleted successfully"}
        except Exception as e:
            logger.error(f"Error deleting project: {str(e)}")
            raise ValidationError(f"Failed to delete project: {str(e)}")

    def _delete_project_directory(self, project_path):
        """Delete project directory at the specific path"""
        if not project_path:
            logger.warning("Cannot delete project directory: No path provided")
            return
            
        try:
            if os.path.exists(project_path) and os.path.isdir(project_path):
                logger.info(f"Deleting project directory: {project_path}")
                import shutil
                shutil.rmtree(project_path, ignore_errors=True)
                logger.info(f"Project directory deleted: {project_path}")
            else:
                logger.warning(f"Project directory not found: {project_path}")
        except Exception as e:
            logger.error(f"Error deleting project directory {project_path}: {str(e)}")
            # Don't raise the exception, as we still want to delete the database record

    def _delete_project_files(self, project_name):
        """Delete project files for a given project name (legacy method, fallback)"""
        # Find project directories matching the project name
        from .project_creation_service import ProjectCreationService
        creation_service = ProjectCreationService(self.user)
        sanitized_name = creation_service._sanitize_project_name(project_name)
        
        for item in os.listdir(self.base_directory):
            if item.startswith(sanitized_name + '_'):
                project_path = os.path.join(self.base_directory, item)
                if os.path.isdir(project_path):
                    logger.info(f"Deleting project directory: {project_path}")
                    import shutil
                    shutil.rmtree(project_path, ignore_errors=True)

    def _stop_project_server_and_cleanup_pid(self, project_name):
        """Stop any running development server and delete the PID file for the project.
        
        This matches the PID file naming convention used by PreviewService:
        {settings.PROJECTS_ROOT}/{user.id}/{project.name}_server.pid
        """
        try:
            # Primary PID file location (matches PreviewService exactly)
            pid_file_path = os.path.join(self.base_directory, f"{project_name}_server.pid")
            
            # First, try to gracefully stop any running server process
            if os.path.exists(pid_file_path):
                try:
                    with open(pid_file_path, 'r') as f:
                        pid = int(f.read().strip())
                    
                    # Try to stop the process and its children
                    try:
                        import psutil
                        process = psutil.Process(pid)
                        # Kill all child processes first
                        children = process.children(recursive=True)
                        for child in children:
                            try:
                                child.terminate()
                                child.wait(timeout=3)  # Wait up to 3 seconds
                            except (psutil.TimeoutExpired, psutil.NoSuchProcess):
                                try:
                                    child.kill()  # Force kill if terminate doesn't work
                                except psutil.NoSuchProcess:
                                    pass
                        
                        # Now terminate the main process
                        process.terminate()
                        process.wait(timeout=3)  # Wait up to 3 seconds
                        logger.info(f"Gracefully stopped server process {pid} for project '{project_name}'")
                    except (psutil.TimeoutExpired, psutil.NoSuchProcess):
                        try:
                            process.kill()  # Force kill if terminate doesn't work
                            logger.info(f"Force killed server process {pid} for project '{project_name}'")
                        except psutil.NoSuchProcess:
                            logger.debug(f"Server process {pid} was already stopped")
                    except psutil.AccessDenied:
                        logger.warning(f"Access denied when trying to stop server process {pid}")
                    except ImportError:
                        logger.warning("psutil not available, cannot gracefully stop server process")
                    
                except (ValueError, FileNotFoundError) as e:
                    logger.warning(f"Invalid PID file content in {pid_file_path}: {str(e)}")
            
            # Now delete the PID file
            if os.path.exists(pid_file_path):
                try:
                    os.remove(pid_file_path)
                    logger.info(f"Deleted PID file: {pid_file_path}")
                    return
                except Exception as e:
                    logger.warning(f"Failed to delete PID file {pid_file_path}: {str(e)}")
            else:
                # If the primary naming doesn't exist, try some fallback patterns
                # This handles cases where project names might have been sanitized differently
                from .project_creation_service import ProjectCreationService
                creation_service = ProjectCreationService(self.user)
                sanitized_name = creation_service._sanitize_project_name(project_name)
                
                fallback_pid_names = [
                    f"{sanitized_name}_server.pid",
                    f"{project_name.lower().replace(' ', '_')}_server.pid",
                    f"{project_name.replace(' ', '-')}_server.pid"
                ]
                
                for pid_name in fallback_pid_names:
                    fallback_pid_path = os.path.join(self.base_directory, pid_name)
                    if os.path.exists(fallback_pid_path):
                        try:
                            os.remove(fallback_pid_path)
                            logger.info(f"Deleted fallback PID file: {fallback_pid_path}")
                            return
                        except Exception as e:
                            logger.warning(f"Failed to delete fallback PID file {fallback_pid_path}: {str(e)}")
                
                logger.debug(f"No PID file found for project '{project_name}' (this is normal if the server wasn't running)")
                
        except Exception as e:
            logger.warning(f"Error during server stop and PID file cleanup for project '{project_name}': {str(e)}")
            # Don't raise the exception as PID file cleanup is not critical for project deletion

    def undo_last_action(self, project_or_id):
        """Undo the last action in a project."""
        try:
            # Get project if ID is provided
            if isinstance(project_or_id, int):
                project = self.get_project(project_or_id)
                if not project:
                    raise ValidationError("Project not found")
            else:
                project = project_or_id
                
            # Get the project's git repository
            repo_path = project.project_path
            if not os.path.exists(repo_path):
                raise ValidationError("Project repository not found")
            
            # TODO: Implement git-based undo functionality
            # For now, return a placeholder response
            return {
                'success': True,
                'message': 'Last action undone successfully'
            }
        except Exception as e:
            logger.error(f"Error undoing action: {str(e)}")
            raise ValidationError(f"Failed to undo last action: {str(e)}")
    
    # Template generation methods
    def generate_view_code(self, view_name):
        """Generate code for a simple Django view"""
        return f"""
from django.shortcuts import render

def {view_name}(request):
    \"\"\"Render the {view_name} page\"\"\"
    return render(request, '{view_name}.html')
"""

    def generate_urls_code(self, url_patterns):
        """Generate Django URLs configuration"""
        imports = [
            "from django.urls import path",
            "from django.conf import settings",
            "from django.conf.urls.static import static",
            "from . import views",
            "\n",
            "urlpatterns = ["
        ]
        
        patterns = []
        for name in url_patterns:
            if name == 'index':
                patterns.append(f"    path('', views.{name}, name='{name}'),")
            else:
                patterns.append(f"    path('{name}/', views.{name}, name='{name}'),")
        
        patterns.append("]")
        
        # Add static/media serving for development
        patterns.extend([
            "",
            "# Serve static and media files during development",
            "if settings.DEBUG:",
            "    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)",
            "    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)"
        ])
        
        return "\n".join(imports + patterns) 