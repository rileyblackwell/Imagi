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
from apps.Payments.services import PaymentService
from apps.Products.Oasis.Builder.services.models_service import (
  get_model_cost, get_model_by_id
)

logger = logging.getLogger(__name__)

# Load environment variables from .env
load_dotenv()
openai_key = os.getenv('OPENAI_KEY') or settings.OPENAI_API_KEY
anthropic_key = os.getenv('ANTHROPIC_KEY') or settings.ANTHROPIC_API_KEY

# Define MODEL_COSTS dictionary with costs per model - imported from model_definitions.py for backward compatibility
# New code should use get_model_cost() function instead of accessing this dictionary directly

# Default model costs for unknown models based on common prefixes - imported from model_definitions.py
# New code should use get_model_cost() function instead

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
    
    # Add project information if available
    if hasattr(conversation, 'project_id') and conversation.project_id:
        try:
            # Import here to avoid circular imports
            from apps.Products.Oasis.ProjectManager.models import Project
            project = Project.objects.get(id=conversation.project_id)
            
            # Enhanced project information including description
            project_info = f"You are currently working on project: {project.name} (ID: {conversation.project_id})"
            
            # Add project description if available
            if hasattr(project, 'description') and project.description:
                project_info += f"\n\nProject Description: {project.description}"
                
            messages.append({
                "role": "system",
                "content": project_info
            })
        except Exception as e:
            logger.warning(f"Could not fetch detailed project info: {str(e)}")
            # Fall back to basic info if available
            project_name = getattr(conversation, 'project_name', None)
            if project_name:
                messages.append({
                    "role": "system",
                    "content": f"You are currently working on project: {project_name} (ID: {conversation.project_id})"
                })
    
    # Add system prompt if it exists
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
                # Skip if this file is already provided as current_file
                if current_file and current_file.get('path') and current_file.get('path').endswith(filename):
                    continue
                    
                file_path = os.path.join(templates_dir, filename)
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        messages.append({
                            "role": "system",
                            "content": f"[File: templates/{filename}]\n{content}"
                        })
                except FileNotFoundError:
                    logger.warning(f"File not found: {filename}")
                    continue
        
        # Add CSS files
        if os.path.exists(css_dir):
            css_files = [f for f in os.listdir(css_dir) if f.endswith('.css')]
            for filename in css_files:
                # Skip if this file is already provided as current_file
                if current_file and current_file.get('path') and current_file.get('path').endswith(filename):
                    continue
                    
                css_path = os.path.join(css_dir, filename)
                try:
                    with open(css_path, 'r') as f:
                        content = f.read()
                        messages.append({
                            "role": "system",
                            "content": f"[File: static/css/{filename}]\n{content}"
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
    Subclasses must implement the abstract methods to provide specialized behavior.
    """
    
    def __init__(self):
        """Initialize the agent service with common resources."""
        # Initialize API clients
        self.openai_client = OpenAI(api_key=openai_key)
        self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
        
        # Initialize payment service
        self.payment_service = PaymentService()
        
        # Set default project files list
        self.project_files = []
        
        # Set default request timeout
        self.request_timeout = 60
        
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
        Must be implemented by subclasses to provide specialized system prompts.
        
        Returns:
            dict: A dictionary with 'role' and 'content' keys for the system prompt
        """
        pass
    
    @abstractmethod
    def validate_response(self, content):
        """
        Validate that the response from the AI model is acceptable.
        Must be implemented by subclasses to provide specialized validation.
        
        Args:
            content (str): The content to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        pass
    
    @abstractmethod
    def process_conversation(self, user_input, model, user, **kwargs):
        """
        Process a conversation with the AI model.
        Must be implemented by subclasses to provide specialized conversation handling.
        
        Args:
            user_input (str): The user's input message
            model (str): The AI model to use
            user: The Django user object
            **kwargs: Additional arguments for the conversation
            
        Returns:
            dict: The result of the conversation
        """
        pass
    
    def get_additional_context(self, **kwargs):
        """
        Get additional context for the conversation.
        May be overridden by subclasses to provide specialized context.
        
        Args:
            **kwargs: Additional arguments for generating context
            
        Returns:
            str: Additional context for the system prompt
        """
        return None
    
    def get_api_model(self, model_id):
        """
        Get the API model to use for a given model ID.
        
        Args:
            model_id (str): The model ID
            
        Returns:
            str: The API model to use
        """
        # Try to get the model definition
        model_def = get_model_by_id(model_id)
        
        # Use api_model from definition if available
        if model_def and 'api_model' in model_def:
            logger.info(f"Using API model from definition: {model_def['api_model']} for model ID: {model_id}")
            return model_def['api_model']
        
        # All OpenAI models use API as-is (no mapping needed, using responses API)
        # Return the model ID directly
        return model_id
    
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
    
    def validate_project_access(self, project_id, user):
        """
        Validate that a project exists and the user has access to it.
        
        Args:
            project_id (str): The ID of the project
            user (User): The Django user object
            
        Returns:
            tuple: (project, error_response)
        """
        try:
            from apps.Products.Oasis.ProjectManager.models import Project
            project = Project.objects.get(id=project_id, user=user)
            
            if not project.project_path:
                logger.error(f"Project {project_id} has no valid project path")
                return None, {
                    'success': False,
                    'error': 'Project path not found. The project may not be properly initialized.'
                }
                
            return project, None
            
        except Project.DoesNotExist:
            logger.error(f"Project {project_id} not found for user {user.username}")
            return None, {
                'success': False,
                'error': 'Project not found or you do not have access to it'
            }
        except Exception as e:
            logger.error(f"Error verifying project: {str(e)}")
            return None, {
                'success': False,
                'error': f'Error accessing project: {str(e)}'
            }
    
    def load_project_files(self, project_path):
        """
        Load all relevant project files to provide context for AI generation.
        
        Args:
            project_path (str): Path to the project directory
            
        Returns:
            list: List of project files with their content
        """
        files = []
        
        try:
            if not project_path or not os.path.exists(project_path):
                logger.warning(f"Invalid project path: {project_path}")
                return files
            
            # Get HTML templates
            templates_dir = os.path.join(project_path, 'templates')
            if os.path.exists(templates_dir):
                html_files = [f for f in os.listdir(templates_dir) if f.endswith('.html')]
                # Sort files but prioritize base.html and index.html
                sorted_files = []
                if 'base.html' in html_files:
                    sorted_files.append('base.html')
                    html_files.remove('base.html')
                if 'index.html' in html_files:
                    sorted_files.append('index.html')
                    html_files.remove('index.html')
                    
                # Add remaining files
                sorted_files.extend(sorted(html_files))
                
                for filename in sorted_files:
                    file_path = os.path.join(templates_dir, filename)
                    try:
                        with open(file_path, 'r') as f:
                            content = f.read()
                            files.append({
                                'path': f'templates/{filename}',
                                'content': content,
                                'type': 'html'
                            })
                    except Exception as e:
                        logger.warning(f"Error reading HTML file {filename}: {str(e)}")
            
            # Get CSS files
            css_dir = os.path.join(project_path, 'static', 'css')
            if os.path.exists(css_dir):
                for filename in os.listdir(css_dir):
                    if filename.endswith('.css'):
                        file_path = os.path.join(css_dir, filename)
                        try:
                            with open(file_path, 'r') as f:
                                content = f.read()
                                files.append({
                                    'path': f'static/css/{filename}',
                                    'content': content,
                                    'type': 'css'
                                })
                        except Exception as e:
                            logger.warning(f"Error reading CSS file {filename}: {str(e)}")
            
            # Get URL and views configuration for additional context
            for python_file in ['urls.py', 'views.py']:
                python_path = None
                for root, dirs, file_list in os.walk(project_path):
                    if python_file in file_list:
                        python_path = os.path.join(root, python_file)
                        break
                        
                if python_path:
                    try:
                        with open(python_path, 'r') as f:
                            content = f.read()
                            rel_path = os.path.relpath(python_path, project_path)
                            files.append({
                                'path': rel_path,
                                'content': content,
                                'type': 'python'
                            })
                    except Exception as e:
                        logger.warning(f"Error reading {python_file}: {str(e)}")
            
            return files
            
        except Exception as e:
            logger.error(f"Error loading project files: {str(e)}")
            return files
    
    def error_response(self, message, code=400):
        """
        Create a standardized error response.
        
        Args:
            message (str): The error message
            code (int): The HTTP status code
            
        Returns:
            dict: An error response dictionary
        """
        logger.error(f"Agent error: {message}")
        return {
            'success': False,
            'error': message,
            'code': code
        }
    
    # Credit Management Methods
    def get_model_cost(self, model_id):
        """
        Get the exact cost for a specific model.
        
        Args:
            model_id (str): The model ID to get the cost for
            
        Returns:
            float: The cost of the model in dollars
        """
        # Log the model ID for which we're calculating cost
        logger.info(f"Calculating cost for model: {model_id}")
        
        # Get the cost from centralized function
        amount = get_model_cost(model_id)
        
        # Log the final cost for debugging
        logger.info(f"Final cost for model {model_id}: ${amount}")
                
        return amount

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
            
            # Get the exact cost for the model with 4 decimal precision
            required_amount = float(f"{self.get_model_cost(model):.4f}")
            
            # Log the required amount for debugging with model name for tracking small amounts
            logger.info(f"Credit check for model {model}: ${required_amount:.4f} required, user balance: ${balance:.4f}")
            
            # Use a small epsilon value to handle floating-point precision issues
            epsilon = 0.0001
            if balance + epsilon < required_amount:
                logger.warning(f"Insufficient credits for {model}: ${balance:.4f} < ${required_amount:.4f}")
                return False, required_amount
                
            logger.info(f"Credit check PASSED for {model}: ${balance:.4f} >= ${required_amount:.4f}")
            return True, required_amount
        except Exception as e:
            logger.error(f"Error checking user balance: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False, 0.04
    
    def deduct_credits(self, user_id, model, completion_tokens=None):
        """
        Deduct credits from user for using the model.
        
        Args:
            user_id (int): The user ID
            model (str): The model ID
            completion_tokens (int, optional): The number of completion tokens
            
        Returns:
            float: The amount of credits deducted
        """
        try:
            # Get the model cost
            amount = self.get_model_cost(model)
            
            # Get user
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(id=user_id)
            
            # Create descriptive message for transaction
            description = f"AI usage: {model}"
            
            # Add token information if available
            if completion_tokens:
                description += f" - {completion_tokens} tokens"
                # Adjust cost based on actual token usage if available
                token_cost = amount / 1000  # Assuming cost is per 1K tokens
                adjusted_amount = token_cost * completion_tokens
                amount = max(adjusted_amount, amount * 0.1)  # Ensure minimum charge of 10% of base cost
                
            # Log the charge details
            logger.info(f"Charging user {user_id} ${amount:.4f} for {description}")
                
            # Charge the user
            payment_result = self.payment_service.credit_service.deduct_credits(user, amount, description)
            
            if not payment_result.get('success', False):
                # This shouldn't happen if check_user_credits was called first
                logger.error(f"Failed to deduct credits for user {user_id}: {payment_result.get('error')}")
                
            return amount
        except Exception as e:
            logger.error(f"Error deducting credits: {str(e)}")
            # Return 0 for amount since deduction failed
            return 0
    
    # Conversation Management Methods
    def get_conversation(self, conversation_id, user):
        """
        Get an existing conversation by ID.
        
        Args:
            conversation_id (str): The ID of the conversation
            user (User): The Django user object
            
        Returns:
            AgentConversation: The conversation object or None
        """
        try:
            return get_object_or_404(AgentConversation, id=conversation_id, user=user)
        except Exception as e:
            logger.error(f"Error getting conversation {conversation_id}: {str(e)}")
            return None
    
    def create_conversation(self, user, model, system_prompt=None, project_id=None):
        """
        Create a new conversation.
        
        Args:
            user (User): The Django user object
            model (str): The model ID to use
            system_prompt (str, optional): The system prompt content
            project_id (str, optional): The project ID
            
        Returns:
            AgentConversation: The created conversation
        """
        try:
            # Create conversation
            conversation = AgentConversation.objects.create(
                user=user,
                model_name=model,
                project_id=project_id
            )
            
            # Add system prompt if provided
            if system_prompt:
                SystemPrompt.objects.create(
                    conversation=conversation,
                    content=system_prompt
                )
            else:
                # Use default system prompt from the agent service
                default_prompt = self.get_system_prompt()
                if default_prompt:
                    SystemPrompt.objects.create(
                        conversation=conversation,
                        content=default_prompt.get('content', '')
                    )
            
            return conversation
        except Exception as e:
            logger.error(f"Error creating conversation: {str(e)}")
            raise
    
    def add_user_message(self, conversation, content, user):
        """
        Add a user message to the conversation.
        
        Args:
            conversation (AgentConversation): The conversation object
            content (str): The message content
            user (User): The Django user object (used for validation but not stored with message)
            
        Returns:
            AgentMessage: The created message
        """
        try:
            message = AgentMessage.objects.create(
                conversation=conversation,
                role="user",
                content=content
            )
            return message
        except Exception as e:
            logger.error(f"Error adding user message: {str(e)}")
            raise
    
    def add_assistant_message(self, conversation, content, user):
        """
        Add an assistant message to the conversation.
        
        Args:
            conversation (AgentConversation): The conversation object
            content (str): The message content
            user (User): The Django user object (used for validation but not stored with message)
            
        Returns:
            AgentMessage: The created message
        """
        try:
            message = AgentMessage.objects.create(
                conversation=conversation,
                role="assistant",
                content=content
            )
            return message
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