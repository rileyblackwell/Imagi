"""
Chat agent service for Imagi Oasis.

This module provides a specialized agent service for chat-based interactions,
allowing users to have natural language conversations about their web applications.
"""

from dotenv import load_dotenv
from .agent_service import BaseAgentService
from ..models import AgentConversation, SystemPrompt, AgentMessage
from django.shortcuts import get_object_or_404
import os

# Load environment variables from .env
load_dotenv()

class ChatAgentService(BaseAgentService):
    """
    Specialized agent service for chat-based interactions.
    
    This service handles natural language conversations with users about their
    web applications, providing explanations, suggestions, and guidance.
    """
    
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
                "- You can see all project files in the conversation history.\n"
                "- Users may switch between different files during the conversation.\n"
                "- Your goal is to help users create professional, modern web applications.\n"
                "- Always maintain a helpful, professional tone."
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

    def build_chat_conversation_history(self, project_path, messages):
        """
        Build a complete conversation history including all project files.
        
        Args:
            project_path (str): Path to the project directory
            messages (list): Existing conversation messages
            
        Returns:
            list: A list of message dictionaries with 'role' and 'content' keys
        """
        api_messages = []
        
        # 1. Add system prompt
        api_messages.append(self.get_system_prompt())
        
        # 2. Add all project files
        if project_path:
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
                    file_path = os.path.join(templates_dir, filename)
                    try:
                        with open(file_path, 'r') as f:
                            content = f.read()
                            api_messages.append({
                                "role": "assistant",
                                "content": f"[File: {filename}]\n{content}"
                            })
                    except FileNotFoundError:
                        continue
            
            # Add CSS file
            css_path = os.path.join(css_dir, 'styles.css')
            if os.path.exists(css_path):
                try:
                    with open(css_path, 'r') as f:
                        content = f.read()
                        api_messages.append({
                            "role": "assistant",
                            "content": f"[File: styles.css]\n{content}"
                        })
                except FileNotFoundError:
                    pass
        
        # 3. Add conversation history
        api_messages.extend(messages)
        
        return api_messages

    def process_chat(self, user_input, model, user, project_path, conversation_history=None):
        """
        Process a chat interaction with complete project context.
        
        Args:
            user_input (str): The user's message
            model (str): The AI model to use
            user: The Django user object
            project_path (str): Path to the project directory
            conversation_history (list, optional): Existing conversation messages
            
        Returns:
            dict: The result of the operation, including success status and response
        """
        try:
            # Build complete conversation history
            api_messages = self.build_chat_conversation_history(
                project_path,
                conversation_history or []
            )
            
            # Add current user message
            api_messages.append({
                "role": "user",
                "content": user_input
            })
            
            # Make API call with complete context
            result = self.process_conversation(
                user_input=user_input,
                model=model,
                user=user,
                conversation_id=None,
                project_path=project_path
            )
            
            return result
            
        except Exception as e:
            print(f"Error in process_chat: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def handle_chat_request(self, user_input, model, user, project_path, conversation_id=None):
        """
        Handle a complete chat request, including conversation management.
        
        Args:
            user_input (str): The user's message
            model (str): The AI model to use
            user: The Django user object
            project_path (str): The path to the project directory
            conversation_id (int, optional): The ID of an existing conversation
            
        Returns:
            dict: The result of the operation, including success status and response
        """
        try:
            # Get or create conversation
            if conversation_id:
                conversation = get_object_or_404(
                    AgentConversation,
                    id=conversation_id,
                    user=user
                )
            else:
                conversation = AgentConversation.objects.create(
                    user=user,
                    model_name=model,
                    provider='anthropic' if model.startswith('claude') else 'openai'
                )
                # Create initial system prompt
                system_prompt = self.get_system_prompt()
                SystemPrompt.objects.create(
                    conversation=conversation,
                    content=system_prompt['content']
                )
            
            # Save user message
            user_message = AgentMessage.objects.create(
                conversation=conversation,
                role='user',
                content=user_input
            )
            
            # Get conversation history
            from .agent_service import build_conversation_history
            history = build_conversation_history(conversation)
            
            # Process chat interaction
            result = self.process_chat(
                user_input=user_input,
                model=model,
                user=user,
                project_path=project_path,
                conversation_history=history
            )
            
            if result.get('success'):
                # Save assistant response
                assistant_message = AgentMessage.objects.create(
                    conversation=conversation,
                    role='assistant',
                    content=result['response']
                )
                
                return {
                    'success': True,
                    'conversation_id': conversation.id,
                    'response': result['response'],
                    'user_message': user_message,
                    'assistant_message': assistant_message
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Unknown error'),
                    'response': result.get('response')
                }
                
        except Exception as e:
            print(f"Error in handle_chat_request: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def process_conversation(self, user_input, model, user, conversation_id=None, project_path=None):
        """
        Process a chat conversation with the AI model.
        
        This method:
        1. Creates or retrieves an existing conversation
        2. Builds the conversation history including system prompt and project files
        3. Sends the conversation to the AI model
        4. Stores the response in the database
        5. Returns a success response with the AI's reply
        
        Args:
            user_input (str): The user's message
            model (str): The AI model to use (e.g., 'claude-3-5-sonnet-20241022', 'gpt-4o')
            user (User): The Django user making the request
            conversation_id (int, optional): ID of an existing conversation
            project_path (str, optional): Path to the project files
            
        Returns:
            dict: Response with status and message data
        """
        try:
            # Get or create conversation
            conversation = None
            if conversation_id:
                try:
                    conversation = AgentConversation.objects.get(id=conversation_id, user=user)
                except AgentConversation.DoesNotExist:
                    conversation = None
            
            if not conversation:
                # Determine provider based on model name
                provider = 'anthropic' if 'claude' in model else 'openai'
                
                # Create new conversation
                conversation = AgentConversation.objects.create(
                    user=user,
                    model_name=model,
                    provider=provider
                )
                
                # Create initial system prompt
                SystemPrompt.objects.create(
                    conversation=conversation,
                    content=self.get_system_prompt()['content']
                )
            
            # Create user message
            user_message = AgentMessage.objects.create(
                conversation=conversation,
                role='user',
                content=user_input
            )
            
            # Build conversation history
            conversation_history = self.build_conversation_history(conversation)
            
            # Add project files to conversation if provided
            if project_path:
                conversation_history = self.build_chat_conversation_history(project_path, conversation_history)
            
            # Process with appropriate model
            if 'claude' in model:
                response_content = self.process_with_anthropic(conversation_history, model)
            else:
                response_content = self.process_with_openai(conversation_history, model)
            
            # Create assistant message
            assistant_message = AgentMessage.objects.create(
                conversation=conversation,
                role='assistant',
                content=response_content
            )
            
            # Return success response
            return {
                'success': True,
                'conversation_id': conversation.id,
                'response': response_content,
                'timestamp': assistant_message.created_at.isoformat()
            }
            
        except Exception as e:
            # Log the error (you can use more sophisticated logging)
            print(f"Error in chat conversation: {str(e)}")
            
            # Return error response
            return {
                'success': False,
                'error': str(e)
            } 