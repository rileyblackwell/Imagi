"""
Undo Service for removing the last AI interaction with a file.

This service handles undoing the last user prompt and AI response for a specific file,
reverting the file back to its previous state.
"""

import logging
from django.shortcuts import get_object_or_404
from django.db.models import Q
from ..models import Conversation, Page, Message
from apps.Products.Oasis.ProjectManager.models import Project as PMProject
from apps.Products.Oasis.Agents.models import AgentConversation, AgentMessage

logger = logging.getLogger(__name__)

class UndoService:
    """
    Service for undoing the last AI interaction with a file.
    """
    
    def __init__(self, project=None):
        self.project = project
        
    def undo_last_interaction(self, user, project_id, file_path):
        """
        Undo the last AI interaction (user prompt and AI response) for a specific file.
        
        Args:
            user: The user making the request
            project_id (int): The ID of the project
            file_path (str): The path of the file to undo changes for
            
        Returns:
            dict: Result of the operation containing success status and message
        """
        try:
            # Get the project
            project = get_object_or_404(PMProject, id=project_id, user=user)
            
            # Try to undo in Builder's conversation first
            builder_result = self._undo_builder_message(user, project_id, file_path)
            
            # If no Builder messages found, try Agents conversation
            if not builder_result.get('success'):
                agents_result = self._undo_agent_message(user, project_id, file_path)
                if agents_result.get('success'):
                    return {
                        'success': True,
                        'message': 'Successfully undid the last AI interaction.',
                        'details': agents_result.get('details', {})
                    }
                else:
                    return {
                        'success': False,
                        'error': 'No AI interactions found for this file.',
                        'details': {
                            'builder': builder_result.get('error'),
                            'agents': agents_result.get('error')
                        }
                    }
            
            return {
                'success': True,
                'message': 'Successfully undid the last AI interaction.',
                'details': builder_result.get('details', {})
            }
            
        except Exception as e:
            logger.error(f"Error undoing last interaction: {str(e)}")
            return {
                'success': False,
                'error': f"Failed to undo the last interaction: {str(e)}"
            }
    
    def _undo_builder_message(self, user, project_id, file_path):
        """
        Undo the last AI interaction in the Builder app.
        
        Args:
            user: The user making the request
            project_id (int): The ID of the project
            file_path (str): The path of the file to undo changes for
            
        Returns:
            dict: Result of the operation containing success status and message
        """
        try:
            # Find the conversation for this project
            conversation = Conversation.objects.filter(
                user=user,
                project_id=project_id
            ).first()
            
            if not conversation:
                return {
                    'success': False,
                    'error': 'No conversation found for this project.'
                }
            
            # Find the page (file) in the conversation
            filename = file_path.split('/')[-1] if '/' in file_path else file_path
            page = Page.objects.filter(
                conversation=conversation,
                filename=filename
            ).first()
            
            if not page:
                return {
                    'success': False,
                    'error': f'No page found for file {filename}.'
                }
            
            # Find the last assistant message and its corresponding user message
            last_assistant_message = Message.objects.filter(
                conversation=conversation,
                page=page,
                role='assistant'
            ).order_by('-created_at').first()
            
            if not last_assistant_message:
                return {
                    'success': False,
                    'error': 'No assistant message found to undo.'
                }
            
            # Find the most recent user message that came before this assistant message
            last_user_message = Message.objects.filter(
                conversation=conversation,
                page=page,
                role='user',
                created_at__lt=last_assistant_message.created_at
            ).order_by('-created_at').first()
            
            # Delete the assistant message
            assistant_message_content = last_assistant_message.content
            last_assistant_message.delete()
            
            # Delete the user message if found
            user_message_content = None
            if last_user_message:
                user_message_content = last_user_message.content
                last_user_message.delete()
            
            return {
                'success': True,
                'message': 'Successfully undid the last AI interaction.',
                'details': {
                    'removed_user_message': user_message_content,
                    'removed_assistant_message': assistant_message_content
                }
            }
            
        except Exception as e:
            logger.error(f"Error undoing builder message: {str(e)}")
            return {
                'success': False,
                'error': f"Failed to undo builder message: {str(e)}"
            }
    
    def _undo_agent_message(self, user, project_id, file_path):
        """
        Undo the last AI interaction in the Agents app.
        
        Args:
            user: The user making the request
            project_id (int): The ID of the project
            file_path (str): The path of the file to undo changes for
            
        Returns:
            dict: Result of the operation containing success status and message
        """
        try:
            # Find the conversation for this project
            # This might be trickier as the Agents app doesn't directly link conversations to projects
            # We might need to find the most recent conversation for this user
            conversations = AgentConversation.objects.filter(
                user=user
            ).order_by('-created_at')
            
            if not conversations:
                return {
                    'success': False,
                    'error': 'No agent conversations found for this user.'
                }
            
            # Get the file name from the path
            filename = file_path.split('/')[-1] if '/' in file_path else file_path
            
            # Find the most recent conversation that has messages related to this file
            for conversation in conversations:
                # Find the last assistant message that mentions this file
                last_assistant_message = AgentMessage.objects.filter(
                    conversation=conversation,
                    role='assistant',
                    content__contains=filename
                ).order_by('-created_at').first()
                
                if last_assistant_message:
                    # Find the most recent user message that came before this assistant message
                    last_user_message = AgentMessage.objects.filter(
                        conversation=conversation,
                        role='user',
                        created_at__lt=last_assistant_message.created_at
                    ).order_by('-created_at').first()
                    
                    # Delete the assistant message
                    assistant_message_content = last_assistant_message.content
                    last_assistant_message.delete()
                    
                    # Delete the user message if found
                    user_message_content = None
                    if last_user_message:
                        user_message_content = last_user_message.content
                        last_user_message.delete()
                    
                    return {
                        'success': True,
                        'message': 'Successfully undid the last agent AI interaction.',
                        'details': {
                            'removed_user_message': user_message_content,
                            'removed_assistant_message': assistant_message_content
                        }
                    }
            
            return {
                'success': False,
                'error': f'No agent messages found for file {filename}.'
            }
            
        except Exception as e:
            logger.error(f"Error undoing agent message: {str(e)}")
            return {
                'success': False,
                'error': f"Failed to undo agent message: {str(e)}"
            } 