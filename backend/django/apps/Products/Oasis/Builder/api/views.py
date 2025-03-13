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
from rest_framework.exceptions import NotFound

from ..models import Project, Conversation, Page, Message
from .serializers import (
    ProjectSerializer,
    ConversationSerializer,
    PageSerializer,
)
from ..services.oasis_service import (
    process_builder_mode_input_service,
    undo_last_action_service,
    process_chat_mode_input_service
)
from apps.Products.Oasis.ProjectManager.services.project_creation_service import ProjectCreationService
from apps.Products.Oasis.ProjectManager.services.project_management_service import ProjectManagementService
from ..services.ai_service import AIService
from ..services.file_service import FileService
from ..services.dev_server_service import DevServerManager
from ..views import BuilderView

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
            project_service = ProjectCreationService(self.request.user)
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
        project_service = ProjectManagementService(self.request.user)
        project_service.delete_project(instance)

@method_decorator(never_cache, name='dispatch')
class ProjectFilesView(APIView, BuilderView):
    """List all files in a project."""
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        try:
            # First try to get the project from the Builder app
            project = Project.objects.get(id=project_id, user=request.user, is_active=True)
        except Project.DoesNotExist:
            # If not found, try to get it from the ProjectManager app
            try:
                from apps.Products.Oasis.ProjectManager.models import Project as PMProject
                pm_project = PMProject.objects.get(id=project_id, user=request.user, is_active=True)
                
                # Create a corresponding project in the Builder app if it doesn't exist
                project, created = Project.objects.get_or_create(
                    id=pm_project.id,
                    defaults={
                        'name': pm_project.name,
                        'description': pm_project.description,
                        'user': request.user,
                        'is_active': True
                    }
                )
                
                if created:
                    logger.info(f"Created Builder project from ProjectManager project: {project.id}")
            except PMProject.DoesNotExist:
                raise NotFound('Project not found')
        
        file_service = FileService(project=project)
        files = file_service.list_files()
        return Response(files)

@method_decorator(never_cache, name='dispatch')
class GenerateCodeView(APIView, BuilderView):
    """Generate code using AI models."""
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id):
        try:
            # Get project
            project = get_object_or_404(Project, id=project_id, user=request.user, is_active=True)
            
            # Get request data
            prompt = request.data.get('prompt', '')
            model = request.data.get('model', 'gpt-4')
            file_path = request.data.get('file_path', None)
            
            if not prompt:
                return Response(
                    {'error': 'Prompt is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Process the prompt
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
            response = ai_service.generate_code(prompt, model, file_content)
            
            return Response(response)
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
            project_service = ProjectManagementService(request.user)
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
                'provider': 'anthropic',
                'type': 'anthropic',
                'description': 'Anthropic\'s most capable model, best for complex tasks and creative work.',
                'capabilities': ['code_generation', 'chat', 'analysis'],
                'maxTokens': 200000,
                'costPerRequest': 0.03
            },
            {
                'id': 'gpt-4o',
                'name': 'GPT-4o',
                'provider': 'openai',
                'type': 'openai',
                'description': 'OpenAI\'s most capable model, excellent for complex reasoning and creative tasks.',
                'capabilities': ['code_generation', 'chat', 'analysis'],
                'maxTokens': 128000,
                'costPerRequest': 0.04
            },
            {
                'id': 'gpt-4o-mini',
                'name': 'GPT-4o Mini',
                'provider': 'openai',
                'type': 'openai',
                'description': 'A more cost-effective version of GPT-4o, good for simpler tasks.',
                'capabilities': ['code_generation', 'chat', 'analysis'],
                'maxTokens': 128000,
                'costPerRequest': 0.01
            }
        ]
        return Response(models)

@method_decorator(never_cache, name='dispatch')
class FileDetailView(APIView, BuilderView):
    """Get or update file details."""
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id, file_path):
        try:
            # First try to get the project from the Builder app
            project = Project.objects.get(id=project_id, user=request.user, is_active=True)
        except Project.DoesNotExist:
            # If not found, try to get it from the ProjectManager app
            try:
                from apps.Products.Oasis.ProjectManager.models import Project as PMProject
                pm_project = PMProject.objects.get(id=project_id, user=request.user, is_active=True)
                
                # Create a corresponding project in the Builder app if it doesn't exist
                project, created = Project.objects.get_or_create(
                    id=pm_project.id,
                    defaults={
                        'name': pm_project.name,
                        'description': pm_project.description,
                        'user': request.user,
                        'is_active': True
                    }
                )
                
                if created:
                    logger.info(f"Created Builder project from ProjectManager project: {project.id}")
            except PMProject.DoesNotExist:
                raise NotFound('Project not found')
        
        file_service = FileService(project=project)
        file_details = file_service.get_file_details(file_path)
        return Response(file_details)

    def put(self, request, project_id, file_path):
        try:
            try:
                # First try to get the project from the Builder app
                project = Project.objects.get(id=project_id, user=request.user, is_active=True)
            except Project.DoesNotExist:
                # If not found, try to get it from the ProjectManager app
                try:
                    from apps.Products.Oasis.ProjectManager.models import Project as PMProject
                    pm_project = PMProject.objects.get(id=project_id, user=request.user, is_active=True)
                    
                    # Create a corresponding project in the Builder app if it doesn't exist
                    project, created = Project.objects.get_or_create(
                        id=pm_project.id,
                        defaults={
                            'name': pm_project.name,
                            'description': pm_project.description,
                            'user': request.user,
                            'is_active': True
                        }
                    )
                    
                    if created:
                        logger.info(f"Created Builder project from ProjectManager project: {project.id}")
                except PMProject.DoesNotExist:
                    raise NotFound('Project not found')
            
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

@method_decorator(never_cache, name='dispatch')
class FileContentView(APIView, BuilderView):
    """Get file content."""
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id, file_path):
        try:
            # First try to get the project from the Builder app
            project = Project.objects.get(id=project_id, user=request.user, is_active=True)
        except Project.DoesNotExist:
            # If not found, try to get it from the ProjectManager app
            try:
                from apps.Products.Oasis.ProjectManager.models import Project as PMProject
                pm_project = PMProject.objects.get(id=project_id, user=request.user, is_active=True)
                
                # Create a corresponding project in the Builder app if it doesn't exist
                project, created = Project.objects.get_or_create(
                    id=pm_project.id,
                    defaults={
                        'name': pm_project.name,
                        'description': pm_project.description,
                        'user': request.user,
                        'is_active': True
                    }
                )
                
                if created:
                    logger.info(f"Created Builder project from ProjectManager project: {project.id}")
            except PMProject.DoesNotExist:
                raise NotFound('Project not found')
        
        file_service = FileService(project=project)
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

@method_decorator(never_cache, name='dispatch')
class PreviewView(APIView, BuilderView):
    """Preview a project by starting a development server."""
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        try:
            project = get_object_or_404(Project, id=project_id, user=request.user, is_active=True)
            
            # Start the development server
            dev_server = DevServerManager(project)
            server_url = dev_server.get_server_url()
            
            return Response({
                'success': True,
                'preview_url': server_url,
                'message': 'Development server started successfully'
            })
        except Exception as e:
            logger.error(f"Error starting preview server: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, project_id):
        try:
            project = get_object_or_404(Project, id=project_id, user=request.user, is_active=True)
            
            # Stop the development server
            dev_server = DevServerManager(project)
            dev_server.stop_server()
            
            return Response({
                'success': True,
                'message': 'Development server stopped successfully'
            })
        except Exception as e:
            logger.error(f"Error stopping preview server: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)