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

import logging
logger = logging.getLogger(__name__)

class ProjectListCreateView(generics.ListCreateAPIView):
    """List all projects or create a new project."""
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user).order_by('-updated_at')

    def perform_create(self, serializer):
        try:
            # Create Django project using ProjectManager service
            service = ProjectGenerationService(self.request.user)
            user_project = service.create_project(serializer.validated_data['name'])
            
            # Create the Project instance
            project = serializer.save(
                user=self.request.user,
                user_project=user_project
            )
            
            # Create initial conversation
            Conversation.objects.create(
                user=self.request.user,
                project=project
            )
            
        except Exception as e:
            logger.error(f"Error creating project: {str(e)}")
            raise

class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a project."""
    serializer_class = ProjectDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'name'
    lookup_url_kwarg = 'project_name'

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user)
    
    def get_object(self):
        queryset = self.get_queryset()
        project_name = self.kwargs[self.lookup_url_kwarg]
        
        # Find project by URL-safe name
        for project in queryset:
            if project.get_url_safe_name() == project_name:
                return project
        return None

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