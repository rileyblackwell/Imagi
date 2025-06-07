"""
Template agent service for Imagi Oasis.

This module provides a specialized agent service for Django HTML template generation,
allowing users to create and modify templates through natural language instructions.
"""

from dotenv import load_dotenv
import logging
from .agent_service import BaseAgentService
import os
import threading
import hashlib


# Load environment variables from .env
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class TemplateAgentService(BaseAgentService):
    """
    Specialized agent service for Django template generation.
    
    This service handles the generation and modification of Django HTML templates
    based on user instructions, ensuring they follow best practices and proper structure.
    """

    def fix_template_issues(self, content, template_name=None):
        """
        Attempt to fix common issues in generated Django template content.
        Args:
            content (str): The generated template content
            template_name (str, optional): The template's filename
        Returns:
            str: The (possibly fixed) template content
        TODO: Implement auto-fix for common template issues (missing blocks, static tags, etc.)
        """
        return content

    def validate_response(self, content):
        """
        Validate that the generated template is a non-empty string and contains Django template tags.
        Args:
            content (str): The template content to validate
        Returns:
            tuple: (is_valid, error_message)
        """
        if not content or not isinstance(content, str):
            return False, "Template content is empty or invalid."
        # Check for at least one Django template tag/block
        if "{%" not in content or "%}" not in content:
            return False, "Template does not contain any Django template tags."
        # Optionally check for required blocks
        required_blocks = ["block content", "block title"]
        missing_blocks = [b for b in required_blocks if b not in content]
        if missing_blocks:
            return False, f"Missing required Django blocks: {', '.join(missing_blocks)}"
        return True, None

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
            for i, msg in enumerate(history):
                if msg.get('role') == 'system' and 'PROJECT INFORMATION:' in msg.get('content', ''):
                    project_info = msg
                    break
                    
            # Prepend only the unique system prompt for this agent
            system_prompt = self.get_system_prompt()
            # Remove any other system prompt if present
            history = [msg for msg in history if msg.get('role') != 'system']
            
            # Insert the system prompt first, then project info
            if project_info:
                history.insert(0, project_info)
            history.insert(0, system_prompt)
        return history


    def __init__(self):
        """Initialize the template agent service."""
        super().__init__()
        self.current_template_name = None
        # Add template cache for improved performance
        self._template_cache = {}
        # Override default timeout for template generation
        self.request_timeout = 30  # Reduced from default 60s in base class
        # Define base system prompt from get_system_prompt for easier access
        self.BASE_SYSTEM_PROMPT = self.get_system_prompt()["content"]

    def get_system_prompt(self):
        """
        Get a concise, optimized system prompt for Django template generation.

        Returns:
        dict: Message with 'role' and 'content'.
        """
        return {
            "role": "system",
            "content": (
                "You are an expert web developer generating only clean, valid Django HTML templates for Imagi Oasis, a platform converting user input into template code."
                "\n\nInstructions:"
                "\n- Provide only valid Django HTML templates; do not include explanations, comments, or additional text."
                "\n- No CSS should be generated within templates; link only to external stylesheet at 'static/css/styles.css'."
                "\n- Templates must always extend 'base.html' and load static files properly."
                "\n- Use Django blocks: 'title', 'content', 'extra_css', and 'extra_js'."
                "\n- Follow minimalist, responsive design inspired by Stripe, AirBnB, Apple, and Google, using semantic HTML5 and clear, intuitive CSS classes."
                "\n- Always use {% static %} tags for asset references."
                "\n- Employ responsive, mobile-first layouts (flexbox/grid); include viewport meta tag."
                "\n- Maintain consistent 2-space indentation."
                "\n- Embed Django template tags within JavaScript inside {% block extra_js %}."
                
                "\n\n!important!"
                "\n- Do not include any hyperlinks or references to other web pages."
                "\n- Do not include images or any references to image files."

                "\n\nNaming conventions:"
                "\n- Use 'index.html' for the homepage (accessible at '/')."
                "\n- Name other templates logically (e.g., 'about.html' for '/about/')."
                "\n- Views and URL patterns are auto-generated based on template names."

                "\n\nExample template:"
                "\n{% extends 'base.html' %}"
                "\n{% load static %}"
                "\n\n{% block title %}Home{% endblock %}"
                "\n\n{% block content %}"
                "\n  <div class=\"hero\">"
                "\n    <h1>Welcome to Imagi Oasis</h1>"
                "\n    <p>Transform your ideas into reality.</p>"
                "\n  </div>"
                "\n{% endblock %}"
                "\n\n{% block extra_css %}"
                "\n  <link rel=\"stylesheet\" href=\"{% static 'css/styles.css' %}\">"
                "\n{% endblock %}"
                "\n\n{% block extra_js %}"
                "\n  <script>"
                "\n    console.log('Imagi Oasis Loaded');"
                "\n  </script>"
                "\n{% endblock %}"
            )
        }

    def get_additional_context(self, **kwargs):
        """
        Get template-specific context.
        
        Args:
            **kwargs: Additional arguments, including template_name
            
        Returns:
            str: Additional context for the system prompt
        """
        context_parts = []
        
        # Get file/template information
        template_name = kwargs.get('template_name')
        file_path = kwargs.get('file_path')
        
        if template_name:
            context_parts.append(f"You are creating/editing the template: {template_name}")
        elif file_path:
            context_parts.append(f"You are creating/editing the file: {file_path}")
        
        # Add project information if available
        project_id = kwargs.get('project_id')
        if project_id:
            try:
                from apps.Products.Oasis.ProjectManager.models import Project
                project = Project.objects.get(id=project_id)
                context_parts.append(f"Project name: {project.name}")
                
                if hasattr(project, 'description') and project.description:
                    context_parts.append(f"Project description: {project.description}")
            except Exception as e:
                logger.warning(f"Could not get project details for context: {str(e)}")
        
        # Add information about other templates in the project
        if hasattr(self, 'project_files') and self.project_files:
            template_files = [f["path"] for f in self.project_files if f["path"].endswith('.html')]
            if template_files:
                context_parts.append(f"Project contains the following templates: {', '.join(template_files)}")
        
        if not context_parts:
            return None
        
        return "\n".join(context_parts)
    
    def _generate_cache_key(self, user_input, template_name):
        """Generate a cache key for template responses."""
        key_str = f"{user_input.lower().strip()}:{template_name}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def handle_template_request(self, user_input, model, user, file_path, conversation_id=None, project_id=None):
        """
        Handle a complete template generation request, including conversation management.
        
        Args:
            user_input (str): The user's message
            model (str): The AI model to use
            user: The Django user object
            file_path (str): The path to the template file
            conversation_id (int, optional): The ID of an existing conversation
            project_id (str, optional): The ID of the project
            
        Returns:
            dict: The result of the operation, including success status and response
        """
        try:
            # Store the current template name for validation
            self.current_template_name = file_path.split('/')[-1] if file_path else None
            
            # Check if we can provide a fast response
            if self.can_provide_fast_response(user_input, self.current_template_name):
                cache_key = self._generate_cache_key(user_input, self.current_template_name)
                
                # If we have a cached response, use it
                if cache_key in self._template_cache:
                    logger.info(f"Using cached template for {self.current_template_name}")
                    return self._template_cache[cache_key]
                
                # For base.html, return the base template directly
                if self.current_template_name == 'base.html':
                    base_template = self.get_base_template()
                    result = {
                        'success': True,
                        'response': base_template,
                        'code': base_template,
                        'is_build_mode': True,
                        'single_message': True
                    }
                    # Cache this result
                    self._template_cache[cache_key] = result
                    return result
                
                # For simple templates, generate standard content
                if self.current_template_name:
                    title = self.current_template_name.replace('.html', '').title()
                    template_content = f"{{% extends 'base.html' %}}\n{{% load static %}}\n\n{{% block title %}}{title}{{% endblock %}}\n\n{{% block content %}}\n  <div class=\"container mx-auto my-8 px-4\">\n    <h1 class=\"text-3xl font-bold mb-6\">{title}</h1>\n    <p>This is the {title} page content.</p>\n  </div>\n{{% endblock %}}"
                    
                    result = {
                        'success': True,
                        'response': template_content,
                        'code': template_content,
                        'is_build_mode': True,
                        'single_message': True
                    }
                    # Cache this result
                    self._template_cache[cache_key] = result
                    return result
            
            # For more complex requests, use the regular flow
            # Get project path and load project files for context
            project_path = None
            project_files = []
            project = None
            
            if project_id:
                try:
                    from apps.Products.Oasis.ProjectManager.models import Project
                    project = Project.objects.get(id=project_id, user=user)
                    project_path = project.project_path
                    
                    # Load all project files for context
                    project_files = self.load_project_files(project_path)
                    logger.info(f"Loaded {len(project_files)} project files for context")
                except Exception as e:
                    logger.warning(f"Could not load project files: {str(e)}")
            
            # Prepare current file data
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
                                'type': 'html'
                            }
                    else:
                        # If file doesn't exist yet, make an empty template to include in context
                        current_file = {
                            'path': file_path,
                            'content': f"# New file: {file_path}",
                            'type': 'html'
                        }
                except Exception as e:
                    logger.warning(f"Could not read file {file_path}: {str(e)}")
            
            # Process the conversation with a shorter timeout
            result = self.process_conversation(
                user_input=user_input,
                model=model,
                user=user,
                conversation_id=conversation_id,
                project_id=project_id,
                template_name=self.current_template_name,
                file_path=file_path,
                project_path=project_path,
                project_files=project_files,
                current_file=current_file,
                is_build_mode=True,  # Flag to indicate this is build mode
                timeout=self.request_timeout  # Use shorter timeout
            )
            
            # Ensure the result is not None and has expected structure
            if result is None:
                logger.error("Received None result from process_conversation in handle_template_request")
                return {
                    'success': False,
                    'error': 'Internal server error: No response from AI model',
                    'single_message': True
                }
            
            # Make sure it has success key
            if 'success' not in result:
                logger.error("Result from process_conversation missing 'success' key")
                result['success'] = False
                
            # Make sure it has error key if not successful
            if not result.get('success') and 'error' not in result:
                logger.error("Unsuccessful result missing 'error' key")
                result['error'] = 'Unknown error occurred during template generation'
            
            # If the operation was successful, try to create view and url
            if result.get('success') and project_id and self.current_template_name:
                try:
                    # Run this in a background thread to avoid blocking
                    threading.Thread(
                        target=self.create_view_and_url,
                        args=(project_id, self.current_template_name, user)
                    ).start()
                    result['view_url_created'] = True
                except Exception as e:
                    logger.error(f"Error creating view and URL: {str(e)}")
                    result['view_url_created'] = False
                    result['view_url_error'] = str(e)
            
            # Add flag to ensure messages appear only once in chat feed
            result['single_message'] = True
            
            # Cache successful results for future use
            if result.get('success') and self.current_template_name:
                cache_key = self._generate_cache_key(user_input, self.current_template_name)
                self._template_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Error in handle_template_request: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': str(e)
            }

    def process_conversation(self, user_input, model, user, **kwargs):
        """
        Process conversation with logging of the complete conversation history.
        """
        # Detect build mode
        is_build_mode = kwargs.get('is_build_mode', False)
        
        # Extract timeout from kwargs if provided
        kwargs.pop('timeout', None) or self.request_timeout
        
        # Get conversation_id if available
        conversation_id = kwargs.get('conversation_id')
        if conversation_id:
            logger.info(f"Processing conversation with ID: {conversation_id}")
        else:
            logger.info("Starting new conversation")
        
        # Print current file path if available
        file_path = kwargs.get('file_path') or self.current_template_name
        if file_path:
            logger.info(f"Working with template file: {file_path}")
        
        # Check if this is a build mode request
        if is_build_mode:
            logger.info(f"Processing in BUILD MODE for file: {file_path}")
            
            # Make sure we have project information
            project_id = kwargs.get('project_id')
            project_path = kwargs.get('project_path')
            if project_id and not project_path:
                # Try to get project path
                try:
                    from apps.Products.Oasis.ProjectManager.models import Project
                    project = Project.objects.get(id=project_id, user=user)
                    kwargs['project_path'] = project.project_path
                    logger.info(f"Added project path: {project.project_path}")
                except Exception as e:
                    logger.warning(f"Could not get project path: {str(e)}")
            
            # Ensure we have all project files loaded
            if not kwargs.get('project_files') and kwargs.get('project_path'):
                kwargs['project_files'] = self.load_project_files(kwargs['project_path'])
                logger.info(f"Loaded {len(kwargs['project_files'])} project files for context")
        
        try:
            # Get or create conversation
            system_prompt_content = kwargs.get('system_prompt')
            project_id = kwargs.get('project_id')
            
            # Get conversation_id if available
            if conversation_id:
                conversation = self.get_conversation(conversation_id, user)
                if not conversation:
                    # Create a new conversation if the requested one doesn't exist
                    conversation = self.create_conversation(user, model, system_prompt_content, project_id)
            else:
                # Create a new conversation if no conversation_id provided
                conversation = self.create_conversation(user, model, system_prompt_content, project_id)
            
            # Determine which AI provider to use based on model ID
            from apps.Products.Oasis.Builder.services.models_service import get_provider_from_model_id
            provider = get_provider_from_model_id(model)

            # Always build conversation history before provider-specific logic
            messages = self.build_conversation_history(
                conversation,
                kwargs.get('project_path'),
                kwargs.get('current_file'),
                is_build_mode=is_build_mode,
                current_user_prompt=user_input
            )

            # Prepare response
            response_content = ""
            completion_tokens = None
            
            # Set up request parameters
            temperature = kwargs.get('temperature', 0.5)  # Lower temperature for templates
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
                    
                    # Make API call to Anthropic
                    completion = self.anthropic_client.messages.create(**anthropic_payload)
                    
                    # Extract response content
                    response_content = completion.content[0].text
                    completion_tokens = completion.usage.output_tokens
                    
                elif provider == 'openai':
                    # Prepare OpenAI API payload
                    openai_payload = {
                        'model': model,
                        'messages': messages,
                        'temperature': temperature,
                        'max_tokens': max_tokens
                    }
                    
                    # Make API call to OpenAI
                    completion = self.openai_client.chat.completions.create(**openai_payload)
                    
                    # Extract response content
                    response_content = completion.choices[0].message.content
                    completion_tokens = completion.usage.completion_tokens
                    
                else:
                    raise ValueError(f"Unsupported AI model provider: {provider}")
                
                # Fix template issues before validation if this is a template
                if self.current_template_name and self.current_template_name.endswith('.html'):
                    response_content = self.fix_template_issues(response_content, self.current_template_name)
                    logger.info("Fixed template issues automatically")
                
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
                'error': f"Error processing template: {str(e)}"
            }

    def process_template(self, prompt, model, user, project_id=None, file_name=None, conversation_id=None):
        """
        Process a template generation request and return the generated code.
        
        Args:
            prompt (str): The user's prompt describing the template
            model (str): The AI model to use
            user (User): The Django user object
            project_id (str, optional): The project ID
            file_name (str, optional): The file name to create/update
            conversation_id (int, optional): ID of existing conversation
            
        Returns:
            dict: The result of the operation
        """
        try:
            # Validate required parameters
            if not prompt:
                return self.error_response("Prompt is required")
            
            if not model:
                return self.error_response("Model is required")
            
            # Store file name if provided and ensure it has .html extension if missing
            if file_name:
                if not file_name.endswith('.html'):
                    file_name = file_name + '.html'
                    logger.info(f"Added .html extension to file name: {file_name}")
                
                self.current_template_name = file_name
                logger.info(f"Set current_template_name to: {self.current_template_name}")
            
            # Get additional system context for this request
            template_context = self.get_additional_context(
                template_name=file_name,
                project_id=project_id,
                file_path=file_name
            )
            
            # Create a custom system prompt
            system_prompt = f"{self.BASE_SYSTEM_PROMPT}\n\n{template_context}".strip()
            
            # Log the complete system prompt for debugging
            logger.info("==================================================================")
            logger.info("============ TEMPLATE AGENT SYSTEM PROMPT (BUILD MODE) ===========")
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
                is_build_mode=True,
                current_template_name=self.current_template_name  # Pass the template name explicitly
            )
            
            # Ensure the result is not None and has expected structure
            if result is None:
                logger.error("Received None result from process_conversation in process_template")
                return {
                    'success': False,
                    'error': 'Internal server error: No response from AI model'
                }
            
            # Make sure it has success key
            if 'success' not in result:
                logger.error("Result from process_conversation missing 'success' key")
                result['success'] = False
                
            # Make sure it has error key if not successful
            if not result.get('success') and 'error' not in result:
                logger.error("Unsuccessful result missing 'error' key")
                result['error'] = 'Unknown error occurred during template generation'
            
            # Make sure successful result has a response
            if result.get('success') and 'response' not in result:
                logger.error("Successful result missing 'response' key")
                result['response'] = 'Template generation completed but no content was returned'
            
            # For successful results, try to fix any remaining template issues
            if result.get('success') and 'response' in result:
                # Apply fix_template_issues one more time to ensure all template issues are fixed
                fixed_content = self.fix_template_issues(result['response'], self.current_template_name)
                result['response'] = fixed_content
                result['code'] = fixed_content  # Make sure code field matches the response
                logger.info("Applied final template fixes to ensure proper structure")
            
            # Enhance response with file info
            if result.get('success') and file_name:
                result['file_name'] = file_name
                result['file_path'] = file_name
                # Set build mode flag to ensure proper UI display
                result['is_build_mode'] = True
            
            return result
            
        except Exception as e:
            logger.error(f"Error in process_template: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': str(e)
            }

    def create_view_and_url(self, project_id, template_name, user):
        """
        Create corresponding Django view and URL pattern for a template.
        
        Args:
            project_id (str): The project ID
            template_name (str): The name of the template file (e.g., 'about.html')
            user: The Django user object
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Import necessary services
            from apps.Products.Oasis.ProjectManager.models import Project
            
            logger.info(f"Creating view and URL for template: {template_name} in project {project_id}")
            
            # Get the project
            try:
                project = Project.objects.get(id=project_id, user=user)
            except Project.DoesNotExist:
                logger.error(f"Project {project_id} not found for user {user.username}")
                return False
                
            # Determine project package directory
            project_dir = project.project_path
            project_name = os.path.basename(project_dir)
            project_package_dir = os.path.join(project_dir, project_name)
            
            # Verify the project package directory exists
            if not os.path.exists(project_package_dir):
                logger.error(f"Project package directory not found: {project_package_dir}")
                # Try to find it by scanning for settings.py
                for root, dirs, files in os.walk(project_dir):
                    if 'settings.py' in files:
                        project_package_dir = root
                        logger.info(f"Found settings.py in {project_package_dir}")
                        break
                else:
                    logger.error("Could not find project package directory containing settings.py")
                    return False
            
            # Extract view name from template name (remove .html extension)
            template_base_name = template_name.replace('.html', '')
            
            # Handle the root/index template differently
            view_name = 'index' if template_base_name == 'index' else template_base_name
            
            # Generate view function code
            view_code = f"""def {view_name}(request):
    \"\"\"
    Render the {template_base_name} page.
    \"\"\"
    return render(request, '{template_base_name}.html')"""
            
            # Update or create views.py
            views_path = os.path.join(project_package_dir, 'views.py')
            
            try:
                # Check if file exists
                with open(views_path, 'r') as f:
                    existing_views = f.read()
                
                # Check if view already exists
                if f"def {view_name}(request)" in existing_views:
                    logger.info(f"View {view_name} already exists, skipping")
                else:
                    # Append the new view
                    updated_views = existing_views + "\n\n" + view_code
                    with open(views_path, 'w') as f:
                        f.write(updated_views)
                    logger.info(f"Added {view_name} view to existing views.py")
            except FileNotFoundError:
                # Create new views.py
                views_initial = f"""from django.shortcuts import render

{view_code}
"""
                with open(views_path, 'w') as f:
                    f.write(views_initial)
                logger.info(f"Created new views.py at {views_path}")
            
            # Generate URL pattern
            url_pattern = (
                f"path('', views.{view_name}, name='{view_name}')," 
                if view_name == 'index' else 
                f"path('{view_name}/', views.{view_name}, name='{view_name}'),"
            )
            
            # Update or create urls.py
            urls_path = os.path.join(project_package_dir, 'urls.py')
            
            try:
                # Check if file exists
                with open(urls_path, 'r') as f:
                    existing_urls = f.read()
                
                # Ensure views is properly imported
                if "from . import views" not in existing_urls and "from .views import" not in existing_urls:
                    # Add import after other imports
                    if "import" in existing_urls:
                        lines = existing_urls.split('\n')
                        import_lines = [i for i, line in enumerate(lines) if 'import' in line]
                        last_import_line = max(import_lines)
                        lines.insert(last_import_line + 1, "from . import views")
                        existing_urls = '\n'.join(lines)
                    else:
                        # Add at the top if no other imports
                        existing_urls = "from . import views\n\n" + existing_urls
                
                # Check if URL pattern already exists
                if f"path('{'' if view_name == 'index' else view_name + '/'}" in existing_urls:
                    logger.info(f"URL pattern for {view_name} already exists, skipping")
                else:
                    # Add URL pattern to urlpatterns
                    if 'urlpatterns = [' in existing_urls:
                        start_index = existing_urls.find('urlpatterns = [') + len('urlpatterns = [')
                        updated_urls = (
                            existing_urls[:start_index] + 
                            "\n    " + url_pattern + 
                            existing_urls[start_index:]
                        )
                        with open(urls_path, 'w') as f:
                            f.write(updated_urls)
                    else:
                        # Create new urlpatterns
                        updated_urls = existing_urls + "\n\n" + f"urlpatterns = [\n    {url_pattern}\n]"
                        with open(urls_path, 'w') as f:
                            f.write(updated_urls)
            except FileNotFoundError:
                # Create new urls.py
                urls_initial = f"""from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    {url_pattern}
]

# Add static/media handling in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    if hasattr(settings, 'MEDIA_URL'):
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
"""
                with open(urls_path, 'w') as f:
                    f.write(urls_initial)
            
            return True
                
        except Exception as e:
            logger.error(f"Error creating view and URL for {template_name}: {str(e)}")
            return False