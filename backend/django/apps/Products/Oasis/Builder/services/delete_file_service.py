"""
Service for deleting project files.
"""

import os
import logging
from rest_framework.exceptions import ValidationError, NotFound
from apps.Products.Oasis.ProjectManager.models import Project

logger = logging.getLogger(__name__)

class DeleteFileService:
    def __init__(self, user=None, project=None):
        """
        Initialize the delete file service with either a user or a project.
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
            raise ValidationError("DeleteFileService initialized without user")
            
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
    
    def delete_file(self, file_path, project_id=None):
        """Delete a file."""
        try:
            project_path = self.get_project_path(project_id)
            full_path = os.path.join(project_path, file_path)
            
            if not os.path.exists(full_path) or not os.path.isfile(full_path):
                raise NotFound(f"File not found: {file_path}")
            
            # Delete the physical file
            os.remove(full_path)
            
            # Delete any database records associated with this file
            project = self.project
            if not project_id and not project:
                # If no project is specified, we can't delete DB records
                logger.warning(f"No project specified when deleting file {file_path}, skipping DB cleanup")
            else:
                # If there are any DB models tracking files, delete those records here
                try:
                    from apps.Products.Oasis.Builder.models import ProjectFile
                    if project_id and not project:
                        from apps.Products.Oasis.ProjectManager.models import Project
                        project = Project.objects.get(id=project_id)
                    
                    # Delete any ProjectFile records for this file
                    ProjectFile.objects.filter(
                        project=project, 
                        path=file_path
                    ).delete()
                    
                    logger.info(f"Deleted database records for file {file_path}")
                except Exception as db_error:
                    # Log but don't fail if DB cleanup has issues
                    logger.error(f"Error cleaning up database records for file {file_path}: {str(db_error)}")
            
            return {
                'success': True,
                'message': f'File {file_path} deleted successfully'
            }
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            raise

