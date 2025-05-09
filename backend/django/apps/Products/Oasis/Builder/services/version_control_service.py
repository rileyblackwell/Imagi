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
from pathlib import Path
from django.shortcuts import get_object_or_404
from apps.Products.Oasis.ProjectManager.models import Project as PMProject
import time

logger = logging.getLogger(__name__)

class VersionControlService:
    """
    Service for managing git-based version control for projects.
    """
    
    def __init__(self, project=None):
        self.project = project
        
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
                logger.info(f"Git repository already exists at {project_path}")
                return True
                
            # Initialize git repository
            result = subprocess.run(
                ['git', 'init'],
                cwd=project_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Set git config for the repository
            subprocess.run(
                ['git', 'config', 'user.name', 'Imagi Oasis'],
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
            
            # Add all files and create initial commit
            subprocess.run(
                ['git', 'add', '.'],
                cwd=project_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            subprocess.run(
                ['git', 'commit', '-m', 'Initial commit'],
                cwd=project_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info(f"Successfully initialized git repository at {project_path}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error initializing git repository: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Error initializing git repository: {str(e)}")
            return False
    
    def commit_changes(self, project_path, message=None):
        """
        Commit all current changes to the git repository.
        
        Args:
            project_path (str): Path to the project directory
            message (str): Commit message, defaults to timestamped message
            
        Returns:
            dict: Result of the operation containing success status and commit hash
        """
        try:
            # Check if there are any changes to commit
            status = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=project_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            if not status.stdout.strip():
                return {
                    'success': False,
                    'message': 'No changes to commit detected'
                }
            
            # Stage all changes
            add_result = subprocess.run(
                ['git', 'add', '.'],
                cwd=project_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Create commit message if not provided
            if not message:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                message = f"Changes made at {timestamp}"
            
            # Commit changes
            commit_result = subprocess.run(
                ['git', 'commit', '-m', message],
                cwd=project_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Get the commit hash
            hash_result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=project_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            commit_hash = hash_result.stdout.strip()
            
            return {
                'success': True,
                'message': 'Successfully committed changes',
                'commit_hash': commit_hash
            }
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error committing changes: {e.stderr}")
            return {
                'success': False,
                'message': f"Error committing changes: {e.stderr}"
            }
        except Exception as e:
            logger.error(f"Error committing changes: {str(e)}")
            return {
                'success': False,
                'message': f"Error committing changes: {str(e)}"
            }
    
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
            # Get the project
            project = get_object_or_404(PMProject, id=project_id, user=user)
            
            # Ensure the project path exists
            if not project.project_path or not os.path.exists(project.project_path):
                return {
                    'success': False,
                    'message': 'Project path does not exist'
                }
            
            # Ensure git repo is initialized
            git_dir = os.path.join(project.project_path, '.git')
            if not os.path.exists(git_dir) or not os.path.isdir(git_dir):
                self.initialize_repo(project.project_path)
            
            # Get commit history
            result = subprocess.run(
                ['git', 'log', '--pretty=format:%H|%s|%an|%ad|%ar', '--date=iso'],
                cwd=project.project_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                # If error is due to no commits, initialize repo
                if "fatal: your current branch 'master' does not have any commits yet" in result.stderr:
                    self.initialize_repo(project.project_path)
                    return {
                        'success': True,
                        'commits': []
                    }
                return {
                    'success': False,
                    'message': f"Error getting commit history: {result.stderr}"
                }
            
            # Parse commit history
            commits = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                parts = line.split('|')
                if len(parts) >= 5:
                    commit = {
                        'hash': parts[0],
                        'message': parts[1],
                        'author': parts[2],
                        'date': parts[3],
                        'relative_date': parts[4]
                    }
                    commits.append(commit)
            
            return {
                'success': True,
                'commits': commits
            }
            
        except Exception as e:
            logger.error(f"Error getting commit history: {str(e)}")
            return {
                'success': False,
                'message': f"Error getting commit history: {str(e)}"
            }
    
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
            # Get the project
            project = get_object_or_404(PMProject, id=project_id, user=user)
            
            # Ensure the project path exists
            if not project.project_path or not os.path.exists(project.project_path):
                return {
                    'success': False,
                    'message': 'Project path does not exist'
                }
            
            # Check if the commit exists
            check_result = subprocess.run(
                ['git', 'rev-parse', '--verify', commit_hash],
                cwd=project.project_path,
                capture_output=True,
                text=True
            )
            
            if check_result.returncode != 0:
                return {
                    'success': False,
                    'message': f"Invalid commit hash: {commit_hash}"
                }
            
            # Reset to the specified commit
            reset_result = subprocess.run(
                ['git', 'reset', '--hard', commit_hash],
                cwd=project.project_path,
                capture_output=True,
                text=True
            )
            
            if reset_result.returncode != 0:
                return {
                    'success': False,
                    'message': f"Error resetting to commit {commit_hash}: {reset_result.stderr}"
                }
            
            return {
                'success': True,
                'message': f'Successfully reset project to version {commit_hash}'
            }
            
        except Exception as e:
            logger.error(f"Error resetting to version: {str(e)}")
            return {
                'success': False,
                'message': f"Error resetting to version: {str(e)}"
            }
    
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
            # Get the project
            project = get_object_or_404(PMProject, id=project_id, user=user)
            
            # Ensure the project path exists
            if not project.project_path or not os.path.exists(project.project_path):
                return {
                    'success': False,
                    'message': 'Project path does not exist'
                }
            
            # Ensure git repo is initialized
            git_dir = os.path.join(project.project_path, '.git')
            if not os.path.exists(git_dir) or not os.path.isdir(git_dir):
                self.initialize_repo(project.project_path)
            
            # Add a small delay to ensure file system operations are complete
            # This helps especially with the initial commit when files are just being created
            time.sleep(0.5)
            
            # Sync the file system
            try:
                subprocess.run(
                    ['sync'],
                    check=True,
                    capture_output=True,
                    text=True
                )
                logger.info(f"File system synced before commit for project {project_id}")
            except Exception as e:
                logger.warning(f"Could not sync file system: {str(e)}")
            
            # Create commit message
            if not description:
                description = f"Updated {file_path}"
            
            message = f"{description} - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Commit changes
            commit_result = self.commit_changes(project.project_path, message)
            
            return commit_result
            
        except Exception as e:
            logger.error(f"Error creating version after file change: {str(e)}")
            return {
                'success': False,
                'message': f"Error creating version after file change: {str(e)}"
            } 