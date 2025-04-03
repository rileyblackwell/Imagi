"""
Chat agent service for Imagi Oasis.

This module provides a specialized agent service for chat-based interactions,
allowing users to have natural language conversations about their web applications.
"""

import logging
from dotenv import load_dotenv
from .agent_service import BaseAgentService
from apps.Payments.services import PaymentService
from django.utils import timezone

# Load environment variables from .env
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class ChatAgentService(BaseAgentService):
    """
    Specialized agent service for chat-based interactions.
    
    This service handles natural language conversations with users about their
    web applications, providing explanations, suggestions, and guidance.
    """
    
    def __init__(self):
        """Initialize the chat agent service"""
        super().__init__()
        self.payment_service = PaymentService()
    
    def get_system_prompt(self):
        """
        Get the system prompt for chat interactions.
        
        Returns:
            dict: A message dictionary with 'role' and 'content' keys
        """
        return {
            "role": "system",
            "content": (
                "You are an expert web designer and developer working within Imagi Oasis, a powerful platform for building web applications. "
                "Your role is to help users understand, design, and improve their web applications through natural conversation.\n\n"
                
                "Key Responsibilities:\n"
                "1. Help users understand their current website structure and design choices.\n"
                "2. Provide clear explanations about Django templates, CSS styling, and web design best practices.\n"
                "3. Suggest improvements and answer questions about the user's web application.\n"
                "4. Maintain context of the entire project while discussing specific files.\n\n"
                
                "Guidelines:\n"
                "1. Always reference the current state of files when discussing them.\n"
                "2. Provide specific, actionable suggestions for improvements.\n"
                "3. Explain technical concepts in a clear, accessible way.\n"
                "4. Consider the entire project context when making recommendations.\n"
                "5. Focus on modern web design principles and best practices.\n\n"
                
                "Remember:\n"
                "- You don't need to prefix your responses with 'As a web development assistant' or similar phrases.\n"
                "- Give direct, practical advice rather than general platitudes.\n"
                "- If you're not sure about something, say so rather than making up information.\n"
                "- Use markdown for formatting when it enhances clarity.\n"
            )
        }
    
    def validate_response(self, content):
        """
        Validate chat response.
        No specific validation needed for chat responses.
        
        Args:
            content (str): The response content to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        return True, None

    def process_message(self, user_input, model_id, user, conversation_id=None, project_id=None, current_file=None, is_build_mode=False):
        """
        Process a chat message and generate a response.
        
        Args:
            user_input (str): The user's input message
            model_id (str): The model identifier to use
            user (User): The user object
            conversation_id (str, optional): The conversation ID
            project_id (str, optional): The project ID
            current_file (dict, optional): The current file
            is_build_mode (bool, optional): Whether we're in build mode
            
        Returns:
            dict: The response data including the AI's response
        """
        try:
            # Check user credits before proceeding
            has_credits, required_amount = self.check_user_credits(user, model_id)
            if not has_credits:
                return {
                    'success': False,
                    'error': f"Insufficient credits: You need ${required_amount:.2f} more to use {model_id}. Please add more credits."
                }
            
            # Get project path from project_id if provided
            project_path = None
            if project_id:
                try:
                    from apps.Products.Oasis.ProjectManager.models import Project
                    project = Project.objects.get(id=project_id, user=user)
                    project_path = project.project_path
                    logger.info(f"Found project path: {project_path}")
                except Exception as e:
                    logger.warning(f"Could not get project path from project_id {project_id}: {str(e)}")
            
            # Validate current file format if provided
            if current_file:
                is_valid, error_response = self.validate_current_file(current_file)
                if not is_valid:
                    return error_response
            
            # Use process_conversation from BaseAgentService
            result = self.process_conversation(
                user_input=user_input,
                model=model_id,
                user=user,
                conversation_id=conversation_id,
                project_path=project_path,
                current_file=current_file
            )
            
            # Add timestamp to result if successful
            if result.get('success', False):
                result['timestamp'] = timezone.now().isoformat()
            
            return result
            
        except Exception as e:
            logger.error(f"Error in process_message: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': str(e)
            }
    
    def validate_current_file(self, current_file):
        """
        Validate the current file format and required fields.
        
        Args:
            current_file (dict): The current file data
            
        Returns:
            tuple: (is_valid, error_response)
            - is_valid: True if validation succeeds, False otherwise
            - error_response: Error dict if validation fails, None otherwise
        """
        if not isinstance(current_file, dict):
            logger.error(f"Invalid current_file format: {current_file}")
            return False, {
                'success': False,
                'error': 'current_file must be a dictionary with path, content, and type'
            }
        
        required_fields = ['path', 'type']
        missing_required = [field for field in required_fields if field not in current_file]
        if missing_required:
            logger.error(f"Missing required fields in current_file: {missing_required}")
            return False, {
                'success': False,
                'error': f"current_file must contain {', '.join(required_fields)} fields"
            }
        
        # If content is not provided, we'll fetch it later if needed
        if 'content' not in current_file:
            logger.info(f"current_file missing content field, will be fetched as needed")
        
        return True, None 