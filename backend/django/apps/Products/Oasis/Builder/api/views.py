"""
API views for the Builder app.
"""

import logging
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator

from ..models import Conversation
from .serializers import (
    ProjectSerializer,
    ConversationSerializer,
    PageSerializer,
    MessageSerializer
)
from ..services.file_service import FileService
from ..services.models_service import ModelsService
from ..services.conversation_service import ConversationService
from ..services.preview_service import PreviewService
from ..services.ai_service import AIService
from ..services.oasis_service import (
    process_builder_mode_input_service,
    undo_last_action_service,
    process_chat_mode_input_service
)
from apps.Products.Oasis.ProjectManager.models import Project as PMProject
from apps.Products.Oasis.ProjectManager.services.project_management_service import ProjectManagementService
from apps.Products.Oasis.ProjectManager.services.project_creation_service import ProjectCreationService
from rest_framework.exceptions import NotFound

logger = logging.getLogger(__name__)

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
        except Exception as e:
            logger.error(f"Error creating project: {str(e)}")
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
class ProjectFilesView(APIView):
    """List all files in a project."""
    permission_classes = [IsAuthenticated]

    def get_project(self, project_id):
        """Get a project by ID, ensuring user has access."""
        try:
            return PMProject.objects.get(id=project_id, user=self.request.user, is_active=True)
        except PMProject.DoesNotExist:
            raise NotFound('Project not found')

    def get(self, request, project_id):
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
            
            file_service = FileService(project=project)
            files = file_service.list_files()
            return Response(files)
        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request, project_id):
        try:
            # Get project from ProjectManager
            project = self.get_project(project_id)
            
            # Create file using the Builder's FileService
            file_service = FileService(project=project)
            file_data = request.data
            result = file_service.create_file(file_data)
            return Response(result, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error creating file: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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
            model = request.data.get('model', 'gpt-4')
            file_path = request.data.get('file_path', None)
            
            if not prompt:
                return Response(
                    {'error': 'Prompt is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Process the prompt using AI service
            ai_service = AIService()
            
            # If file_path is provided, get the file content
            file_content = None
            if file_path:
                file_service = FileService(project=project)
                try:
                    file_content = file_service.get_file_content(file_path)
                except Exception as e:
                    logger.error(f"Error getting file content: {str(e)}")
            
            # Generate code
            response = ai_service.generate_code(project, prompt, model, file_content)
            
            return Response(response)
        except Exception as e:
            logger.error(f"Error generating code: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@method_decorator(never_cache, name='dispatch')
class UndoActionView(APIView):
    """Undo last action in a project."""
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
            project_management_service = ProjectManagementService(request.user)
            result = project_management_service.undo_last_action(project)
            return Response(result)
        except Exception as e:
            logger.error(f"Error undoing action: {str(e)}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@method_decorator(never_cache, name='dispatch')
class AIModelsView(APIView):
    """Get available AI models."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        models_service = ModelsService()
        models = models_service.get_available_models()
        return Response(models)

@method_decorator(never_cache, name='dispatch')
class FileDetailView(APIView):
    """Get or update file details."""
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
            
            file_service = FileService(project=project)
            file_details = file_service.get_file_details(file_path)
            return Response(file_details)
        except Exception as e:
            logger.error(f"Error getting file details: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, project_id, file_path):
        try:
            # Get project from ProjectManager
            project = self.get_project(project_id)
            
            file_service = FileService(project=project)
            
            content = request.data.get('content', '')
            if not content:
                return Response(
                    {'error': 'Content is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            result = file_service.update_file(file_path, content)
            return Response(result)
        except Exception as e:
            logger.error(f"Error updating file: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, project_id, file_path):
        try:
            # Get project from ProjectManager
            project = self.get_project(project_id)
            
            file_service = FileService(project=project)
            result = file_service.delete_file(file_path)
            return Response(result)
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@method_decorator(never_cache, name='dispatch')
class FileContentView(APIView):
    """Get file content."""
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
            
            file_service = FileService(project=project)
            content = file_service.get_file_content(file_path)
            return Response({'content': content})
        except Exception as e:
            logger.error(f"Error getting file content: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ConversationListView(generics.ListAPIView):
    """List conversations for a project."""
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        project_name = self.kwargs['project_name']
        conversation_service = ConversationService(self.request.user)
        return conversation_service.list_conversations(project_name)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_input(request):
    """Handle file generation requests."""
    try:
        user_input = request.data.get('user_input')
        model = request.data.get('model', 'claude-3-5-sonnet-20241022')
        file_name = request.data.get('file')
        mode = request.data.get('mode', 'build')
        
        if not all([user_input, file_name]):
            return Response({
                'error': 'Missing required fields'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if mode == 'chat':
            response = process_chat_mode_input_service(
                user_input, model, request.user
            )
        else:
            response = process_builder_mode_input_service(
                user_input, model, file_name, request.user
            )
        
        if not response['success'] and response.get('error') == 'insufficient_credits':
            return Response({
                'success': False,
                'error': 'Insufficient credits',
                'required_credits': response.get('required_credits', 1.0),
                'redirect_url': response.get('redirect_url')
            }, status=status.HTTP_402_PAYMENT_REQUIRED)
        
        return Response(response)
        
    except Exception as e:
        logger.error(f"Error processing input: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def undo_last_action(request):
    """Undo the last action in a conversation."""
    try:
        conversation_id = request.data.get('conversation_id')
        if not conversation_id:
            return Response({
                'error': 'Missing conversation_id'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        response = undo_last_action_service(conversation_id)
        return Response(response)
        
    except Exception as e:
        logger.error(f"Error undoing last action: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clear_conversation(request):
    """Clear all messages in a conversation."""
    try:
        conversation_id = request.data.get('conversation_id')
        if not conversation_id:
            return Response({
                'error': 'Missing conversation_id'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        conversation_service = ConversationService(request.user)
        result = conversation_service.clear_conversation(conversation_id)
        return Response(result)
        
    except Exception as e:
        logger.error(f"Error clearing conversation: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PageView(generics.RetrieveAPIView):
    """Retrieve a specific page and its messages."""
    serializer_class = PageSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        conversation_id = self.kwargs.get('conversation_id')
        filename = self.kwargs.get('filename')
        
        conversation_service = ConversationService(self.request.user)
        return conversation_service.get_page(conversation_id, filename)

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
        try:
            project = self.get_project(project_id)
            
            preview_service = PreviewService(project)
            result = preview_service.start_preview()
            
            return Response(result)
        except Exception as e:
            logger.error(f"Error starting preview server: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, project_id):
        try:
            project = self.get_project(project_id)
            
            preview_service = PreviewService(project)
            result = preview_service.stop_preview()
            
            return Response(result)
        except Exception as e:
            logger.error(f"Error stopping preview server: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)