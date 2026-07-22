"""
Version Control Service for managing git-based version history.

This service handles git operations for project versioning, including:
- Listing commit history
- Resetting to previous versions
- Creating new commits on file changes
"""

import contextlib
import fcntl
import logging
import os
import shutil
import subprocess
import datetime
import time
from django.shortcuts import get_object_or_404
from apps.Imagi.ProjectManager.models import Project as PMProject

logger = logging.getLogger(__name__)


class MergeConflict(Exception):
    """A task branch could not be merged into the canonical tree cleanly.

    Raised after the conflicted merge has been aborted, so the canonical
    tree is left untouched. The API maps this to a 409 merge_conflict.
    """


class StaleForkPoint(Exception):
    """The canonical tree was restored to before this task's fork point.

    Merging the task branch would resurrect the history the restore
    removed (the branch's ancestry contains the pre-restore commits), so
    the merge is refused before touching the canonical tree. The API maps
    this to a 409 stale_base.
    """


def task_worktree_path(project_path: str, conversation_id: int) -> str:
    """Directory of a task conversation's git worktree.

    A SIBLING of the project directory, never inside it: the canonical
    tree's file walks, `git add .`, and the preview servers must never see
    another task's in-progress variant.
    """
    return f"{project_path.rstrip(os.sep)}--wt-{conversation_id}"


def task_branch(conversation_id: int) -> str:
    """Branch a task conversation's worktree has checked out."""
    return f"task/{conversation_id}"


def task_base_ref(conversation_id: int) -> str:
    """Git ref recording the canonical commit a task branch forked from.

    Stored in the repo itself (not the database) so merge_task_worktree can
    detect a canonical restore-to-before-the-fork without extra plumbing;
    absent for worktrees created before this ref existed, in which case the
    merge falls back to the plain behaviour.
    """
    return f"refs/imagi/task-base/{conversation_id}"


@contextlib.contextmanager
def canonical_repo_lock(project_path):
    """Serialize canonical-repo git mutations for one project.

    An exclusive flock on the project's .git directory: two near-simultaneous
    task dispatches (or a dispatch racing a merge) would otherwise collide on
    .git/index.lock and fail nondeterministically. When the repo does not
    exist yet there is nothing to contend on, so the lock is skipped.
    """
    git_dir = os.path.join(project_path, '.git')
    fd = None
    try:
        if os.path.isdir(git_dir):
            try:
                fd = os.open(git_dir, os.O_RDONLY)
                fcntl.flock(fd, fcntl.LOCK_EX)
            except OSError as e:  # pragma: no cover - defensive
                logger.warning(f"Could not lock repo at {git_dir}: {e}")
                if fd is not None:
                    os.close(fd)
                    fd = None
        yield
    finally:
        if fd is not None:
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
            except OSError:  # pragma: no cover - defensive
                pass
            os.close(fd)


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

            # Check if git repository already exists. Existence, not isdir:
            # in a linked worktree '.git' is a FILE pointing at the main
            # repo, and re-initing there would nest a repo inside it.
            if os.path.exists(git_dir):
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
    
    def reset_to_version(self, user, project_id, commit_hash, tree_path=None):
        """
        Reset the project to a specific version (commit).

        Args:
            user: The user making the request
            project_id (int): The ID of the project
            commit_hash (str): The hash of the commit to reset to
            tree_path (str): Working tree to reset (a task's worktree);
                defaults to the canonical project tree

        Returns:
            dict: Result of the operation containing success status and message
        """
        try:
            project = get_object_or_404(PMProject, id=project_id, user=user)

            target_path = tree_path or project.project_path
            if not target_path or not os.path.exists(target_path):
                return {'success': False, 'message': 'Project path does not exist'}

            # Check if the commit exists
            check_result = subprocess.run(
                ['git', 'rev-parse', '--verify', commit_hash],
                cwd=target_path,
                capture_output=True,
                text=True
            )

            if check_result.returncode != 0:
                return {'success': False, 'message': f"Invalid commit hash: {commit_hash}"}

            # Reset to the specified commit
            reset_result = subprocess.run(
                ['git', 'reset', '--hard', commit_hash],
                cwd=target_path,
                capture_output=True,
                text=True
            )

            if reset_result.returncode != 0:
                return {'success': False, 'message': f"Error resetting to commit {commit_hash}: {reset_result.stderr}"}

            # The reset rewrote the working copy wholesale — bring the
            # database copy of the project files back in sync with disk.
            # Canonical tree only: the mirror tracks canonical content, so a
            # task-worktree reset must never write its variant files into it.
            if target_path == project.project_path:
                try:
                    from .project_files_service import import_project_from_disk
                    import_project_from_disk(project)
                except Exception as sync_error:
                    logger.error(f"Project reset succeeded but database re-sync failed: {sync_error}")

            return {'success': True, 'message': f'Successfully reset project to version {commit_hash}'}

        except Exception as e:
            return {'success': False, 'message': f"Error resetting to version: {str(e)}"}
    
    def ensure_checkpoint(self, project_path, message=None):
        """
        Return a commit hash representing the working tree's current state.

        If the tree is dirty the changes are committed first (so the
        checkpoint really captures what is on disk right now); if it is
        clean the existing HEAD already is that state. Used to stamp each
        user message with the project state it started from, so the
        workspace can offer per-message restore points.

        Returns:
            dict: {'success': bool, 'commit_hash': str | None, 'message': str}
        """
        try:
            commit_result = self.commit_changes(
                project_path,
                message or 'Checkpoint before agent run'
            )
            if not commit_result.get('success'):
                return commit_result
            if commit_result.get('commit_hash'):
                return commit_result

            # Nothing to commit — the checkpoint is the current HEAD.
            hash_result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=project_path,
                capture_output=True,
                text=True
            )
            if hash_result.returncode != 0:
                # A repo with no commits yet (fresh init): create an empty
                # baseline commit so there is something to restore to.
                subprocess.run(
                    ['git', 'commit', '--allow-empty', '-m', 'Initial checkpoint'],
                    cwd=project_path, capture_output=True, text=True, check=True
                )
                hash_result = subprocess.run(
                    ['git', 'rev-parse', 'HEAD'],
                    cwd=project_path, capture_output=True, text=True, check=True
                )
            return {
                'success': True,
                'commit_hash': hash_result.stdout.strip(),
                'message': 'Checkpoint at current HEAD'
            }
        except subprocess.CalledProcessError as e:
            return {'success': False, 'commit_hash': None, 'message': f"Error creating checkpoint: {e.stderr}"}
        except Exception as e:
            return {'success': False, 'commit_hash': None, 'message': f"Error creating checkpoint: {str(e)}"}

    # ------------------------------------------------------------------
    # Per-task worktrees (one isolated checkout per task conversation)
    # ------------------------------------------------------------------

    def create_task_worktree(self, project_path, conversation_id, snapshot_pending=True):
        """Create (or reuse) the git worktree a task conversation runs in.

        The worktree lives beside the project directory and checks out
        branch task/<id> forked from the canonical HEAD, so parallel tasks
        each edit their own tree and merge back explicitly on accept.

        Args:
            snapshot_pending: When True (the default), pending canonical
                changes are committed first so the task forks from what is
                on disk right now. Callers pass False while a canonical-tree
                run is live: committing its half-written edits would bake a
                broken intermediate state into a permanent canonical commit,
                so the task forks from the last committed HEAD instead.

        Returns:
            dict: {'success': bool, 'worktree_path': str | None, 'message': str}
        """
        try:
            worktree_path = task_worktree_path(project_path, conversation_id)
            branch = task_branch(conversation_id)

            if os.path.isdir(worktree_path):
                return {
                    'success': True,
                    'worktree_path': worktree_path,
                    'message': 'Task worktree already exists',
                }

            # Serialized per project: parallel dispatches (the best-of-N
            # form fires several without awaiting) would otherwise race on
            # .git/index.lock.
            with canonical_repo_lock(project_path):
                # The branch forks from HEAD, so make sure one exists.
                head_exists = subprocess.run(
                    ['git', 'rev-parse', '--verify', '--quiet', 'HEAD'],
                    cwd=project_path, capture_output=True, text=True
                ).returncode == 0
                if snapshot_pending or not head_exists:
                    checkpoint = self.ensure_checkpoint(
                        project_path, f'Checkpoint before task {conversation_id}'
                    )
                    if not checkpoint.get('success'):
                        return {
                            'success': False,
                            'worktree_path': None,
                            'message': checkpoint.get('message', 'Could not checkpoint the project'),
                        }

                # Drop stale bookkeeping from a worktree directory that was
                # deleted without `git worktree remove`.
                subprocess.run(
                    ['git', 'worktree', 'prune'],
                    cwd=project_path, capture_output=True, text=True
                )

                branch_exists = subprocess.run(
                    ['git', 'rev-parse', '--verify', f'refs/heads/{branch}'],
                    cwd=project_path, capture_output=True, text=True
                ).returncode == 0
                if branch_exists:
                    cmd = ['git', 'worktree', 'add', worktree_path, branch]
                else:
                    cmd = ['git', 'worktree', 'add', '-b', branch, worktree_path]

                result = subprocess.run(
                    cmd, cwd=project_path, capture_output=True, text=True
                )
                if result.returncode != 0:
                    return {
                        'success': False,
                        'worktree_path': None,
                        'message': f"Error creating task worktree: {result.stderr}",
                    }

                # Record the fork point for a freshly-created branch, so an
                # accept can detect a canonical restore to before it. A
                # pre-existing branch keeps its original base ref (or none,
                # for branches created before the ref existed).
                if not branch_exists:
                    subprocess.run(
                        ['git', 'update-ref', task_base_ref(conversation_id), 'HEAD'],
                        cwd=project_path, capture_output=True, text=True
                    )

            return {
                'success': True,
                'worktree_path': worktree_path,
                'message': 'Task worktree created',
            }
        except Exception as e:
            return {
                'success': False,
                'worktree_path': None,
                'message': f"Error creating task worktree: {str(e)}",
            }

    def remove_task_worktree(self, project_path, conversation_id):
        """Remove a task conversation's worktree and branch.

        Tolerates pieces that are already gone (a manually deleted
        directory, a pruned branch, a project directory that was removed
        first) — cleanup must be safe to repeat.
        """
        worktree_path = task_worktree_path(project_path, conversation_id)
        branch = task_branch(conversation_id)
        try:
            if os.path.isdir(project_path):
                with canonical_repo_lock(project_path):
                    subprocess.run(
                        ['git', 'worktree', 'remove', '--force', worktree_path],
                        cwd=project_path, capture_output=True, text=True
                    )
                    if os.path.isdir(worktree_path):
                        shutil.rmtree(worktree_path, ignore_errors=True)
                    subprocess.run(
                        ['git', 'branch', '-D', branch],
                        cwd=project_path, capture_output=True, text=True
                    )
                    subprocess.run(
                        ['git', 'update-ref', '-d', task_base_ref(conversation_id)],
                        cwd=project_path, capture_output=True, text=True
                    )
                    subprocess.run(
                        ['git', 'worktree', 'prune'],
                        cwd=project_path, capture_output=True, text=True
                    )
            if os.path.isdir(worktree_path):
                shutil.rmtree(worktree_path, ignore_errors=True)
            return {'success': True, 'message': 'Task worktree removed'}
        except Exception as e:
            return {'success': False, 'message': f"Error removing task worktree: {str(e)}"}

    def merge_task_worktree(self, project_path, conversation_id):
        """Merge a task's branch back into the canonical tree.

        Commits pending changes on both sides first (the same auto-commit
        style the workspace uses everywhere), then merges task/<id> into
        the canonical branch. On conflict the merge is aborted — leaving
        the canonical tree untouched — and MergeConflict is raised. If the
        canonical tree was restored to before the task's fork point while
        the task was pending, StaleForkPoint is raised before anything is
        touched: merging would silently resurrect the restored-away history.

        Returns:
            dict: {'success': bool, 'message': str, 'commit_hash': str | None}
        """
        worktree_path = task_worktree_path(project_path, conversation_id)
        branch = task_branch(conversation_id)

        if not os.path.isdir(worktree_path):
            return {'success': False, 'message': 'Task worktree does not exist'}

        # Commit whatever the task run left uncommitted inside its worktree,
        # so the merge carries the tree the user actually reviewed.
        worktree_commit = self.commit_changes(
            worktree_path, f'Task {conversation_id} changes'
        )
        if not worktree_commit.get('success'):
            return {
                'success': False,
                'message': worktree_commit.get('message', 'Could not commit task changes'),
            }

        with canonical_repo_lock(project_path):
            # A restore/reset while the task was pending moved canonical HEAD
            # to before the fork point; merging the branch (whose ancestry
            # contains the undone commits) would re-apply them wholesale.
            base = subprocess.run(
                ['git', 'rev-parse', '--verify', '--quiet', task_base_ref(conversation_id)],
                cwd=project_path, capture_output=True, text=True
            )
            if base.returncode == 0:
                fork_point = base.stdout.strip()
                ancestor = subprocess.run(
                    ['git', 'merge-base', '--is-ancestor', fork_point, 'HEAD'],
                    cwd=project_path, capture_output=True, text=True
                )
                if ancestor.returncode == 1:
                    raise StaleForkPoint(
                        'The project was restored to an earlier version after '
                        'this draft was made, so accepting it would undo that '
                        'restore.'
                    )

            # And any pending canonical edits, so the merge target is clean.
            canonical_commit = self.commit_changes(
                project_path, f'Checkpoint before merging task {conversation_id}'
            )
            if not canonical_commit.get('success'):
                return {
                    'success': False,
                    'message': canonical_commit.get('message', 'Could not commit canonical changes'),
                }

            merge = subprocess.run(
                ['git', 'merge', '--no-edit', branch],
                cwd=project_path, capture_output=True, text=True
            )
            if merge.returncode != 0:
                subprocess.run(
                    ['git', 'merge', '--abort'],
                    cwd=project_path, capture_output=True, text=True
                )
                detail = (merge.stdout or '').strip() or (merge.stderr or '').strip()
                raise MergeConflict(
                    detail or f'Task {conversation_id} conflicts with the current project state'
                )

            hash_result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=project_path, capture_output=True, text=True
            )
        return {
            'success': True,
            'message': f'Task {conversation_id} merged',
            'commit_hash': hash_result.stdout.strip() if hash_result.returncode == 0 else None,
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