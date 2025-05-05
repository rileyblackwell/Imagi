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
import json
from dotenv import load_dotenv
from openai import OpenAI
import anthropic
from ..models import AgentMessage, AgentConversation, SystemPrompt
from abc import ABC, abstractmethod
from django.conf import settings
from django.shortcuts import get_object_or_404
from apps.Payments.services import PaymentService
from .model_definitions import (
    get_model_cost, 
    get_provider_from_model_id
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
            str: The system prompt text
        """
        pass
    
    def validate_response(self, content):
        """
        Validate that the response from the AI model is acceptable.
        
        Args:
            content (str): The content to validate
            
        Returns:
            bool: Whether the response is valid
            
        Raises:
            ValueError: If the response is invalid
        """
        # Basic validation
        if not content or not isinstance(content, str):
            raise ValueError("Empty or invalid response received from AI model")
            
        # Check for response length
        if len(content) < 10:
            raise ValueError(f"Response too short ({len(content)} chars)")
            
        return True
    
    # Credit Management Methods
    def check_user_credits(self, user_id, model, completion_tokens=None):
        """
        Check if user has sufficient credits for the model.
        
        Args:
            user_id (int): The user ID
            model (str): The model ID
            completion_tokens (int, optional): The number of completion tokens if known
            
        Returns:
            bool: True if user has sufficient credits
            
        Raises:
            ValueError: If user does not have sufficient credits
        """
        # Get the model cost
        model_cost = get_model_cost(model)
        
        # Check if user has sufficient credits
        payment_result = self.payment_service.check_balance(user_id, model_cost)
        
        if not payment_result.get('success', False):
            # Handle insufficient credits
            error_message = payment_result.get('error', 'Insufficient credits to use this AI model')
            logger.warning(f"Credit check failed for user {user_id}: {error_message}")
            raise ValueError(error_message)
        
        return True
    
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
        # Get the model cost
        amount = get_model_cost(model)
        
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
        payment_result = self.payment_service.charge_tokens(user_id, amount, description)
        
        if not payment_result.get('success', False):
            # This shouldn't happen if check_user_credits was called first
            logger.error(f"Failed to deduct credits for user {user_id}: {payment_result.get('error')}")
            
        return amount
    
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
                        content=default_prompt
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
            user (User): The Django user object
            
        Returns:
            AgentMessage: The created message
        """
        try:
            message = AgentMessage.objects.create(
                conversation=conversation,
                role="user",
                content=content,
                user=user
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
            user (User): The Django user object
            
        Returns:
            AgentMessage: The created message
        """
        try:
            message = AgentMessage.objects.create(
                conversation=conversation,
                role="assistant",
                content=content,
                user=user
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
    
    def process_conversation(self, user_input, model, user, **kwargs):
        """
        Process a conversation with the AI model.
        
        Args:
            user_input (str): The user's input message
            model (str): The model ID to use (e.g., 'gpt-4', 'claude-3-sonnet')
            user (User): The Django user object
            **kwargs: Additional parameters such as project_id, file, etc.
            
        Returns:
            dict: A dictionary containing the AI's response and other metadata
        """
        # Extract optional parameters
        project_id = kwargs.get('project_id')
        project_path = kwargs.get('project_path')
        conversation_id = kwargs.get('conversation_id')
        system_prompt_content = kwargs.get('system_prompt')
        is_stream = kwargs.get('stream', False)
        temperature = kwargs.get('temperature', 0.7)
        max_tokens = kwargs.get('max_tokens', None)
        current_file = kwargs.get('file')
        
        # Get or create conversation
        if conversation_id:
            conversation = self.get_conversation(conversation_id, user)
            if not conversation:
                # Create a new conversation if the requested one doesn't exist
                conversation = self.create_conversation(user, model, system_prompt_content, project_id)
        else:
            # Create a new conversation if no conversation_id provided
            conversation = self.create_conversation(user, model, system_prompt_content, project_id)
        
        # Add the user's message to the conversation
        self.add_user_message(conversation, user_input, user)
        
        # Build conversation history including system prompts
        messages = self.build_conversation_history(conversation, project_path, current_file)
        
        # Convert model ID into a provider name
        provider = get_provider_from_model_id(model)
        
        # Prepare response
        response_content = ""
        
        # Check user has sufficient credits
        completion_tokens = None  # We don't know yet how many tokens will be used
        self.check_user_credits(user.id, model, completion_tokens)
        
        # Log all messages for debugging with complete request payloads
        for i, msg in enumerate(messages):
            safe_msg = msg.copy()
            if 'content' in safe_msg and safe_msg['content']:
                # Truncate long content for logging
                if len(safe_msg['content']) > 500:
                    safe_msg['content'] = safe_msg['content'][:500] + f"... [truncated, total length: {len(msg['content'])}]"
            logger.debug(f"Message {i+1}/{len(messages)}: {safe_msg}")
        
        try:
            if provider == 'anthropic':
                # Prepare Anthropic API payload
                anthropic_messages = []
                
                # Add system prompt as a system message if the first message is a system prompt
                if messages and messages[0]['role'] == 'system':
                    system_prompt = messages[0]['content']
                    messages = messages[1:]  # Remove system prompt from messages list
                else:
                    system_prompt = None
                
                # Convert messages to Anthropic format
                for msg in messages:
                    if msg['role'] in ['user', 'assistant']:
                        anthropic_messages.append({
                            'role': msg['role'],
                            'content': msg['content']
                        })
                
                # Prepare complete API request payload
                anthropic_payload = {
                    'model': model,
                    'messages': anthropic_messages,
                    'max_tokens': max_tokens or 4096,
                    'temperature': temperature,
                }
                
                # Add system prompt if present
                if system_prompt:
                    anthropic_payload['system'] = system_prompt
                
                # Log the complete payload sent to Anthropic
                masked_payload = anthropic_payload.copy()
                logger.info(f"🤖 API REQUEST TO ANTHROPIC - Model: {model}")
                logger.info(f"Complete API payload: {json.dumps(masked_payload, indent=2)}")
                
                # Make API call to Anthropic
                completion = self.anthropic_client.messages.create(**anthropic_payload)
                
                # Extract response content
                response_content = completion.content[0].text
                completion_tokens = completion.usage.output_tokens
                
                # Log usage information
                logger.info(f"🔄 ANTHROPIC COMPLETION TOKENS: {completion_tokens}")
                logger.info(f"🔄 ANTHROPIC PROMPT TOKENS: {completion.usage.input_tokens}")
                
            elif provider == 'openai':
                # Prepare OpenAI API payload
                openai_payload = {
                    'model': model,
                    'messages': messages,
                    'temperature': temperature,
                }
                
                if max_tokens:
                    openai_payload['max_tokens'] = max_tokens
                
                # Log the complete payload sent to OpenAI
                masked_payload = openai_payload.copy()
                logger.info(f"🤖 API REQUEST TO OPENAI - Model: {model}")
                logger.info(f"Complete API payload: {json.dumps(masked_payload, indent=2)}")
                
                # Make API call to OpenAI
                completion = self.openai_client.chat.completions.create(**openai_payload)
                
                # Extract response content
                response_content = completion.choices[0].message.content
                completion_tokens = completion.usage.completion_tokens
                
                # Log usage information
                logger.info(f"🔄 OPENAI COMPLETION TOKENS: {completion_tokens}")
                logger.info(f"🔄 OPENAI PROMPT TOKENS: {completion.usage.prompt_tokens}")
                
            else:
                raise ValueError(f"Unsupported AI model provider: {provider}")
            
            # Validate the response
            self.validate_response(response_content)
            
            # Add the assistant's message to the conversation
            self.add_assistant_message(conversation, response_content, user)
            
            # Deduct credits for this API call
            credits_used = self.deduct_credits(user.id, model, completion_tokens)
            
            return {
                'success': True,
                'response': response_content,
                'conversation_id': conversation.id,
                'credits_used': credits_used
            }
            
        except Exception as e:
            # Log the error
            logger.error(f"Error processing conversation: {str(e)}")
            
            # Return error message
            return {
                'success': False,
                'error': str(e),
                'conversation_id': conversation.id if conversation else None
            } 