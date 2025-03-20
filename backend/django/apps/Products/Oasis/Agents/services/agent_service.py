"""
Base agent service module for Imagi Oasis.

This module provides the base class and utility functions for all agent services.
The BaseAgentService class is meant to be inherited by specialized agent services,
not used directly.

Utility functions:
- build_conversation_history: Builds a formatted conversation history for AI models
- format_system_prompt: Formats a system prompt with optional context
- get_last_assistant_message: Gets the most recent assistant message from a conversation
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
from django.urls import reverse
from django.db.models import F
from apps.Products.Oasis.ProjectManager.models import Project as PMProject
from apps.Products.Oasis.Builder.models import Message, Conversation, Page

logger = logging.getLogger(__name__)

# Load environment variables from .env
load_dotenv()
openai_key = os.getenv('OPENAI_KEY') or settings.OPENAI_API_KEY
anthropic_key = os.getenv('ANTHROPIC_KEY') or settings.ANTHROPIC_API_KEY

# Initialize API clients
openai_client = OpenAI(api_key=openai_key)
anthropic_client = anthropic.Anthropic(api_key=anthropic_key)

# Add model costs constants
MODEL_COSTS = {
    'claude-3-5-sonnet-20241022': 0.04,  # $0.10 per request
    'gpt-4': 0.04,  # $0.10 per request
    'gpt-4-mini': 0.005  # $0.005 per request
}

# Credit Management Functions
def check_user_credits(user, model):
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
        required_amount = MODEL_COSTS.get(model, 0.10)
        
        if profile.balance < required_amount:
            return False, required_amount
        return True, required_amount
    except Exception as e:
        logger.error(f"Error checking user balance: {str(e)}")
        return False, 0.10

def deduct_credits(user, model):
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
        amount_to_deduct = MODEL_COSTS.get(model, 0.10)
        profile.balance = F('balance') - amount_to_deduct
        profile.save(update_fields=['balance'])
        
        # Refresh from database to get the new value
        profile.refresh_from_db()
        return True
    except Exception as e:
        logger.error(f"Error deducting amount: {str(e)}")
        return False

def get_active_conversation(user):
    """
    Retrieve the active conversation for the user.
    
    Args:
        user: The Django user object
        
    Returns:
        Conversation: The active conversation
    """
    conversation = Conversation.objects.filter(
        user=user,
        project__isnull=False
    ).select_related('project').order_by('-project__updated_at').first()
    
    if not conversation:
        raise ValueError('No active project found. Please select or create a project first.')
    
    return conversation

# Conversation Management Functions
def list_conversations(user, project_id=None):
    """
    List all agent conversations for a user, optionally filtered by project.
    
    Args:
        user: The Django user object
        project_id (int, optional): The ID of the project to filter by
        
    Returns:
        QuerySet: Agent conversations for the user
    """
    conversations = AgentConversation.objects.filter(
        user=user
    ).order_by('-created_at')
    
    if project_id:
        try:
            project = get_object_or_404(PMProject, id=project_id, user=user)
            conversations = conversations.filter(project=project)
        except Exception as e:
            logger.error(f"Error filtering conversations by project: {str(e)}")
            pass
            
    return conversations

def get_conversation(user, conversation_id):
    """
    Get a specific conversation by ID.
    
    Args:
        user: The Django user object
        conversation_id (int): The ID of the conversation
        
    Returns:
        AgentConversation: The conversation object
    """
    return get_object_or_404(
        AgentConversation,
        id=conversation_id,
        user=user
    )

def get_conversation_messages(user, conversation_id):
    """
    Get all messages for a specific conversation.
    
    Args:
        user: The Django user object
        conversation_id (int): The ID of the conversation
        
    Returns:
        QuerySet: All messages in the conversation
    """
    conversation = get_conversation(user, conversation_id)
    return AgentMessage.objects.filter(
        conversation=conversation
    ).order_by('created_at')

def clear_conversation(user, conversation_id):
    """
    Clear all messages in a conversation, keeping the system prompt.
    
    Args:
        user: The Django user object
        conversation_id (int): The ID of the conversation
        
    Returns:
        dict: Result of the operation
    """
    try:
        conversation = get_conversation(user, conversation_id)
        
        # Delete all messages but keep the system prompt
        AgentMessage.objects.filter(conversation=conversation).delete()
        
        return {"success": True, "message": "Conversation cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing conversation: {str(e)}")
        return {"success": False, "error": str(e)}

def delete_conversation(user, conversation_id):
    """
    Delete a conversation including all messages and system prompt.
    
    Args:
        user: The Django user object
        conversation_id (int): The ID of the conversation
        
    Returns:
        dict: Result of the operation
    """
    try:
        conversation = get_conversation(user, conversation_id)
        
        # Delete the entire conversation
        conversation.delete()
        
        return {"success": True, "message": "Conversation deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting conversation: {str(e)}")
        return {"success": False, "error": str(e)}

def build_conversation_history(conversation):
    """
    Builds a formatted conversation history for the AI model.
    Returns a list of messages in the format expected by the AI APIs.
    
    Args:
        conversation: The AgentConversation object
        
    Returns:
        list: A list of message dictionaries with 'role' and 'content' keys
    """
    messages = []
    
    # Add system prompt if it exists
    if hasattr(conversation, 'system_prompt'):
        messages.append({
            "role": "system",
            "content": conversation.system_prompt.content
        })
    
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

def get_last_assistant_message(conversation):
    """
    Gets the most recent assistant message from a conversation.
    
    Args:
        conversation: The AgentConversation object
        
    Returns:
        AgentMessage: The most recent assistant message, or None if none exists
    """
    return AgentMessage.objects.filter(
        conversation=conversation,
        role='assistant'
    ).order_by('-created_at').first()

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
    Abstract base class for specialized agent services.
    
    This class provides common functionality for all agent services and defines
    the interface that specialized services must implement. It should not be
    instantiated directly.
    """
    
    def __init__(self):
        """Initialize the agent service with API clients."""
        self.openai_client = openai_client
        self.anthropic_client = anthropic_client
    
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
        return check_user_credits(user, model)
    
    def deduct_credits(self, user, model):
        """
        Deduct amount from user's account based on model used.
        
        Args:
            user: The Django user object
            model (str): The AI model to use
            
        Returns:
            bool: Success status
        """
        return deduct_credits(user, model)
    
    def get_active_conversation(self, user):
        """
        Retrieve the active conversation for the user.
        
        Args:
            user: The Django user object
            
        Returns:
            Conversation: The active conversation
        """
        return get_active_conversation(user)
    
    # Conversation Management Methods
    def list_conversations(self, user, project_id=None):
        """
        List all agent conversations for a user, optionally filtered by project.
        
        Args:
            user: The Django user object
            project_id (int, optional): The ID of the project to filter by
            
        Returns:
            QuerySet: Agent conversations for the user
        """
        return list_conversations(user, project_id)
    
    def get_conversation(self, user, conversation_id):
        """
        Get a specific conversation by ID.
        
        Args:
            user: The Django user object
            conversation_id (int): The ID of the conversation
            
        Returns:
            AgentConversation: The conversation object
        """
        return get_conversation(user, conversation_id)
    
    def get_conversation_messages(self, user, conversation_id):
        """
        Get all messages for a specific conversation.
        
        Args:
            user: The Django user object
            conversation_id (int): The ID of the conversation
            
        Returns:
            QuerySet: All messages in the conversation
        """
        return get_conversation_messages(user, conversation_id)
    
    def clear_conversation(self, user, conversation_id):
        """
        Clear all messages in a conversation, keeping the system prompt.
        
        Args:
            user: The Django user object
            conversation_id (int): The ID of the conversation
            
        Returns:
            dict: Result of the operation
        """
        return clear_conversation(user, conversation_id)
    
    def delete_conversation(self, user, conversation_id):
        """
        Delete a conversation including all messages and system prompt.
        
        Args:
            user: The Django user object
            conversation_id (int): The ID of the conversation
            
        Returns:
            dict: Result of the operation
        """
        return delete_conversation(user, conversation_id)
    
    # Builder Mode Methods
    def process_builder_mode_input(self, user_input, model, file_name, user):
        """
        Process a user input in builder mode to generate website content.
        
        Args:
            user_input (str): The user's input message
            model (str): The AI model to use
            file_name (str): The name of the file to generate or modify
            user: The Django user object
            
        Returns:
            dict: The result of the operation
        """
        try:
            # Check if user has enough credits
            has_credits, required_credits = self.check_user_credits(user, model)
            if not has_credits:
                return {
                    'success': False,
                    'error': 'insufficient_credits',
                    'required_credits': required_credits,
                    'redirect_url': reverse('payments:create-checkout-session')
                }

            logger.info(f"Processing builder mode input: {user_input}")
            
            # Validate required fields
            if not user_input or not user_input.strip():
                raise ValueError('User input cannot be empty')
            if not model:
                raise ValueError('Model selection is required')
            if not file_name:
                raise ValueError('File selection is required')

            # Get the active conversation for the specific project
            conversation = self.get_active_conversation(user)
            
            if not conversation.project.user_project:
                raise ValueError("No associated user project found")
                
            # Get or create the page/file
            page, created = Page.objects.get_or_create(
                conversation=conversation,
                filename=file_name
            )

            # Get project paths
            project_path = conversation.project.user_project.project_path
            file_path = os.path.join(project_path, 
                                    'static/css' if file_name.endswith('.css') else 'templates', 
                                    file_name)
            
            from .template_agent_service import TemplateAgentService
            from .stylesheet_agent_service import StylesheetAgentService
            
            # Create agents on demand
            template_agent = TemplateAgentService()
            stylesheet_agent = StylesheetAgentService()
            
            # Choose the appropriate agent based on file type
            agent = stylesheet_agent if file_name.endswith('.css') else template_agent
            
            # Process the request with the appropriate agent
            result = agent.handle_template_request(
                user_input=user_input,
                model=model,
                user=user,
                file_path=file_path
            ) if file_name.endswith('.html') else agent.handle_stylesheet_request(
                user_input=user_input,
                model=model,
                user=user,
                file_path=file_path
            )
            
            # If successful, deduct credits
            if result.get('success'):
                self.deduct_credits(user, model)
                
                # Store message in the Builder conversation too
                Message.objects.create(
                    conversation=conversation,
                    role='user',
                    content=user_input,
                    page=page
                )
                
                Message.objects.create(
                    conversation=conversation,
                    role='assistant',
                    content=result['response'],
                    page=page
                )
            
            return result
                
        except Exception as e:
            logger.error(f"Error in process_builder_mode_input: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    # Chat Mode Methods
    def process_chat_mode_input(self, user_input, model, user, project_id=None, conversation_id=None):
        """
        Process a user input in chat mode.
        
        Args:
            user_input (str): The user's input message
            model (str): The AI model to use
            user: The Django user object
            project_id (int, optional): The ID of the project
            conversation_id (int, optional): The ID of an existing conversation
            
        Returns:
            dict: The result of the operation
        """
        try:
            # Check if user has enough credits
            has_credits, required_credits = self.check_user_credits(user, model)
            if not has_credits:
                return {
                    'success': False,
                    'error': 'insufficient_credits',
                    'required_credits': required_credits,
                    'redirect_url': reverse('payments:create-checkout-session')
                }

            logger.info(f"Processing chat mode input: {user_input}")
            
            from .chat_agent_service import ChatAgentService
            
            # Create chat agent on demand
            chat_agent = ChatAgentService()
            
            # Process the request with the chat agent
            result = chat_agent.handle_chat_request(
                user_input=user_input,
                model=model,
                user=user,
                project_path=project_id,
                conversation_id=conversation_id
            )
            
            # If successful, deduct credits
            if result.get('success'):
                self.deduct_credits(user, model)
            
            return result
                
        except Exception as e:
            logger.error(f"Error in process_chat_mode_input: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    # Undo Method
    def undo_last_action(self, user, page_name):
        """
        Undo the last AI-generated change to a specific file.
        
        Args:
            user: The Django user object
            page_name (str): The name of the file to undo changes for
            
        Returns:
            dict: Result of the operation
        """
        try:
            # Get the active conversation
            conversation = self.get_active_conversation(user)
            
            # Validate the page exists
            try:
                page = Page.objects.get(
                    conversation=conversation,
                    filename=page_name
                )
            except Page.DoesNotExist:
                return {
                    'success': False,
                    'error': f"No file named '{page_name}' found in the current project."
                }
            
            # Get the last assistant message for this page
            last_message = Message.objects.filter(
                conversation=conversation,
                page=page,
                role='assistant'
            ).order_by('-created_at').first()
            
            if not last_message:
                return {
                    'success': False,
                    'error': f"No previous AI-generated content found for '{page_name}'."
                }
            
            # Get the previous assistant message
            previous_message = Message.objects.filter(
                conversation=conversation,
                page=page,
                role='assistant',
                created_at__lt=last_message.created_at
            ).order_by('-created_at').first()
            
            if not previous_message:
                return {
                    'success': False,
                    'error': f"No previous version available for '{page_name}'."
                }
                
            # Get the file path
            project_path = conversation.project.user_project.project_path
            file_path = os.path.join(project_path, 
                                    'static/css' if page_name.endswith('.css') else 'templates', 
                                    page_name)
            
            # Update the file with the previous content
            with open(file_path, 'w') as f:
                f.write(previous_message.content)
            
            # Delete the most recent assistant message
            last_message.delete()
            
            return {
                'success': True,
                'message': f"Successfully reverted '{page_name}' to the previous version.",
                'content': previous_message.content
            }
            
        except Exception as e:
            logger.error(f"Error in undo_last_action: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_content(self, prompt, model='claude-3-5-sonnet-20241022', system_prompt=None, file_path=None):
        """
        Generate content using the specified AI model.
        
        Args:
            prompt (str): The user prompt to send to the AI model
            model (str): The AI model to use
            system_prompt (str, optional): Custom system prompt to use
            file_path (str, optional): Path to the file being generated or modified
            
        Returns:
            dict: Result of the generation containing success status and content
        """
        try:
            if 'claude' in model:
                return self._generate_with_anthropic(prompt, model, system_prompt or self._get_default_system_prompt(file_path))
            elif 'gpt' in model:
                return self._generate_with_openai(prompt, model, system_prompt or self._get_default_system_prompt(file_path))
            else:
                raise ValueError(f"Unsupported model: {model}")
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            raise
    
    def _generate_with_anthropic(self, prompt, model, system_prompt):
        """
        Generate content using Anthropic's Claude models.
        
        Args:
            prompt (str): The user prompt to send to Claude
            model (str): The specific Claude model to use
            system_prompt (str): The system prompt to set context
            
        Returns:
            dict: Result containing success status and generated content
        """
        try:
            # Make the API call
            response = self.anthropic_client.messages.create(
                model=model,
                max_tokens=4096,
                temperature=0.7,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            return {
                'success': True,
                'content': response.content[0].text,
                'model': model
            }
        except Exception as e:
            logger.error(f"Error with Anthropic API: {str(e)}")
            raise
    
    def _generate_with_openai(self, prompt, model, system_prompt):
        """
        Generate content using OpenAI's GPT models.
        
        Args:
            prompt (str): The user prompt to send to GPT
            model (str): The specific GPT model to use
            system_prompt (str): The system prompt to set context
            
        Returns:
            dict: Result containing success status and generated content
        """
        try:
            # Map model names to actual OpenAI models
            model_mapping = {
                'gpt-4o': 'gpt-4',
                'gpt-4o-mini': 'gpt-4-turbo-preview'
            }
            openai_model = model_mapping.get(model, model)
            
            # Make the API call
            response = self.openai_client.chat.completions.create(
                model=openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4096
            )
            
            return {
                'success': True,
                'content': response.choices[0].message.content,
                'model': model
            }
        except Exception as e:
            logger.error(f"Error with OpenAI API: {str(e)}")
            raise
    
    def _get_default_system_prompt(self, file_path=None):
        """
        Get a default system prompt based on the context.
        
        Args:
            file_path (str, optional): The path to the file being generated or modified
            
        Returns:
            str: A system prompt appropriate for the context
        """
        base_prompt = """You are an expert web developer assistant helping to build web applications.
You write clean, maintainable, and modern code following best practices.
When generating code, focus on:
1. Modern design patterns and practices
2. Responsive and accessible UI
3. Clean and well-documented code
4. Security best practices
5. Performance optimization"""

        if file_path:
            file_type = os.path.splitext(file_path)[1]
            if file_type == '.html':
                base_prompt += "\nYou are currently working on an HTML template file. Focus on semantic HTML and accessibility."
            elif file_type == '.css':
                base_prompt += "\nYou are currently working on a CSS file. Use modern CSS features and maintain a consistent design system."
            elif file_type == '.js':
                base_prompt += "\nYou are currently working on a JavaScript file. Write clean, modular code with proper error handling."
        
        return base_prompt
    
    def process_conversation(self, user_input, model, user, system_prompt_content=None, **kwargs):
        """
        Process a conversation with an AI agent.
        
        Args:
            user_input (str): The user's message
            model (str): The AI model to use
            user: The Django user object
            system_prompt_content (str, optional): Content for a new system prompt
            **kwargs: Additional arguments for specialized processing
                    Returns:
            dict: The result of the operation, including success status and response
        """
        try:
            # Get or create conversation
            if system_prompt_content:
                conversation = AgentConversation.objects.create(
                    user=user,
                    model_name=model
                )
                SystemPrompt.objects.create(
                    conversation=conversation,
                    content=system_prompt_content
                )
            else:
                conversation = kwargs.get('conversation')
                
                if not conversation:
                    conversation = AgentConversation.objects.filter(
                        user=user
                    ).order_by('-created_at').first()
                    
                    if not conversation:
                        return {
                            'success': False,
                            'error': 'no_active_conversation'
                        }

            # Use provided messages if available, otherwise build them
            api_messages = kwargs.get('messages', [])
            if not kwargs.get('use_provided_messages', False):
                api_messages = []
                
                # 1. Add system prompt (from the specific agent service)
                system_prompt = self.get_system_prompt()
                print("\n=== SYSTEM PROMPT ===")
                print(system_prompt['content'])
                api_messages.append(system_prompt)
                
                # 2. Add project files if available
                project_path = kwargs.get('project_path')
                if project_path:
                    print("\n=== PROJECT FILES ===")
                    templates_dir = os.path.join(project_path, 'templates')
                    css_dir = os.path.join(project_path, 'static', 'css')
                    
                    # Add HTML files
                    if os.path.exists(templates_dir):
                        html_files = [f for f in os.listdir(templates_dir) if f.endswith('.html')]
                        html_files.sort()
                        
                        # Ensure base.html is first, followed by index.html
                        if 'base.html' in html_files:
                            html_files.remove('base.html')
                            html_files.insert(0, 'base.html')
                        if 'index.html' in html_files:
                            html_files.remove('index.html')
                            html_files.insert(1 if 'base.html' in html_files else 0, 'index.html')
                        
                        for filename in html_files:
                            print(f"Adding file: {filename}")
                            file_path = os.path.join(templates_dir, filename)
                            try:
                                with open(file_path, 'r') as f:
                                    content = f.read()
                                    api_messages.append({
                                        "role": "assistant",
                                        "content": f"[File: {filename}]\n{content}"
                                    })
                            except FileNotFoundError:
                                print(f"File not found: {filename}")
                                continue
                    
                    # Add CSS file
                    css_path = os.path.join(css_dir, 'styles.css')
                    if os.path.exists(css_path):
                        print("Adding file: styles.css")
                        try:
                            with open(css_path, 'r') as f:
                                content = f.read()
                                api_messages.append({
                                    "role": "assistant",
                                    "content": f"[File: styles.css]\n{content}"
                                })
                        except FileNotFoundError:
                            print("File not found: styles.css")
                            pass
                
                # 3. Add conversation history
                history_messages = AgentMessage.objects.filter(
                    conversation=conversation
                ).order_by('created_at')
                
                for msg in history_messages:
                    api_messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })
            
            # 4. Add the user's message
            api_messages.append({
                "role": "user",
                "content": user_input
            })
            
            # Generate the response using the appropriate model
            if 'claude' in model:
                completion = self.anthropic_client.messages.create(
                    model=model,
                    max_tokens=4096,
                    temperature=0.7,
                    system=api_messages[0]['content'] if api_messages[0]['role'] == 'system' else "",
                    messages=[msg for msg in api_messages if msg['role'] != 'system']
                )
                response_content = completion.content[0].text
            elif 'gpt' in model:
                completion = self.openai_client.chat.completions.create(
                    model=model,
                    messages=api_messages,
                    temperature=0.7,
                    max_tokens=4096
                )
                response_content = completion.choices[0].message.content
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
                AgentMessage.objects.create(
                    conversation=conversation,
                    role='user',
                    content=user_input
                )
                
                # Store assistant response
                AgentMessage.objects.create(
                    conversation=conversation,
                    role='assistant',
                    content=response_content
                )
            
            return {
                'success': True,
                'response': response_content,
                'conversation_id': conversation.id
            }
        except Exception as e:
            logger.error(f"Error processing conversation: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            } 