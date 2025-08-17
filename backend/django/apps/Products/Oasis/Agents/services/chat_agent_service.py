"""
Chat agent service for Imagi Oasis.

This module provides a specialized agent service for chat-based interactions,
allowing users to have natural language conversations about their web applications.
It handles both general chat functionality and conversational AI interactions.
"""

import logging
import os
import re
import json
from dotenv import load_dotenv
from .agent_service import BaseAgentService, format_system_prompt
from apps.Products.Oasis.Builder.services.models_service import (
   get_provider_from_model_id, model_supports_temperature
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

    def get_project_name(self, project_id):
        """
        Return the project's name given a project_id, or None if unavailable.
        """
        if not project_id:
            return None
        try:
            from apps.Products.Oasis.ProjectManager.models import Project
            project = Project.objects.get(id=project_id)
            return getattr(project, 'name', None)
        except Exception as e:
            logger.warning(f"Could not get project name for project_id={project_id}: {e}")
            return None

    def get_project_description(self, project_id):
        """
        Return the project's description given a project_id, stripped, or None.
        """
        if not project_id:
            return None
        try:
            from apps.Products.Oasis.ProjectManager.models import Project
            project = Project.objects.get(id=project_id)
            desc = getattr(project, 'description', None)
            if isinstance(desc, str):
                desc = desc.strip()
            return desc or None
        except Exception as e:
            logger.warning(f"Could not get project description for project_id={project_id}: {e}")
            return None

    def get_current_file_name(self, file):
        """
        Return the current file path/name from a file dict, or None.
        """
        if file and isinstance(file, dict):
            return file.get('path') or None
        return None

    def get_current_file_type(self, file):
        """
        Return a human-friendly description of the current file type from a file dict, or None.
        """
        if not (file and isinstance(file, dict)):
            return None
        ftype = (file.get('type') or '').lower()
        mapping = {
            'html': "This is a Django HTML template file.",
            'vue': "This is a Vue.js component file.",
            'css': "This is a CSS stylesheet file.",
            'js': "This is a JavaScript file.",
            'ts': "This is a TypeScript file.",
            'python': "This is a Python file.",
            'py': "This is a Python file.",
        }
        return mapping.get(ftype)

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
            
            # Build additional context using helper methods
            context_parts = []
            file_name = self.get_current_file_name(file)
            file_type_desc = self.get_current_file_type(file)
            if file_name:
                context_parts.append(f"The user is currently working with file: {file_name}")
            if file_type_desc:
                context_parts.append(file_type_desc)

            proj_name = self.get_project_name(project_id)
            if proj_name:
                context_parts.append(f"Detailed context for project: {proj_name}")
            proj_desc = self.get_project_description(project_id)
            if proj_desc:
                context_parts.append(f"Additional project details: {proj_desc}")

            additional_context = "\n".join(context_parts) if context_parts else None

            # Build a combined system prompt: base chat system prompt + additional context
            base_system = self.get_system_prompt(project_name=proj_name)
            combined_system = format_system_prompt(
                base_system.get('content', ''),
                context=additional_context
            )

            # Resolve project path from project_id, and enrich current_file with content if missing
            project_path = None
            if project_id:
                try:
                    from apps.Products.Oasis.ProjectManager.models import Project
                    project = Project.objects.get(id=project_id, user=user)
                    project_path = getattr(project, 'project_path', None)
                except Exception as e:
                    logger.warning(f"Could not resolve project path for project_id={project_id}: {e}")

            # If we have a file dict but no content, try to read it from disk using project_path
            current_file = file
            if current_file and isinstance(current_file, dict):
                fpath = current_file.get('path')
                fcontent = current_file.get('content')
                if not fcontent and project_path and fpath:
                    try:
                        abs_path = os.path.join(project_path, fpath)
                        if os.path.exists(abs_path):
                            with open(abs_path, 'r') as fh:
                                current_file['content'] = fh.read()
                    except Exception as e:
                        logger.warning(f"Failed reading current_file content from {fpath}: {e}")
            
            # Process the conversation using the base implementation
            return self.process_conversation(
                user_input=prompt,
                model=model,
                user=user,
                project_id=project_id,
                file=current_file,
                project_path=project_path,
                conversation_id=conversation_id,
                system_prompt=combined_system.get('content', '')
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
                # Create a new conversation if the requested one doesn't exist
                conversation = self.create_conversation(user, model, system_prompt_content, project_id)
        else:
            # Create a new conversation if no conversation_id provided
            conversation = self.create_conversation(user, model, system_prompt_content, project_id)
        
        # Add the user's message to the conversation
        self.add_user_message(conversation, user_input, user)
        
        # Build conversation history including system prompts
        messages = self.build_conversation_history(
            conversation,
            project_path,
            current_file
        )
        
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
                # Prepare OpenAI Responses API payload
                api_model = self.get_api_model(model)

                # Normalize messages to Responses API content parts with role-aware types
                def to_openai_msg(msg):
                    role = msg.get('role', 'user')
                    desired_type = 'output_text' if role == 'assistant' else 'input_text'
                    content = msg.get('content')
                    parts = []
                    if isinstance(content, list):
                        for p in content:
                            if isinstance(p, dict):
                                text_val = p.get('text') if 'text' in p else str(p.get('content', ''))
                                parts.append({"type": desired_type, "text": text_val or ""})
                            else:
                                parts.append({"type": desired_type, "text": str(p)})
                    else:
                        parts = [{"type": desired_type, "text": str(content) if content is not None else ""}]
                    return {
                        'role': role,
                        'content': parts
                    }

                # Extract a top-level system prompt for the Responses API 'instructions' field
                instructions = None
                if messages and messages[0].get('role') == 'system':
                    try:
                        instructions = str(messages[0].get('content') or '')
                        messages = messages[1:]
                    except Exception:
                        # Fallback: leave messages intact if anything goes wrong
                        instructions = None

                openai_messages = [to_openai_msg(m) for m in messages]

                openai_payload = {
                    'model': api_model,
                    'input': openai_messages,
                }
                # Only attach instructions if present
                if instructions:
                    openai_payload['instructions'] = instructions

                # Only include temperature if model supports it
                try:
                    if model_supports_temperature(model):
                        openai_payload['temperature'] = temperature
                except Exception:
                    # Default to not sending temperature on error
                    pass

                if max_tokens:
                    # Responses API uses max_output_tokens
                    openai_payload['max_output_tokens'] = max_tokens
                else:
                    # Provide a safe default to avoid provider-specific requirements
                    openai_payload['max_output_tokens'] = 1024

                # Log the complete payload sent to OpenAI (without large message contents)
                try:
                    masked = {
                        'model': openai_payload['model'],
                        'temperature': openai_payload.get('temperature'),
                        'max_output_tokens': openai_payload.get('max_output_tokens'),
                        'input_count': len(messages)
                    }
                    logger.info(f"🤖 API REQUEST TO OPENAI - Model: {model}")
                    logger.info(f"Complete API payload (masked): {json.dumps(masked, indent=2)}")
                except Exception:
                    logger.info("Prepared OpenAI Responses API payload")

                # Make API call to OpenAI Responses API
                completion = self.openai_client.responses.create(**openai_payload)

                # Extract response content with robust fallbacks
                response_content = getattr(completion, 'output_text', None)
                if not response_content:
                    try:
                        # Fallback to structured output path if available
                        if hasattr(completion, 'output') and completion.output:
                            first = completion.output[0]
                            if hasattr(first, 'content') and first.content:
                                part = first.content[0]
                                # Handle text parts
                                text = getattr(part, 'text', None) or part.get('text') if isinstance(part, dict) else None
                                if text:
                                    response_content = text
                    except Exception:
                        pass
                response_content = response_content or ""
                completion_tokens = getattr(getattr(completion, 'usage', None), 'output_tokens', None)

                # Log usage information
                logger.info(f"🔄 OPENAI COMPLETION TOKENS: {completion_tokens}")
                
            else:
                raise ValueError(f"Unsupported AI model provider: {provider}")

            # Normalize and deduplicate repeated content to avoid duplicate rendering artifacts
            try:
                def _collapse_exact_repeats(raw: str) -> str:
                    if not raw:
                        return raw
                    s = raw.strip()
                    n = len(s)
                    # Check triple then double repeats of the entire content
                    for k in (3, 2):
                        if n % k == 0:
                            part = s[: n // k]
                            if part * k == s:
                                # Return corresponding slice of original to preserve formatting as much as possible
                                return raw[: len(raw) // k]
                    return raw

                def _collapse_consecutive_paragraph_dupes(raw: str) -> str:
                    parts = raw.split("\n\n")
                    deduped = []
                    prev_norm = None
                    for p in parts:
                        normp = re.sub(r"\s+", " ", p.strip())
                        if prev_norm is not None and normp and normp == prev_norm:
                            # skip consecutive identical paragraph
                            continue
                        deduped.append(p)
                        prev_norm = normp
                    return "\n\n".join(deduped)

                # Apply deduplication steps
                response_content = _collapse_exact_repeats(response_content)
                response_content = _collapse_consecutive_paragraph_dupes(response_content)
            except Exception as _norm_err:
                logger.warning(f"Response deduplication failed: {_norm_err}")

            # Add the assistant's message to the conversation (robust dedupe by normalized content within recent window)
            try:
                from apps.Products.Oasis.Agents.models import AgentMessage
                from django.utils import timezone
                from datetime import timedelta

                def norm(txt: str) -> str:
                    try:
                        # Collapse all whitespace and trim for robust comparison
                        return re.sub(r"\s+", " ", (txt or "").strip())
                    except Exception:
                        return (txt or "").strip()

                now = timezone.now()
                window_start = now - timedelta(minutes=2)
                normalized_new = norm(response_content)

                recent_assistant = (
                    AgentMessage.objects
                    .filter(conversation=conversation, role="assistant", created_at__gte=window_start)
                    .order_by('-id')[:3]
                )
                is_duplicate = any(norm(m.content) == normalized_new for m in recent_assistant)

                if is_duplicate:
                    logger.info("Skipped saving duplicate assistant message (matched recent normalized content)")
                else:
                    self.add_assistant_message(conversation, response_content, user)
            except Exception as _dedupe_err:
                logger.warning(f"Deduplication check failed (saving message anyway): {_dedupe_err}")
                self.add_assistant_message(conversation, response_content, user)
            
            # Deduct credits for this API call
            credits_used = self.deduct_credits(user.id, model, request_type='chat', completion_tokens=completion_tokens)
            
            return {
                'success': True,
                'response': response_content,
                'conversation_id': conversation.id,
                'credits_used': credits_used,
                'single_message': True
            }
        except Exception as e:
            # Log the error with traceback
            try:
                import traceback
                logger.error("Error processing conversation:\n" + traceback.format_exc())
            except Exception:
                logger.error(f"Error processing conversation: {str(e)}")
            # Return error message
            return {
                'success': False,
                'error': str(e),
                'conversation_id': conversation.id if 'conversation' in locals() and conversation else None
            }