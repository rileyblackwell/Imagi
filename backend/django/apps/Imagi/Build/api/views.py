"""
API views for the Build app.

Contains the builder workspace endpoints (files, directories, preview,
version control, app creation, layout) and the agent endpoints (the
Imagi agent plus conversation CRUD), merged from the former Builder
and Agents sub-apps.
"""

import json
import logging
import traceback
from datetime import timedelta
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from asgiref.sync import sync_to_async
from django.db import IntegrityError, transaction
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from ..models import AgentCheckIn, AgentConversation, AgentMessage, CANONICAL_TREE_KINDS
from ..services.base_agent import ImagiAgentService, DEFAULT_MODEL
from ..services.usage_limits import check_usage_allowed
from ..services.create_file_service import CreateFileService
from ..services.view_file_service import ViewFileService
from ..services.delete_file_service import DeleteFileService
from ..services.models_service import get_model_by_id
from ..services.browser_preview_service import (
    BrowserNotRunning,
    BrowserPreviewError,
    BrowserPreviewService,
)
from apps.Imagi.ProjectManager.models import Project as PMProject
from rest_framework.exceptions import NotFound, APIException
from ..services.version_control_service import (
    MergeConflict,
    StaleForkPoint,
    VersionControlService,
)
from ..services.create_app_service import CreateAppService
from ..services.directory_service import DirectoryService

logger = logging.getLogger(__name__)

@method_decorator(never_cache, name='dispatch')
class ProjectDirectoriesView(APIView):
    """Return a flat list of project files for the builder workspace.

    This endpoint restores backward compatibility for the frontend, which first
    queries `/api/v1/builder/<project_id>/directories/` to render the workspace tree.
    It uses the Builder FileService to list files. For dual-stack projects, only
    VueJS frontend files are returned (frontend/vuejs), including `src/apps`.
    """
    permission_classes = [IsAuthenticated]

    def get_project(self, project_id):
        try:
            return PMProject.objects.get(id=project_id, user=self.request.user, is_active=True)
        except PMProject.DoesNotExist:
            raise NotFound('Project not found')

    def get(self, request, project_id):
        try:
            project = self.get_project(project_id)

            # Materialize the working copy from the database if this
            # environment doesn't have the project files on disk yet.
            try:
                from ..services.project_files_service import ensure_working_copy
                ensure_working_copy(project)
            except Exception as hydrate_err:
                logger.warning(f"Could not ensure working copy before listing files: {hydrate_err}")

            view_file_service = ViewFileService(project=project)
            files = view_file_service.list_files()
            return Response(files)
        except APIException:
            raise
        except Exception:
            logger.exception("Error listing project files")
            raise

@method_decorator(never_cache, name='dispatch')
class FileContentView(APIView):
    """Get or update file content."""
    permission_classes = [IsAuthenticated]

    def get_project(self, project_id):
        """Get a project by ID, ensuring user has access."""
        try:
            return PMProject.objects.get(id=project_id, user=self.request.user, is_active=True)
        except PMProject.DoesNotExist:
            raise NotFound('Project not found')

    def get(self, request, project_id, file_path):
        try:
            # Get project from ProjectManager
            project = self.get_project(project_id)
            
            view_file_service = ViewFileService(project=project)
            content = view_file_service.get_file_content(file_path)
            return Response({'content': content})
        except APIException:
            raise
        except Exception:
            logger.exception("Error getting file content")
            raise
            
    def post(self, request, project_id, file_path):
        """Create or update file content."""
        try:
            # Get project from ProjectManager
            project = self.get_project(project_id)
            
            # Check if project path exists
            if not project.project_path:
                logger.error(f"Project path not found for project: {project.id}")
                return Response(
                    {'error': 'Project path not found. The project may not be properly initialized.'},
                    status=status.HTTP_404_NOT_FOUND
                )
                
            # Get content from request
            content = request.data.get('content', '')
            
            # Create parent directories if needed
            import os
            dir_path = os.path.dirname(file_path)
            if dir_path:
                try:
                    # Create all necessary parent directories
                    logger.info(f"Creating directory structure for {file_path}: {dir_path}")
                    os.makedirs(os.path.join(project.project_path, dir_path), exist_ok=True)
                except Exception as dir_error:
                    logger.error(f"Error creating directory structure: {str(dir_error)}")
                    # Continue anyway as the file creation might still succeed
            
            # Create or update the file
            view_file_service = ViewFileService(project=project)
            file_data = view_file_service.update_file(file_path, content)
            
            return Response(file_data, status=status.HTTP_201_CREATED)
        except APIException:
            raise
        except Exception:
            logger.exception("Error creating/updating file content")
            raise

@method_decorator(never_cache, name='dispatch')
class BrowserPreviewBaseView(APIView):
    """Shared plumbing for the browser-preview endpoints.

    The preview runs a real headless Chromium next to the project's dev
    servers on the backend host and tunnels frames/input through this API,
    so it behaves identically in development and production.
    """
    permission_classes = [IsAuthenticated]

    def get_project(self, project_id):
        """Get a project by ID, ensuring user has access."""
        try:
            return PMProject.objects.get(id=project_id, user=self.request.user, is_active=True)
        except PMProject.DoesNotExist:
            raise NotFound('Project not found')

    def get_service(self, project_id):
        return BrowserPreviewService(self.get_project(project_id))

    def handle_exception(self, exc):
        # Session died (browser killed, container restarted): 409 tells the
        # client to offer a restart rather than showing a hard failure.
        if isinstance(exc, BrowserNotRunning):
            return Response({'running': False, 'error': str(exc)},
                            status=status.HTTP_409_CONFLICT)
        if isinstance(exc, BrowserPreviewError):
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return super().handle_exception(exc)


class PreviewSessionView(BrowserPreviewBaseView):
    """Start / query / stop a project's browser preview session."""

    def get(self, request, project_id):
        service = self.get_service(project_id)
        if not service.is_running():
            return Response({'running': False})
        payload = service.frame()
        payload['running'] = True
        return Response(payload)

    def post(self, request, project_id):
        project = self.get_project(project_id)

        # Materialize the working copy from the database if this
        # environment doesn't have the project files on disk yet.
        try:
            from ..services.project_files_service import ensure_working_copy
            ensure_working_copy(project)
        except Exception as hydrate_err:
            logger.warning(f"Could not ensure working copy before preview: {hydrate_err}")

        viewport = request.data.get('viewport') or {}
        try:
            service = BrowserPreviewService(project)
            payload = service.start(
                viewport=(viewport.get('width'), viewport.get('height')) if viewport else None,
                device_scale_factor=request.data.get('device_scale_factor'),
            )
            payload['running'] = True
            return Response(payload)
        except Exception as e:
            logger.exception("Error starting browser preview")
            # The failure reason concerns the user's own project (npm install
            # output, missing scaffold, ...) and is what they need to fix it.
            return Response({
                'running': False,
                'error': f'Preview failed to start: {str(e)}'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    def delete(self, request, project_id):
        try:
            service = self.get_service(project_id)
            result = service.stop()
            return Response(result)
        except APIException:
            raise
        except Exception:
            logger.exception("Error stopping preview")
            raise


class ProjectPagesView(BrowserPreviewBaseView):
    """List the project's navigable pages, read from its actual Vue routers.

    Powers the preview's app/page menu; parsing the generated router files
    keeps the menu truthful even when routes don't follow the default
    view-filename conventions.
    """

    def get(self, request, project_id):
        project = self.get_project(project_id)
        try:
            from ..services.project_files_service import ensure_working_copy
            ensure_working_copy(project)
        except Exception as hydrate_err:
            logger.warning(f"Could not ensure working copy before listing pages: {hydrate_err}")
        from ..services.pages_service import list_app_pages
        return Response({'apps': list_app_pages(project)})


# ---------------------------------------------------------------------------
# Hot preview endpoints (async)
# ---------------------------------------------------------------------------
# Under ASGI, every sync view in the process shares ONE thread, so a frame
# poll or scroll batch would queue behind whatever other sync view happens to
# be running (file saves, version control, ...). These four endpoints carry
# all of the preview's interactive traffic, so they are plain async views
# that push the blocking CDP work onto the thread pool instead. The installed
# DRF has no async APIView support, so they mirror agent_stream's pattern:
# manual token-only auth, and csrf_exempt is safe for the same reason it is
# there — only the Authorization header authenticates, and browsers never
# send it cross-origin. Success and preview-error response shapes are
# identical to the previous DRF views'.


def _preview_project(user, project_id):
    """The user's active project, or None.

    select_related('user') matters: BrowserPreviewService's constructor
    reads project.user.id, and the service runs on a non-thread-sensitive
    pool thread where lazy ORM access would open a per-thread DB connection
    that Django's request cleanup never closes.
    """
    return PMProject.objects.select_related('user').filter(
        id=project_id, user=user, is_active=True
    ).first()


def _preview_json_body(request):
    """The request body as a JSON object, or None if it is not one."""
    try:
        data = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


async def _run_preview_call(request, project_id, call):
    """Authenticate, resolve the project, then run ``call(service)``.

    ORM work (token auth, project fetch) stays on sync_to_async's default
    thread-sensitive executor — Django's managed sync thread and DB
    connection. The preview call runs with thread_sensitive=False: it only
    touches sockets, state files and psutil, never the ORM, and the CDP pool
    serializes each browser's connection behind its per-entry lock, so
    concurrent pool threads are safe.
    """
    user = await _authenticate_stream_request(request)
    if user is None:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    project = await sync_to_async(_preview_project)(user, project_id)
    if project is None:
        return JsonResponse({'detail': 'Project not found'}, status=404)

    try:
        # The service is constructed inside the pool thread too: its
        # constructor touches the filesystem, which must not block the loop.
        payload = await sync_to_async(
            lambda: call(BrowserPreviewService(project)), thread_sensitive=False
        )()
    except BrowserNotRunning as e:
        # Session died (browser killed, container restarted): 409 tells the
        # client to offer a restart rather than showing a hard failure.
        return JsonResponse({'running': False, 'error': str(e)}, status=409)
    except BrowserPreviewError as e:
        return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse(payload)


@csrf_exempt
@never_cache
async def preview_frame(request, project_id):
    """Poll the latest screenshot; `etag` elides an unchanged frame."""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    etag = request.GET.get('etag')
    return await _run_preview_call(
        request, project_id, lambda service: service.frame(etag=etag)
    )


@csrf_exempt
@never_cache
async def preview_input(request, project_id):
    """Forward a batch of mouse/keyboard/wheel events to the page."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    data = _preview_json_body(request)
    if data is None:
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)
    return await _run_preview_call(
        request, project_id,
        lambda service: service.dispatch_input(
            data.get('events') or [], etag=data.get('etag')
        ),
    )


@csrf_exempt
@never_cache
async def preview_navigate(request, project_id):
    """Navigate the page: goto (path within the app), back, forward, reload."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    data = _preview_json_body(request)
    if data is None:
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)
    return await _run_preview_call(
        request, project_id,
        lambda service: service.navigate(
            data.get('action') or 'goto', path=data.get('path')
        ),
    )


@csrf_exempt
@never_cache
async def preview_resize(request, project_id):
    """Match the browser viewport to the client's preview pane size."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    data = _preview_json_body(request)
    if data is None:
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)
    return await _run_preview_call(
        request, project_id,
        lambda service: service.resize(
            data.get('width'), data.get('height'),
            device_scale_factor=data.get('device_scale_factor'),
        ),
    )

@method_decorator(never_cache, name='dispatch')
class CreateFileView(APIView):
    """Create a new file in a project."""
    permission_classes = [IsAuthenticated]

    def get_project(self, project_id):
        """Get a project by ID, ensuring user has access."""
        try:
            return PMProject.objects.get(id=project_id, user=self.request.user, is_active=True)
        except PMProject.DoesNotExist:
            raise NotFound('Project not found')

    def post(self, request, project_id):
        try:
            # Get project from ProjectManager
            project = self.get_project(project_id)
            
            # Check if project path exists
            if not project.project_path:
                logger.error(f"Project path not found for project: {project.id}")
                return Response(
                    {'error': 'Project path not found. The project may not be properly initialized.'},
                    status=status.HTTP_404_NOT_FOUND
                )
                
            # Copy request data before mutating: a form-encoded request
            # yields an immutable QueryDict, so assigning name/type below
            # would raise. .copy() returns a mutable copy for both JSON and
            # form payloads.
            file_data = request.data.copy()
            
            if not file_data.get('path') and not file_data.get('name'):
                return Response(
                    {'error': 'File path or name is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create file using the CreateFileService
            create_file_service = CreateFileService(project=project)
            
            # Handle requests with path directly
            if file_data.get('path'):
                # Update file_data to include name field based on path if missing
                if not file_data.get('name'):
                    file_data['name'] = file_data['path']
                
                # Determine file type from extension if not provided
                if not file_data.get('type'):
                    import os
                    ext = os.path.splitext(file_data['path'])[1].lower()
                    if ext == '.html':
                        file_data['type'] = 'html'
                    elif ext == '.css':
                        file_data['type'] = 'css'
                    elif ext == '.js':
                        file_data['type'] = 'javascript'
                    elif ext == '.py':
                        file_data['type'] = 'python'
                    elif ext == '.json':
                        file_data['type'] = 'json'
                    elif ext == '.md':
                        file_data['type'] = 'markdown'
                    elif ext == '.vue':
                        file_data['type'] = 'vue'
                    elif ext == '.ts':
                        file_data['type'] = 'typescript'
                    else:
                        file_data['type'] = 'text'
            
            # Create the file (CreateFileService handles directory creation)
            result = create_file_service.create_file(file_data)
            
            # Automatic view/URL creation removed - implement via OpenAI Agents SDK if needed
            
            return Response(result, status=status.HTTP_201_CREATED)
        except APIException:
            raise
        except Exception:
            logger.exception("Error creating file")
            raise

@method_decorator(never_cache, name='dispatch')
class DeleteFileView(APIView):
    """Delete a file from a project."""
    permission_classes = [IsAuthenticated]

    def get_project(self, project_id):
        """Get a project by ID, ensuring user has access."""
        try:
            return PMProject.objects.get(id=project_id, user=self.request.user, is_active=True)
        except PMProject.DoesNotExist:
            raise NotFound('Project not found')

    def post(self, request, project_id, file_path):
        """Handle file deletion via POST method."""
        return self._delete_file(request, project_id, file_path)
        
    def delete(self, request, project_id, file_path):
        """Handle file deletion via DELETE method."""
        return self._delete_file(request, project_id, file_path)
        
    def _delete_file(self, request, project_id, file_path):
        """Common implementation for file deletion."""
        try:
            # Get project from ProjectManager
            project = self.get_project(project_id)
            
            # Check if project path exists
            if not project.project_path:
                logger.error(f"Project path not found for project: {project.id}")
                return Response(
                    {'error': 'Project path not found. The project may not be properly initialized.'},
                    status=status.HTTP_404_NOT_FOUND
                )
                
            # Delete file using the DeleteFileService
            delete_file_service = DeleteFileService(project=project)
            result = delete_file_service.delete_file(file_path)
            return Response(result, status=status.HTTP_200_OK)
        except APIException:
            raise
        except Exception:
            logger.exception("Error deleting file")
            raise


@method_decorator(never_cache, name='dispatch')
class CreateDirectoryView(APIView):
    """Create a new directory in a project."""
    permission_classes = [IsAuthenticated]

    def get_project(self, project_id):
        """Get a project by ID, ensuring user has access."""
        try:
            return PMProject.objects.get(id=project_id, user=self.request.user, is_active=True)
        except PMProject.DoesNotExist:
            raise NotFound('Project not found')

    def post(self, request, project_id):
        try:
            project = self.get_project(project_id)

            if not project.project_path:
                return Response(
                    {'error': 'Project path not found. The project may not be properly initialized.'},
                    status=status.HTTP_404_NOT_FOUND
                )

            dir_path = request.data.get('path', '')
            if not dir_path:
                return Response(
                    {'error': 'Directory path is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            directory_service = DirectoryService(project=project)
            result = directory_service.create_directory(dir_path)
            return Response(result, status=status.HTTP_201_CREATED)
        except APIException:
            raise
        except Exception:
            logger.exception("Error creating directory")
            raise


@method_decorator(never_cache, name='dispatch')
class DeleteDirectoryView(APIView):
    """Delete a directory from a project."""
    permission_classes = [IsAuthenticated]

    def get_project(self, project_id):
        """Get a project by ID, ensuring user has access."""
        try:
            return PMProject.objects.get(id=project_id, user=self.request.user, is_active=True)
        except PMProject.DoesNotExist:
            raise NotFound('Project not found')

    def delete(self, request, project_id, dir_path):
        """Handle directory deletion via DELETE method."""
        return self._delete_directory(request, project_id, dir_path)

    def post(self, request, project_id, dir_path):
        """Handle directory deletion via POST method."""
        return self._delete_directory(request, project_id, dir_path)

    def _delete_directory(self, request, project_id, dir_path):
        """Common implementation for directory deletion."""
        try:
            project = self.get_project(project_id)

            if not project.project_path:
                return Response(
                    {'error': 'Project path not found. The project may not be properly initialized.'},
                    status=status.HTTP_404_NOT_FOUND
                )

            recursive = request.data.get('recursive', False)

            directory_service = DirectoryService(project=project)
            result = directory_service.delete_directory(dir_path, recursive=recursive)
            return Response(result, status=status.HTTP_200_OK)
        except APIException:
            raise
        except Exception:
            logger.exception("Error deleting directory")
            raise


@method_decorator(never_cache, name='dispatch')
class VersionControlHistoryView(APIView):
    """Get version control history for a project."""
    permission_classes = [IsAuthenticated]

    def get_project(self, project_id):
        """Get a project by ID, ensuring user has access."""
        try:
            return PMProject.objects.get(id=project_id, user=self.request.user, is_active=True)
        except PMProject.DoesNotExist:
            raise NotFound('Project not found')

    def get(self, request, project_id):
        """Get commit history for the project."""
        try:
            # Get project
            project = self.get_project(project_id)
            
            # Use VersionControlService to get history
            version_service = VersionControlService(project=project)
            result = version_service.get_commit_history(request.user, project_id)
            
            if result.get('success'):
                return Response({
                    'success': True,
                    'versions': result.get('commits', [])
                })
            else:
                return Response({
                    'success': False,
                    'error': result.get('message', 'Failed to get version history')
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except APIException:
            raise
        except Exception:
            logger.exception("Error getting version history")
            raise
    
    def post(self, request, project_id):
        """Create a new version (commit)."""
        try:
            # Get project
            project = self.get_project(project_id)
            
            # Get request data
            file_path = request.data.get('file_path', None)
            description = request.data.get('description', None)
            
            # Use VersionControlService to create version
            version_service = VersionControlService(project=project)
            result = version_service.create_version_after_file_change(
                request.user, project_id, file_path, description
            )
            
            if result.get('success'):
                return Response({
                    'success': True,
                    'message': result.get('message', 'Successfully created version'),
                    'commit_hash': result.get('commit_hash')
                })
            else:
                return Response({
                    'success': False,
                    'error': result.get('message', 'Failed to create version')
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except APIException:
            raise
        except Exception:
            logger.exception("Error creating version")
            raise

@method_decorator(never_cache, name='dispatch')
class VersionControlResetView(APIView):
    """Reset project to a specific version."""
    permission_classes = [IsAuthenticated]

    def get_project(self, project_id):
        """Get a project by ID, ensuring user has access."""
        try:
            return PMProject.objects.get(id=project_id, user=self.request.user, is_active=True)
        except PMProject.DoesNotExist:
            raise NotFound('Project not found')

    def post(self, request, project_id):
        """Reset project to specified version."""
        try:
            # Get project
            project = self.get_project(project_id)
            
            # Get request data
            commit_hash = request.data.get('commit_hash', None)
            
            if not commit_hash:
                return Response({
                    'success': False,
                    'error': 'Commit hash is required'
                }, status=status.HTTP_400_BAD_REQUEST)

            # The reset runs `git reset --hard` on the canonical working
            # tree, so refuse while a canonical-tree (chat/lead) run is
            # live (same contract as the stream endpoint's agent_busy
            # guard). Task runs don't block it: their worktrees branched
            # from an earlier HEAD and keep their own checkouts, so a
            # canonical reset leaves them untouched.
            if _project_has_running_conversation(request.user, project_id):
                return Response({'detail': 'agent_busy'}, status=status.HTTP_409_CONFLICT)

            # Use VersionControlService to reset to version
            version_service = VersionControlService(project=project)
            result = version_service.reset_to_version(
                request.user, project_id, commit_hash
            )
            
            if result.get('success'):
                return Response({
                    'success': True,
                    'message': result.get('message', 'Successfully reset project to specified version')
                })
            else:
                return Response({
                    'success': False,
                    'error': result.get('message', 'Failed to reset project')
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except APIException:
            raise
        except Exception:
            logger.exception("Error resetting project")
            raise

@method_decorator(never_cache, name='dispatch')
class CreateAppView(APIView):
    """Create a new Vue.js app with complete structure."""
    permission_classes = [IsAuthenticated]

    def get_project(self, project_id):
        """Get a project by ID, ensuring user has access."""
        try:
            return PMProject.objects.get(id=project_id, user=self.request.user, is_active=True)
        except PMProject.DoesNotExist:
            raise NotFound('Project not found')

    def post(self, request, project_id):
        """Create a new app from gallery or ensure default apps."""
        try:
            # Get project
            project = self.get_project(project_id)
            
            # Get request data
            action = request.data.get('action', 'create_app')  # 'create_app' or 'ensure_defaults'
            app_name = request.data.get('app_name', '')
            app_description = request.data.get('app_description', '')
            
            # Initialize service
            app_service = CreateAppService(user=self.request.user, project=project)
            
            if action == 'ensure_defaults':
                # Ensure default apps exist
                result = app_service.ensure_default_apps()
            else:
                # Create new app from gallery
                if not app_name:
                    return Response(
                        {'error': 'App name is required for app creation'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                result = app_service.create_app_from_gallery(
                    app_name=app_name,
                    app_description=app_description
                )
            
            if result.get('success'):
                return Response(result, status=status.HTTP_201_CREATED)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
                
        except APIException:
            raise
        except Exception:
            logger.exception("Error creating app")
            raise


@method_decorator(never_cache, name='dispatch')
class ProjectLayoutView(APIView):
    """Manage project layout positions and connections."""
    permission_classes = [IsAuthenticated]

    def get_project(self, project_id):
        """Get a project by ID, ensuring user has access."""
        try:
            return PMProject.objects.get(id=project_id, user=self.request.user, is_active=True)
        except PMProject.DoesNotExist:
            raise NotFound('Project not found')

    def get(self, request, project_id):
        """Load saved layout for a project."""
        try:
            from ..models import ProjectLayout
            
            # Get project to verify access
            project = self.get_project(project_id)
            
            # Try to get existing layout
            layout = ProjectLayout.objects.filter(
                user=request.user,
                project_id=str(project_id)
            ).first()
            
            if layout:
                return Response({
                    'success': True,
                    'layout_data': layout.layout_data,
                    'updated_at': layout.updated_at.isoformat()
                })
            else:
                # No saved layout - return empty
                return Response({
                    'success': True,
                    'layout_data': {'positions': {}, 'connections': []},
                    'updated_at': None
                })
                
        except APIException:
            raise
        except Exception:
            logger.exception("Error loading project layout")
            raise

    def post(self, request, project_id):
        """Save layout positions and connections."""
        try:
            from ..models import ProjectLayout
            
            # Get project to verify access
            project = self.get_project(project_id)
            
            # Get layout data from request
            layout_data = request.data.get('layout_data', {})
            
            if not isinstance(layout_data, dict):
                return Response({
                    'success': False,
                    'error': 'layout_data must be an object'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create or update layout
            layout, created = ProjectLayout.objects.update_or_create(
                user=request.user,
                project_id=str(project_id),
                defaults={'layout_data': layout_data}
            )
            
            return Response({
                'success': True,
                'message': 'Layout saved successfully',
                'updated_at': layout.updated_at.isoformat()
            })
                
        except APIException:
            raise
        except Exception:
            logger.exception("Error saving project layout")
            raise

    def delete(self, request, project_id):
        """Delete saved layout (reset to default)."""
        try:
            from ..models import ProjectLayout
            
            # Get project to verify access
            project = self.get_project(project_id)
            
            # Delete layout if it exists
            deleted_count, _ = ProjectLayout.objects.filter(
                user=request.user,
                project_id=str(project_id)
            ).delete()
            
            return Response({
                'success': True,
                'message': f'Layout reset successfully (deleted {deleted_count} record(s))'
            })
                
        except APIException:
            raise
        except Exception:
            logger.exception("Error resetting project layout")
            raise


# ---------------------------------------------------------------------------
# Agent endpoints (the Imagi agent, conversation CRUD)
# ---------------------------------------------------------------------------

def resolve_model(model):
    """
    Resolve a requested model id to a valid GPT 5.6 suite model.

    Any of the available suite models (Sol, Terra, Luna) is accepted; anything
    unrecognized falls back to the default model.
    """
    if model and get_model_by_id(model):
        return model
    return DEFAULT_MODEL



def create_error_response(error, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR):
    """
    Create a properly rendered error response with CORS headers.
    """
    from rest_framework.renderers import JSONRenderer
    
    error_message = str(error)
    response = Response(
        {'error': error_message}, 
        status=status_code
    )
    
    response = add_cors_headers(response)
    
    if not hasattr(response, 'accepted_renderer') or not response.accepted_renderer:
        response.accepted_renderer = JSONRenderer()
    
    response.accepted_media_type = getattr(response, 'accepted_media_type', 'application/json')
    response.renderer_context = getattr(response, 'renderer_context', {})
    
    try:
        response.render()
    except Exception as e:
        logger.error(f"Error rendering response: {str(e)}")
        from django.http import HttpResponse
        return HttpResponse(
            content=json.dumps({'error': error_message}),
            content_type='application/json',
            status=status_code
        )
    
    return response


def add_cors_headers(response):
    """Add CORS headers to any response object."""
    response["Access-Control-Allow-Origin"] = "http://localhost:5174"
    response["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Authorization, Content-Type, Accept, X-Requested-With, x-csrftoken, x-api-client"
    response["Access-Control-Allow-Credentials"] = "true"
    response["Access-Control-Max-Age"] = "86400"
    return response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def agent(request):
    """
    Process a message with the Imagi agent.

    The single Imagi agent both chats and edits project files using function
    tools from the OpenAI Agents SDK. It autonomously decides when to
    read/write files versus just responding conversationally.
    """
    try:
        message = request.data.get('message')
        model = request.data.get('model', DEFAULT_MODEL)
        reasoning_effort = request.data.get('reasoning_effort')
        conversation_id = request.data.get('conversation_id')
        project_id = request.data.get('project_id')
        current_file = request.data.get('current_file')

        logger.info(f"Agent API request - Model: {model}, Project ID: {project_id}")

        if not message:
            return create_error_response('Message is required', status.HTTP_400_BAD_REQUEST)

        if not project_id:
            return create_error_response('Project ID is required', status.HTTP_400_BAD_REQUEST)

        # Use the selected GPT 5.6 suite model (falls back to default if invalid)
        model = resolve_model(model)

        # Ensure project_id is an integer
        try:
            project_id = int(project_id)
        except (ValueError, TypeError):
            return create_error_response('Invalid project ID', status.HTTP_400_BAD_REQUEST)

        # Ensure conversation_id is an integer if provided
        if conversation_id:
            try:
                conversation_id = int(conversation_id)
            except (ValueError, TypeError):
                conversation_id = None

        # Busy guard, same scoping as the stream endpoint: canonical-tree
        # (chat/lead) runs are serialized per project, a task run is blocked
        # only while that same task is already running.
        conversation = None
        if conversation_id:
            conversation = AgentConversation.objects.filter(
                id=conversation_id, user=request.user
            ).first()
        if conversation is not None and conversation.kind == 'task':
            if _conversation_is_running(conversation):
                return Response({'detail': 'agent_busy'}, status=status.HTTP_409_CONFLICT)
        elif _project_has_running_conversation(
            request.user, project_id, exclude_conversation_id=conversation_id
        ):
            return Response({'detail': 'agent_busy'}, status=status.HTTP_409_CONFLICT)

        # Plan usage limits, enforced before any model work starts.
        allowed, limit_payload = check_usage_allowed(request.user)
        if not allowed:
            return Response(limit_payload, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # Create agent service instance
        agent_service = ImagiAgentService(model=model, reasoning_effort=reasoning_effort)

        logger.info(f"Agent request: message length={len(message)}, model={model}, effort={reasoning_effort}, project_id={project_id}")

        # Process the message with the Imagi agent
        result = agent_service.process(
            user_input=message,
            user=request.user,
            model=model,
            project_id=project_id,
            current_file=current_file,
            conversation_id=conversation_id,
            reasoning_effort=reasoning_effort,
        )

        if not result.get('success', False):
            error_message = result.get('error', 'Error processing message')
            return create_error_response(error_message, status.HTTP_400_BAD_REQUEST)

        response_data = {
            'conversation_id': result.get('conversation_id'),
            'response': result.get('response', ''),
            'files_changed': result.get('files_changed', []),
            'tool_calls': result.get('tool_calls', []),
            'plan': result.get('plan', []),
            'single_message': result.get('single_message', True),
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error in agent API: {str(e)}")
        logger.error(traceback.format_exc())
        return create_error_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)


def _sse(event: dict) -> str:
    """Frame one event as an SSE message."""
    return f"data: {json.dumps(event)}\n\n"


async def _authenticate_stream_request(request):
    """Resolve the user for a streaming request from its auth token, or None.

    DRF's decorators are sync-only, so this endpoint authenticates by hand.
    Token only, deliberately: this view is csrf_exempt (DRF's CSRF handling
    comes with SessionAuthentication, which it cannot use), and honouring the
    session cookie without a CSRF check would let any origin drive an agent run
    against the victim's project. An Authorization header is not sent
    cross-origin by default, so requiring one closes that off. The frontend
    always authenticates by token.
    """
    from rest_framework.authentication import TokenAuthentication
    from rest_framework.exceptions import AuthenticationFailed

    if not request.META.get('HTTP_AUTHORIZATION'):
        return None
    try:
        result = await sync_to_async(TokenAuthentication().authenticate)(request)
    except AuthenticationFailed:
        return None
    return result[0] if result else None


@csrf_exempt
async def agent_stream(request):
    """Stream an agent run as Server-Sent Events.

    Same work as the blocking `agent` endpoint, but the client sees text and
    tool activity as they happen instead of waiting for the whole run. The
    terminal "done" event carries the payload `agent` would have returned.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    user = await _authenticate_stream_request(request)
    if user is None:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        payload = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)

    message = payload.get('message')
    project_id = payload.get('project_id')

    if not message:
        return JsonResponse({'error': 'Message is required'}, status=400)
    if not project_id:
        return JsonResponse({'error': 'Project ID is required'}, status=400)
    try:
        project_id = int(project_id)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid project ID'}, status=400)

    conversation_id = payload.get('conversation_id')
    if conversation_id:
        try:
            conversation_id = int(conversation_id)
        except (ValueError, TypeError):
            conversation_id = None

    model = resolve_model(payload.get('model', DEFAULT_MODEL))
    reasoning_effort = payload.get('reasoning_effort')

    # Busy guard, scoped by what the run will edit. Chat/lead runs edit the
    # shared canonical tree, so only one of those may be live per project;
    # kind='task' runs edit their own git worktree, so a task is blocked only
    # while that same conversation is already running — tasks run in parallel
    # with the lead and with each other. Best-effort guard, not a lock: two
    # simultaneous submits may both pass, which is acceptable — this protects
    # against a user launching runs that trample each other's file edits, not
    # against a determined race.
    conversation = None
    if conversation_id:
        conversation = await sync_to_async(
            AgentConversation.objects.filter(id=conversation_id, user=user).first
        )()
    if conversation is not None and conversation.kind == 'task':
        if _conversation_is_running(conversation):
            return JsonResponse({'detail': 'agent_busy'}, status=409)
    else:
        busy = await sync_to_async(_project_has_running_conversation)(
            user, project_id, exclude_conversation_id=conversation_id
        )
        if busy:
            return JsonResponse({'detail': 'agent_busy'}, status=409)

    # Plan usage limits: refuse before the stream opens, following the same
    # pre-stream JSON contract as the agent_busy 409 above.
    allowed, limit_payload = await sync_to_async(check_usage_allowed)(user)
    if not allowed:
        return JsonResponse(limit_payload, status=429)

    agent_service = ImagiAgentService(model=model, reasoning_effort=reasoning_effort)

    async def event_stream():
        try:
            async for event in agent_service.process_stream(
                user_input=message,
                user=user,
                model=model,
                project_id=project_id,
                current_file=payload.get('current_file'),
                conversation_id=conversation_id,
                reasoning_effort=reasoning_effort,
            ):
                yield _sse(event)
        except Exception as e:  # pragma: no cover - defensive
            logger.error(f"Error in agent stream: {e}")
            logger.error(traceback.format_exc())
            yield _sse({"type": "error", "error": str(e)})

    response = StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream',
    )
    response['Cache-Control'] = 'no-cache'
    # Tell nginx not to buffer this response; without it the whole stream is
    # held back and delivered at once, which defeats the point.
    response['X-Accel-Buffering'] = 'no'
    return response


# ---------------------------------------------------------------------------
# Conversation (agent instance) CRUD
# ---------------------------------------------------------------------------

# A run whose marker hasn't been refreshed within this window is treated as
# not running: a crashed worker never clears run_started_at. Long legitimate
# runs stay fresh via the streaming loop's heartbeat (base_agent.py), so this
# measures silence since the last event, not total run duration.
RUN_STALENESS_WINDOW = timedelta(minutes=10)


def _conversation_is_running(conversation):
    started = conversation.run_started_at
    return bool(started and timezone.now() - started < RUN_STALENESS_WINDOW)


def _project_has_running_conversation(
    user, project_id, exclude_conversation_id=None, kinds=CANONICAL_TREE_KINDS
):
    """Does any conversation of these kinds have a fresh run in this project?

    Backs the 409 agent_busy guards. Scoped to the canonical-tree kinds
    (chat/lead) by default: those runs edit the shared canonical tree and
    must be serialized, while kind='task' runs edit only their own git
    worktree — tasks neither block nor are blocked by this guard, so they
    run in parallel with the lead and with each other. The staleness window
    matches is_running, so a crashed worker that never cleared
    run_started_at cannot wedge the project.
    """
    threshold = timezone.now() - RUN_STALENESS_WINDOW
    qs = AgentConversation.objects.filter(
        user=user,
        project_id=project_id,
        run_started_at__gt=threshold,
        kind__in=kinds,
    )
    if exclude_conversation_id:
        qs = qs.exclude(id=exclude_conversation_id)
    return qs.exists()


def _conversation_total_tokens(conversation):
    """Sum input+output tokens across the conversation's message usage.

    None (not 0) when no message carries usage: absent usage means the run's
    tokens were never captured, never that it was free. Aggregated in Python
    because usage lives inside the metadata JSONField.
    """
    total = None
    metadatas = conversation.messages.exclude(metadata__isnull=True).values_list(
        'metadata', flat=True
    )
    for metadata in metadatas:
        usage = metadata.get('usage') if isinstance(metadata, dict) else None
        if not isinstance(usage, dict):
            continue
        input_tokens = usage.get('input_tokens')
        output_tokens = usage.get('output_tokens')
        if not isinstance(input_tokens, int) or not isinstance(output_tokens, int):
            continue
        total = (total or 0) + input_tokens + output_tokens
    return total


def _serialize_conversation(conversation):
    last_message = conversation.messages.order_by('-created_at').first()
    preview = ''
    if last_message and last_message.content:
        preview = last_message.content.strip().splitlines()[0][:140]
    return {
        'id': conversation.id,
        'title': conversation.title or '',
        'model_name': conversation.model_name,
        'project_id': conversation.project_id,
        'kind': conversation.kind,
        'parent': conversation.parent_id,
        'review_status': conversation.review_status,
        'variant_group': conversation.variant_group,
        # The path itself is server-internal; the client only needs to know
        # whether this task has an unmerged worktree to review.
        'has_worktree': bool(conversation.worktree_path),
        'archived_at': conversation.archived_at.isoformat() if conversation.archived_at else None,
        'created_at': conversation.created_at.isoformat(),
        'updated_at': conversation.updated_at.isoformat(),
        'last_message_preview': preview,
        'is_running': _conversation_is_running(conversation),
        'total_tokens': _conversation_total_tokens(conversation),
        # A dispatched-but-not-yet-run task's brief: the client fires the run
        # with it (and _prepare_run clears it when that run starts).
        'queued_prompt': conversation.queued_prompt or '',
    }


def _conversation_project(conversation):
    """The conversation's project row, or None (project_id is a plain int)."""
    if not conversation.project_id:
        return None
    return PMProject.objects.filter(
        id=conversation.project_id, user=conversation.user
    ).first()


def _remove_conversation_worktree(conversation):
    """Best-effort removal of a task conversation's git worktree.

    Failures are logged, never raised: a leaked worktree directory must not
    block deleting or dismissing the conversation itself.
    """
    if not conversation.worktree_path:
        return
    try:
        project = _conversation_project(conversation)
        if project and project.project_path:
            VersionControlService().remove_task_worktree(
                project.project_path, conversation.id
            )
    except Exception as e:
        logger.warning(
            f"Could not remove worktree for conversation {conversation.id}: {e}"
        )


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def conversations_list_create(request):
    """List conversations for a project, or create a new one."""
    if request.method == 'GET':
        project_id = request.query_params.get('project_id')
        qs = AgentConversation.objects.filter(user=request.user)
        if project_id:
            try:
                qs = qs.filter(project_id=int(project_id))
            except (ValueError, TypeError):
                return create_error_response('Invalid project_id', status.HTTP_400_BAD_REQUEST)
        data = [_serialize_conversation(c) for c in qs.order_by('-updated_at')]
        return Response(data, status=status.HTTP_200_OK)

    # POST -> create
    try:
        project_id = request.data.get('project_id')
        model_name = request.data.get('model_name') or DEFAULT_MODEL
        title = (request.data.get('title') or '').strip()[:120]

        if project_id is not None:
            try:
                project_id = int(project_id)
            except (ValueError, TypeError):
                return create_error_response('Invalid project_id', status.HTTP_400_BAD_REQUEST)

        kind = request.data.get('kind')
        if kind not in ('lead', 'task'):
            kind = 'chat'
        variant_group = (request.data.get('variant_group') or '').strip()[:64]

        parent = None
        parent_id = request.data.get('parent')
        if parent_id is not None:
            try:
                parent = AgentConversation.objects.filter(
                    id=int(parent_id), user=request.user
                ).first()
            except (ValueError, TypeError):
                parent = None

        # Single-lead invariant: a project has at most one live lead thread.
        # Asking for another returns the existing one (200) instead of
        # creating a duplicate, so racing clients converge on the same lead.
        if kind == 'lead' and project_id is not None:
            existing_lead = AgentConversation.objects.filter(
                user=request.user,
                project_id=project_id,
                kind='lead',
                archived_at__isnull=True,
            ).order_by('created_at').first()
            if existing_lead is not None:
                return Response(
                    _serialize_conversation(existing_lead), status=status.HTTP_200_OK
                )

        agent_service = ImagiAgentService(model=model_name)
        try:
            with transaction.atomic():
                conversation = agent_service.create_conversation(
                    user=request.user,
                    model=model_name,
                    project_id=project_id,
                    title=title,
                    kind=kind,
                    parent=parent,
                    variant_group=variant_group,
                )
        except IntegrityError:
            # Lost the race against the one_live_lead_per_project constraint:
            # a concurrent request created the lead between our check and our
            # insert. Converge on the winner instead of erroring.
            existing_lead = AgentConversation.objects.filter(
                user=request.user,
                project_id=project_id,
                kind='lead',
                archived_at__isnull=True,
            ).order_by('created_at').first()
            if kind == 'lead' and existing_lead is not None:
                return Response(
                    _serialize_conversation(existing_lead), status=status.HTTP_200_OK
                )
            raise
        return Response(_serialize_conversation(conversation), status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"Error creating conversation: {str(e)}")
        logger.error(traceback.format_exc())
        return create_error_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def conversation_detail(request, conversation_id):
    """Retrieve, update, or delete a single conversation."""
    conversation = get_object_or_404(
        AgentConversation, id=conversation_id, user=request.user
    )

    if request.method == 'GET':
        return Response(_serialize_conversation(conversation), status=status.HTTP_200_OK)

    if request.method == 'DELETE':
        # A live task run is executing inside the worktree this delete would
        # remove: deleting under it leaves an orphan non-git directory (the
        # run's file tools recreate plain paths) and a run writing into a
        # dead tree. Same 409 contract as accept/dismiss. Canonical-tree
        # conversations have no worktree, so their delete-while-running flow
        # (disconnect the run, keep what landed) is unchanged.
        if conversation.kind == 'task' and _conversation_is_running(conversation):
            return Response({'detail': 'agent_busy'}, status=status.HTTP_409_CONFLICT)
        # A task's worktree would otherwise leak beside the project dir.
        _remove_conversation_worktree(conversation)
        conversation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # PATCH
    updated_fields = []
    if 'title' in request.data:
        conversation.title = (request.data.get('title') or '').strip()[:120]
        updated_fields.append('title')
    if 'model_name' in request.data:
        conversation.model_name = request.data.get('model_name') or conversation.model_name
        updated_fields.append('model_name')
    if 'archived' in request.data:
        archived = bool(request.data.get('archived'))
        # Unarchiving a lead while a newer live lead exists would violate the
        # single-lead invariant (and trip its DB constraint) — refuse rather
        # than resurrect a second live lead.
        if (
            not archived
            and conversation.kind == 'lead'
            and conversation.archived_at is not None
            and AgentConversation.objects.filter(
                user=request.user,
                project_id=conversation.project_id,
                kind='lead',
                archived_at__isnull=True,
            ).exclude(id=conversation.id).exists()
        ):
            return Response(
                {
                    'error': 'lead_exists',
                    'detail': 'This project already has a live lead thread.',
                },
                status=status.HTTP_409_CONFLICT,
            )
        conversation.archived_at = timezone.now() if archived else None
        updated_fields.append('archived_at')

    if updated_fields:
        conversation.save(update_fields=updated_fields + ['updated_at'])

    return Response(_serialize_conversation(conversation), status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def conversation_cancel(request, conversation_id):
    """Release a conversation's running-run marker.

    Used by the Stop button when this tab has no live stream to abort
    (restored after a reload, opened elsewhere, or a crashed worker). There
    is no server-side task handle for a run driven by another tab's stream,
    so this cannot halt the agent itself — it clears run_started_at so
    is_running flips false and the project's agent_busy guard lifts.
    """
    conversation = get_object_or_404(
        AgentConversation, id=conversation_id, user=request.user
    )
    if conversation.run_started_at is not None:
        conversation.run_started_at = None
        conversation.save(update_fields=['run_started_at'])
    return Response(_serialize_conversation(conversation), status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def conversation_restore_checkpoint(request, conversation_id):
    """Rewind a conversation (and the project files) to a user message.

    Body: {"message_id": <id of a user message carrying a checkpoint>}

    Restores the working tree to the checkpoint commit captured when that
    message was sent, then deletes the message and everything after it —
    conversation and files rewind together, like Cursor's per-message
    restore. Returns the removed prompt text so the client can hand it back
    to the composer for editing.
    """
    conversation = get_object_or_404(
        AgentConversation, id=conversation_id, user=request.user
    )
    message = get_object_or_404(
        AgentMessage, id=request.data.get('message_id'), conversation=conversation
    )

    checkpoint = (message.metadata or {}).get('checkpoint')
    if message.role != 'user' or not checkpoint:
        return Response(
            {'error': 'That message has no restore point.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # A restore rewinds the tree the conversation's runs edit. For a task
    # that is its own worktree (checkpoints were committed there), guarded
    # only against that task's run; for chat/lead it is the canonical tree,
    # guarded against canonical-tree runs — task runs don't block it, their
    # worktrees branched from an earlier HEAD and are unaffected by a
    # canonical reset.
    if conversation.kind == 'task':
        if not conversation.worktree_path:
            return Response(
                {'error': 'This task no longer has a worktree to restore.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if _conversation_is_running(conversation):
            return Response({'detail': 'agent_busy'}, status=status.HTTP_409_CONFLICT)
        result = VersionControlService().reset_to_version(
            request.user, conversation.project_id, checkpoint,
            tree_path=conversation.worktree_path,
        )
    else:
        if conversation.project_id and _project_has_running_conversation(
            request.user, conversation.project_id
        ):
            return Response({'detail': 'agent_busy'}, status=status.HTTP_409_CONFLICT)
        result = VersionControlService().reset_to_version(
            request.user, conversation.project_id, checkpoint
        )
    if not result.get('success'):
        return Response(
            {'error': result.get('message', 'Could not restore the project files.')},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Truncate the thread: the restored-to message and everything after it.
    # created_at can collide within a burst, so break ties by id.
    prompt_text = message.content
    conversation.messages.filter(created_at__gt=message.created_at).delete()
    conversation.messages.filter(created_at=message.created_at, id__gte=message.id).delete()
    # The rewind removed the reply that made a task reviewable.
    if conversation.kind == 'task' and conversation.review_status == 'ready':
        conversation.review_status = 'active'
        conversation.save(update_fields=['review_status', 'updated_at'])
    else:
        conversation.save(update_fields=['updated_at'])

    return Response({
        'success': True,
        'checkpoint': checkpoint,
        'prompt': prompt_text,
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def conversation_accept(request, conversation_id):
    """Accept a reviewed task: merge its worktree into the canonical tree.

    Commits pending changes on both sides, merges the task branch, re-syncs
    the ProjectFile mirror from the (now merged) canonical disk — worktree
    runs skipped mirror writes by design — marks the task accepted, and
    removes the worktree. A conflicted merge is aborted and reported as a
    409 merge_conflict, leaving the canonical tree untouched.
    """
    conversation = get_object_or_404(
        AgentConversation, id=conversation_id, user=request.user
    )
    if conversation.kind != 'task' or not conversation.worktree_path:
        return Response(
            {'error': 'Only task conversations with a worktree can be accepted.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    if _conversation_is_running(conversation):
        return Response({'detail': 'agent_busy'}, status=status.HTTP_409_CONFLICT)
    # The merge also rewrites the canonical tree, so it needs the same
    # guard as version resets: no canonical-tree (chat/lead) run may be live.
    if conversation.project_id and _project_has_running_conversation(
        request.user, conversation.project_id
    ):
        return Response({'detail': 'agent_busy'}, status=status.HTTP_409_CONFLICT)

    project = _conversation_project(conversation)
    if project is None or not project.project_path:
        return Response(
            {'error': 'Project not found for this conversation.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    service = VersionControlService()
    try:
        result = service.merge_task_worktree(project.project_path, conversation.id)
    except MergeConflict as e:
        return Response(
            {'error': 'merge_conflict', 'detail': str(e)},
            status=status.HTTP_409_CONFLICT
        )
    except StaleForkPoint as e:
        # The canonical tree was restored to before this task's fork point;
        # merging would silently resurrect the restored-away history.
        return Response(
            {'error': 'stale_base', 'detail': str(e)},
            status=status.HTTP_409_CONFLICT
        )
    if not result.get('success'):
        return Response(
            {'error': result.get('message', 'Could not merge the task worktree.')},
            status=status.HTTP_400_BAD_REQUEST
        )

    # The merge rewrote the canonical working copy wholesale — bring the
    # database mirror back in sync with disk.
    try:
        from ..services.project_files_service import import_project_from_disk
        import_project_from_disk(project)
    except Exception as sync_error:
        logger.error(f"Task merge succeeded but database re-sync failed: {sync_error}")

    service.remove_task_worktree(project.project_path, conversation.id)
    conversation.review_status = 'accepted'
    conversation.worktree_path = ''
    conversation.save(update_fields=['review_status', 'worktree_path', 'updated_at'])
    # Accepting consumes the task's queue slot in the main thread.
    _resolve_conversation_check_ins(conversation)

    return Response({'status': 'accepted'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def conversation_dismiss(request, conversation_id):
    """Dismiss a task: discard its worktree without merging anything."""
    conversation = get_object_or_404(
        AgentConversation, id=conversation_id, user=request.user
    )
    if conversation.kind != 'task':
        return Response(
            {'error': 'Only task conversations can be dismissed.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    # 'accepted' is terminal: the worktree is already merged into the
    # canonical tree, so relabeling it 'dismissed' (e.g. from a stale tab)
    # would make the record claim merged changes were discarded.
    if conversation.review_status == 'accepted':
        return Response(
            {
                'error': 'already_accepted',
                'detail': 'This task was already accepted; its changes are part of your app.',
            },
            status=status.HTTP_409_CONFLICT
        )
    if _conversation_is_running(conversation):
        return Response({'detail': 'agent_busy'}, status=status.HTTP_409_CONFLICT)

    _remove_conversation_worktree(conversation)
    conversation.review_status = 'dismissed'
    conversation.worktree_path = ''
    conversation.save(update_fields=['review_status', 'worktree_path', 'updated_at'])
    # Dismissing consumes the task's queue slot in the main thread.
    _resolve_conversation_check_ins(conversation)

    return Response({'status': 'dismissed'}, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# Check-ins (the main thread's processing queue)
# ---------------------------------------------------------------------------

def _resolve_conversation_check_ins(conversation):
    """Mark every pending check-in for this task resolved (its queue slot is
    consumed by whatever action the caller just took)."""
    AgentCheckIn.objects.filter(
        conversation=conversation, status='pending'
    ).update(status='resolved', resolved_at=timezone.now())


def _serialize_check_in(check_in):
    task = check_in.conversation
    return {
        'id': check_in.id,
        'kind': check_in.kind,
        'body': check_in.body,
        'status': check_in.status,
        'created_at': check_in.created_at.isoformat(),
        'resolved_at': check_in.resolved_at.isoformat() if check_in.resolved_at else None,
        'project_id': check_in.project_id,
        'lead_id': check_in.lead_id,
        # Enough of the task's state to render and act on the queue card
        # without a second fetch.
        'task': {
            'id': task.id,
            'title': task.title or '',
            'kind': task.kind,
            'review_status': task.review_status,
            'variant_group': task.variant_group,
            'has_worktree': bool(task.worktree_path),
            'is_running': _conversation_is_running(task),
        },
    }


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_ins_list(request):
    """The check-in queue for a project, oldest first (FIFO).

    Pending only by default — the queue the lead thread renders. Pass
    ?status=all for history.
    """
    project_id = request.query_params.get('project_id')
    if not project_id:
        return create_error_response('project_id is required', status.HTTP_400_BAD_REQUEST)
    try:
        project_id = int(project_id)
    except (ValueError, TypeError):
        return create_error_response('Invalid project_id', status.HTTP_400_BAD_REQUEST)

    qs = AgentCheckIn.objects.filter(
        user=request.user, project_id=project_id
    ).select_related('conversation')
    status_param = request.query_params.get('status', 'pending')
    if status_param != 'all':
        qs = qs.filter(status=status_param)
    data = [_serialize_check_in(ci) for ci in qs.order_by('created_at')]
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_in_resolve(request, check_in_id):
    """Resolve one check-in without further action (the queue's dismiss).

    Accepting/dismissing a task and re-running it resolve its check-ins as
    side effects; this endpoint is for clearing an entry the user has simply
    dealt with (read an error, decided a question answer isn't needed).
    """
    check_in = get_object_or_404(AgentCheckIn, id=check_in_id, user=request.user)
    if check_in.status != 'resolved':
        check_in.status = 'resolved'
        check_in.resolved_at = timezone.now()
        check_in.save(update_fields=['status', 'resolved_at'])
    return Response(_serialize_check_in(check_in), status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def conversation_messages(request, conversation_id):
    """Return messages for a conversation."""
    conversation = get_object_or_404(
        AgentConversation, id=conversation_id, user=request.user
    )
    messages = [
        {
            'id': m.id,
            'role': m.role,
            'content': m.content,
            'timestamp': m.created_at.isoformat(),
            'metadata': m.metadata,
        }
        for m in conversation.messages.order_by('created_at')
    ]
    return Response(messages, status=status.HTTP_200_OK)
