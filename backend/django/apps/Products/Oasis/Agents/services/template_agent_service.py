"""
Template agent service for Imagi Oasis.

This module provides a specialized agent service for Django HTML template generation,
allowing users to create and modify templates through natural language instructions.
"""

from dotenv import load_dotenv
import re
import logging
from .agent_service import BaseAgentService
from ..models import AgentConversation, SystemPrompt, AgentMessage
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
        
    def process_message(self, user_input, model, **kwargs):
        """
        Process a message from the API endpoint.
        This method is used by the API endpoint to process messages without creating a conversation.
        
        Args:
            user_input (str): The user's message
            model (str): The AI model to use
            **kwargs: Additional arguments for template generation
            
        Returns:
            str: The generated template content
        """
        conversation_history = kwargs.get('conversation_history', [])
        provider = kwargs.get('provider', 'anthropic')
        file_name = kwargs.get('file_name')
        
        # Store the current template name for validation
        self.current_template_name = file_name
        
        # Prepare messages for the API call
        api_messages = []
        
        # Add system prompt
        system_prompt = self.get_system_prompt()
        api_messages.append(system_prompt)
        
        # Add conversation history
        for msg in conversation_history:
            api_messages.append(msg)
        
        # Add current task context if file_name is provided
        if file_name:
            context_msg = {
                "role": "system",
                "content": f"\n=== CURRENT TASK ===\nYou are working on: {file_name}"
            }
            api_messages.append(context_msg)
        
        # Add user message
        api_messages.append({
            "role": "user",
            "content": user_input
        })
        
        # Make API call based on provider and model
        try:
            if provider == 'anthropic' or model.startswith('claude'):
                # Verify anthropic client is available
                if not hasattr(self, 'anthropic_client') or self.anthropic_client is None:
                    logger.error("Anthropic client not available - check API key configuration")
                    raise ValueError("Anthropic client not initialized - check API key configuration")
                
                # Get the system message content for Claude
                system_content = ""
                for msg in api_messages:
                    if msg['role'] == 'system':
                        system_content += msg['content'] + "\n\n"
                
                # Extract messages for Claude (excluding system messages)
                claude_messages = [
                    msg for msg in api_messages 
                    if msg["role"] != "system"
                ]
                
                # Make the API call
                logger.info(f"Calling Anthropic API with model {model} for template generation")
                completion = self.anthropic_client.messages.create(
                    model=model,
                    max_tokens=2048,
                    system=system_content.strip(),
                    messages=claude_messages
                )
                
                if completion.content:
                    response = completion.content[0].text
                else:
                    raise ValueError("Empty response from Claude API")
            else:
                # Verify OpenAI client is available
                if not hasattr(self, 'openai_client') or self.openai_client is None:
                    logger.error("OpenAI client not available - check API key configuration")
                    raise ValueError("OpenAI client not initialized - check API key configuration")
                
                # Make the API call
                logger.info(f"Calling OpenAI API with model {model} for template generation")
                completion = self.openai_client.chat.completions.create(
                    model=model,
                    messages=api_messages
                )
                response = completion.choices[0].message.content
            
            # Fix any template issues if file_name is provided
            if file_name:
                response = self.fix_template_issues(response, file_name)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in process_message: {str(e)}")
            raise

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
            
            # Get project path if project_id is provided
            project_path = None
            if project_id:
                try:
                    from apps.Products.Oasis.ProjectManager.models import Project
                    project = Project.objects.get(id=project_id, user=user)
                    project_path = project.project_path
                except Exception as e:
                    logger.warning(f"Could not get project path from project_id {project_id}: {str(e)}")
            
            # Process template generation with project context
            result = self.process_conversation(
                user_input=user_input,
                model=model,
                user=user,
                file_name=file_path,
                conversation=conversation,
                project_path=project_path
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
            print(f"Error in handle_template_request: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def process_template(self, prompt, model, user, project_id=None, file_name=None, conversation_id=None):
        """
        Process a template generation request.
        
        Args:
            prompt (str): The user's prompt
            model (str): The model to use
            user (User): The user object
            project_id (str, optional): The project ID
            file_name (str, optional): The file name
            conversation_id (str, optional): The conversation ID
            
        Returns:
            dict: The response data
        """
        try:
            # Get or create conversation
            conversation = None
            if conversation_id:
                conversation = self.get_conversation(conversation_id, user)
            
            if not conversation:
                # Get system prompt
                system_prompt = self.get_system_prompt()
                conversation = self.create_conversation(user, model, system_prompt)
            
            # Log the function call with all parameters for debugging
            logger.info(f"process_template called with: prompt={prompt[:50]}..., model={model}, " 
                       f"user_id={user.id}, project_id={project_id}, file_name={file_name}, " 
                       f"conversation_id={conversation_id}")
            
            # Add user message to conversation
            self.add_user_message(conversation, prompt, user)
            
            # Build conversation history with project context
            api_messages = self.build_conversation_history(conversation)
            
            # Get project path if project_id is provided
            project_path = None
            if project_id:
                try:
                    from apps.Products.Oasis.ProjectManager.models import Project
                    project = Project.objects.get(id=project_id, user=user)
                    project_path = project.project_path
                    logger.info(f"Found project path: {project_path}")
                except Exception as e:
                    logger.warning(f"Could not get project path from project_id {project_id}: {str(e)}")
                    return {
                        'success': False,
                        'error': f"Project not found or inaccessible: {str(e)}",
                    }
            
            # Add project files context if available
            if hasattr(self, 'project_files') and self.project_files:
                logger.info(f"Adding {len(self.project_files)} project files to context")
                project_files_context = "\n\nProject Files:\n"
                for file in self.project_files:
                    file_path = file.get('path', 'unknown')
                    file_type = file.get('type', 'unknown')
                    content = file.get('content', '')
                    if len(content) > 1000:
                        content_preview = content[:1000] + "... (truncated)"
                    else:
                        content_preview = content
                    project_files_context += f"\nFile: {file_path}\nType: {file_type}\nContent:\n{content_preview}\n"
                api_messages.append({
                    'role': 'system',
                    'content': project_files_context
                })
            
            # Add current file context if available
            if file_name:
                current_file_context = f"\n\nCurrent File: {file_name}\n"
                current_file_context += f"You are creating or editing the file: {file_name}\n"
                current_file_context += f"Focus your generation on producing ONLY the content for this file."
                api_messages.append({
                    'role': 'system',
                    'content': current_file_context
                })
            
            # Generate the response using the appropriate model
            try:
                logger.info(f"Generating response with model: {model}")
                if 'claude' in model:
                    # Verify anthropic client is available
                    if not hasattr(self, 'anthropic_client') or self.anthropic_client is None:
                        logger.error("Anthropic client not available - check API key configuration")
                        return {
                            'success': False,
                            'error': "Anthropic client not initialized - check API key configuration",
                        }
                    
                    # Get the system message content for Claude
                    system_content = ""
                    for msg in api_messages:
                        if msg['role'] == 'system':
                            system_content += msg['content'] + "\n\n"
                    
                    # Filter out system messages for Claude API
                    claude_messages = [msg for msg in api_messages if msg['role'] != 'system']
                    
                    # Make the API call
                    completion = self.anthropic_client.messages.create(
                        model=model,
                        max_tokens=4096,
                        temperature=0.7,
                        system=system_content.strip(),
                        messages=claude_messages
                    )
                    response_content = completion.content[0].text
                elif 'gpt' in model:
                    # Verify OpenAI client is available
                    if not hasattr(self, 'openai_client') or self.openai_client is None:
                        logger.error("OpenAI client not available - check API key configuration")
                        return {
                            'success': False,
                            'error': "OpenAI client not initialized - check API key configuration",
                        }
                    
                    # Make the API call
                    completion = self.openai_client.chat.completions.create(
                        model=model,
                        messages=api_messages,
                        temperature=0.7,
                        max_tokens=4096
                    )
                    response_content = completion.choices[0].message.content
                else:
                    raise ValueError(f"Unsupported model: {model}")
                
                logger.info(f"Generated response length: {len(response_content)}")
            except Exception as model_error:
                logger.error(f"Error generating response: {str(model_error)}")
                return {
                    'success': False,
                    'error': f"Error generating template: {str(model_error)}",
                    'response': None
                }
            
            # Validate the response
            is_valid, error = self.validate_response(response_content)
            if not is_valid:
                logger.warning(f"Response validation failed: {error}")
                return {
                    'success': False,
                    'error': error,
                    'response': response_content
                }
            
            # Store the assistant response
            self.add_assistant_message(conversation, response_content, user)
            
            # Try to save the file if project_id and file_name are provided
            if project_id and file_name and project_path:
                try:
                    logger.info(f"Attempting to save file {file_name} to project {project_id}")
                    from apps.Products.Oasis.Builder.services.file_service import FileService
                    file_service = FileService(user=user)
                    
                    # Determine file type based on extension
                    if file_name.endswith('.html'):
                        file_type = 'html'
                    elif file_name.endswith('.css'):
                        file_type = 'css'
                    elif file_name.endswith('.js'):
                        file_type = 'javascript'
                    else:
                        file_type = 'text'
                    
                    # Prepare file data
                    file_data = {
                        'name': file_name,
                        'content': response_content,
                        'type': file_type
                    }
                    
                    # Create or update the file
                    file_result = file_service.create_file(file_data, project_id)
                    logger.info(f"File saved successfully: {file_result['path']}")
                    
                    # Include file information in the response
                    return {
                        'success': True,
                        'conversation_id': str(conversation.id),
                        'response': response_content,
                        'timestamp': timezone.now().isoformat(),
                        'file': {
                            'path': file_result['path'],
                            'type': file_result['type']
                        }
                    }
                except Exception as file_error:
                    logger.error(f"Error saving file: {str(file_error)}")
                    # Return success for the AI generation but include warning about file saving
                    return {
                        'success': True,
                        'conversation_id': str(conversation.id),
                        'response': response_content,
                        'timestamp': timezone.now().isoformat(),
                        'warning': f"File generated but could not be saved: {str(file_error)}"
                    }
            
            # Return the successful response
            return {
                'success': True,
                'conversation_id': str(conversation.id),
                'response': response_content,
                'timestamp': timezone.now().isoformat()
            }
            
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
            from apps.Products.Oasis.Builder.services.file_service import FileService
            import logging
            
            logger = logging.getLogger(__name__)
            logger.info(f"Creating view and URL for template: {template_name} in project {project_id}")
            
            # Get the project
            try:
                project = Project.objects.get(id=project_id, user=user)
            except Project.DoesNotExist:
                logger.error(f"Project {project_id} not found for user {user.username}")
                return False
                
            file_service = FileService(project=project)
            
            # Determine project package directory - same location as settings.py
            # First get the project folder name from path
            project_dir = project.project_path
            
            # Get the project name from directory structure - last part of the path
            project_name = os.path.basename(project_dir)
            
            # For Django projects, there will be a nested directory with the same name
            # This directory contains settings.py, urls.py, etc.
            project_package_dir = os.path.join(project_dir, project_name)
            logger.info(f"Project package directory: {project_package_dir}")
            
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
            
            # First clean up any duplicate views and URL patterns
            self.cleanup_duplicate_views_and_urls(project_id, user)
            
            # Extract view name from template name (remove .html extension)
            template_base_name = template_name.replace('.html', '')
            
            # Handle the root/index template differently
            view_name = 'index' if template_base_name == 'index' else template_base_name
            
            # Generate view function
            view_code = self._generate_view_code(template_base_name)
            
            # Update or create views.py in the project package directory
            views_path = os.path.join(project_package_dir, 'views.py')
            views_rel_path = os.path.relpath(views_path, project_dir)
            
            try:
                # Try to read existing views.py
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
                # File doesn't exist, create it
                logger.info(f"Creating new views.py file with {view_name} view")
                views_initial = f"""from django.shortcuts import render

{view_code}
"""
                with open(views_path, 'w') as f:
                    f.write(views_initial)
                logger.info(f"Created new views.py at {views_path}")
            except Exception as e:
                logger.error(f"Error updating views.py: {str(e)}")
                return False
                
            # Update or create urls.py in the project package directory
            urls_path = os.path.join(project_package_dir, 'urls.py')
            urls_rel_path = os.path.relpath(urls_path, project_dir)
            url_pattern = self._generate_url_pattern(view_name, template_base_name)
            
            try:
                # Try to read existing urls.py
                with open(urls_path, 'r') as f:
                    existing_urls = f.read()
                
                # Ensure views is properly imported
                existing_urls = self._ensure_views_import_in_urls(existing_urls)
                
                # Check if URL pattern already exists
                if f"path('{'' if view_name == 'index' else view_name + '/'}" in existing_urls:
                    logger.info(f"URL pattern for {view_name} already exists, skipping")
                else:
                    # Add the new URL pattern before the closing bracket
                    if 'urlpatterns = [' in existing_urls:
                        # Find the position after the opening bracket of urlpatterns
                        start_index = existing_urls.find('urlpatterns = [') + len('urlpatterns = [')
                        
                        # Insert the new URL pattern
                        updated_urls = (
                            existing_urls[:start_index] + 
                            "\n    " + url_pattern + 
                            existing_urls[start_index:]
                        )
                        
                        with open(urls_path, 'w') as f:
                            f.write(updated_urls)
                        logger.info(f"Added URL pattern for {view_name} to existing urls.py")
                    else:
                        # If urlpatterns isn't found in the expected format, append the whole pattern
                        updated_urls = existing_urls + "\n\n" + f"urlpatterns = [\n    {url_pattern}\n]"
                        with open(urls_path, 'w') as f:
                            f.write(updated_urls)
                        logger.info(f"Added URL pattern for {view_name} to existing urls.py with new urlpatterns")
            except FileNotFoundError:
                # File doesn't exist, create it
                logger.info(f"Creating new urls.py file with {view_name} URL pattern")
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
                logger.info(f"Created new urls.py at {urls_path}")
            except Exception as e:
                logger.error(f"Error updating urls.py: {str(e)}")
                return False
                
            logger.info(f"Successfully created view and URL for {template_name}")
            return True
                
        except Exception as e:
            logger.error(f"Error creating view and URL for {template_name}: {str(e)}")
            import traceback
            logger.error(f"Stack trace: {traceback.format_exc()}")
            return False
            
    def _generate_view_code(self, template_base_name):
        """
        Generate code for a Django view function.
        
        Args:
            template_base_name (str): The base name of the template (without .html)
            
        Returns:
            str: Python code for the view function
        """
        # Clean the template_base_name to remove any 'templates/' prefix
        if template_base_name.startswith('templates/'):
            template_base_name = template_base_name.replace('templates/', '')
            
        view_name = 'index' if template_base_name == 'index' else template_base_name
        return f"""def {view_name}(request):
    \"\"\"
    Render the {template_base_name} page.
    \"\"\"
    return render(request, '{template_base_name}.html')"""
    
    def _generate_url_pattern(self, view_name, template_base_name):
        """
        Generate a URL pattern for a view.
        
        Args:
            view_name (str): The name of the view function
            template_base_name (str): The base name of the template
            
        Returns:
            str: URL pattern code
        """
        # Clean template_base_name to remove any 'templates/' prefix
        if template_base_name.startswith('templates/'):
            template_base_name = template_base_name.replace('templates/', '')
            
        # Clean view_name as well to remove any 'templates/' prefix
        if view_name.startswith('templates/'):
            view_name = view_name.replace('templates/', '')
        
        # For index, use the root URL; for others, use the template name as the URL
        if view_name == 'index':
            return f"path('', views.{view_name}, name='{view_name}'),"
        else:
            return f"path('{view_name}/', views.{view_name}, name='{view_name}'),"

    def _ensure_views_import_in_urls(self, urls_content):
        """
        Ensure that the views module is properly imported in the urls.py file.
        
        Args:
            urls_content (str): The current content of the urls.py file
            
        Returns:
            str: Updated urls.py content with proper views import
        """
        # Check if views is imported
        if "from . import views" not in urls_content and "from .views import" not in urls_content:
            # Add the import statement after other imports
            if "import" in urls_content:
                lines = urls_content.split('\n')
                import_lines = [i for i, line in enumerate(lines) if 'import' in line]
                last_import_line = max(import_lines)
                lines.insert(last_import_line + 1, "from . import views")
                return '\n'.join(lines)
            else:
                # If there are no import statements, add it at the top
                return "from . import views\n\n" + urls_content
                
        return urls_content
        
    def cleanup_duplicate_views_and_urls(self, project_id, user):
        """
        Clean up duplicate views and URL patterns that contain 'templates/' prefix.
        
        Args:
            project_id (str): The project ID
            user: The Django user object
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            from apps.Products.Oasis.ProjectManager.models import Project
            import logging
            import os
            import re
            
            logger = logging.getLogger(__name__)
            logger.info(f"Cleaning up duplicate views and URL patterns in project {project_id}")
            
            # Get the project
            try:
                project = Project.objects.get(id=project_id, user=user)
            except Project.DoesNotExist:
                logger.error(f"Project {project_id} not found for user {user.username}")
                return False
                
            # Determine project package directory - same location as settings.py
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
            
            # Check views.py
            views_path = os.path.join(project_package_dir, 'views.py')
            if os.path.exists(views_path):
                try:
                    with open(views_path, 'r') as f:
                        views_content = f.read()
                    
                    # Find duplicate views with 'templates/' prefix
                    # Look for patterns like: def templates/about(request): or def templates_about(request):
                    duplicate_view_pattern = r'def\s+(templates[/_]([a-zA-Z0-9_]+))\s*\(request\):'
                    matches = re.finditer(duplicate_view_pattern, views_content)
                    
                    for match in matches:
                        full_match = match.group(0)  # The entire match
                        duplicate_view_name = match.group(1)  # The view name with templates/ prefix
                        clean_view_name = match.group(2)  # The clean view name without templates/ prefix
                        
                        # Check if the clean version of the view already exists
                        clean_view_pattern = rf'def\s+{clean_view_name}\s*\(request\):'
                        if re.search(clean_view_pattern, views_content):
                            # Remove the duplicate view function entirely
                            # Find the start and end of the function
                            function_start = views_content.find(full_match)
                            if function_start >= 0:
                                # Look for the next function definition or end of file
                                next_function = re.search(r'def\s+[a-zA-Z0-9_]+\s*\(request\):', views_content[function_start + len(full_match):])
                                if next_function:
                                    function_end = function_start + len(full_match) + next_function.start()
                                else:
                                    function_end = len(views_content)
                                
                                # Remove the entire function
                                views_content = views_content[:function_start] + views_content[function_end:]
                                logger.info(f"Removed duplicate view function: {duplicate_view_name}")
                    
                    # Write the updated content back to the file
                    with open(views_path, 'w') as f:
                        f.write(views_content)
                    
                except Exception as e:
                    logger.error(f"Error cleaning up views.py: {str(e)}")
                    
            # Check urls.py
            urls_path = os.path.join(project_package_dir, 'urls.py')
            if os.path.exists(urls_path):
                try:
                    with open(urls_path, 'r') as f:
                        urls_content = f.read()
                    
                    # Find duplicate URL patterns with 'templates/' prefix
                    # Look for patterns like: path('templates/about/', views.templates_about, name='templates_about'),
                    duplicate_url_pattern = r"path\(['\"]templates/([a-zA-Z0-9_]+)/['\"]\s*,\s*views\.templates[/_]\1\s*,\s*name=['\"]templates[/_]\1['\"]\s*\),?"
                    
                    # Also look for patterns without the 'templates/' prefix in the URL but with it in the view name
                    alternate_url_pattern = r"path\(['\"]([a-zA-Z0-9_]+)/['\"]\s*,\s*views\.templates[/_]\1\s*,\s*name=['\"]templates[/_]\1['\"]\s*\),?"
                    
                    # Combine the patterns
                    patterns = [duplicate_url_pattern, alternate_url_pattern]
                    
                    for pattern in patterns:
                        matches = re.finditer(pattern, urls_content)
                        for match in matches:
                            full_match = match.group(0)  # The entire URL pattern
                            clean_name = match.group(1)  # The clean name without templates/ prefix
                            
                            # Check if the clean version of the URL pattern already exists
                            clean_url_pattern = rf"path\(['\"]({clean_name}/)?['\"]\s*,\s*views\.{clean_name}\s*,"
                            if re.search(clean_url_pattern, urls_content):
                                # Remove the duplicate URL pattern
                                urls_content = urls_content.replace(full_match, "")
                                logger.info(f"Removed duplicate URL pattern for: {clean_name}")
                    
                    # Clean up any double commas or other syntax issues
                    urls_content = re.sub(r',\s*,', ',', urls_content)
                    
                    # Write the updated content back to the file
                    with open(urls_path, 'w') as f:
                        f.write(urls_content)
                    
                except Exception as e:
                    logger.error(f"Error cleaning up urls.py: {str(e)}")
            
            logger.info(f"Successfully cleaned up duplicate views and URL patterns in project {project_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error cleaning up duplicate views and URL patterns: {str(e)}")
            import traceback
            logger.error(f"Stack trace: {traceback.format_exc()}")
            return False

    def build_template_response(self, result, message, file_path):
        """
        Format template generation result into a standardized response object.
        
        Args:
            result (dict): The template generation result
            message (str): The original user message
            file_path (str): The file path for the template
            
        Returns:
            dict: A formatted response object for the API
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            if result.get('success'):
                # Format the response to match the frontend's expected format
                template_content = result.get('template', '')
                current_time = result.get('timestamp', '')
                
                # Extract template name for the success message
                template_name = file_path.split('/')[-1] if '/' in file_path else file_path
                base_name = template_name.replace('.html', '')
                
                # Create a success message that includes info about the view and URL
                success_message = f"I've generated the {base_name} template based on your requirements."
                
                # Add info about auto-generated view and URL
                if base_name == 'index':
                    url_path = '/'
                else:
                    url_path = f'/{base_name}/'
                    
                view_url_info = f" A view function and URL pattern were automatically created. You can access this page at {url_path}"
                
                # Create response object that matches CodeGenerationResponse
                response_data = {
                    'success': True,
                    'code': template_content,  # This is the generated code the frontend expects
                    'response': success_message + view_url_info,
                    'conversation_id': result.get('conversation_id'),
                    'user_message': {
                        'role': 'user',
                        'content': message,
                        'timestamp': current_time
                    },
                    'assistant_message': {
                        'role': 'assistant',
                        'content': success_message + view_url_info,
                        'code': template_content,
                        'timestamp': current_time
                    }
                }
                
                return response_data
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Unknown error')
                }
        except Exception as e:
            logger.error(f"Error formatting template response: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def validate_project_access(self, project_id, user):
        """
        Validate that a project exists and the user has access to it.
        
        Args:
            project_id (str): The ID of the project
            user (User): The Django user object
            
        Returns:
            tuple: (project, error_response)
            - project: The Project object if validation succeeds, None otherwise
            - error_response: Error dict if validation fails, None otherwise
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