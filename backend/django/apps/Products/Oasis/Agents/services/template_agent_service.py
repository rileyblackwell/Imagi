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
        template_name = kwargs.get('template_name')
        if template_name:
            return f"You are creating/editing the template: {template_name}"
        return None
    
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
            # Process the conversation with a shorter timeout
            result = self.process_conversation(
                user_input=user_input,
                model=model,
                user=user,
                conversation_id=conversation_id,
                project_id=project_id,
                template_name=self.current_template_name,
                file_path=file_path,
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

    def process_template(self, prompt, model, user, project_id=None, file_name=None, conversation_id=None):
        """
        Process a template generation request.
        
        Args:
            prompt (str): The user's prompt
            model (str): The AI model to use
            user: The Django user object
            project_id (str, optional): The ID of the project
            file_name (str, optional): The name of the template file
            conversation_id (int, optional): The ID of an existing conversation
            
        Returns:
            dict: The result of the operation, including success status and response
        """
        # Store the current template name for validation
        self.current_template_name = file_name
        
        # Determine file path
        file_path = None
        if project_id and file_name:
            try:
                from apps.Products.Oasis.ProjectManager.models import Project
                project = Project.objects.get(id=project_id, user=user)
                file_path = os.path.join(project.project_path, 'templates', file_name)
            except Exception as e:
                logger.warning(f"Could not determine file path: {str(e)}")
                
        # Get response from conversation
        response = self.handle_template_request(
            user_input=prompt,
            model=model,
            user=user,
            file_path=file_path,
            conversation_id=conversation_id,
            project_id=project_id
        )
        
        # Enhance response with file info
        if response.get('success') and file_name:
            response['file_name'] = file_name
            response['file_path'] = file_path
            # Set build mode flag to ensure proper UI display
            response['is_build_mode'] = True
        
        return response

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