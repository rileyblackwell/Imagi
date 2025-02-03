"""
Service for managing project files.
"""

import os
import logging
from pathlib import Path
from django.conf import settings

logger = logging.getLogger(__name__)

class FileService:
    def __init__(self, project):
        self.project = project
        self.project_path = project.user_project.project_path
    
    def list_files(self):
        """List all files in the project."""
        try:
            files = []
            for root, _, filenames in os.walk(self.project_path):
                for filename in filenames:
                    full_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(full_path, self.project_path)
                    
                    # Skip hidden files and directories
                    if any(part.startswith('.') for part in rel_path.split(os.sep)):
                        continue
                    
                    files.append({
                        'path': rel_path,
                        'type': self._get_file_type(rel_path),
                        'size': os.path.getsize(full_path),
                        'modified': os.path.getmtime(full_path)
                    })
            
            return sorted(files, key=lambda x: x['path'])
        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            raise
    
    def get_file_details(self, file_path):
        """Get details about a specific file."""
        try:
            full_path = os.path.join(self.project_path, file_path)
            if not os.path.exists(full_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            return {
                'path': file_path,
                'type': self._get_file_type(file_path),
                'size': os.path.getsize(full_path),
                'modified': os.path.getmtime(full_path),
                'content': self.get_file_content(file_path)
            }
        except Exception as e:
            logger.error(f"Error getting file details: {str(e)}")
            raise
    
    def get_file_content(self, file_path):
        """Get the content of a file."""
        try:
            full_path = os.path.join(self.project_path, file_path)
            if not os.path.exists(full_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            with open(full_path, 'r') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading file content: {str(e)}")
            raise
    
    def update_file(self, file_path, content, commit_message='Update file'):
        """Update the content of a file."""
        try:
            full_path = os.path.join(self.project_path, file_path)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # Write the content
            with open(full_path, 'w') as f:
                f.write(content)
            
            # TODO: Add git commit functionality
            
            return {
                'success': True,
                'message': f'File {file_path} updated successfully'
            }
        except Exception as e:
            logger.error(f"Error updating file: {str(e)}")
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
            '.txt': 'text'
        }
        
        return type_mapping.get(ext, 'unknown') 