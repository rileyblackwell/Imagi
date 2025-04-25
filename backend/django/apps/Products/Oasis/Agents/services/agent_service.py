"""
Base agent service module for Imagi Oasis.

This module provides the base class and utility functions for all agent services.
The BaseAgentService class is meant to be inherited by specialized agent services,
not used directly.

Utility functions:
- build_conversation_history: Builds a formatted conversation history for AI models
- format_system_prompt: Formats a system prompt with optional context
- get_conversation_summary: Creates a summary of a conversation
"""

import os
import logging
from dotenv import load_dotenv
from openai import OpenAI
import anthropic
from ..models import AgentMessage, AgentConversation, SystemPrompt
from abc import ABC, abstractmethod
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db.models import F
from apps.Payments.services import PaymentService

logger = logging.getLogger(__name__)

# Load environment variables from .env
load_dotenv()
openai_key = os.getenv('OPENAI_KEY') or settings.OPENAI_API_KEY
anthropic_key = os.getenv('ANTHROPIC_KEY') or settings.ANTHROPIC_API_KEY

# Add model costs constants
MODEL_COSTS = {
    'claude-3-7-sonnet-20250219': 0.04,  # $0.04 per request
    'claude-3-7-sonnet': 0.04,  # $0.04 per request
    'gpt-4o': 0.04,  # $0.04 per request
    'gpt-4o-mini': 0.005  # $0.005 per request
}

def build_conversation_history(conversation, project_path=None, current_file=None):
    """
    Builds a formatted conversation history for the AI model.
    Returns a list of messages in the format expected by the AI APIs.
    
    Args:
        conversation: The AgentConversation object
        project_path (str, optional): Path to the project directory to include template and CSS files
        current_file (dict, optional): Current file being edited or chatted about with keys: path, content, type
        
    Returns:
        list: A list of message dictionaries with 'role' and 'content' keys
    """
    messages = []
    
    # Add system prompt if it exists
    system_prompt = None
    if hasattr(conversation, 'system_prompt'):
        system_prompt = SystemPrompt.objects.filter(conversation=conversation).first()
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt.content
            })
    
    # Add current file if provided - give this priority
    if current_file and current_file.get('path') and current_file.get('content'):
        messages.append({
            "role": "system",
            "content": f"CURRENTLY WORKING WITH FILE: {current_file.get('path')}\n\nCONTENT:\n{current_file.get('content')}"
        })
    
    # Include project files if project_path is provided
    if project_path:
        templates_dir = os.path.join(project_path, 'templates')
        css_dir = os.path.join(project_path, 'static', 'css')
        
        # Add HTML files
        if os.path.exists(templates_dir):
            html_files = [f for f in os.listdir(templates_dir) if f.endswith('.html')]
            html_files.sort()
            
            # Ensure base.html is first, followed by index.html for better context
            if 'base.html' in html_files:
                html_files.remove('base.html')
                html_files.insert(0, 'base.html')
            if 'index.html' in html_files:
                html_files.remove('index.html')
                html_files.insert(1 if 'base.html' in html_files else 0, 'index.html')
            
            for filename in html_files:
                file_path = os.path.join(templates_dir, filename)
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        messages.append({
                            "role": "system",
                            "content": f"[File: {filename}]\n{content}"
                        })
                except FileNotFoundError:
                    logger.warning(f"File not found: {filename}")
                    continue
        
        # Add CSS files
        if os.path.exists(css_dir):
            css_files = [f for f in os.listdir(css_dir) if f.endswith('.css')]
            for filename in css_files:
                css_path = os.path.join(css_dir, filename)
                try:
                    with open(css_path, 'r') as f:
                        content = f.read()
                        messages.append({
                            "role": "system",
                            "content": f"[File: {filename}]\n{content}"
                        })
                except FileNotFoundError:
                    logger.warning(f"File not found: {filename}")
                    continue
    
    # Add conversation history
    history_messages = AgentMessage.objects.filter(
        conversation=conversation
    ).order_by('created_at')
    
    for msg in history_messages:
        messages.append({
            "role": msg.role,
            "content": msg.content
        })
    
    return messages

def format_system_prompt(base_prompt, context=None):
    """
    Formats a system prompt with optional context.
    
    Args:
        base_prompt (str): The base system prompt
        context (str, optional): Additional context to append
        
    Returns:
        dict: A message dictionary with 'role' and 'content' keys
    """
    prompt = base_prompt
    
    if context:
        prompt += f"\n\nCONTEXT:\n{context}"
        
    return {
        "role": "system",
        "content": prompt
    }

def get_conversation_summary(conversation):
    """
    Creates a summary of the conversation including metadata and message count.
    
    Args:
        conversation: The AgentConversation object
        
    Returns:
        dict: A summary of the conversation
    """
    message_count = AgentMessage.objects.filter(conversation=conversation).count()
    system_prompt = getattr(conversation.system_prompt, 'content', None) if hasattr(conversation, 'system_prompt') else None
    
    return {
        'id': conversation.id,
        'model_name': conversation.model_name,
        'created_at': conversation.created_at.isoformat(),
        'message_count': message_count,
        'has_system_prompt': bool(system_prompt),
        'system_prompt_preview': system_prompt[:100] + '...' if system_prompt else None
    }

class BaseAgentService(ABC):
    """
    Base class for all agent services.
    
    This abstract class provides common functionality for agent services,
    such as conversation management, credit management, and prompt generation.
    """
    
    def __init__(self):
        """Initialize the agent service."""
        # Initialize API clients
        self.openai_client = OpenAI(api_key=openai_key)
        self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
        
        # Initialize payment service
        self.payment_service = PaymentService()
        
        # Set default project files list
        self.project_files = []
        
        # Log initialization
        logger.debug(f"Initialized {self.__class__.__name__}")
        
        # Check if API keys are available
        if not openai_key:
            logger.warning("OpenAI API key not found - OpenAI features will not work properly")
        if not anthropic_key:
            logger.warning("Anthropic API key not found - Claude features will not work properly")
    
    @abstractmethod
    def get_system_prompt(self):
        """
        Get the system prompt for this agent type.
        Must be implemented by subclasses.
        
        Returns:
            dict: A message dictionary with 'role' and 'content' keys
        """
        raise NotImplementedError("Subclasses must implement get_system_prompt()")
    
    @abstractmethod
    def validate_response(self, content):
        """
        Validate the AI model's response.
        Must be implemented by subclasses.
        
        Args:
            content (str): The response content to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        raise NotImplementedError("Subclasses must implement validate_response()")
    
    # Credit Management Methods
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
            profile = user.profile
            
            # Get the exact amount from MODEL_COSTS using the model ID directly
            required_amount = MODEL_COSTS.get(model)
            
            # If model not found in MODEL_COSTS, use correct default based on model pattern
            if required_amount is None:
                if 'claude-3-7-sonnet' in model:
                    required_amount = 0.04
                elif model == 'gpt-4o':
                    required_amount = 0.04
                elif 'gpt-4o-mini' in model:
                    required_amount = 0.005
                else:
                    # Default fallback
                    required_amount = 0.04
            
            # Log the required amount for debugging
            logger.info(f"Credit check for model {model}: ${required_amount:.4f} required, user balance: ${profile.balance:.4f}")
            
            # Use a small epsilon value to handle floating-point precision issues
            epsilon = 0.0001
            if profile.balance + epsilon < required_amount:
                return False, required_amount
            return True, required_amount
        except Exception as e:
            logger.error(f"Error checking user balance: {str(e)}")
            return False, 0.04
    
    def deduct_credits(self, user, model):
        """
        Deduct amount from user's account based on model used.
        
        Args:
            user: The Django user object
            model (str): The AI model to use
            
        Returns:
            bool: Success status
        """
        try:
            profile = user.profile
            
            # Get the exact amount from MODEL_COSTS using the model ID directly
            amount_to_deduct = MODEL_COSTS.get(model)
            
            # If model not found in MODEL_COSTS, use correct default based on model pattern
            if amount_to_deduct is None:
                if 'claude-3-7-sonnet' in model:
                    amount_to_deduct = 0.04
                elif model == 'gpt-4o':
                    amount_to_deduct = 0.04
                elif 'gpt-4o-mini' in model:
                    amount_to_deduct = 0.005
                else:
                    # Default fallback
                    amount_to_deduct = 0.04
            
            # Log the amount being deducted for debugging
            logger.info(f"Deducting ${amount_to_deduct:.4f} for model {model} from user {user.username}")
            
            profile.balance = F('balance') - amount_to_deduct
            profile.save(update_fields=['balance'])
            
            # Refresh from database to get the new value
            profile.refresh_from_db()
            return True
        except Exception as e:
            logger.error(f"Error deducting amount: {str(e)}")
            return False
    
    # Conversation Management Methods
    def get_conversation(self, conversation_id, user):
        """
        Get a specific conversation by ID.
        
        Args:
            conversation_id (str): The ID of the conversation
            user: The Django user object
            
        Returns:
            AgentConversation: The conversation object or None if not found
        """
        try:
            return get_object_or_404(AgentConversation, id=conversation_id, user=user)
        except Exception as e:
            logger.error(f"Error getting conversation: {str(e)}")
            return None
    
    def create_conversation(self, user, model, system_prompt):
        """
        Create a new conversation.
        
        Args:
            user: The Django user object
            model: The model to use
            system_prompt: The system prompt dictionary
            
        Returns:
            AgentConversation: The created conversation object
        """
        try:
            # Create the conversation
            conversation = AgentConversation.objects.create(
                user=user,
                model_name=model,
                provider='anthropic' if 'claude' in model else 'openai'
            )
            
            # Add the system prompt
            SystemPrompt.objects.create(
                conversation=conversation,
                content=system_prompt['content']
            )
            
            return conversation
        except Exception as e:
            logger.error(f"Error creating conversation: {str(e)}")
            raise
    
    def add_user_message(self, conversation, content, user):
        """
        Add a user message to a conversation.
        
        Args:
            conversation: The conversation object
            content: The message content
            user: The Django user object
            
        Returns:
            AgentMessage: The created message
        """
        try:
            return AgentMessage.objects.create(
                conversation=conversation,
                role='user',
                content=content
            )
        except Exception as e:
            logger.error(f"Error adding user message: {str(e)}")
            raise
    
    def add_assistant_message(self, conversation, content, user):
        """
        Add an assistant message to a conversation.
        
        Args:
            conversation: The conversation object
            content: The message content
            user: The Django user object
            
        Returns:
            AgentMessage: The created message
        """
        try:
            return AgentMessage.objects.create(
                conversation=conversation,
                role='assistant',
                content=content
            )
        except Exception as e:
            logger.error(f"Error adding assistant message: {str(e)}")
            raise
    
    def build_conversation_history(self, conversation, project_path=None, current_file=None):
        """
        Build the conversation history for the AI model.
        
        Args:
            conversation: The conversation object
            project_path: Optional project path for context
            current_file: Optional current file being edited
            
        Returns:
            list: A list of message dictionaries with 'role' and 'content' keys
        """
        return build_conversation_history(conversation, project_path, current_file)
    
    def process_conversation(self, user_input, model, user, **kwargs):
        """
        Process a conversation message and generate a response.
        
        Args:
            user_input (str): The user's message
            model (str): The ID of the model to use
            user (User): The Django user making the request
            **kwargs: Additional arguments
                - conversation_id (str, optional): ID of an existing conversation
                - project_path (str, optional): Path to project files
                - current_file (dict, optional): Current file being edited or chatted about
            
        Returns:
            dict: The result of processing the message
        """
        try:
            # Get or create conversation
            conversation_id = kwargs.get('conversation_id')
            if conversation_id:
                try:
                    conversation = self.get_conversation(conversation_id, user)
                    if not conversation:
                        return {
                            'success': False,
                            'error': 'Conversation not found'
                        }
                except Exception as e:
                    return {
                        'success': False,
                        'error': f'Error retrieving conversation: {str(e)}'
                    }
            else:
                conversation = self.create_conversation(user, model, self.get_system_prompt())
            
            # Charge the user for using AI models
            # Determine charge amount based on model
            amount = MODEL_COSTS.get(model)
            
            # If model not found in MODEL_COSTS, use correct default based on model pattern
            if amount is None:
                if 'claude-3-7-sonnet' in model:
                    amount = 0.04
                elif model == 'gpt-4o':
                    amount = 0.04
                elif 'gpt-4o-mini' in model:
                    amount = 0.005
                else:
                    # Default fallback
                    amount = 0.04
            
            # Create descriptive message for transaction
            description = f"AI usage: {model} - ${amount:.4f}"
            
            # Charge the user
            payment_result = self.payment_service.charge_tokens(user, amount, description)
            
            if not payment_result.get('success', False):
                # Handle insufficient credits
                return {
                    'success': False,
                    'error': payment_result.get('error', 'Insufficient credits to use this AI model'),
                    'current_balance': payment_result.get('current_balance', 0),
                    'required_amount': amount
                }
            
            # Get project path for context
            project_path = kwargs.get('project_path')
            current_file = kwargs.get('current_file')
            
            # Build conversation history including system prompt, project files, and messages
            api_messages = self.build_conversation_history(conversation, project_path, current_file)
            
            # Add the user's message
            api_messages.append({
                "role": "user",
                "content": user_input
            })
            
            # Generate the response using the appropriate model
            if 'claude' in model:
                # Get the system message content for Claude
                system_content = ""
                for msg in api_messages:
                    if msg['role'] == 'system':
                        system_content += msg['content'] + "\n\n"
                
                # Filter out system messages for Claude API
                claude_messages = [msg for msg in api_messages if msg['role'] != 'system']
                
                # Add additional context to system prompt if file is being discussed
                if current_file and current_file.get('path'):
                    file_info = f"You are currently discussing the file: {current_file.get('path')}"
                    system_content = f"{file_info}\n\n{system_content}"
                
                # Adjust system prompt to include instructions about not using streaming
                system_content = f"{system_content}\n\nIMPORTANT: Provide complete responses at once, not streamed. The user will see a processing animation while waiting."
                
                # Make the API call with better error handling
                try:
                    completion = self.anthropic_client.messages.create(
                        model=model,
                        max_tokens=4096,
                        temperature=0.7,
                        system=system_content.strip(),
                        messages=claude_messages
                    )
                    response_content = completion.content[0].text
                except Exception as api_error:
                    logger.error(f"Anthropic API error: {str(api_error)}")
                    if "API key" in str(api_error):
                        raise ValueError("The Anthropic API key is invalid or missing. Please check your ANTHROPIC_KEY environment variable.")
                    raise
                    
            elif 'gpt' in model:
                # Add file context as an additional system message
                if current_file and current_file.get('path'):
                    file_info_msg = {
                        "role": "system", 
                        "content": f"You are currently discussing the file: {current_file.get('path')}"
                    }
                    # Insert file context as the second message (after the main system prompt)
                    system_exists = any(msg['role'] == 'system' for msg in api_messages)
                    if system_exists:
                        # Find position of last system message
                        last_system_idx = max(i for i, msg in enumerate(api_messages) 
                                            if msg['role'] == 'system')
                        api_messages.insert(last_system_idx + 1, file_info_msg)
                    else:
                        api_messages.insert(0, file_info_msg)
                
                # Add instruction about not using streaming
                api_messages.insert(0, {
                    "role": "system",
                    "content": "IMPORTANT: Provide complete responses at once, not streamed. The user will see a processing animation while waiting."
                })
                
                # Make the API call with better error handling
                try:
                    completion = self.openai_client.chat.completions.create(
                        model=model,
                        messages=api_messages,
                        temperature=0.7,
                        max_tokens=4096,
                        stream=False  # Explicitly disable streaming
                    )
                    response_content = completion.choices[0].message.content
                except Exception as api_error:
                    logger.error(f"OpenAI API error: {str(api_error)}")
                    if "API key" in str(api_error):
                        raise ValueError("The OpenAI API key is invalid or missing. Please check your OPENAI_KEY environment variable.")
                    raise
                    
            else:
                raise ValueError(f"Unsupported model: {model}")
            
            # Validate the response
            is_valid, error = self.validate_response(response_content)
            if not is_valid:
                return {
                    'success': False,
                    'error': error,
                    'response': response_content
                }
            
            # Store the messages
            if not kwargs.get('skip_store', False):
                # Store user message
                self.add_user_message(conversation, user_input, user)
                
                # Store assistant response
                self.add_assistant_message(conversation, response_content, user)
            
            return {
                'success': True,
                'response': response_content,
                'conversation_id': conversation.id
            }
            
        except Exception as e:
            logger.error(f"Error in process_conversation: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': str(e)
            } 