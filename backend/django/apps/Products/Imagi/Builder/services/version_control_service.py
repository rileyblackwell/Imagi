"""
Version Control Service for managing git-based version history.

This service handles git operations for project versioning, including:
- Listing commit history
- Resetting to previous versions
- Creating new commits on file changes
"""

import logging
import os
import subprocess
import datetime
import time
from django.shortcuts import get_object_or_404
from apps.Products.Imagi.ProjectManager.models import Project as PMProject

logger = logging.getLogger(__name__)

class VersionControlService:
    """
    Service for managing git-based version control for projects.
    """
    
    def __init__(self, project=None):
        self.project = project
        
    def _wait_for_file_system_sync(self, project_path, file_path=None, max_wait=5):
        """
        Wait for file system operations to complete and ensure files are visible to git.
        
        Args:
            project_path (str): Path to the project directory
            file_path (str): Specific file path to check (optional)
            max_wait (int): Maximum time to wait in seconds
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                # Force file system sync on Unix systems
                if hasattr(os, 'sync'):
                    os.sync()
                
                # If a specific file was mentioned, verify it exists
                if file_path and file_path != '/':
                    # Remove leading slash and check if file exists
                    clean_path = file_path.lstrip('/')
                    full_path = os.path.join(project_path, clean_path)
                    
                    if os.path.exists(full_path):
                        # File exists, check if git can see any changes
                        status_result = subprocess.run(
                            ['git', 'status', '--porcelain'],
                            cwd=project_path,
                            capture_output=True,
                            text=True
                        )
                        
                        if status_result.returncode == 0 and status_result.stdout.strip():
                            # Git can see changes, we're good to go
                            return True
                
                # For general sync or when no specific file is provided
                # Just ensure git status command works and wait a bit
                status_result = subprocess.run(
                    ['git', 'status', '--porcelain'],
                    cwd=project_path,
                    capture_output=True,
                    text=True
                )
                
                if status_result.returncode == 0:
                    # If there are changes or if we're not checking a specific file, we're good
                    if not file_path or file_path == '/' or status_result.stdout.strip():
                        time.sleep(0.1)  # Small additional buffer
                        return True
                
                # Wait a bit before checking again
                time.sleep(0.2)
                
            except Exception:
                # If anything fails, just wait a bit more
                time.sleep(0.2)
        
        # Return True after max wait time to avoid blocking forever
        return True
        
    def initialize_repo(self, project_path):
        """
        Initialize a git repository for the project if it doesn't exist.
        
        Args:
            project_path (str): Path to the project directory
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            git_dir = os.path.join(project_path, '.git')
            
            # Check if git repository already exists
            if os.path.exists(git_dir) and os.path.isdir(git_dir):
                return True
                
            # Initialize git repository
            subprocess.run(
                ['git', 'init'],
                cwd=project_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Set git config for the repository
            subprocess.run(
                ['git', 'config', 'user.name', 'Imagi'],
                cwd=project_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            subprocess.run(
                ['git', 'config', 'user.email', 'system@imagioasis.com'],
                cwd=project_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Create .gitignore file
            gitignore_path = os.path.join(project_path, '.gitignore')
            if not os.path.exists(gitignore_path):
                with open(gitignore_path, 'w') as f:
                    f.write("__pycache__/\n*.py[cod]\n*$py.class\n*.so\n.env\ndb.sqlite3\n")
            
            # Wait for file system to sync before initial commit
            self._wait_for_file_system_sync(project_path)
            
            # Add all files and create initial commit
            subprocess.run(['git', 'add', '.'], cwd=project_path, capture_output=True, text=True, check=True)
            subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=project_path, capture_output=True, text=True, check=True)
            
            return True
            
        except subprocess.CalledProcessError:
            return False
        except Exception:
            return False
    
    def commit_changes(self, project_path, message=None, file_path=None):
        """
        Commit all current changes to the git repository.
        
        Args:
            project_path (str): Path to the project directory
            message (str): Commit message, defaults to timestamped message
            file_path (str): Specific file that was changed (for sync verification)
            
        Returns:
            dict: Result of the operation containing success status and commit hash
        """
        try:
            # Ensure git repo exists
            git_dir = os.path.join(project_path, '.git')
            if not os.path.exists(git_dir):
                if not self.initialize_repo(project_path):
                    return {'success': False, 'message': 'Failed to initialize git repository'}
            
            # Wait for file system operations to complete
            self._wait_for_file_system_sync(project_path, file_path)
            
            # Check if there are any changes to commit
            status = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=project_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            if not status.stdout.strip():
                return {'success': True, 'message': 'No changes to commit', 'commit_hash': None}
            
            # Stage all changes and commit
            subprocess.run(['git', 'add', '.'], cwd=project_path, capture_output=True, text=True, check=True)
            
            # Create commit message if not provided
            if not message:
                message = f"Changes made at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            subprocess.run(['git', 'commit', '-m', message], cwd=project_path, capture_output=True, text=True, check=True)
            
            # Get the commit hash
            hash_result = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=project_path, capture_output=True, text=True, check=True)
            commit_hash = hash_result.stdout.strip()
            
            return {'success': True, 'message': 'Successfully committed changes', 'commit_hash': commit_hash}
            
        except subprocess.CalledProcessError as e:
            return {'success': False, 'message': f"Error committing changes: {e.stderr}"}
        except Exception as e:
            return {'success': False, 'message': f"Error committing changes: {str(e)}"}
    
    def get_commit_history(self, user, project_id):
        """
        Get the commit history for a project.
        
        Args:
            user: The user making the request
            project_id (int): The ID of the project
            
        Returns:
            dict: Result of the operation containing success status and commit history
        """
        try:
            project = get_object_or_404(PMProject, id=project_id, user=user)
            
            if not project.project_path or not os.path.exists(project.project_path):
                return {'success': False, 'message': 'Project path does not exist'}
            
            # Ensure git repo exists
            git_dir = os.path.join(project.project_path, '.git')
            if not os.path.exists(git_dir):
                if not self.initialize_repo(project.project_path):
                    return {'success': False, 'message': 'Failed to initialize git repository'}
                return {'success': True, 'commits': []}
            
            # Get commit history
            result = subprocess.run(
                ['git', 'log', '--pretty=format:%H|%s|%an|%ad|%ar', '--date=iso'],
                cwd=project.project_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                if "fatal: your current branch 'master' does not have any commits yet" in result.stderr:
                    return {'success': True, 'commits': []}
                return {'success': False, 'message': f"Error getting commit history: {result.stderr}"}
            
            # Parse commit history
            commits = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                parts = line.split('|')
                if len(parts) >= 5:
                    commits.append({
                        'hash': parts[0],
                        'message': parts[1],
                        'author': parts[2],
                        'date': parts[3],
                        'relative_date': parts[4]
                    })
            
            return {'success': True, 'commits': commits}
            
        except Exception as e:
            return {'success': False, 'message': f"Error getting commit history: {str(e)}"}
    
    def reset_to_version(self, user, project_id, commit_hash):
        """
        Reset the project to a specific version (commit).
        
        Args:
            user: The user making the request
            project_id (int): The ID of the project
            commit_hash (str): The hash of the commit to reset to
            
        Returns:
            dict: Result of the operation containing success status and message
        """
        try:
            project = get_object_or_404(PMProject, id=project_id, user=user)
            
            if not project.project_path or not os.path.exists(project.project_path):
                return {'success': False, 'message': 'Project path does not exist'}
            
            # Check if the commit exists
            check_result = subprocess.run(
                ['git', 'rev-parse', '--verify', commit_hash],
                cwd=project.project_path,
                capture_output=True,
                text=True
            )
            
            if check_result.returncode != 0:
                return {'success': False, 'message': f"Invalid commit hash: {commit_hash}"}
            
            # Reset to the specified commit
            reset_result = subprocess.run(
                ['git', 'reset', '--hard', commit_hash],
                cwd=project.project_path,
                capture_output=True,
                text=True
            )
            
            if reset_result.returncode != 0:
                return {'success': False, 'message': f"Error resetting to commit {commit_hash}: {reset_result.stderr}"}
            
            return {'success': True, 'message': f'Successfully reset project to version {commit_hash}'}
            
        except Exception as e:
            return {'success': False, 'message': f"Error resetting to version: {str(e)}"}
    
    def create_version_after_file_change(self, user, project_id, file_path, description=None):
        """
        Create a new commit after a file has been changed.
        
        Args:
            user: The user making the request
            project_id (int): The ID of the project
            file_path (str): The path of the file that was changed
            description (str): Optional description of the change
            
        Returns:
            dict: Result of the operation containing success status and commit hash
        """
        try:
            project = get_object_or_404(PMProject, id=project_id, user=user)
            
            if not project.project_path or not os.path.exists(project.project_path):
                return {'success': False, 'message': 'Project path does not exist'}
            
            # Create commit message
            if not description:
                description = f"Updated {file_path}" if file_path and file_path != '/' else "Project update"
            
            message = f"{description} - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Commit changes with file path for proper sync verification
            return self.commit_changes(project.project_path, message, file_path)
            
        except Exception as e:
            return {'success': False, 'message': f"Error creating version after file change: {str(e)}"} 