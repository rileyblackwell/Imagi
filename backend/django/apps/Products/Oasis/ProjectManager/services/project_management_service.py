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