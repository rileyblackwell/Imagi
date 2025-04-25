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

    def deduct_credits(self, user, model):
        """
        Deduct credits from user's account for using the selected model.
        
        Args:
            user: The Django user object
            model (str): The AI model that was used
            
        Returns:
            bool: True if credits were successfully deducted, False otherwise
        """
        try:
            # Get the exact cost based on the model name
            required_amount = self.get_model_cost(model)
            
            # Use the payment service to charge tokens directly (amount in dollars)
            description = f"Chat using model: {model}"
            
            # Access the credit balance directly instead of going through payment service
            from apps.Payments.models import CreditBalance
            from django.db import transaction
            from decimal import Decimal
            
            # Perform the transaction with database-level locking
            with transaction.atomic():
                try:
                    balance = CreditBalance.objects.select_for_update().get(user=user)
                    
                    # Convert to float for epsilon comparison (handling floating point precision)
                    epsilon = 0.0001
                    current_balance = float(balance.balance)
                    
                    if current_balance + epsilon < required_amount:
                        logger.warning(f"Insufficient balance: ${current_balance:.4f} available, ${required_amount:.4f} required")
                        return False
                    
                    # Update balance
                    balance.balance = Decimal(str(float(balance.balance) - required_amount))
                    balance.save()
                    
                    logger.info(f"Deducted ${required_amount:.4f} from user {user.username} for model {model}. New balance: ${float(balance.balance):.4f}")
                    return True
                    
                except CreditBalance.DoesNotExist:
                    logger.error(f"No credit balance found for user {user.username}")
                    return False
            
        except Exception as e:
            logger.error(f"Error deducting credits: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False

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
            # Get the exact model cost for logging
            model_cost = self.get_model_cost(model_id)
            logger.info(f"Processing message with model {model_id} (cost: ${model_cost:.4f})")
            
            # Check user credits before proceeding
            has_credits, required_amount = self.check_user_credits(user, model_id)
            if not has_credits:
                return {
                    'success': False,
                    'error': f"Insufficient credits: You need ${required_amount:.4f} more to use {model_id}. Please add more credits."
                }
            
            # Check API key availability
            api_key_error = self.check_api_key_available(model_id)
            if api_key_error:
                logger.error(f"API key error: {api_key_error}")
                return {
                    'success': False,
                    'error': api_key_error
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
            
            # If successful, deduct credits for using the model
            if result.get('success', False):
                # Explicitly deduct credits after successful processing
                deduction_success = self.deduct_credits(user, model_id)
                
                if not deduction_success:
                    logger.error(f"Failed to deduct credits for user {user.username} using model {model_id}")
                    return {
                        'success': False,
                        'error': f"Failed to process payment for {model_id}. Please try again later."
                    }
                
                # Log successful credit deduction
                logger.info(f"Successfully deducted credits for user {user.username} using model {model_id}")
                
                # Add timestamp to result
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

    def check_api_key_available(self, model_id):
        """
        Check if the required API key is available for the selected model.
        
        Args:
            model_id (str): The model ID to check
            
        Returns:
            str: Error message if API key is not available, None otherwise
        """
        try:
            import os
            from django.conf import settings
            
            # Check if model is from OpenAI or Anthropic
            if 'gpt' in model_id:
                openai_key = os.getenv('OPENAI_KEY') or settings.OPENAI_API_KEY
                if not openai_key:
                    return "OpenAI API key is not configured. Please set the OPENAI_KEY environment variable."
            elif 'claude' in model_id:
                anthropic_key = os.getenv('ANTHROPIC_KEY') or settings.ANTHROPIC_API_KEY
                if not anthropic_key:
                    return "Anthropic API key is not configured. Please set the ANTHROPIC_KEY environment variable."
            return None
        except Exception as e:
            logger.error(f"Error checking API key: {str(e)}")
            return f"Error checking API key: {str(e)}"

    def get_model_cost(self, model_id):
        """
        Get the exact cost for a specific model.
        
        Args:
            model_id (str): The model ID to get the cost for
            
        Returns:
            float: The cost of the model in dollars
        """
        # Import MODEL_COSTS from agent_service
        from .agent_service import MODEL_COSTS
        
        # Get the exact amount from MODEL_COSTS using the model ID directly
        amount = MODEL_COSTS.get(model_id)
        
        # If model not found in MODEL_COSTS, use correct default based on model pattern
        if amount is None:
            if 'claude-3-7-sonnet' in model_id:
                amount = 0.04
            elif model_id == 'gpt-4o':
                amount = 0.04
            elif 'gpt-4o-mini' in model_id:
                amount = 0.005
            else:
                # Default fallback
                amount = 0.04
                
        return amount
            
    def get_conversation_history(self, conversation_id, user):
        """
        Get conversation history for a specific conversation.
        
        Args:
            conversation_id (str): The ID of the conversation
            user (User): The Django user object
            
        Returns:
            dict: The conversation history data
        """
        try:
            # Get the conversation object
            from ..models import AgentConversation, AgentMessage
            
            # Make sure conversation exists and belongs to user
            conversation = AgentConversation.objects.get(id=conversation_id, user=user)
            
            # Get all messages in this conversation
            messages = AgentMessage.objects.filter(conversation=conversation).order_by('created_at')
            
            # Format messages for the response
            message_list = []
            for msg in messages:
                message_list.append({
                    'role': msg.role,
                    'content': msg.content,
                    'timestamp': msg.created_at.isoformat()
                })
            
            # Return conversation data including messages and metadata
            return {
                'success': True,
                'conversation_id': conversation_id,
                'model': conversation.model_name,
                'messages': message_list,
                'created_at': conversation.created_at.isoformat(),
                'updated_at': conversation.updated_at.isoformat() if hasattr(conversation, 'updated_at') else None
            }
        except AgentConversation.DoesNotExist:
            logger.error(f"Conversation not found: {conversation_id}")
            raise ValueError(f"Conversation with ID {conversation_id} not found")
        except Exception as e:
            logger.error(f"Error getting conversation history: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise ValueError(f"Error retrieving conversation: {str(e)}")

    def check_user_credits(self, user, model):
        """
        Check if user has enough balance for the selected model.
        
        Args:
            user: The Django user object
            model (str): The AI model to use
            
        Returns:
            tuple: (has_credits, required_amount)
        """
        try:
            # Get credit balance directly from the CreditBalance model
            from apps.Payments.models import CreditBalance
            
            try:
                credit_balance = CreditBalance.objects.get(user=user)
                balance = float(credit_balance.balance)
            except CreditBalance.DoesNotExist:
                # Create a new balance record with zero balance if it doesn't exist
                credit_balance = CreditBalance.objects.create(user=user, balance=0)
                balance = 0.0
            
            # Get the exact cost for the model
            required_amount = self.get_model_cost(model)
            
            # Log the required amount for debugging
            logger.info(f"Credit check for model {model}: ${required_amount:.4f} required, user balance: ${balance:.4f}")
            
            # Use a small epsilon value to handle floating-point precision issues
            epsilon = 0.0001
            if balance + epsilon < required_amount:
                return False, required_amount
            return True, required_amount
        except Exception as e:
            logger.error(f"Error checking user balance: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False, 0.04 