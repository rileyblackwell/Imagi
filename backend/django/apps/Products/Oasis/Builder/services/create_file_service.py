"""
Service for creating files in projects.
"""

import os
import uuid
import logging
from datetime import datetime
from rest_framework.exceptions import ValidationError, NotFound
from apps.Products.Oasis.ProjectManager.models import Project

logger = logging.getLogger(__name__)

class CreateFileService:
    def __init__(self, user=None, project=None):
        """
        Initialize the file creation service with either a user or a project.
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
            raise ValidationError("CreateFileService initialized without user")
            
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
    
    def _is_dual_stack_project(self, project_path):
        """Check if this is a dual-stack project (has frontend/vuejs and backend/django directories)."""
        frontend_vuejs_path = os.path.join(project_path, 'frontend', 'vuejs')
        backend_django_path = os.path.join(project_path, 'backend', 'django')
        return os.path.exists(frontend_vuejs_path) and os.path.exists(backend_django_path)
    
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
    
    def create_file(self, file_data, project_id=None):
        """Create a new file."""
        try:
            # Get the project path
            project_path = self.get_project_path(project_id)
            
            # Check if this is a dual-stack project
            is_dual_stack = self._is_dual_stack_project(project_path)
            
            # Extract file data
            if isinstance(file_data, dict):
                # Handle new format with detailed file info
                name = file_data.get('name', '')
                content = file_data.get('content', '')
                file_type = file_data.get('type', '')
                
                if not name:
                    raise ValueError("File name is required")
                
                # Check if this is a relative path or just a filename
                if '/' in name:
                    # This is a relative path - use as is
                    file_path = name
                else:
                    # Determine directory based on file type and project structure
                    if not any(name.startswith(prefix) for prefix in ['templates/', 'static/', 'backend/', 'frontend/']):
                        if file_type == 'html':
                            if is_dual_stack:
                                file_path = f"backend/django/templates/{name}"
                            else:
                                file_path = f"templates/{name}"
                        elif file_type == 'css':
                            if is_dual_stack:
                                file_path = f"backend/django/static/css/{name}"
                            else:
                                file_path = f"static/css/{name}"
                        elif file_type == 'javascript':
                            if is_dual_stack:
                                file_path = f"backend/django/static/js/{name}"
                            else:
                                file_path = f"static/{name}"
                        elif file_type in ['vue', 'typescript']:
                            # For Vue.js files, if no path prefix, assume frontend/vuejs/src/
                            if is_dual_stack:
                                file_path = f"frontend/vuejs/src/{name}"
                            else:
                                file_path = name
                        else:
                            file_path = name
                    else:
                        file_path = name
                    
                    # Ensure CSS files are in the correct location
                    if file_type == 'css':
                        if is_dual_stack and not file_path.startswith('backend/django/static/css/'):
                            file_name = os.path.basename(file_path)
                            file_path = f"backend/django/static/css/{file_name}"
                        elif not is_dual_stack and not file_path.startswith('static/css/'):
                            file_name = os.path.basename(file_path)
                            file_path = f"static/css/{file_name}"
            
            # Create full file path
            full_file_path = os.path.join(project_path, file_path)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(full_file_path)), exist_ok=True)
            
            # Write content to file with UTF-8 encoding
            with open(full_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Get file stats
            stats = os.stat(full_file_path)
            
            # Generate a unique ID for the file
            file_id = str(uuid.uuid4())
            
            # Determine if this is an HTML template file
            is_template = file_type == 'html' or (file_path.endswith('.html') and ('templates/' in file_path))
            
            logger.info(f"Successfully created file: {file_path}")
            
            return {
                'id': file_id,
                'name': os.path.basename(file_path),
                'path': file_path,
                'content': content,
                'type': file_type or self._get_file_type(file_path),
                'lastModified': datetime.fromtimestamp(stats.st_mtime).isoformat(),
                'is_template': is_template
            }
        except Exception as e:
            logger.error(f"Error creating file: {str(e)}")
            raise

