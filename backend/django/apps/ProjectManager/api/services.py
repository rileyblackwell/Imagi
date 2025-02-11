from typing import List, Optional
from rest_framework.exceptions import ValidationError, NotFound
from ..models import Project
from ..services.project_service import ProjectGenerationService

class ProjectService:
    def __init__(self, user):
        self.user = user
        self.generation_service = ProjectGenerationService(user)

    def get_active_projects(self) -> List[Project]:
        """Get all active projects for the current user."""
        return Project.objects.filter(user=self.user, is_active=True)

    def create_project(self, project: Project) -> Project:
        """Generate project files for a newly created project."""
        try:
            self.generation_service.create_project(project.name)
            return project
        except Exception as e:
            project.delete()
            raise ValidationError(f"Failed to generate project files: {str(e)}")

    def get_project(self, project_id: int) -> Optional[Project]:
        """Get a specific project by ID."""
        return self.get_active_projects().filter(id=project_id).first()

    def delete_project(self, project: Project) -> None:
        """Delete a project and its associated files."""
        try:
            self.generation_service.delete_project(project.name)
            project.delete()
        except Exception as e:
            raise ValidationError(f"Failed to delete project: {str(e)}")

class FileService:
    def __init__(self, user):
        self.user = user
        self.project_service = ProjectService(user)

    def get_project_files(self, project_id):
        project = self.project_service.get_project(project_id)
        if not project:
            raise NotFound('Project not found')
            
        # Implement file listing logic here
        return []  # Placeholder - implement actual file listing

    def get_file(self, project_id, file_path):
        project = self.project_service.get_project(project_id)
        if not project:
            raise NotFound('Project not found')
            
        # Implement file retrieval logic here
        return None  # Placeholder - implement actual file retrieval

    def create_file(self, project_id, file_data):
        project = self.project_service.get_project(project_id)
        if not project:
            raise NotFound('Project not found')
            
        # Implement file creation logic here
        return None  # Placeholder - implement actual file creation

    def update_file(self, project_id, file_path, file_data):
        project = self.project_service.get_project(project_id)
        if not project:
            raise NotFound('Project not found')
            
        # Implement file update logic here
        return None  # Placeholder - implement actual file update
