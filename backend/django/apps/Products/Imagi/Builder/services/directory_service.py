"""
Service for creating and deleting directories in projects.
"""

import os
import shutil
import logging
from rest_framework.exceptions import ValidationError, NotFound
from apps.Products.Imagi.ProjectManager.models import Project

logger = logging.getLogger(__name__)


class DirectoryService:
    def __init__(self, user=None, project=None):
        """
        Initialize the directory service with either a user or a project.
        If a project is provided, it will be used directly.
        If a user is provided, project_id must be passed to methods.
        """
        self.user = user
        self.project = project

        if project:
            self.project_path = project.project_path

    def get_project(self, project_id):
        """Get a project by ID when initialized with user."""
        if not self.user:
            raise ValidationError("DirectoryService initialized without user")

        try:
            return Project.objects.get(id=project_id, user=self.user, is_active=True)
        except Project.DoesNotExist:
            raise NotFound('Project not found')

    def get_project_path(self, project_id=None):
        """Get the project path for the current project or specified project ID."""
        try:
            if self.project:
                if not self.project.project_path:
                    logger.error(f"Project {self.project.id} has no project_path")
                    return None
                return self.project.project_path

            if project_id:
                project = self.get_project(project_id)
                if not project.project_path:
                    logger.error(f"Project {project.id} has no project_path")
                    return None
                return project.project_path

            raise ValidationError("No project specified")
        except Exception as e:
            logger.error(f"Error getting project path: {str(e)}")
            return None

    def _validate_path(self, project_path, relative_path):
        """Validate that the resolved path stays within the project root."""
        full_path = os.path.realpath(os.path.join(project_path, relative_path))
        project_root = os.path.realpath(project_path)
        if not full_path.startswith(project_root + os.sep) and full_path != project_root:
            raise ValidationError(f"Path traversal detected: {relative_path}")
        return full_path

    def create_directory(self, dir_path, project_id=None):
        """Create a directory within the project.

        Args:
            dir_path: Relative path for the new directory within the project.
            project_id: Optional project ID (required if initialized with user).

        Returns:
            dict with success status, path, and message.
        """
        try:
            project_path = self.get_project_path(project_id)
            full_path = self._validate_path(project_path, dir_path)

            os.makedirs(full_path, exist_ok=True)

            logger.info(f"Successfully created directory: {dir_path}")
            return {
                'success': True,
                'path': dir_path,
                'message': f'Directory {dir_path} created successfully'
            }
        except Exception as e:
            logger.error(f"Error creating directory: {str(e)}")
            raise

    def delete_directory(self, dir_path, project_id=None, recursive=False):
        """Delete a directory from the project.

        Args:
            dir_path: Relative path to the directory within the project.
            project_id: Optional project ID (required if initialized with user).
            recursive: If True, delete non-empty directories. If False, only delete empty ones.

        Returns:
            dict with success status, path, and message.
        """
        try:
            project_path = self.get_project_path(project_id)
            full_path = self._validate_path(project_path, dir_path)

            # Prevent deleting the project root
            project_root = os.path.realpath(project_path)
            if full_path == project_root:
                raise ValidationError("Cannot delete the project root directory")

            if not os.path.exists(full_path):
                raise NotFound(f"Directory not found: {dir_path}")

            if not os.path.isdir(full_path):
                raise ValidationError(f"Path is not a directory: {dir_path}")

            if recursive:
                shutil.rmtree(full_path)
            else:
                # os.rmdir only removes empty directories
                os.rmdir(full_path)

            logger.info(f"Successfully deleted directory: {dir_path}")
            return {
                'success': True,
                'path': dir_path,
                'message': f'Directory {dir_path} deleted successfully'
            }
        except OSError as e:
            if "not empty" in str(e).lower() or e.errno == 39:
                raise ValidationError(
                    f"Directory {dir_path} is not empty. Use recursive=true to delete non-empty directories."
                )
            raise
        except Exception as e:
            logger.error(f"Error deleting directory: {str(e)}")
            raise
