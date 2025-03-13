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
from dotenv import load_dotenv
from openai import OpenAI
import anthropic
from ..models import AgentMessage, AgentConversation, SystemPrompt
from abc import ABC, abstractmethod

# Load environment variables from .env
load_dotenv()
openai_key = os.getenv('OPENAI_KEY')
anthropic_key = os.getenv('ANTHROPIC_KEY')

# Initialize API clients
openai_client = OpenAI(api_key=openai_key)
anthropic_client = anthropic.Anthropic(api_key=anthropic_key)

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
                
                # 3. Add conversation history
                messages = AgentMessage.objects.filter(
                    conversation=conversation
                ).order_by('created_at')
                
                if messages.exists():
                    print("\n=== CONVERSATION HISTORY ===")
                    for msg in messages:
                        print(f"[{msg.role.upper()}]: {msg.content[:100]}...")
                        api_messages.append({
                            "role": msg.role,
                            "content": msg.content
                        })
                
                # 4. Add current task context
                current_file = kwargs.get('template_name') or kwargs.get('file_name')
                if current_file:
                    context_msg = {
                        "role": "system",
                        "content": f"\n=== CURRENT TASK ===\nYou are working on: {current_file}"
                    }
                    print("\n=== TASK CONTEXT ===")
                    print(context_msg['content'])
                    api_messages.append(context_msg)
                
                # 5. Add new user message
                api_messages.append({
                    "role": "user",
                    "content": user_input
                })
                print("\n=== USER INPUT ===")
                print(user_input)

            # Make API call based on model
            if model.startswith('claude'):
                # Extract messages for Claude (excluding system messages)
                claude_messages = [
                    msg for msg in api_messages 
                    if msg["role"] != "system"
                ]
                
                # Get system content
                system_content = next(
                    (msg["content"] for msg in api_messages if msg["role"] == "system"),
                    self.get_system_prompt()["content"]
                )
                
                completion = self.anthropic_client.messages.create(
                    model=model,
                    max_tokens=2048,
                    system=system_content,
                    messages=claude_messages
                )
                
                if completion.content:
                    response = completion.content[0].text
                else:
                    raise ValueError("Empty response from Claude API")
            else:
                completion = self.openai_client.chat.completions.create(
                    model=model,
                    messages=api_messages
                )
                response = completion.choices[0].message.content

            # Log the response
            print("\n=== AI RESPONSE ===")
            print(response)
            print("\n=== END CONVERSATION ===\n")

            # Validate and save messages
            is_valid, error_message = self.validate_response(response)
            if not is_valid:
                return {
                    'success': False,
                    'error': error_message,
                    'response': response
                }

            # Only save messages if we're not using provided ones
            if not kwargs.get('use_provided_messages', False):
                AgentMessage.objects.create(
                    conversation=conversation,
                    role="user",
                    content=user_input
                )

                AgentMessage.objects.create(
                    conversation=conversation,
                    role="assistant",
                    content=response
                )

            return {
                'success': True,
                'response': response,
                'conversation_id': conversation.id
            }

        except Exception as e:
            print(f"Error in process_conversation: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            } 