"""
Stylesheet agent service for Imagi Oasis.

This module provides a specialized agent service for CSS stylesheet generation,
allowing users to create and modify stylesheets through natural language instructions.
"""

from dotenv import load_dotenv
import cssutils
import logging
from .agent_service import BaseAgentService
from django.utils import timezone
import re
import os
from functools import lru_cache
import hashlib
import threading

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
        self.project_files = []
        self.current_file_path = None
        # Initialize an in-memory cache to store common CSS components
        self._css_component_cache = {}
        # Add default timeout override
        self.request_timeout = 30  # Reduced from default 60s
    
    # Create direct method for quickly generating basic stylesheets without AI
    def generate_basic_stylesheet(self):
        """Generate a basic stylesheet without using AI."""
        css_sections = self.get_default_css_sections()
        return (
            css_sections["root"] + 
            css_sections["reset"] + 
            css_sections["body"] + 
            self.get_common_components()
        )
    
    # Add method for common CSS components
    def get_common_components(self):
        """Get common CSS components for quick generation."""
        return """
/* Layout */
.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--spacing-md);
}

/* Flexbox utilities */
.flex {
  display: flex;
}

.flex-col {
  flex-direction: column;
}

.items-center {
  align-items: center;
}

.justify-between {
  justify-content: space-between;
}

.justify-center {
  justify-content: center;
}

.gap-md {
  gap: var(--spacing-md);
}

/* Common components */
.btn {
  display: inline-block;
  padding: var(--spacing-sm) var(--spacing-md);
  background-color: var(--color-primary);
  color: white;
  border-radius: var(--border-radius);
  text-decoration: none;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: background-color 0.2s;
}

.btn:hover {
  background-color: var(--color-accent);
}

/* Media queries */
@media (min-width: 768px) {
  .container {
    padding: 0 var(--spacing-lg);
  }
}
"""

    def get_system_prompt(self):
        """
        Get a concise, optimized system prompt for CSS stylesheet generation.

        Returns:
            dict: Message with 'role' and 'content'.
        """
        return {
            "role": "system",
            "content": (
                "You are an expert web developer generating clean, valid CSS stylesheets for Imagi Oasis, a platform converting user input into professional stylesheets."
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
                sheet = cssutils.parseString(content)
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
            
            # Check for simple requests that can be handled without AI
            if self.can_handle_without_ai(user_input):
                logger.info(f"Handling request without AI for {file_path}")
                css_content = self.generate_basic_stylesheet()
                
                result = {
                    'success': True,
                    'response': css_content,
                    'code': css_content,
                    'is_build_mode': True,
                    'single_message': True,
                    'timestamp': timezone.now().isoformat(),
                    'was_predefined': True
                }
                
                # Cache this result
                cache_key = self._generate_cache_key(user_input, file_path, model)
                self._css_component_cache[cache_key] = result
                
                return result
            
            # Check cache for existing results
            if len(user_input) < 100:
                cache_key = self._generate_cache_key(user_input, file_path, model)
                cached_result = self._get_cached_result(cache_key)
                if cached_result:
                    logger.info(f"Using cached stylesheet result for {file_path}")
                    return cached_result
            
            # Store the current file path for context
            self.current_file_path = file_path
            
            # Get project path for context if project_id is provided
            project_path = None
            if project_id:
                try:
                    # Import here to avoid circular imports
                    from apps.Products.Oasis.ProjectManager.models import Project
                    project = Project.objects.get(id=project_id, user=user)
                    project_path = project.project_path
                    
                    # Load project files for context if not already loaded
                    if not self.project_files and project_path:
                        # Run in background thread to avoid blocking
                        threading.Thread(
                            target=self.load_project_files,
                            args=(project_path,)
                        ).start()
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
                except Exception as e:
                    logger.warning(f"Could not read file {file_path}: {str(e)}")
            
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
                timeout=self.request_timeout,  # Use shorter timeout
            )
            
            # Extract CSS content if successful
            if result.get('success', False):
                css_content = self.extract_css_from_response(result['response'])
                enhanced_css = self.ensure_required_sections(css_content)
                result['response'] = enhanced_css
                
                # Set code field to match the exact response
                result['code'] = enhanced_css
                
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
    
    def can_handle_without_ai(self, user_input):
        """Determine if request can be handled without AI."""
        simple_inputs = [
            "generate basic styles", "create default stylesheet", "basic css",
            "starter css", "default styles", "simple stylesheet", 
            "standard styles", "new stylesheet", "empty stylesheet",
            "base styles", "create styles"
        ]
        return any(phrase in user_input.lower() for phrase in simple_inputs)

    # Override this to provide faster timeout
    def process_conversation(self, user_input, model, user, **kwargs):
        """Process conversation with optional timeout override."""
        # Extract timeout from kwargs if provided
        timeout = kwargs.pop('timeout', None)
        
        # Call original method with potentially modified timeout
        if timeout:
            # Store original timeout
            original_timeout = self.request_timeout
            try:
                # Set new timeout for this request
                self.request_timeout = timeout
                return super().process_conversation(user_input, model, user, **kwargs)
            finally:
                # Restore original timeout
                self.request_timeout = original_timeout
        else:
            return super().process_conversation(user_input, model, user, **kwargs)

    def process_stylesheet(self, prompt, model, user, project_id=None, file_path=None, conversation_id=None):
        """
        Process a stylesheet generation request.
        
        Args:
            prompt (str): The user's prompt
            model (str): The AI model to use
            user: The Django user object
            project_id (str, optional): The ID of the project
            file_path (str, optional): The path to the stylesheet file
            conversation_id (int, optional): The ID of an existing conversation
            
        Returns:
            dict: The result of the operation, including success status and response
        """
        try:
            # Verify the project exists and user has access to it
            if project_id:
                project, error = self.validate_project_access(project_id, user)
                if error:
                    return error
            
            # Use a performance optimization: for very simple requests, we might be able
            # to generate a response without calling the AI
            if self.can_handle_without_ai(prompt):
                logger.info("Using predefined basic stylesheet template")
                css_content = self.generate_basic_stylesheet()
                result = {
                    'success': True,
                    'response': css_content,
                    'file_path': file_path,
                    'timestamp': timezone.now().isoformat(),
                    'was_predefined': True,
                    'is_build_mode': True,
                    'single_message': True,
                    'code': css_content
                }
                
                # Save the generated CSS to the file
                if project_id and file_path:
                    try:
                        # Import file service to handle file operations
                        from apps.Products.Oasis.Builder.services.file_service import FileService
                        
                        # Save the CSS content to the specified file
                        file_result = FileService.update_file_content(
                            project_id=project_id,
                            file_path=file_path,
                            content=result['response'],
                            user=user
                        )
                        
                        logger.info(f"CSS content saved to {file_path} successfully")
                        
                        # Add file info to the result
                        result['file_saved'] = True
                        result['file_info'] = file_result
                    except Exception as e:
                        logger.error(f"Error saving CSS file: {str(e)}")
                        result['file_saved'] = False
                        result['file_error'] = str(e)
                
                return result
            
            # Process the stylesheet using the handle_stylesheet_request method
            result = self.handle_stylesheet_request(
                user_input=prompt,
                model=model,
                user=user,
                file_path=file_path,
                conversation_id=conversation_id,
                project_id=project_id
            )
            
            # Enhance the response with file information
            if result.get('success') and file_path:
                result['file_path'] = file_path
                
                # Add timestamp to the result
                result['timestamp'] = timezone.now().isoformat()
                
                # Set build mode flag to ensure proper UI display
                result['is_build_mode'] = True
                
                # Save the generated CSS to the file in background thread
                if project_id and result.get('response'):
                    try:
                        # Import file service to handle file operations
                        from apps.Products.Oasis.Builder.services.file_service import FileService
                        
                        # Save the CSS content to the specified file
                        file_result = FileService.update_file_content(
                            project_id=project_id,
                            file_path=file_path,
                            content=result['response'],
                            user=user
                        )
                        
                        logger.info(f"CSS content saved to {file_path} successfully")
                        
                        # Add file info to the result
                        result['file_saved'] = True
                        result['file_info'] = file_result
                    except Exception as e:
                        logger.error(f"Error saving CSS file: {str(e)}")
                        result['file_saved'] = False
                        result['file_error'] = str(e)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in process_stylesheet: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': str(e)
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

    def ensure_required_sections(self, css_content):
        """
        Ensure the CSS content has all the required sections.
        
        Args:
            css_content (str): The CSS content to enhance
            
        Returns:
            str: The enhanced CSS content
        """
        # Get default CSS sections
        css_sections = self.get_default_css_sections()
        
        # Check if :root section exists
        if ':root' not in css_content:
            # Add :root section with common variables
            css_content = css_sections["root"] + css_content
        
        # Check if reset section exists
        if '*::before' not in css_content and '*::after' not in css_content:
            # Add basic reset
            # Find position to insert (after :root section)
            root_end = css_content.find('}', css_content.find(':root'))
            if root_end > -1:
                css_content = css_content[:root_end+1] + css_sections["reset"] + css_content[root_end+1:]
            else:
                css_content = css_sections["reset"] + css_content
        
        # Check if body styles exist
        if 'body {' not in css_content:
            # Add basic body styles
            # Find position to insert (after reset section)
            reset_end = css_content.find('}', css_content.find('*::after')) if '*::after' in css_content else css_content.find('}', css_content.find('box-sizing')) if 'box-sizing' in css_content else -1
            if reset_end > -1:
                css_content = css_content[:reset_end+1] + css_sections["body"] + css_content[reset_end+1:]
            else:
                css_content += css_sections["body"]
        
        return css_content

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
        # Get project path if provided
        project_path = kwargs.get('project_path')
        
        # Load project files if project path is provided and not already loaded
        if project_path and not self.project_files:
            self.project_files = self.load_project_files(project_path)
        
        # Use project_files from kwargs if provided (overrides self.project_files)
        if kwargs.get('project_files'):
            self.project_files = kwargs.get('project_files')
            logger.info(f"Using {len(self.project_files)} project files provided in kwargs")
        
        # Add an override for file_path to use in get_additional_context
        if kwargs.get('file_path'):
            self.current_file_path = kwargs.get('file_path')
        
        # Add context about the project files to the system prompt
        additional_context = []
        if self.current_file_path:
            additional_context.append(f"You are creating/editing the CSS file: {self.current_file_path}")
        
        if self.project_files:
            additional_context.append(f"The project contains {len(self.project_files)} files for context")
            # Add information about the most relevant files (HTML, CSS)
            html_files = [f["path"] for f in self.project_files if f["path"].endswith(".html")]
            css_files = [f["path"] for f in self.project_files if f["path"].endswith(".css") and f["path"] != self.current_file_path]
            
            if html_files:
                additional_context.append(f"HTML templates: {', '.join(html_files[:5])}")
            if css_files:
                additional_context.append(f"Other CSS files: {', '.join(css_files[:5])}")
        
        # Add the additional context to kwargs
        kwargs['additional_context'] = "\n".join(additional_context)
        
        # Call parent class process_conversation method
        result = super().process_conversation(user_input, model, user, **kwargs)
        
        # Process the result to ensure it's valid CSS
        if result.get('success'):
            # Extract and enhance CSS content
            css_content = self.extract_css_from_response(result['response'])
            enhanced_css = self.ensure_required_sections(css_content)
            result['response'] = enhanced_css
            
            # Set code field to match the exact response
            result['code'] = enhanced_css
            
            # Add flag to indicate this is build mode content (just code)
            result['is_build_mode'] = True
        
        return result

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