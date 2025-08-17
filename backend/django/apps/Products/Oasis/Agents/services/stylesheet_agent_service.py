"""
Stylesheet agent service for Imagi Oasis.

This module provides a specialized agent service for CSS stylesheet generation,
allowing users to create and modify stylesheets through natural language instructions.
"""

from dotenv import load_dotenv
import cssutils
import logging
from .agent_service import BaseAgentService
import re
import os
from functools import lru_cache
import hashlib


# Set up logger
logger = logging.getLogger(__name__)

# Suppress cssutils parsing warnings
cssutils.log.setLevel(logging.CRITICAL)

# Load environment variables from .env
load_dotenv()

class StylesheetAgentService(BaseAgentService):
    """
    Specialized agent service for CSS stylesheet generation.
    
    This service handles the generation and modification of CSS stylesheets
    based on user instructions, ensuring they follow best practices and proper structure.
    """
    
    def __init__(self):
        """Initialize the stylesheet agent service."""
        super().__init__()
        self.current_file_path = None
        # Initialize an in-memory cache to store common CSS components
        self._css_component_cache = {}
        # Override default timeout for stylesheet generation
        self.request_timeout = 30  # Reduced from default 60s in base class
        # Define base system prompt from get_system_prompt for easier access
        self.BASE_SYSTEM_PROMPT = self.get_system_prompt()["content"]
    
    def get_system_prompt(self, project_name=None):
        """
        Get a concise, optimized system prompt for CSS stylesheet generation.

        Args:
            project_name (str, optional): The name of the project
            
        Returns:
            dict: Message with 'role' and 'content'.
        """
        # Use provided project name or default
        if not project_name:
            project_name = "your project"
            
        return {
            "role": "system",
            "content": (
                f"You are an expert web developer generating clean, valid CSS stylesheets for {project_name}."
                "\n\nInstructions:"
                "\n- Provide only complete, valid CSS code with proper indentation; no explanations, plain text, or non-CSS comments."
                "\n- Include CSS comments only when necessary for clarity within the stylesheet."
                "\n- Structure stylesheets clearly into sections: CSS variables (:root), resets, base styles, layouts, components, and media queries."
                "\n- Use CSS variables consistently for colors, spacing, and fonts."
                "\n- Follow a mobile-first approach, progressively enhanced using responsive design via media queries."
                "\n- Leverage modern CSS features (flexbox, grid, clamp(), min(), max(), gap)."
                "\n- Draw design inspiration from modern, visually appealing companies like Stripe, Airbnb, Twilio, Discord, and Google."
                "\n\nExample format:"
                "\n:root {"
                "\n  --color-primary: #6366f1;"
                "\n  --color-secondary: #0ea5e9;"
                "\n  --font-family: 'Inter', sans-serif;"
                "\n  --spacing-unit: 16px;"
                "\n}"
                "\n\n*, *::before, *::after {"
                "\n  box-sizing: border-box;"
                "\n  margin: 0;"
                "\n  padding: 0;"
                "\n}"
                "\n\nbody {"
                "\n  font-family: var(--font-family);"
                "\n  color: var(--color-primary);"
                "\n  padding: var(--spacing-unit);"
                "\n}"
                "\n\n.container {"
                "\n  max-width: 1200px;"
                "\n  margin: 0 auto;"
                "\n  display: flex;"
                "\n  gap: var(--spacing-unit);"
                "\n}"
                "\n\n.button {"
                "\n  background-color: var(--color-primary);"
                "\n  color: #fff;"
                "\n  border: none;"
                "\n  border-radius: 4px;"
                "\n  padding: 0.5rem 1rem;"
                "\n  cursor: pointer;"
                "\n}"
                "\n\n@media (min-width: 768px) {"
                "\n  .container { flex-direction: row; }"
                "\n  .button { font-size: 1.2rem; }"
                "\n}"
            )
        }


    def get_additional_context(self, **kwargs):
        """
        Get stylesheet-specific context.
        
        Args:
            **kwargs: Additional arguments
            
        Returns:
            str: Additional context for the system prompt
        """
        # If additional_context is provided directly in kwargs, use it
        if 'additional_context' in kwargs and kwargs['additional_context']:
            return kwargs['additional_context']
            
        # Otherwise build the context based on file_path and other parameters
        context_parts = []
        
        # Add file path context
        file_path = kwargs.get('file_path') or self.current_file_path
        if file_path:
            context_parts.append(f"You are creating/editing the CSS file: {file_path}")
        else:
            context_parts.append("You are creating/editing styles.css for the project")
            
        # Add project files context if available
        if self.project_files:
            context_parts.append(f"The project contains {len(self.project_files)} files for context")
            
        return "\n".join(context_parts)
    
    def validate_response(self, content):
        """
        Validate CSS syntax and structure.
        
        Args:
            content (str): The CSS content to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            # Check if content is empty
            if not content or not content.strip():
                logger.error("CSS content is empty")
                return False, "CSS content is empty"
            
            # Parse CSS to check for syntax errors
            try:
                cssutils.parseString(content)
                logger.info("CSS parsed successfully")
            except Exception as e:
                logger.warning(f"CSS parsing error: {str(e)}")
                # Return true anyway, we'll just use the raw content
                return True, None
            
            return True, None
            
        except Exception as e:
            logger.error(f"Unexpected error in CSS validation: {str(e)}")
            # Be forgiving - return true even if validation fails
            return True, None

    def handle_stylesheet_request(self, user_input, model, user, file_path, conversation_id=None, project_id=None):
        """
        Handle a complete stylesheet generation request, including conversation management.
        
        Args:
            user_input (str): The user's message
            model (str): The AI model to use
            user: The Django user object
            file_path (str): The path to the stylesheet file
            conversation_id (int, optional): The ID of an existing conversation
            project_id (str, optional): The ID of the project
            
        Returns:
            dict: The result of the operation, including success status and response
        """
        try:
            logger.info(f"StylesheetAgentService handling request for file: {file_path}")
            
            # Check cache for existing results
            if len(user_input) < 100:
                cache_key = self._generate_cache_key(user_input, file_path, model)
                cached_result = self._get_cached_result(cache_key)
                if cached_result:
                    logger.info(f"Using cached stylesheet result for {file_path}")
                    return cached_result
            
            # Store the current file path for context
            self.current_file_path = file_path
            
            # Get project details and load project files for context
            project_path = None
            project = None
            
            if project_id:
                try:
                    # Import here to avoid circular imports
                    from apps.Products.Oasis.ProjectManager.models import Project
                    project = Project.objects.get(id=project_id, user=user)
                    project_path = project.project_path
                    
                    # Load project files for context if not already loaded
                    if not self.project_files and project_path:
                        # Load synchronously for build mode to ensure context is available
                        self.project_files = self.load_project_files(project_path)
                        logger.info(f"Loaded {len(self.project_files)} project files for context")
                except Exception as e:
                    logger.warning(f"Could not get project path: {str(e)}")
            
            # Prepare current file data for the API
            current_file = None
            if file_path and project_path:
                try:
                    full_path = os.path.join(project_path, file_path)
                    if os.path.exists(full_path):
                        with open(full_path, 'r') as f:
                            file_content = f.read()
                            current_file = {
                                'path': file_path,
                                'content': file_content,
                                'type': 'css'
                            }
                    else:
                        # If file doesn't exist yet, make an empty CSS file for context
                        current_file = {
                            'path': file_path,
                            'content': "/* New CSS file */",
                            'type': 'css'
                        }
                except Exception as e:
                    logger.warning(f"Could not read file {file_path}: {str(e)}")
            
            # Build additional context for the stylesheet generation
            additional_context = []
            
            # File context
            if self.current_file_path:
                additional_context.append(f"You are creating/editing the CSS file: {self.current_file_path}")
            
            # Project context
            if project:
                additional_context.append(f"Project name: {project.name}")
                if hasattr(project, 'description') and project.description:
                    additional_context.append(f"Project description: {project.description}")
            
            # HTML files for styling context
            html_files = [f["path"] for f in self.project_files if f["path"].endswith(".html")]
            if html_files:
                additional_context.append(f"HTML templates: {', '.join(html_files[:5])}")
            
            # Other CSS files 
            css_files = [f["path"] for f in self.project_files if f["path"].endswith(".css") and f["path"] != self.current_file_path]
            if css_files:
                additional_context.append(f"Other CSS files: {', '.join(css_files[:5])}")
            
            # Process the conversation using the parent class method with additional context
            result = self.process_conversation(
                user_input=user_input,
                model=model,
                user=user,
                conversation_id=conversation_id,
                project_id=project_id,
                project_path=project_path,
                current_file=current_file,
                file_path=file_path,
                project_files=self.project_files,
                additional_context="\n".join(additional_context),
                is_build_mode=True,  # Flag to indicate this is build mode
                timeout=self.request_timeout,  # Use shorter timeout
            )
            
            # Extract CSS content if successful
            if result.get('success', False):
                css_content = self.extract_css_from_response(result['response'])
                result['response'] = css_content
                
                # Set code field to match the exact response
                result['code'] = css_content
                
                # Add flag to indicate this is build mode content (just code)
                result['is_build_mode'] = True
                
                # Cache the result for future similar requests
                if len(user_input) < 100:
                    cache_key = self._generate_cache_key(user_input, file_path, model)
                    self._cache_result(cache_key, result)
            
            # Add flag to ensure messages appear only once in chat feed
            result['single_message'] = True
            
            return result
            
        except Exception as e:
            logger.error(f"Error in handle_stylesheet_request: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': str(e)
            }
    
    def build_conversation_history(self, conversation, project_path=None, current_file=None, is_build_mode=False, current_user_prompt=None):
        """
        Only override to handle unique system prompt logic in build mode. All other logic is delegated to BaseAgentService.
        """
        history = super().build_conversation_history(
            conversation,
            project_path=project_path,
            current_file=current_file,
            current_user_prompt=current_user_prompt
        )
        if is_build_mode:
            # Preserve project information when modifying the history
            project_info = None
            project_name = None
            
            for i, msg in enumerate(history):
                if msg.get('role') == 'system' and 'PROJECT INFORMATION:' in msg.get('content', ''):
                    project_info = msg
                    # Extract project name from project info
                    content = msg.get('content', '')
                    if 'Project Name:' in content:
                        lines = content.split('\n')
                        for line in lines:
                            if line.strip().startswith('Project Name:'):
                                project_name = line.split(':', 1)[1].strip()
                                break
                    break
                    
            # Prepend only the unique system prompt for this agent with project name
            system_prompt = self.get_system_prompt(project_name=project_name)
            # Remove any other system prompt if present
            history = [msg for msg in history if msg.get('role') != 'system']
            
            # Insert the system prompt first, then project info
            if project_info:
                history.insert(0, project_info)
            history.insert(0, system_prompt)
        return history

    # Override this to provide faster timeout and add logging
    def process_conversation(self, user_input, model, user, **kwargs):
        """
        Process a conversation with the stylesheet agent.
        
        Args:
            user_input (str): The user's message
            model (str): The AI model to use
            user: The Django user object
            **kwargs: Additional arguments for processing
            
        Returns:
            dict: The result of the operation, including success status and response
        """
        try:
            # Extract timeout from kwargs if provided
            kwargs.pop('timeout', None) or self.request_timeout
            
            # Get project path and files
            project_path = kwargs.get('project_path')
            if project_path and not self.project_files:
                self.project_files = self.load_project_files(project_path)
                logger.info(f"Loaded {len(self.project_files)} project files for stylesheet context")
            
            # Get or create conversation
            conversation_id = kwargs.get('conversation_id')
            project_id = kwargs.get('project_id')
            system_prompt_content = kwargs.get('system_prompt')
            
            if conversation_id:
                conversation = self.get_conversation(conversation_id, user)
                if not conversation:
                    # Create a new conversation if the requested one doesn't exist
                    conversation = self.create_conversation(user, model, system_prompt_content, project_id)
            else:
                # Create a new conversation if no conversation_id provided
                conversation = self.create_conversation(user, model, system_prompt_content, project_id)
            
            # Get current file
            current_file = kwargs.get('current_file')
            is_build_mode = kwargs.get('is_build_mode', False)
            
            # Build conversation history
            messages = self.build_conversation_history(
                conversation,
                project_path=project_path,
                current_file=current_file,
                is_build_mode=is_build_mode,
                current_user_prompt=user_input
            )
            
            logger.info(f"Processing stylesheet conversation with {len(messages)} messages")
            
            # Determine which AI provider to use based on model ID
            from apps.Products.Oasis.Builder.services.models_service import get_provider_from_model_id
            provider = get_provider_from_model_id(model)
            
            # Prepare response
            response_content = ""
            completion_tokens = None
            
            # Set up request parameters
            temperature = kwargs.get('temperature', 0.5)  # Lower temperature for stylesheets
            max_tokens = kwargs.get('max_tokens', 4096)
            
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
                        'max_tokens': max_tokens,
                        'temperature': temperature,
                    }
                    
                    # Add system prompt if present
                    if system_prompt:
                        anthropic_payload['system'] = system_prompt
                    
                    logger.info(f"Making Anthropic API call for stylesheet generation")
                    
                    # Make API call to Anthropic
                    completion = self.anthropic_client.messages.create(**anthropic_payload)
                    
                    # Extract response content
                    response_content = completion.content[0].text
                    completion_tokens = completion.usage.output_tokens
                    
                    logger.info(f"Received {completion_tokens} tokens from Anthropic API")
                    
                elif provider == 'openai':
                    # Prepare OpenAI Responses API payload
                    openai_payload = {
                        'model': model,
                        'input': messages,
                        'temperature': temperature,
                    }

                    if max_tokens:
                        openai_payload['max_output_tokens'] = max_tokens

                    logger.info(f"Making OpenAI Responses API call for stylesheet generation")

                    # Make API call to OpenAI Responses API
                    completion = self.openai_client.responses.create(**openai_payload)

                    # Extract response content
                    response_content = getattr(completion, 'output_text', None) or ""
                    completion_tokens = getattr(getattr(completion, 'usage', None), 'output_tokens', None)

                    logger.info(f"Received {completion_tokens} output tokens from OpenAI API")
                    
                else:
                    raise ValueError(f"Unsupported AI model provider: {provider}")
                
                # Extract pure CSS from the response
                css_content = self.extract_css_from_response(response_content)
                
                # Validate the response
                is_valid, error_message = self.validate_response(css_content)
                if not is_valid:
                    raise ValueError(f"Invalid CSS: {error_message}")
                
                # Add the assistant's message to the conversation
                self.add_assistant_message(conversation, css_content, user)
                
                # Deduct credits for this API call
                credits_used = self.deduct_credits(user.id, model, completion_tokens)
                
                logger.info(f"Stylesheet generation successful, {credits_used} credits used")
                
                return {
                    'success': True,
                    'response': css_content,
                    'code': css_content,
                    'conversation_id': conversation.id,
                    'credits_used': credits_used
                }
                
            except Exception as e:
                logger.error(f"Error in AI API call: {str(e)}")
                return {
                    'success': False,
                    'error': f"Error calling AI model: {str(e)}",
                    'conversation_id': conversation.id if conversation else None
                }
                
        except Exception as e:
            logger.error(f"Exception in process_conversation: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': f"Error processing stylesheet: {str(e)}"
            }

    def load_project_files(self, project_path):
        """
        Load all relevant project files to provide context for stylesheet generation.
        
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
            
            # Check for CSS files in static/css directory
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
            
            # Check for HTML templates to provide context for styling
            templates_dir = os.path.join(project_path, 'templates')
            if os.path.exists(templates_dir):
                for filename in os.listdir(templates_dir):
                    if filename.endswith('.html'):
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
            
            # Store the project files for later use
            self.project_files = files
            
            return files
            
        except Exception as e:
            logger.error(f"Error loading project files: {str(e)}")
            return files

            reset_end = css_content.find('}', css_content.find('*::after')) if '*::after' in css_content else css_content.find('}', css_content.find('box-sizing')) if 'box-sizing' in css_content else -1
            if reset_end > -1:
                css_content = css_content[:reset_end+1] + css_sections["body"] + css_content[reset_end+1:]
            else:
                css_content += css_sections["body"]
        
        return css_content

    def _generate_cache_key(self, user_input, file_path, model):
        """
        Generate a cache key for storing stylesheet results.
        
        Args:
            user_input (str): The user's prompt
            file_path (str): The path to the stylesheet file
            model (str): The AI model used
            
        Returns:
            str: A unique cache key
        """
        # Create a hash of the inputs to use as a cache key
        key_str = f"{user_input}:{file_path}:{model}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _get_cached_result(self, cache_key):
        """
        Get a cached stylesheet result if available.
        
        Args:
            cache_key (str): The cache key to look up
            
        Returns:
            dict or None: The cached result or None if not found
        """
        return self._css_component_cache.get(cache_key)
    
    def _cache_result(self, cache_key, result):
        """
        Cache a stylesheet result for future use.
        
        Args:
            cache_key (str): The cache key to store under
            result (dict): The result to cache
            
        Returns:
            None
        """
        # Limit cache size to avoid memory issues
        if len(self._css_component_cache) > 100:
            # Clear the oldest 20% of entries
            keys_to_remove = list(self._css_component_cache.keys())[:20]
            for key in keys_to_remove:
                del self._css_component_cache[key]
        
        self._css_component_cache[cache_key] = result

    def extract_css_from_response(self, response):
        """
        Extract pure CSS content from the response.
        
        Args:
            response (str): The response containing CSS
            
        Returns:
            str: The extracted CSS content
        """
        # If the response already looks like pure CSS, return it
        if response.strip().startswith(':root') or response.strip().startswith('/*'):
            return response
        
        # Try to extract CSS content between markdown code blocks
        css_pattern = r'```css\s*([\s\S]*?)\s*```'
        css_match = re.search(css_pattern, response)
        
        if css_match:
            return css_match.group(1).strip()
        
        # Try with just triple backticks (no language specified)
        css_pattern = r'```\s*([\s\S]*?)\s*```'
        css_match = re.search(css_pattern, response)
        
        if css_match:
            return css_match.group(1).strip()
        
        # Fall back to returning the original response with text content removed
        # Remove any explanatory text before or after that's not part of the CSS
        lines = response.split('\n')
        css_start = 0
        css_end = len(lines)
        
        # Find the first line that looks like CSS
        for i, line in enumerate(lines):
            if ':' in line or '{' in line or line.strip().startswith('/*'):
                css_start = i
                break
        
        # Find the last line that looks like CSS
        for i in range(len(lines) - 1, -1, -1):
            line = lines[i].strip()
            if line and ('}' in line or line.endswith(';') or line.endswith('*/')):
                css_end = i + 1
                break
        
        return '\n'.join(lines[css_start:css_end])

    # Apply LRU cache to this method for better performance
    @lru_cache(maxsize=32)
    def get_default_css_sections(self):
        """
        Get default CSS sections for the stylesheet.
        
        Returns:
            dict: A dictionary of default CSS sections
        """
        return {
            "root": """
:root {
  /* Color Variables */
  --color-primary: #6366f1;
  --color-secondary: #0ea5e9;
  --color-text: #1f2937;
  --color-background: #ffffff;
  --color-muted: #9ca3af;
  --color-accent: #fb923c;
  
  /* Typography */
  --font-family: 'Inter', system-ui, -apple-system, sans-serif;
  --font-size-base: 16px;
  
  /* Spacing */
  --spacing-unit: 16px;
  --spacing-xs: calc(var(--spacing-unit) * 0.25);
  --spacing-sm: calc(var(--spacing-unit) * 0.5);
  --spacing-md: var(--spacing-unit);
  --spacing-lg: calc(var(--spacing-unit) * 1.5);
  --spacing-xl: calc(var(--spacing-unit) * 2);
  
  /* Borders */
  --border-radius: 4px;
  --border-color: #e5e7eb;
}
""",
            "reset": """
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}
""",
            "body": """
body {
  font-family: var(--font-family);
  color: var(--color-text);
  background-color: var(--color-background);
  line-height: 1.5;
  font-size: var(--font-size-base);
}
"""
        }

    def process_stylesheet(self, prompt, model, user, project_id=None, file_path=None, conversation_id=None):
        """
        Process a stylesheet generation request.
        
        Args:
            prompt (str): The user's prompt describing the stylesheet
            model (str): The AI model to use
            user (User): The Django user object
            project_id (str, optional): The project ID
            file_path (str, optional): The file path to create/update
            conversation_id (int, optional): ID of existing conversation
            
        Returns:
            dict: The result of the operation
        """
        try:
            # Store file path
            if file_path:
                self.current_file_path = file_path
            
            # Get additional context for this request
            context = self.get_additional_context(
                file_path=file_path,
                project_id=project_id
            )
            
            # Create a custom system prompt
            system_prompt = f"{self.BASE_SYSTEM_PROMPT}\n\n{context}".strip()
            
            # Log the complete system prompt for debugging
            logger.info("==================================================================")
            logger.info("=========== STYLESHEET AGENT SYSTEM PROMPT (BUILD MODE) ==========")
            logger.info("==================================================================")
            logger.info(system_prompt)
            logger.info("==================================================================")
            logger.info("==================== END OF SYSTEM PROMPT ========================")
            logger.info("==================================================================")
            
            # Process the conversation with the agent service
            result = self.process_conversation(
                user_input=prompt,
                model=model,
                user=user,
                project_id=project_id,
                system_prompt=system_prompt,
                conversation_id=conversation_id,
                is_build_mode=True
            )
            
            # Enhance response with file info
            if result.get('success') and file_path:
                result['file_path'] = file_path
                # Set build mode flag to ensure proper UI display
                result['is_build_mode'] = True
            
            return result
            
        except Exception as e:
            logger.error(f"Error in process_stylesheet: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            } 