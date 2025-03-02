from typing import List, Optional
from rest_framework.exceptions import ValidationError, NotFound
from ..models import Project
from ..services.project_service import ProjectGenerationService
import os
import uuid
from datetime import datetime

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
            
        # Get project directory path
        project_name = project.name
        timestamp = project.created_at.strftime("%Y%m%d%H%M%S")
        sanitized_name = self.project_service.generation_service._sanitize_project_name(project_name)
        unique_name = f"{sanitized_name}_{timestamp}"
        project_path = os.path.join(self.project_service.generation_service.base_directory, unique_name)
        
        # Check if directory exists
        if not os.path.exists(project_path):
            return []
            
        # Get list of files
        files = []
        for root, _, filenames in os.walk(project_path):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                rel_path = os.path.relpath(file_path, project_path)
                
                # Determine file type based on extension
                _, ext = os.path.splitext(filename)
                file_type = 'text'  # Default type
                
                if ext == '.py':
                    file_type = 'python'
                elif ext == '.html':
                    file_type = 'html'
                elif ext == '.css':
                    file_type = 'css'
                elif ext == '.js':
                    file_type = 'javascript'
                elif ext == '.ts':
                    file_type = 'typescript'
                elif ext == '.vue':
                    file_type = 'vue'
                
                # Get file stats
                stats = os.stat(file_path)
                
                # Generate a unique ID for the file
                file_id = str(uuid.uuid4())
                
                files.append({
                    'id': file_id,
                    'name': filename,
                    'path': rel_path,
                    'type': file_type,
                    'lastModified': datetime.fromtimestamp(stats.st_mtime).isoformat()
                })
                
        return files

    def get_file(self, project_id, file_path):
        project = self.project_service.get_project(project_id)
        if not project:
            raise NotFound('Project not found')
            
        # Get project directory path
        project_name = project.name
        timestamp = project.created_at.strftime("%Y%m%d%H%M%S")
        sanitized_name = self.project_service.generation_service._sanitize_project_name(project_name)
        unique_name = f"{sanitized_name}_{timestamp}"
        project_path = os.path.join(self.project_service.generation_service.base_directory, unique_name)
        
        # Create full file path
        full_file_path = os.path.join(project_path, file_path)
        
        # Check if file exists
        if not os.path.exists(full_file_path) or not os.path.isfile(full_file_path):
            raise NotFound(f"File not found: {file_path}")
            
        # Read file content
        try:
            with open(full_file_path, 'r') as f:
                content = f.read()
        except Exception as e:
            raise ValidationError(f"Failed to read file: {str(e)}")
            
        # Determine file type based on extension
        _, ext = os.path.splitext(file_path)
        file_type = 'text'  # Default type
        
        if ext == '.py':
            file_type = 'python'
        elif ext == '.html':
            file_type = 'html'
        elif ext == '.css':
            file_type = 'css'
        elif ext == '.js':
            file_type = 'javascript'
        elif ext == '.ts':
            file_type = 'typescript'
        elif ext == '.vue':
            file_type = 'vue'
            
        # Get file stats
        stats = os.stat(full_file_path)
        
        # Generate a unique ID for the file
        file_id = str(uuid.uuid4())
        
        return {
            'id': file_id,
            'name': os.path.basename(file_path),
            'path': file_path,
            'content': content,
            'type': file_type,
            'lastModified': datetime.fromtimestamp(stats.st_mtime).isoformat()
        }

    def create_file(self, project_id, file_data):
        project = self.project_service.get_project(project_id)
        if not project:
            raise NotFound('Project not found')
            
        # Get project directory path
        project_name = project.name
        timestamp = project.created_at.strftime("%Y%m%d%H%M%S")
        sanitized_name = self.project_service.generation_service._sanitize_project_name(project_name)
        unique_name = f"{sanitized_name}_{timestamp}"
        project_path = os.path.join(self.project_service.generation_service.base_directory, unique_name)
        
        # Validate file data
        name = file_data.get('name', '')
        file_type = file_data.get('type', '')
        content = file_data.get('content', '')
        
        if not name:
            raise ValidationError('File name is required')
        
        # Determine file path based on type
        if file_type == 'python':
            file_path = f"{name}.py"
        elif file_type == 'html':
            file_path = f"{name}.html"
        elif file_type == 'css':
            file_path = f"{name}.css"
        elif file_type == 'js':
            file_path = f"{name}.js"
        elif file_type == 'json':
            file_path = f"{name}.json"
        elif file_type == 'md':
            file_path = f"{name}.md"
        else:
            file_path = name
        
        # Create full file path
        full_file_path = os.path.join(project_path, file_path)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(full_file_path)), exist_ok=True)
        
        # Write content to file
        try:
            with open(full_file_path, 'w') as f:
                f.write(content)
        except Exception as e:
            raise ValidationError(f"Failed to create file: {str(e)}")
        
        # Generate a unique ID for the file
        file_id = str(uuid.uuid4())
        
        # Return file information
        return {
            'id': file_id,
            'name': os.path.basename(file_path),
            'path': file_path,
            'content': content,
            'type': file_type,
            'lastModified': datetime.now().isoformat()
        }

    def update_file(self, project_id, file_path, file_data):
        project = self.project_service.get_project(project_id)
        if not project:
            raise NotFound('Project not found')
            
        # Get project directory path
        project_name = project.name
        timestamp = project.created_at.strftime("%Y%m%d%H%M%S")
        sanitized_name = self.project_service.generation_service._sanitize_project_name(project_name)
        unique_name = f"{sanitized_name}_{timestamp}"
        project_path = os.path.join(self.project_service.generation_service.base_directory, unique_name)
        
        # Create full file path
        full_file_path = os.path.join(project_path, file_path)
        
        # Check if file exists
        if not os.path.exists(full_file_path) or not os.path.isfile(full_file_path):
            raise NotFound(f"File not found: {file_path}")
            
        # Get content from file_data
        content = file_data.get('content', '')
        
        # Write content to file
        try:
            with open(full_file_path, 'w') as f:
                f.write(content)
        except Exception as e:
            raise ValidationError(f"Failed to update file: {str(e)}")
            
        # Determine file type based on extension
        _, ext = os.path.splitext(file_path)
        file_type = 'text'  # Default type
        
        if ext == '.py':
            file_type = 'python'
        elif ext == '.html':
            file_type = 'html'
        elif ext == '.css':
            file_type = 'css'
        elif ext == '.js':
            file_type = 'javascript'
        elif ext == '.ts':
            file_type = 'typescript'
        elif ext == '.vue':
            file_type = 'vue'
            
        # Get file stats
        stats = os.stat(full_file_path)
        
        # Generate a unique ID for the file
        file_id = str(uuid.uuid4())
        
        return {
            'id': file_id,
            'name': os.path.basename(file_path),
            'path': file_path,
            'content': content,
            'type': file_type,
            'lastModified': datetime.fromtimestamp(stats.st_mtime).isoformat()
        }
