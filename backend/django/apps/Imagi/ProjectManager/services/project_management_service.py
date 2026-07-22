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
            
            # Stop any running preview servers and delete the PID, log and
            # preview-port files that live outside the project directory
            self._stop_project_server_and_cleanup_files(project)
            
            # Delete project files using path (preferred) or name as fallback
            if project_path and os.path.exists(project_path):
                self._delete_project_directory(project_path)
            else:
                # Fallback to name-based deletion if path doesn't exist
                self._delete_project_files(project_name)

            # Task worktrees live beside the project directory
            # ('<project_path>--wt-<conversation_id>', see Build's
            # version_control_service); sweep them so deleted projects
            # don't leak per-task checkouts.
            self._delete_task_worktrees(project_path)
            
            # Perform a hard delete by using the hard_delete=True parameter
            project.delete(hard_delete=True)
            
            # Verify deletion and force if needed
            if Project.objects.filter(id=project_id).exists():
                logger.warning(f"Project {project_id} still exists after deletion attempt, forcing removal")
                # Force delete with raw SQL if needed
                from django.db import connection
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM Products_Imagi_ProjectManager_project WHERE id = %s", [project_id])
            
            logger.info(f"Project {project_name} deleted successfully (path: {project_path})")
            return {"success": True, "message": f"Project {project_name} deleted successfully"}
        except Exception as e:
            logger.error(f"Error deleting project: {str(e)}")
            raise ValidationError(f"Failed to delete project: {str(e)}")

    def _delete_project_directory(self, project_path):
        """Delete project directory at the specific path with robust cleanup.
        
        Handles common issues like permission problems with node_modules,
        locked files, and ensures complete cleanup of all project files.
        """
        if not project_path:
            logger.warning("Cannot delete project directory: No path provided")
            return
            
        try:
            if not os.path.exists(project_path):
                logger.warning(f"Project directory not found: {project_path}")
                return
                
            if not os.path.isdir(project_path):
                logger.warning(f"Project path is not a directory: {project_path}")
                return
            
            logger.info(f"Deleting project directory: {project_path}")
            import shutil
            import stat
            
            def handle_remove_readonly(func, path, exc_info):
                """Handle permission errors during rmtree by making files writable."""
                # If the error is a permission error, try to fix it
                if exc_info[0] == PermissionError or (hasattr(exc_info[1], 'errno') and exc_info[1].errno == 13):
                    try:
                        # Make the file/directory writable
                        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                        # Try the operation again
                        func(path)
                    except Exception as e:
                        logger.warning(f"Could not remove {path} after chmod: {e}")
                else:
                    logger.warning(f"Error removing {path}: {exc_info[1]}")
            
            # First, try to handle node_modules specifically (most common problem)
            node_modules_paths = [
                os.path.join(project_path, 'frontend', 'vuejs', 'node_modules'),
                os.path.join(project_path, 'node_modules'),
            ]
            
            for node_modules_path in node_modules_paths:
                if os.path.exists(node_modules_path):
                    logger.info(f"Removing node_modules at: {node_modules_path}")
                    try:
                        # Make all files in node_modules writable before deletion
                        for root, dirs, files in os.walk(node_modules_path):
                            for d in dirs:
                                try:
                                    os.chmod(os.path.join(root, d), stat.S_IRWXU)
                                except Exception:
                                    pass
                            for f in files:
                                try:
                                    os.chmod(os.path.join(root, f), stat.S_IRWXU)
                                except Exception:
                                    pass
                        shutil.rmtree(node_modules_path, onerror=handle_remove_readonly)
                    except Exception as e:
                        logger.warning(f"Error removing node_modules: {e}")
            
            # Now delete the entire project directory
            shutil.rmtree(project_path, onerror=handle_remove_readonly)
            
            # Verify deletion succeeded
            if os.path.exists(project_path):
                logger.warning(f"Directory still exists after deletion attempt: {project_path}")
                # Try one more time with more aggressive approach
                try:
                    # Walk through and force delete everything
                    for root, dirs, files in os.walk(project_path, topdown=False):
                        for name in files:
                            file_path = os.path.join(root, name)
                            try:
                                os.chmod(file_path, stat.S_IRWXU)
                                os.remove(file_path)
                            except Exception as e:
                                logger.warning(f"Could not remove file {file_path}: {e}")
                        for name in dirs:
                            dir_path = os.path.join(root, name)
                            try:
                                os.chmod(dir_path, stat.S_IRWXU)
                                os.rmdir(dir_path)
                            except Exception as e:
                                logger.warning(f"Could not remove directory {dir_path}: {e}")
                    # Finally try to remove the root
                    os.rmdir(project_path)
                except Exception as e:
                    logger.error(f"Final cleanup attempt failed for {project_path}: {e}")
            
            # Final verification
            if os.path.exists(project_path):
                logger.error(f"Failed to completely delete project directory: {project_path}")
            else:
                logger.info(f"Project directory deleted successfully: {project_path}")
                
        except Exception as e:
            logger.error(f"Error deleting project directory {project_path}: {str(e)}")
            # Don't raise the exception, as we still want to delete the database record

    def _delete_task_worktrees(self, project_path):
        """Delete the per-task git worktree directories beside the project.

        Best-effort: a worktree that cannot be removed is logged, never
        raised — it must not block deleting the project itself.
        """
        if not project_path:
            return
        try:
            import glob
            for worktree_path in glob.glob(glob.escape(project_path.rstrip(os.sep)) + '--wt-*'):
                if os.path.isdir(worktree_path):
                    logger.info(f"Deleting task worktree: {worktree_path}")
                    self._delete_project_directory(worktree_path)
        except Exception as e:
            logger.warning(f"Error deleting task worktrees for {project_path}: {e}")

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
                    # Use the robust deletion method
                    self._delete_project_directory(project_path)

    def _project_name_variants(self, project_name):
        """Every name a project's sidecar files may have been written under.

        PreviewService uses project.name verbatim, but older code sanitized it
        first, so both spellings can exist on disk.
        """
        variants = [
            project_name,
            project_name.lower().replace(' ', '_'),
            project_name.replace(' ', '-'),
        ]
        try:
            from .project_creation_service import ProjectCreationService
            creation_service = ProjectCreationService(self.user)
            variants.append(creation_service._sanitize_project_name(project_name))
        except Exception:
            # If sanitization fails, continue with available names
            pass

        # Deduplicate while preserving order
        seen = set()
        return [v for v in variants if v and not (v in seen or seen.add(v))]

    def _stop_project_server_and_cleanup_files(self, project):
        """Stop the project's dev servers and delete the files they left behind.

        PreviewService owns those processes and files, so it does the work; this
        only supplies the older spellings of the project name to sweep. A stale
        ports file is worse than clutter: a later project reusing this name would
        read it and kill whatever now holds those ports.
        """
        try:
            # Imported here because PreviewService imports this package back.
            from apps.Imagi.Build.services.preview_service import PreviewService

            PreviewService(project).cleanup_project_files(
                name_variants=self._project_name_variants(project.name)
            )
        except Exception as e:
            logger.warning(f"Error during server stop and file cleanup for project '{project.name}': {str(e)}")
            # Don't raise: this cleanup is not critical for project deletion

