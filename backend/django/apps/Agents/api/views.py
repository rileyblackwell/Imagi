"""
API views for the Agents app.
"""

import logging
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import transaction

from ..models import AgentConversation, SystemPrompt, AgentMessage
from .serializers import (
    AgentConversationSerializer,
    SystemPromptSerializer,
    AgentMessageSerializer,
    ConversationHistorySerializer
)
from ..services.agent_service import build_conversation_history
from ..services.template_agent_service import TemplateAgentService

logger = logging.getLogger(__name__)

class ConversationListCreateView(generics.ListCreateAPIView):
    """List all conversations or create a new conversation."""
    serializer_class = AgentConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return AgentConversation.objects.filter(
            user=self.request.user
        ).order_by('-created_at')

    def perform_create(self, serializer):
        conversation = serializer.save(user=self.request.user)
        
        # Create initial system prompt
        template_agent = TemplateAgentService()
        system_prompt = template_agent.get_system_prompt()
        
        SystemPrompt.objects.create(
            conversation=conversation,
            content=system_prompt['content']
        )

class ConversationDetailView(generics.RetrieveDestroyAPIView):
    """Retrieve or delete a conversation."""
    serializer_class = ConversationHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return AgentConversation.objects.filter(user=self.request.user)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request):
    """Send a message to the agent and get a response."""
    try:
        conversation_id = request.data.get('conversation_id')
        user_input = request.data.get('message')
        model = request.data.get('model', 'claude-3-5-sonnet-20241022')
        
        if not all([conversation_id, user_input]):
            return Response({
                'error': 'Missing required fields'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get conversation
        conversation = get_object_or_404(
            AgentConversation,
            id=conversation_id,
            user=request.user
        )
        
        # Save user message
        user_message = AgentMessage.objects.create(
            conversation=conversation,
            role='user',
            content=user_input
        )
        
        # Build conversation history
        history = build_conversation_history(conversation)
        
        # Get agent response
        template_agent = TemplateAgentService()
        response = template_agent.process_message(
            user_input=user_input,
            model=model,
            conversation_history=history
        )
        
        # Save agent response
        assistant_message = AgentMessage.objects.create(
            conversation=conversation,
            role='assistant',
            content=response
        )
        
        return Response({
            'user_message': AgentMessageSerializer(user_message).data,
            'assistant_message': AgentMessageSerializer(assistant_message).data
        })
        
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clear_conversation(request):
    """Clear all messages from a conversation."""
    try:
        conversation_id = request.data.get('conversation_id')
        if not conversation_id:
            return Response({
                'error': 'Missing conversation_id'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        conversation = get_object_or_404(
            AgentConversation,
            id=conversation_id,
            user=request.user
        )
        
        # Delete all messages except system prompt
        AgentMessage.objects.filter(
            conversation=conversation
        ).exclude(
            role='system'
        ).delete()
        
        return Response({
            'message': 'Conversation cleared successfully'
        })
        
    except Exception as e:
        logger.error(f"Error clearing conversation: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_system_prompt(request):
    """Update the system prompt for a conversation."""
    try:
        conversation_id = request.data.get('conversation_id')
        new_prompt = request.data.get('prompt')
        
        if not all([conversation_id, new_prompt]):
            return Response({
                'error': 'Missing required fields'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        conversation = get_object_or_404(
            AgentConversation,
            id=conversation_id,
            user=request.user
        )
        
        system_prompt = conversation.system_prompt
        system_prompt.content = new_prompt
        system_prompt.save()
        
        return Response(SystemPromptSerializer(system_prompt).data)
        
    except Exception as e:
        logger.error(f"Error updating system prompt: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 