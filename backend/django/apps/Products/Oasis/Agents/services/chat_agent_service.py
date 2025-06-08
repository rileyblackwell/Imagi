"""
Chat agent service for Imagi Oasis.

This module provides a specialized agent service for chat-based interactions,
allowing users to have natural language conversations about their web applications.
It handles both general chat functionality and conversational AI interactions.
"""

import logging
import re
import json
from dotenv import load_dotenv
from .agent_service import BaseAgentService
from apps.Products.Oasis.Builder.services.models_service import (
   get_provider_from_model_id
)


# Load environment variables from .env
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class ChatAgentService(BaseAgentService):
    """
    Specialized agent service for chat-based interactions.
    
    This service handles natural language conversations with users about their
    web applications, providing explanations, suggestions, and guidance.
    It serves as the primary agent for general conversational interactions.
    """
    
    def __init__(self):
        """Initialize the chat agent service"""
        super().__init__()
        # Standard timeout for general queries
        self.request_timeout = 45  # 45 seconds timeout for general queries
    
    def get_system_prompt(self, project_name=None):
        """
        Get the system prompt for chat interactions.
        
        Args:
            project_name (str, optional): The name of the project
        
        Returns:
            dict: A message dictionary with 'role' and 'content' keys
        """
        # Use provided project name or default
        if not project_name:
            project_name = "your project"
            
        return {
            "role": "system",
            "content": (
                f"You are an expert web designer and developer called Imagi Oasis, a powerful ai platform for building web applications. "
                f"You are currently helping the user with their project called {project_name}. "
                "You assist users with understanding their project code, explaining concepts, and providing guidance "
                "on web development using Django, Vue.js, and modern frontend technologies.\n\n"
                
                "Key Responsibilities:\n"
                "1. Help users understand their current website structure and design choices.\n"
                "2. Provide clear explanations about Django templates, CSS styling, and web design best practices.\n"
                "3. Suggest improvements and answer questions about the user's web application.\n"
                "4. Maintain context of the entire project while discussing specific files.\n\n"
                
                "Guidelines for your responses:\n"
                "1. Be concise, clear, and focused on providing actionable information.\n"
                "2. When explaining code, focus on the most important concepts first.\n"
                "3. If asked about a specific file, focus your answer on that file's content.\n"
                "4. Use code examples when helpful, but keep them brief and targeted.\n"
                "5. When suggesting improvements, explain the rationale briefly.\n"
                "6. For technical questions, provide specific, practical guidance.\n"
                "7. Remember that users may be at different skill levels - adjust accordingly.\n"
                
                f"The project '{project_name}' uses:\n"
                "- Backend: Django with REST framework\n"
                "- Frontend: Vue.js 3 with Composition API\n"
                "- Styling: TailwindCSS\n"
                "- Build tools: Vite\n"
                "- State management: Pinia\n"
                "- HTTP client: Axios\n\n"
                
                "Remember:\n"
                "- You don't need to prefix your responses with 'As a web development assistant' or similar phrases.\n"
                "- Give direct, practical advice rather than general platitudes.\n"
                "- If you're not sure about something, say so rather than making up information.\n"
                "- When responding, prioritize being helpful, accurate, and concise.\n"
            )
        }
    
    def validate_response(self, content):
        """
        Validate that the response is appropriate and meets quality standards.
        
        Args:
            content (str): The content to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        # Basic validation
        if not content or not isinstance(content, str):
            return False, "Empty or invalid response received from AI model"
            
        # Check for response length
        if len(content) < 10:
            return False, f"Response too short ({len(content)} chars)"
        
        # Check for common error responses
        error_phrases = [
            "I'm sorry, I cannot",
            "I apologize, but I cannot",
            "As an AI language model",
            "I don't have the ability to"
        ]
        
        # If the response starts with a refusal, it's likely not a good response
        for phrase in error_phrases:
            if content.lower().startswith(phrase.lower()):
                return False, f"Response starts with refusal: '{phrase}...'"
        
        # Check for excessive code blocks - general chat shouldn't have too many code samples
        code_blocks = re.findall(r'```[^`]*```', content)
        if len(code_blocks) > 5:
            return False, f"Too many code blocks in response ({len(code_blocks)})"
            
        return True, None
    
    def get_additional_context(self, **kwargs):
        """
        Get additional context for the chat based on current project and file.
        
        Args:
            **kwargs: Additional arguments including file and project information
            
        Returns:
            str: Additional context for the system prompt
        """
        context_parts = []
        
        # Add current file context if available
        current_file = kwargs.get('file')
        if current_file and isinstance(current_file, dict):
            file_path = current_file.get('path')
            file_type = current_file.get('type', 'unknown')
            
            if file_path:
                context_parts.append(f"The user is currently working with file: {file_path}")
                
                # Add file type context
                if file_type == 'html':
                    context_parts.append("This is a Django HTML template file.")
                elif file_type == 'vue':
                    context_parts.append("This is a Vue.js component file.")
                elif file_type == 'css':
                    context_parts.append("This is a CSS stylesheet file.")
                elif file_type == 'js':
                    context_parts.append("This is a JavaScript file.")
                elif file_type == 'ts':
                    context_parts.append("This is a TypeScript file.")
                elif file_type == 'python':
                    context_parts.append("This is a Python file.")
        
        # Add project information if available - this is separate from the project info
        # added by build_conversation_history, and provides additional context to the system prompt
        project_id = kwargs.get('project_id')
        if project_id:
            try:
                from apps.Products.Oasis.ProjectManager.models import Project
                project = Project.objects.get(id=project_id)
                context_parts.append(f"Detailed context for project: {project.name}")
                
                if hasattr(project, 'description') and project.description:
                    # Format the description to be included in the additional context
                    # This won't replace the main project info, but adds extra context to the system prompt
                    description = project.description.strip()
                    if description:
                        context_parts.append(f"Additional project details: {description}")
            except Exception as e:
                logger.warning(f"Could not get project details for context: {str(e)}")
        
        if not context_parts:
            return None
        
        return "\n".join(context_parts)

    def process_chat(self, prompt, model, user, project_id=None, file=None, conversation_id=None):
        """
        Process a general chat query and return the AI's response.
        
        Args:
            prompt (str): The user's message
            model (str): The AI model to use
            user: The Django user object
            project_id (str, optional): The project ID
            file (dict, optional): The current file with keys: path, content, type
            conversation_id (int, optional): ID of existing conversation
            
        Returns:
            dict: The result of the operation with the AI's response
        """
        try:
            # Validate required parameters
            if not prompt:
                return self.error_response("Prompt is required")
            
            if not model:
                return self.error_response("Model is required")
            
            # Get additional context for this request
            additional_context = self.get_additional_context(
                file=file,
                project_id=project_id
            )
            
            # Process the conversation using the base implementation
            return self.process_conversation(
                user_input=prompt,
                model=model,
                user=user,
                project_id=project_id,
                file=file,
                conversation_id=conversation_id,
                system_prompt=additional_context,
                current_user_prompt=prompt
            )
            
        except Exception as e:
            logger.error(f"Error in process_chat: {str(e)}")
            return self.error_response(str(e))

    def process_message(self, user_input, model_id, user, conversation_id=None, project_id=None, current_file=None, is_build_mode=False):
        """
        Process a chat message and return the AI's response.
        
        This method is a convenience wrapper around process_chat that handles
        additional validation and preprocessing.
        
        Args:
            user_input (str): The user's message
            model_id (str): The AI model to use
            user: The Django user object
            conversation_id (int, optional): ID of existing conversation
            project_id (str, optional): The project ID
            current_file (dict, optional): The current file details
            is_build_mode (bool, optional): Whether this is being used in build mode
            
        Returns:
            dict: The result of the operation with the AI's response
        """
        # Validate current_file if provided
        if current_file:
            is_valid, error = self.validate_current_file(current_file)
            if not is_valid:
                return self.error_response(error)
        
        # Use process_chat to handle the request
        return self.process_chat(
            prompt=user_input,
            model=model_id,
            user=user,
            project_id=project_id,
            file=current_file,
            conversation_id=conversation_id
        )

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
        

    def process_conversation(self, user_input, model, user, **kwargs):
        """
        Process a conversation with the AI model.
        Implements the abstract method from BaseAgentService.
        """
        # Extract optional parameters
        project_id = kwargs.get('project_id')
        project_path = kwargs.get('project_path')
        conversation_id = kwargs.get('conversation_id')
        system_prompt_content = kwargs.get('system_prompt')
        temperature = kwargs.get('temperature', 0.7)
        max_tokens = kwargs.get('max_tokens', None)
        current_file = kwargs.get('file')

        # Get or create conversation
        if conversation_id:
            conversation = self.get_conversation(conversation_id, user)
            if not conversation:
                conversation = self.create_conversation(user, model, project_id)
        else:
            conversation = self.create_conversation(user, model, project_id)

        # ... (rest of method logic)
        project_id = kwargs.get('project_id')
        project_path = kwargs.get('project_path')
        conversation_id = kwargs.get('conversation_id')
        system_prompt_content = kwargs.get('system_prompt')
        kwargs.get('stream', False)
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
        self.check_user_credits(user, model)
        
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
            is_valid, error_message = self.validate_response(response_content)
            if not is_valid:
                raise ValueError(f"Invalid response: {error_message}")
            
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