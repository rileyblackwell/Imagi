"""
Service for managing project files.
"""

import os
import uuid
import logging
from datetime import datetime
from rest_framework.exceptions import ValidationError, NotFound
from apps.Products.Oasis.ProjectManager.models import Project

logger = logging.getLogger(__name__)

class FileService:
    def __init__(self, user=None, project=None):
        """
        Initialize the file service with either a user or a project.
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
            raise ValidationError("FileService initialized without user")
            
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
    
    def list_files(self, project_id=None):
        """List all files in the project."""
        try:
            project_path = self.get_project_path(project_id)
            
            # Check if project path exists
            if not project_path or not os.path.exists(project_path):
                logger.error(f"Project path does not exist: {project_path}")
                return []
                
            files = []
            
            for root, _, filenames in os.walk(project_path):
                for filename in filenames:
                    full_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(full_path, project_path)
                    
                    # Skip hidden files and directories
                    if any(part.startswith('.') for part in rel_path.split(os.sep)):
                        continue
                    
                    # Only include HTML templates and CSS files
                    file_extension = os.path.splitext(filename)[1].lower()
                    if file_extension not in ['.html', '.css']:
                        continue
                        
                    # Skip files outside templates or static directories
                    if not ('templates' in rel_path or ('static' in rel_path and file_extension == '.css')):
                        continue
                    
                    # Get file stats
                    stats = os.stat(full_path)
                    
                    # Generate a unique ID for the file
                    file_id = str(uuid.uuid4())
                    
                    files.append({
                        'id': file_id,
                        'name': filename,
                        'path': rel_path,
                        'type': self._get_file_type(rel_path),
                        'size': os.path.getsize(full_path),
                        'lastModified': datetime.fromtimestamp(stats.st_mtime).isoformat()
                    })
            
            return sorted(files, key=lambda x: x['path'])
        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            raise
    
    def get_file_details(self, file_path, project_id=None):
        """Get details about a specific file."""
        try:
            project_path = self.get_project_path(project_id)
            full_path = os.path.join(project_path, file_path)
            
            if not os.path.exists(full_path) or not os.path.isfile(full_path):
                raise NotFound(f"File not found: {file_path}")
            
            # Get file stats
            stats = os.stat(full_path)
            
            # Generate a unique ID for the file
            file_id = str(uuid.uuid4())
            
            return {
                'id': file_id,
                'name': os.path.basename(file_path),
                'path': file_path,
                'type': self._get_file_type(file_path),
                'size': os.path.getsize(full_path),
                'lastModified': datetime.fromtimestamp(stats.st_mtime).isoformat(),
                'content': self.get_file_content(file_path, project_id)
            }
        except Exception as e:
            logger.error(f"Error getting file details: {str(e)}")
            raise
    
    def get_file_content(self, file_path, project_id=None):
        """Get the content of a file."""
        try:
            project_path = self.get_project_path(project_id)
            full_path = os.path.join(project_path, file_path)
            
            if not os.path.exists(full_path) or not os.path.isfile(full_path):
                raise NotFound(f"File not found: {file_path}")
            
            with open(full_path, 'r') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading file content: {str(e)}")
            raise
    
    def update_file(self, file_path, content, project_id=None, commit_message='Update file'):
        """Update the content of a file."""
        try:
            project_path = self.get_project_path(project_id)
            full_path = os.path.join(project_path, file_path)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(full_path)), exist_ok=True)
            
            # Write content to file
            with open(full_path, 'w') as f:
                f.write(content)
            
            # Get file stats
            stats = os.stat(full_path)
            
            # Generate a unique ID for the file
            file_id = str(uuid.uuid4())
            
            return {
                'id': file_id,
                'name': os.path.basename(file_path),
                'path': file_path,
                'content': content,
                'type': self._get_file_type(file_path),
                'lastModified': datetime.fromtimestamp(stats.st_mtime).isoformat(),
                'message': f'File {file_path} updated successfully'
            }
        except Exception as e:
            logger.error(f"Error updating file: {str(e)}")
            raise
    
    def create_file(self, file_data, project_id=None):
        """Create a new file."""
        try:
            project_path = self.get_project_path(project_id)
            
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
            elif file_type == 'javascript':
                file_path = f"{name}.js"
            elif file_type == 'json':
                file_path = f"{name}.json"
            elif file_type == 'markdown':
                file_path = f"{name}.md"
            else:
                file_path = name
            
            # Create full file path
            full_file_path = os.path.join(project_path, file_path)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(full_file_path)), exist_ok=True)
            
            # Write content to file
            with open(full_file_path, 'w') as f:
                f.write(content)
            
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
        except Exception as e:
            logger.error(f"Error creating file: {str(e)}")
            raise
    
    def delete_file(self, file_path, project_id=None):
        """Delete a file."""
        try:
            project_path = self.get_project_path(project_id)
            full_path = os.path.join(project_path, file_path)
            
            if not os.path.exists(full_path) or not os.path.isfile(full_path):
                raise NotFound(f"File not found: {file_path}")
            
            os.remove(full_path)
            
            return {
                'success': True,
                'message': f'File {file_path} deleted successfully'
            }
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            raise
    
    def _get_file_type(self, file_path):
        """Get the type of a file based on its extension."""
        ext = os.path.splitext(file_path)[1].lower()
        
        type_mapping = {
            '.html': 'html',
            '.css': 'css',
            '.js': 'javascript',
            '.json': 'json',
            '.py': 'python',
            '.md': 'markdown',
            '.txt': 'text',
            '.vue': 'vue',
            '.ts': 'typescript'
        }
        
        return type_mapping.get(ext, 'unknown') 