"""
Template agent service for Imagi Oasis.

This module provides a specialized agent service for Django HTML template generation,
allowing users to create and modify templates through natural language instructions.
"""

from dotenv import load_dotenv
import re
import logging
from .agent_service import BaseAgentService
import os
import threading
from functools import lru_cache
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
    
    def __init__(self):
        """Initialize the template agent service."""
        super().__init__()
        self.current_template_name = None
        # Add template cache for improved performance
        self._template_cache = {}
        # Add default timeout override
        self.request_timeout = 30  # Reduced from default 60s
        # Define base system prompt
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

    def get_api_model(self, model_id):
        """
        Get the API model to use for a given model ID.
        
        Args:
            model_id (str): The model ID
            
        Returns:
            str: The API model to use
        """
        # Import model definitions
        from .model_definitions import get_model_by_id
        
        # Try to get the model definition
        model_def = get_model_by_id(model_id)
        
        # Use api_model from definition if available
        if model_def and 'api_model' in model_def:
            logger.info(f"Using API model from definition: {model_def['api_model']} for model ID: {model_id}")
            return model_def['api_model']
        
        # All OpenAI models use API as-is (no mapping needed, using responses API)
        # Return the model ID directly
        return model_id

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
    
    def fix_template_issues(self, content, template_name):
        """
        Fix common template issues and ensure proper tag order.
        
        Args:
            content (str): The template content to fix
            template_name (str): The name of the template file
            
        Returns:
            str: The fixed template content
        """
        # Add missing DOCTYPE and basic HTML structure for base.html
        if template_name == 'base.html' and '<!DOCTYPE html>' not in content:
            return (
                "<!DOCTYPE html>\n"
                '<html lang="en">\n'
                "<head>\n"
                '    <meta charset="UTF-8">\n'
                '    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
                "    <title>{% block title %}{% endblock %}</title>\n"
                "    {% load static %}\n"
                "    {% block extra_css %}{% endblock %}\n"
                "</head>\n"
                "<body>\n"
                "    {% block content %}{% endblock %}\n"
                "    {% block extra_js %}{% endblock %}\n"
                "</body>\n"
                "</html>"
            )
        
        # For non-base templates, ensure proper tag order
        if template_name != 'base.html':
            # Remove existing tags
            content = re.sub(r'{%\s*extends.*?%}', '', content)
            content = re.sub(r'{%\s*load\s+static\s*%}', '', content)
            
            # Add tags in correct order (extends must come first)
            content = (
                "{% extends 'base.html' %}\n"
                "{% load static %}\n\n"
            ) + content.lstrip()
            
            # If somehow load static got added before extends, fix it
            if re.search(r'{%\s*load\s+static\s*%}\s*{%\s*extends', content):
                content = re.sub(
                    r'{%\s*load\s+static\s*%}\s*({%\s*extends.*?%})',
                    r'\1\n{% load static %}',
                    content
                )
        
        return content

    def validate_response(self, content):
        """
        Validate Django template syntax and structure.
        
        Args:
            content (str): The template content to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        # Get the current template name
        template_name = self.current_template_name
        
        # Define checks based on template type
        if template_name == 'base.html':
            checks = [
                (r"{%\s*load\s+static\s*%}", "Missing {% load static %} tag"),
                (r"<!DOCTYPE\s+html>", "Missing DOCTYPE declaration"),
                (r"<html.*?>", "Missing <html> tag"),
                (r"<head>.*?</head>", "Missing <head> section", re.DOTALL),
                (r"<body>.*?</body>", "Missing <body> section", re.DOTALL),
                (r'<meta\s+name="viewport"', "Missing viewport meta tag"),
            ]
        else:
            # For non-base templates, first check if extends comes before load static
            if re.search(r'{%\s*load\s+static\s*%}\s*{%\s*extends', content):
                return False, "{% extends 'base.html' %} must come before {% load static %}"
            
            # Then check for the presence of both tags
            checks = [
                (r"{%\s*extends\s+'base\.html'\s*%}", "Missing {% extends 'base.html' %} tag"),
                (r"{%\s*load\s+static\s*%}", "Missing {% load static %} tag"),
            ]
        
        # Run all checks
        for pattern, error_msg, *flags in checks:
            if not re.search(pattern, content, *flags):
                return False, error_msg
        
        # Check for matching template tags
        block_starts = len(re.findall(r"{%\s*block\s+\w+\s*%}", content))
        block_ends = len(re.findall(r"{%\s*endblock\s*%}", content))
        if block_starts != block_ends:
            return False, "Mismatched block tags"
        
        return True, None

    # Add caching for frequently used templates
    @lru_cache(maxsize=32)
    def get_base_template(self):
        """Get the base template with standard structure."""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}{% endblock %}</title>
    {% load static %}
    <link rel="stylesheet" href="{% static 'css/styles.css' %}">
    {% block extra_css %}{% endblock %}
</head>
<body>
    {% block content %}{% endblock %}
    
    {% block extra_js %}{% endblock %}
</body>
</html>"""

    # Create a method to check if we can provide a fast response
    def can_provide_fast_response(self, user_input, template_name):
        """Check if we can provide a fast cached response based on input and template name."""
        # Simple inputs that can be handled without calling the AI
        simple_inputs = [
            "create basic template", "basic template", "empty template", 
            "starter template", "default template", "template starter",
            "simple template", "blank template", "new template"
        ]
        
        # For simple requests with standard template names, we can respond faster
        if any(phrase in user_input.lower() for phrase in simple_inputs):
            return True
            
        # Check if we have a cached response for this input
        cache_key = self._generate_cache_key(user_input, template_name)
        return cache_key in self._template_cache
    
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

    # Override process_conversation to include detailed conversation logging
    def process_conversation(self, user_input, model, user, **kwargs):
        """Process conversation with logging of the complete conversation history."""
        # Extract timeout from kwargs if provided
        timeout = kwargs.pop('timeout', None)
        
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
        is_build_mode = kwargs.get('is_build_mode', False)
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
        
        # Call original method with potentially modified timeout
        if timeout:
            # Store original timeout
            original_timeout = self.request_timeout
            try:
                # Set new timeout for this request
                self.request_timeout = timeout
                result = super().process_conversation(user_input, model, user, **kwargs)
                
                # Log the response (preview only)
                if result.get('success'):
                    response_preview = result.get('response', '')[:100]
                    logger.info(f"Response preview: {response_preview}...")
                else:
                    logger.error(f"Error in response: {result.get('error')}")
                
                return result
            finally:
                # Restore original timeout
                self.request_timeout = original_timeout
        else:
            result = super().process_conversation(user_input, model, user, **kwargs)
            
            # Log the response (preview only)
            if result.get('success'):
                response_preview = result.get('response', '')[:100]
                logger.info(f"Response preview: {response_preview}...")
            else:
                logger.error(f"Error in response: {result.get('error')}")
            
            return result

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
            
            # Store file name if provided
            if file_name:
                self.current_template_name = file_name
            
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
                is_build_mode=True
            )
            
            # Enhance response with file info
            if result.get('success') and file_name:
                result['file_name'] = file_name
                result['file_path'] = file_name
                # Set build mode flag to ensure proper UI display
                result['is_build_mode'] = True
            
            return result
            
        except Exception as e:
            logger.error(f"Error in process_template: {str(e)}")
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
            from apps.Products.Oasis.Builder.services.file_service import FileService
            
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
        Load all relevant project files to provide context for template generation.
        
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
            
            # Get templates
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
            
            # Get CSS files for styling context
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
            
            # Get URL configuration for additional context
            urls_py_path = None
            for root, dirs, file_list in os.walk(project_path):
                if 'urls.py' in file_list:
                    urls_py_path = os.path.join(root, 'urls.py')
                    break
                    
            if urls_py_path:
                try:
                    with open(urls_py_path, 'r') as f:
                        content = f.read()
                        rel_path = os.path.relpath(urls_py_path, project_path)
                        files.append({
                            'path': rel_path,
                            'content': content,
                            'type': 'python'
                        })
                except Exception as e:
                    logger.warning(f"Error reading urls.py: {str(e)}")
            
            # Get views.py for additional context
            views_py_path = None
            for root, dirs, file_list in os.walk(project_path):
                if 'views.py' in file_list:
                    views_py_path = os.path.join(root, 'views.py')
                    break
                    
            if views_py_path:
                try:
                    with open(views_py_path, 'r') as f:
                        content = f.read()
                        rel_path = os.path.relpath(views_py_path, project_path)
                        files.append({
                            'path': rel_path,
                            'content': content,
                            'type': 'python'
                        })
                except Exception as e:
                    logger.warning(f"Error reading views.py: {str(e)}")
                
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
        logger.error(f"Template agent error: {message}")
        return {
            'success': False,
            'error': message,
            'code': code
        }