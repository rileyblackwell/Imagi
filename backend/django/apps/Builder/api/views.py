"""
API views for the Builder app.
"""

from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.conf import settings
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator

from ..models import Project, Conversation, Page, Message
from .serializers import (
    ProjectSerializer,
    ProjectDetailSerializer,
    ConversationSerializer,
    PageSerializer,
    MessageSerializer
)
from ..services.oasis_service import (
    process_builder_mode_input_service,
    undo_last_action_service,
    process_chat_mode_input_service
)
from apps.ProjectManager.services import ProjectGenerationService
from ..services.project_service import ProjectService
from ..services.ai_service import AIService
from ..services.file_service import FileService
from ..views import BuilderView

import logging
logger = logging.getLogger(__name__)

@method_decorator(never_cache, name='dispatch')
class ProjectListCreateView(generics.ListCreateAPIView, BuilderView):
    """List all projects or create a new project."""
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user, is_active=True).order_by('-updated_at')

    def perform_create(self, serializer):
        try:
            project_service = ProjectService(self.request.user)
            project = project_service.create_project(serializer.validated_data['name'])
            serializer.save(user=self.request.user, project=project)
        except Exception as e:
            logger.error(f"Error creating project: {str(e)}")
            raise

@method_decorator(never_cache, name='dispatch')
class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView, BuilderView):
    """Retrieve, update or delete a project."""
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user, is_active=True)

    def perform_destroy(self, instance):
        project_service = ProjectService(self.request.user)
        project_service.delete_project(instance)

@method_decorator(never_cache, name='dispatch')
class ProjectFilesView(APIView, BuilderView):
    """List all files in a project."""
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        project = get_object_or_404(Project, id=project_id, user=request.user)
        file_service = FileService(project)
        files = file_service.list_files()
        return Response(files)

@method_decorator(never_cache, name='dispatch')
class GenerateCodeView(APIView, BuilderView):
    """Generate code using AI models."""
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id, user=request.user)
        
        # Get request data
        prompt = request.data.get('prompt')
        model = request.data.get('model', 'claude-3-5-sonnet-20241022')
        file_path = request.data.get('file_path')
        mode = request.data.get('mode', 'build')
        
        if not prompt:
            return Response(
                {'error': 'Prompt is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if not file_path:
            return Response(
                {'error': 'File path is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            ai_service = AIService()
            result = ai_service.generate_code(
                project=project,
                prompt=prompt,
                model=model,
                file_path=file_path
            )
            
            if mode == 'build':
                # Update the file content
                file_service = FileService(project)
                file_service.update_file(
                    file_path=file_path,
                    content=result['content'],
                    commit_message=f'Update {file_path} via AI generation'
                )
            
            return Response(result)
        except Exception as e:
            logger.error(f"Error generating code: {str(e)}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@method_decorator(never_cache, name='dispatch')
class UndoActionView(APIView, BuilderView):
    """Undo last action in a project."""
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id, user=request.user)
        
        try:
            project_service = ProjectService(request.user)
            result = project_service.undo_last_action(project)
            return Response(result)
        except Exception as e:
            logger.error(f"Error undoing action: {str(e)}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@method_decorator(never_cache, name='dispatch')
class AIModelsView(APIView, BuilderView):
    """Get available AI models."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        models = [
            {
                'id': 'claude-3-5-sonnet-20241022',
                'name': 'Claude 3.5 Sonnet',
                'description': 'Anthropic\'s Claude 3.5 Sonnet model',
                'type': 'anthropic'
            },
            {
                'id': 'gpt-4o',
                'name': 'GPT-4o',
                'description': 'OpenAI\'s GPT-4 model',
                'type': 'openai'
            },
            {
                'id': 'gpt-4o-mini',
                'name': 'GPT-4o Mini',
                'description': 'OpenAI\'s GPT-4 Mini model',
                'type': 'openai'
            }
        ]
        return Response(models)

@method_decorator(never_cache, name='dispatch')
class FileDetailView(APIView, BuilderView):
    """Get or update file details."""
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id, file_path):
        project = get_object_or_404(Project, id=project_id, user=request.user)
        file_service = FileService(project)
        file_details = file_service.get_file_details(file_path)
        return Response(file_details)

    def put(self, request, project_id, file_path):
        project = get_object_or_404(Project, id=project_id, user=request.user)
        file_service = FileService(project)
        
        try:
            result = file_service.update_file(
                file_path=file_path,
                content=request.data.get('content'),
                commit_message=request.data.get('commit_message', 'Update file')
            )
            return Response(result)
        except Exception as e:
            logger.error(f"Error updating file: {str(e)}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@method_decorator(never_cache, name='dispatch')
class FileContentView(APIView, BuilderView):
    """Get file content."""
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id, file_path):
        project = get_object_or_404(Project, id=project_id, user=request.user)
        file_service = FileService(project)
        content = file_service.get_file_content(file_path)
        return Response({'content': content})

class ConversationListView(generics.ListAPIView):
    """List conversations for a project."""
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        project_name = self.kwargs['project_name']
        project = get_object_or_404(Project, user=self.request.user, name=project_name)
        return Conversation.objects.filter(project=project)

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
            
        conversation = get_object_or_404(
            Conversation, 
            id=conversation_id,
            user=request.user
        )
        
        Message.objects.filter(conversation=conversation).delete()
        Page.objects.filter(conversation=conversation).delete()
        
        return Response({'message': 'Conversation cleared successfully'})
        
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
        
        return get_object_or_404(
            Page,
            conversation__id=conversation_id,
            conversation__user=self.request.user,
            filename=filename
        ) 