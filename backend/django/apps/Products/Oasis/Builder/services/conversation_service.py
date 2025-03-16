"""
Service for conversation operations in the Builder app.
"""

import logging
from django.shortcuts import get_object_or_404
from ..models import Conversation, Page, Message
from apps.Products.Oasis.ProjectManager.models import Project as PMProject

logger = logging.getLogger(__name__)

class ConversationService:
    """Service for conversation operations."""
    
    def __init__(self, user):
        self.user = user
    
    def list_conversations(self, project_name):
        """List all conversations for a project."""
        project = get_object_or_404(PMProject, user=self.user, name=project_name)
        return Conversation.objects.filter(project=project)
    
    def get_page(self, conversation_id, filename):
        """Get a specific page by conversation ID and filename."""
        return get_object_or_404(
            Page,
            conversation__id=conversation_id,
            conversation__user=self.user,
            filename=filename
        )
    
    def clear_conversation(self, conversation_id):
        """Clear all messages in a conversation."""
        try:
            conversation = get_object_or_404(
                Conversation, 
                id=conversation_id,
                user=self.user
            )
            
            Message.objects.filter(conversation=conversation).delete()
            Page.objects.filter(conversation=conversation).delete()
            
            return {"message": "Conversation cleared successfully"}
        except Exception as e:
            logger.error(f"Error clearing conversation: {str(e)}")
            raise 