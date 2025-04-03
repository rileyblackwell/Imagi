"""
Template agent service for Imagi Oasis.

This module provides a specialized agent service for Django HTML template generation,
allowing users to create and modify templates through natural language instructions.
"""

from dotenv import load_dotenv
import re
import logging
from .agent_service import BaseAgentService
from django.shortcuts import get_object_or_404
import os
from django.utils import timezone

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

    def get_system_prompt(self):
        """
        Get the optimized system prompt for Django template generation.
        
        Returns:
            dict: A message dictionary with 'role' and 'content' keys
        """
        return {
            "role": "system",
            "content": (
                "You are an expert web designer specializing in creating professional, sleek, and visually stunning Django HTML templates. "
                "You work iteratively with users to create templates that meet their specific requirements. "
                "The tool you are supporting is called Imagi Oasis, a cutting-edge platform that translates user input into Django HTML template code.\n\n"
                
                "Your responsibilities:\n"
                "1. Generate **only complete Django HTML templates** in response to user messages.\n"
                "2. Never include plain text, explanations, non-Django HTML comments, links (e.g., <a> tags), or images (e.g., <img> tags) in your responses.\n"
                "3. Work interactively with the user by interpreting their natural language messages to refine templates and meet their needs.\n\n"
                
                "Template naming conventions:\n"
                "- For a home/landing page, use 'index.html' which will be accessible at the root URL ('/').\n"
                "- For other pages, name them accordingly (e.g., 'about.html' for an about page, accessible at '/about/').\n"
                "- When you create a template, the system will AUTOMATICALLY generate the corresponding Django view function and URL pattern.\n\n"
                
                "Key requirements for template generation:\n"
                "1. **TEMPLATE STRUCTURE**:\n"
                "   - For non-base templates, ALWAYS start with {% extends 'base.html' %} as the FIRST line.\n"
                "   - Then include {% load static %} as the SECOND line (never before extends).\n"
                "   - Use the stylesheet located at `static/css/styles.css` by linking it within {% block extra_css %}.\n"
                "   - Define content within Django blocks: 'title', 'content', 'extra_css', and 'extra_js'.\n\n"
                
                "2. **CONTENT RULES**:\n"
                "   - Provide only valid, renderable Django HTML templates.\n"
                "   - Use {% static %} for referencing static assets (e.g., {% static 'css/styles.css' %}).\n"
                "   - Dynamically include content using Django template tags (e.g., {{ variable }}).\n"
                "   - Do not include any links (<a> tags) or images (<img> tags) in the templates, as they are not currently supported.\n\n"
                
                "3. **DESIGN PRINCIPLES**:\n"
                "   - Follow modern design trends inspired by companies like Stripe, AirBnB, Apple, and Google.\n"
                "   - Use minimalist, accessible, and semantic HTML5 structures.\n"
                "   - Ensure all class names are consistent and intuitive for CSS styling.\n\n"
                
                "4. **RESPONSIVE DESIGN**:\n"
                "   - Use a mobile-first approach with responsive layouts (e.g., flexbox, grid).\n"
                "   - Include <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"> for responsive scaling.\n"
                "   - Ensure all elements adapt elegantly to various screen sizes.\n\n"
                
                "5. **OUTPUT REQUIREMENTS**:\n"
                "   - Maintain consistent 2-space indentation for readability.\n"
                "   - Provide only the complete HTML template without additional comments or explanations.\n\n"
                
                "6. **DYNAMIC CONTENT & JAVASCRIPT**:\n"
                "   - Use Django template tags within JavaScript blocks when applicable, wrapped inside {% block extra_js %}.\n"
                "   - Example:\n"
                "     <script>\n"
                "       {% for item in items %}\n"
                "         console.log('{{ item }}');\n"
                "       {% endfor %}\n"
                "     </script>\n\n"
                
                "7. **AUTO-GENERATED VIEWS AND URLS**:\n"
                "   - When you create a template named 'index.html', a view function named 'index' will be created automatically.\n"
                "   - For templates like 'about.html', a view function named 'about' will be created automatically.\n"
                "   - URL patterns will be automatically created to match template names (e.g., '/about/' for 'about.html').\n\n"
                
                "EXAMPLE TEMPLATE:\n"
                "{% extends 'base.html' %}\n"
                "{% load static %}\n\n"
                "{% block title %}Welcome to Imagi Oasis{% endblock %}\n\n"
                "{% block content %}\n"
                "  <div class=\"hero-section\">\n"
                "    <h1>Transform Your Ideas Into Reality</h1>\n"
                "    <p>Build world-class web apps effortlessly with Imagi Oasis.</p>\n"
                "    <button class=\"cta-button\">Start Now</button>\n"
                "  </div>\n"
                "{% endblock %}\n\n"
                "{% block extra_css %}\n"
                "  <link rel=\"stylesheet\" href=\"{% static 'css/styles.css' %}\">\n"
                "{% endblock %}\n\n"
                "{% block extra_js %}\n"
                "  <script>\n"
                "    console.log('Welcome to Imagi Oasis!');\n"
                "  </script>\n"
                "{% endblock %}\n"
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

    def process_conversation(self, user_input, model, user, **kwargs):
        """
        Process a conversation with the template agent.
        
        Args:
            user_input (str): The user's message
            model (str): The AI model to use
            user: The Django user object
            **kwargs: Additional arguments for template generation
            
        Returns:
            dict: The result of the operation, including success status and response
        """
        # Store the current template name
        self.current_template_name = kwargs.get('template_name') or kwargs.get('file_name')
        
        # Get the response from the parent class
        result = super().process_conversation(user_input, model, user, **kwargs)
        
        if result.get('success'):
            # Fix any template issues
            fixed_content = self.fix_template_issues(result['response'], self.current_template_name)
            
            # Validate the fixed content
            is_valid, error_msg = self.validate_response(fixed_content)
            
            if is_valid:
                result['response'] = fixed_content
            else:
                result['success'] = False
                result['error'] = error_msg
                result['original_response'] = result['response']
                result['response'] = fixed_content
        
        return result
        
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
            
            # Process the conversation
            result = self.process_conversation(
                user_input=user_input,
                model=model,
                user=user,
                conversation_id=conversation_id,
                project_id=project_id,
                template_name=self.current_template_name,
                file_path=file_path
            )
            
            # If the operation was successful, try to create view and url
            if result.get('success') and project_id and self.current_template_name:
                try:
                    view_url_result = self.create_view_and_url(project_id, self.current_template_name, user)
                    if view_url_result.get('success'):
                        result['view_url_created'] = True
                except Exception as e:
                    logger.error(f"Error creating view and URL: {str(e)}")
                    result['view_url_created'] = False
                    result['view_url_error'] = str(e)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in handle_template_request: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': str(e)
            }
    
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