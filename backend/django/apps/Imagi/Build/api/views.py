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
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .serializers import (
    ProjectSerializer,
)
from ..models import AgentConversation, AgentMessage
from ..services.base_agent import ImagiAgentService, DEFAULT_MODEL
from ..services.create_file_service import CreateFileService
from ..services.view_file_service import ViewFileService
from ..services.delete_file_service import DeleteFileService
from ..services.models_service import ModelsService, get_default_model_id, get_model_by_id
from ..services.preview_service import PreviewService
from apps.Imagi.ProjectManager.models import Project as PMProject
from apps.Imagi.ProjectManager.services.project_management_service import ProjectManagementService
from apps.Imagi.ProjectManager.services.project_creation_service import ProjectCreationService
from rest_framework.exceptions import NotFound, APIException
from ..services.version_control_service import VersionControlService
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
class ProjectListCreateView(generics.ListCreateAPIView):
    """List all projects or create a new project."""
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PMProject.objects.filter(user=self.request.user, is_active=True).order_by('-updated_at')

    def perform_create(self, serializer):
        try:
            project_creation_service = ProjectCreationService(self.request.user)
            project = project_creation_service.create_project(serializer.validated_data['name'])
            serializer.save(user=self.request.user, project=project)
        except APIException:
            raise
        except Exception:
            logger.exception("Error creating project")
            raise

@method_decorator(never_cache, name='dispatch')
class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a project."""
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        return PMProject.objects.filter(user=self.request.user, is_active=True)

    def perform_destroy(self, instance):
        project_management_service = ProjectManagementService(self.request.user)
        project_management_service.delete_project(instance)

@method_decorator(never_cache, name='dispatch')
class GenerateCodeView(APIView):
    """Generate code using AI models."""
    permission_classes = [IsAuthenticated]

    def get_project(self, project_id):
        """Get a project by ID, ensuring user has access."""
        try:
            return PMProject.objects.get(id=project_id, user=self.request.user, is_active=True)
        except PMProject.DoesNotExist:
            raise NotFound('Project not found')

    def post(self, request, project_id):
        try:
            # Get project
            project = self.get_project(project_id)
            
            # Get request data
            prompt = request.data.get('prompt', '')
            model = request.data.get('model') or get_default_model_id()
            if not get_model_by_id(model):
                model = get_default_model_id()
            file_path = request.data.get('file_path', None)
            
            if not prompt:
                return Response(
                    {'error': 'Prompt is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Process the prompt using models service
            models_service = ModelsService()
            
            # If file_path is provided, get the file content
            file_content = None
            if file_path:
                view_file_service = ViewFileService(project=project)
                try:
                    file_content = view_file_service.get_file_content(file_path)
                except Exception as e:
                    logger.error(f"Error getting file content: {str(e)}")
            
            # Generate code
            response = models_service.generate_code(project, prompt, model, file_content)
            
            return Response(response)
        except APIException:
            raise
        except Exception:
            logger.exception("Error generating code")
            raise

@method_decorator(never_cache, name='dispatch')
class AIModelsView(APIView):
    """Get available AI models."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        models_service = ModelsService()
        models = models_service.get_available_models()
        return Response({'models': models})

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

# Removed old process_input view - use Agents API instead

@method_decorator(never_cache, name='dispatch')
class PreviewView(APIView):
    """Preview a project by starting a development server."""
    permission_classes = [IsAuthenticated]

    def get_project(self, project_id):
        """Get a project by ID, ensuring user has access."""
        try:
            return PMProject.objects.get(id=project_id, user=self.request.user, is_active=True)
        except PMProject.DoesNotExist:
            raise NotFound('Project not found')

    def get(self, request, project_id):
        # Preview spawns local Django + Vite dev servers; only viable when DEBUG is on.
        if not settings.DEBUG:
            return Response({
                'success': False,
                'error': 'Preview server is not available in production.'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        try:
            project = self.get_project(project_id)

            # Materialize the working copy from the database if this
            # environment doesn't have the project files on disk yet.
            try:
                from ..services.project_files_service import ensure_working_copy
                ensure_working_copy(project)
            except Exception as hydrate_err:
                logger.warning(f"Could not ensure working copy before preview: {hydrate_err}")

            preview_service = PreviewService(project)
            result = preview_service.start_preview()

            response_data = {
                'success': result.get('success', False),
                'preview_url': result.get('preview_url'),
                'message': result.get('message', 'Preview server operation completed')
            }

            return Response(response_data)
        except APIException:
            raise
        except Exception as e:
            logger.error(f"Error starting preview server: {str(e)}")
            # Preview is a DEBUG-only feature, so the real reason is safe to
            # surface and saves a trip to the server logs.
            return Response({
                'success': False,
                'error': f'Preview server failed to start: {str(e)}'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    def delete(self, request, project_id):
        try:
            project = self.get_project(project_id)
            
            preview_service = PreviewService(project)
            result = preview_service.stop_preview()
            
            return Response(result)
        except APIException:
            raise
        except Exception:
            logger.exception("Error stopping preview server")
            raise

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
class FileUndoView(APIView):
    """Undo changes to a specific file."""
    permission_classes = [IsAuthenticated]

    def get_project(self, project_id):
        """Get a project by ID, ensuring user has access."""
        try:
            return PMProject.objects.get(id=project_id, user=self.request.user, is_active=True)
        except PMProject.DoesNotExist:
            raise NotFound('Project not found')

    def post(self, request, project_id, file_path):
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
                
            # Get file type based on extension
            import os
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if not file_extension:
                return Response(
                    {'error': 'Cannot determine file type - no extension found'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Call the appropriate service to handle the undo
            project_management_service = ProjectManagementService(request.user)
            
            # Call undo_file_changes with the specific file path
            result = project_management_service.undo_file_changes(project, file_path)
            
            # After a successful undo, refresh the file list
            if result.get('success', False):
                # Also update the file content with the undone version
                view_file_service = ViewFileService(project=project)
                if 'content' in result:
                    # Overwrite the file with the undone content
                    view_file_service.update_file(file_path, result['content'])
            
            return Response(result)
        except APIException:
            raise
        except Exception:
            logger.exception("Error undoing file changes")
            raise

@method_decorator(never_cache, name='dispatch')
class AnalyzeTemplateView(APIView):
    """Analyze template content and structure."""
    permission_classes = [IsAuthenticated]

    def get_project(self, project_id):
        """Get a project by ID, ensuring user has access."""
        try:
            return PMProject.objects.get(id=project_id, user=self.request.user, is_active=True)
        except PMProject.DoesNotExist:
            raise NotFound('Project not found')

    def post(self, request):
        try:
            # Get template content from request
            template_content = request.data.get('template_content', '')
            template_name = request.data.get('template_name', 'template.html')
            
            if not template_content:
                return Response(
                    {'error': 'Template content is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Basic validation - implement advanced validation via OpenAI Agents SDK if needed
            response_data = {
                'is_valid': bool(template_content and len(template_content.strip()) > 0),
                'template_name': template_name,
            }
            
            return Response(response_data)
            
        except APIException:
            raise
        except Exception:
            logger.exception("Error analyzing template")
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


@api_view(['OPTIONS'])
@csrf_exempt
def cors_preflight(request):
    """Handle OPTIONS requests for CORS preflight checks."""
    response = Response()
    return add_cors_headers(response)


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


# ---------------------------------------------------------------------------
# Conversation (agent instance) CRUD
# ---------------------------------------------------------------------------

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
        'archived_at': conversation.archived_at.isoformat() if conversation.archived_at else None,
        'created_at': conversation.created_at.isoformat(),
        'updated_at': conversation.updated_at.isoformat(),
        'last_message_preview': preview,
    }


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

        agent_service = ImagiAgentService(model=model_name)
        conversation = agent_service.create_conversation(
            user=request.user,
            model=model_name,
            project_id=project_id,
            title=title,
        )
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
        conversation.archived_at = timezone.now() if archived else None
        updated_fields.append('archived_at')

    if updated_fields:
        conversation.save(update_fields=updated_fields + ['updated_at'])

    return Response(_serialize_conversation(conversation), status=status.HTTP_200_OK)


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
        }
        for m in conversation.messages.order_by('created_at')
    ]
    return Response(messages, status=status.HTTP_200_OK)
