"""
Stylesheet agent service for Imagi Oasis.

This module provides a specialized agent service for CSS stylesheet generation,
allowing users to create and modify stylesheets through natural language instructions.
"""

from dotenv import load_dotenv
import cssutils
import logging
from .agent_service import BaseAgentService
from ..models import AgentConversation, SystemPrompt, AgentMessage
from django.shortcuts import get_object_or_404
from django.utils import timezone

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
    
    def get_system_prompt(self):
        """
        Get the system prompt for CSS stylesheet generation.
        
        Returns:
            dict: A message dictionary with 'role' and 'content' keys
        """
        return {
            "role": "system",
            "content": (
                "Your name is Imagi Oasis, and you are an advanced tool specialized in creating professional, sleek, and visually stunning CSS stylesheets. "
                "Your sole responsibility is to generate valid CSS code based on user input. The output should be a complete and ready-to-use CSS stylesheet, "
                "with no additional text, explanations, or comments outside valid CSS comments.\n\n"
                
                "Your responsibilities:\n"
                "1. Generate **only valid CSS code** with proper formatting and indentation.\n"
                "2. Ensure that your output matches the format of the provided example CSS exactly, starting and ending with valid CSS or CSS comments.\n"
                "3. Do not include any text or comments before the opening CSS rule or after the closing CSS rule.\n"
                "4. Respond iteratively with updated CSS styles based on user feedback.\n\n"
                
                "Key guidelines for CSS generation:\n"
                "1. **OUTPUT REQUIREMENTS**:\n"
                "   - Only generate valid CSS and CSS comments.\n"
                "   - Do not include any plain text, explanations, or non-CSS comments.\n"
                "   - The output must look identical to the example CSS in structure and format.\n\n"
                
                "2. **CSS ARCHITECTURE**:\n"
                "   - Use CSS variables (:root) for consistent theming (e.g., colors, spacing, fonts).\n"
                "   - Organize styles into logical sections: variables, reset, base styles, layout, components, and media queries.\n"
                "   - Follow a mobile-first approach with base styles first, enhanced with responsive @media rules.\n\n"
                
                "3. **MODERN FEATURES**:\n"
                "   - Leverage flexbox and grid for layout design.\n"
                "   - Use modern CSS properties like `clamp()`, `min()`, `max()`, and `gap`.\n\n"
                
                "4. **EXAMPLE FORMAT**:\n"
                "   - Use the following example as a template for your output. Your response must follow this format exactly:\n\n"
                
                ":root {\n"
                "  /* Color Variables */\n"
                "  --color-primary: #6366f1;\n"
                "  --color-secondary: #0ea5e9;\n"
                "  --font-family: 'Inter', sans-serif;\n"
                "  --spacing-unit: 16px;\n"
                "}\n\n"
                "*, *::before, *::after {\n"
                "  box-sizing: border-box;\n"
                "  margin: 0;\n"
                "  padding: 0;\n"
                "}\n\n"
                "body {\n"
                "  font-family: var(--font-family);\n"
                "  color: var(--color-primary);\n"
                "  padding: var(--spacing-unit);\n"
                "}\n\n"
                ".container {\n"
                "  max-width: 1200px;\n"
                "  margin: 0 auto;\n"
                "  display: flex;\n"
                "  gap: var(--spacing-unit);\n"
                "}\n\n"
                ".button {\n"
                "  background-color: var(--color-primary);\n"
                "  color: #fff;\n"
                "  border: none;\n"
                "  border-radius: 4px;\n"
                "  padding: 0.5rem 1rem;\n"
                "  cursor: pointer;\n"
                "}\n\n"
                "@media (min-width: 768px) {\n"
                "  .container {\n"
                "    flex-direction: row;\n"
                "  }\n"
                "  .button {\n"
                "    font-size: 1.2rem;\n"
                "  }\n"
                "}"
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
        return "You are creating/editing styles.css for the project"
    
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
            logger.info(f"[DEBUG] handle_stylesheet_request started with model={model}, file_path={file_path}")
            
            # Get or create conversation
            if conversation_id:
                try:
                    conversation = get_object_or_404(
                        AgentConversation,
                        id=conversation_id,
                        user=user
                    )
                    logger.info(f"[DEBUG] Using existing conversation: {conversation_id}")
                except Exception as e:
                    logger.error(f"[ERROR] Error retrieving conversation {conversation_id}: {str(e)}")
                    # Create a new conversation instead of failing
                    conversation = AgentConversation.objects.create(
                        user=user,
                        model_name=model,
                        provider='anthropic' if model.startswith('claude') else 'openai'
                    )
                    logger.info(f"[DEBUG] Created new conversation as fallback: {conversation.id}")
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
                logger.info(f"[DEBUG] Created new conversation: {conversation.id}")
            
            # Save user message
            user_message = AgentMessage.objects.create(
                conversation=conversation,
                role='user',
                content=user_input
            )
            logger.info(f"[DEBUG] Saved user message, ID: {user_message.id}")
            
            # Get project path if project_id is provided
            project_path = None
            if project_id:
                try:
                    from apps.Products.Oasis.ProjectManager.models import Project
                    project = Project.objects.get(id=project_id, user=user)
                    project_path = project.project_path
                    logger.info(f"[DEBUG] Using project path: {project_path}")
                except Exception as e:
                    logger.warning(f"[WARNING] Could not get project path from project_id {project_id}: {str(e)}")
            
            # Process stylesheet generation
            logger.info(f"[DEBUG] Calling process_conversation")
            result = self.process_conversation(
                user_input=user_input,
                model=model,
                user=user,
                file_name=file_path,
                conversation=conversation,
                project_path=project_path
            )
            
            logger.info(f"[DEBUG] process_conversation result: success={result.get('success', False)}")
            
            if result.get('success'):
                # Extract CSS from response
                raw_response = result.get('response', '')
                logger.info(f"[DEBUG] Raw response length: {len(raw_response)}")
                
                # Extract CSS content from the response
                css_content = self.extract_css_from_response(raw_response)
                logger.info(f"[DEBUG] Extracted CSS length: {len(css_content)}")
                
                if not css_content:
                    logger.warning(f"[WARNING] No CSS content could be extracted from response")
                    # Use the original response as fallback
                    css_content = raw_response
                
                # Save assistant response with the extracted CSS
                assistant_message = AgentMessage.objects.create(
                    conversation=conversation,
                    role='assistant',
                    content=css_content
                )
                logger.info(f"[DEBUG] Saved assistant message, ID: {assistant_message.id}")
                
                # Get timestamp for consistency
                current_time = timezone.now().isoformat()
                
                return {
                    'success': True,
                    'conversation_id': conversation.id,
                    'response': css_content,
                    'user_message': {
                        'id': user_message.id,
                        'role': 'user',
                        'content': user_input,
                        'timestamp': current_time
                    },
                    'assistant_message': {
                        'id': assistant_message.id,
                        'role': 'assistant',
                        'content': css_content,
                        'timestamp': current_time
                    },
                    'timestamp': current_time
                }
            else:
                error_msg = result.get('error', 'Unknown error')
                logger.error(f"[ERROR] Failed to generate CSS: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'response': result.get('response')
                }
                
        except Exception as e:
            import traceback
            logger.error(f"[ERROR] Exception in handle_stylesheet_request: {str(e)}")
            logger.error(f"[ERROR] Traceback: {traceback.format_exc()}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def extract_css_from_response(self, response):
        """
        Extract CSS content from the AI response.
        
        This function handles various ways CSS might be formatted in the response,
        including markdown code blocks, CSS comments, or plain CSS.
        
        Args:
            response (str): The raw response from the AI
            
        Returns:
            str: The extracted CSS content
        """
        # Handle case where response is already clean CSS
        if response.strip().startswith(':root') or response.strip().startswith('/*'):
            return response
            
        # Try to extract from markdown code blocks
        import re
        css_block_pattern = r'```css\s*([\s\S]*?)\s*```'
        css_blocks = re.findall(css_block_pattern, response)
        
        if css_blocks:
            # Return the largest CSS block (most likely the complete stylesheet)
            return max(css_blocks, key=len)
            
        # Try to find CSS content between comments or style tags
        css_content_pattern = r'/\*[\s\S]*?\*/|<style>[\s\S]*?</style>'
        css_content = re.findall(css_content_pattern, response)
        
        if css_content:
            # Join all CSS content
            return '\n'.join(css_content)
            
        # If no clear CSS markers, try to extract anything that looks like CSS rules
        css_rule_pattern = r'[.#]?[\w-]+\s*{[^}]*}'
        css_rules = re.findall(css_rule_pattern, response)
        
        if css_rules:
            # Join all CSS rules
            return '\n'.join(css_rules)
            
        # If all else fails, return the original response
        return response

    def process_stylesheet(self, prompt, model, user, project_id=None, file_path=None, conversation_id=None):
        """
        Process a stylesheet generation request.
        
        Args:
            prompt (str): The user's prompt describing the desired stylesheet
            model (str): The AI model to use (e.g., 'claude-3-7-sonnet-20250219')
            user: The Django user object
            project_id (str, optional): The project ID
            file_path (str, optional): The target file path
            conversation_id (str, optional): The ID of an existing conversation
            
        Returns:
            dict: A dictionary containing the result, including the generated stylesheet
        """
        try:
            # Log basic info
            logger.info(f"process_stylesheet called with: model={model}, file_path={file_path}")
            
            # Set default file path if not provided
            if not file_path:
                file_path = 'static/css/styles.css'
                logger.info(f"Using default file_path: {file_path}")
            
            # Get or create conversation
            conversation = None
            if conversation_id:
                conversation = self.get_conversation(conversation_id, user)
            
            if not conversation:
                # Get system prompt
                system_prompt = self.get_system_prompt()
                conversation = self.create_conversation(user, model, system_prompt)
            
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
            if self.project_files:
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
            if file_path:
                current_file_context = f"\n\nCurrent File: {file_path}\n"
                current_file_context += f"You are creating or editing the file: {file_path}\n"
                current_file_context += f"Focus your generation on producing ONLY valid CSS content for this file."
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
                    'error': f"Error generating stylesheet: {str(model_error)}",
                    'response': None
                }
            
            # Extract CSS from the response
            css_content = self.extract_css_from_response(response_content)
            
            # Ensure all required sections are present
            css_content = self.ensure_required_sections(css_content)
            
            # Validate the CSS
            is_valid, error = self.validate_response(css_content)
            if not is_valid:
                logger.warning(f"CSS validation failed: {error}")
                return {
                    'success': False,
                    'error': error,
                    'response': css_content
                }
            
            # Store the assistant response
            self.add_assistant_message(conversation, css_content, user)
            
            # Try to save the file if project_id and file_path are provided
            if project_id and file_path and project_path:
                try:
                    logger.info(f"Attempting to save file {file_path} to project {project_id}")
                    from apps.Products.Oasis.Builder.services.file_service import FileService
                    file_service = FileService(user=user)
                    
                    # Prepare file data
                    file_data = {
                        'name': file_path,
                        'content': css_content,
                        'type': 'css'
                    }
                    
                    # Create or update the file
                    file_result = file_service.create_file(file_data, project_id)
                    logger.info(f"File saved successfully: {file_result['path']}")
                    
                    # Return success response with file information
                    return {
                        'success': True,
                        'conversation_id': str(conversation.id),
                        'stylesheet': css_content,
                        'code': css_content,
                        'response': f"Successfully created {file_path}",
                        'timestamp': timezone.now().isoformat(),
                        'file': {
                            'path': file_result['path'],
                            'type': file_result['type']
                        },
                        'user_message': {
                            'role': 'user',
                            'content': prompt,
                            'timestamp': timezone.now().isoformat()
                        },
                        'assistant_message': {
                            'role': 'assistant',
                            'content': f"Successfully created {file_path}",
                            'code': css_content,
                            'timestamp': timezone.now().isoformat()
                        }
                    }
                except Exception as file_error:
                    logger.error(f"Error saving file: {str(file_error)}")
                    return {
                        'success': True,
                        'conversation_id': str(conversation.id),
                        'stylesheet': css_content,
                        'code': css_content,
                        'response': css_content,
                        'timestamp': timezone.now().isoformat(),
                        'warning': f"File generated but could not be saved: {str(file_error)}",
                        'user_message': {
                            'role': 'user',
                            'content': prompt,
                            'timestamp': timezone.now().isoformat()
                        },
                        'assistant_message': {
                            'role': 'assistant',
                            'content': f"Generated stylesheet but encountered an error saving it",
                            'code': css_content,
                            'timestamp': timezone.now().isoformat()
                        }
                    }
            
            # Return the successful response
            return {
                'success': True,
                'conversation_id': str(conversation.id),
                'stylesheet': css_content,
                'code': css_content,
                'response': "Successfully created stylesheet",
                'timestamp': timezone.now().isoformat(),
                'user_message': {
                    'role': 'user',
                    'content': prompt,
                    'timestamp': timezone.now().isoformat()
                },
                'assistant_message': {
                    'role': 'assistant',
                    'content': "Successfully created stylesheet",
                    'code': css_content,
                    'timestamp': timezone.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error in process_stylesheet: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': str(e)
            }
            
    def ensure_required_sections(self, css_content):
        """
        Ensure all required sections are present in the stylesheet.
        
        Args:
            css_content (str): The generated stylesheet content
            
        Returns:
            str: The enhanced stylesheet with all required sections
        """
        logger.info(f"Ensuring required sections in CSS of length: {len(css_content)}")
        
        # Try to parse the CSS to work with it programmatically
        try:
            sheet = cssutils.parseString(css_content)
            
            # Check for existing sections using comments as markers
            sections = {
                'variables': False,
                'reset': False,
                'base': False,
                'media_queries': False
            }
            
            # Look for section markers in comments
            comment_pattern = r'/\*\s*(variables|reset|base|media\s*queries)\s*\*/'
            import re
            found_sections = set()
            for match in re.finditer(comment_pattern, css_content, re.IGNORECASE):
                section = match.group(1).lower().replace(' ', '_')
                if section in sections:
                    sections[section] = True
                    found_sections.add(section)
            
            # Check for :root (variables) section and media queries
            for rule in sheet:
                if rule.type == rule.STYLE_RULE and rule.selectorText == ':root':
                    sections['variables'] = True
                    found_sections.add('variables')
                elif rule.type == rule.MEDIA_RULE:
                    sections['media_queries'] = True
                    found_sections.add('media_queries')
            
            # If we're missing any sections, add them
            if not all(sections.values()):
                missing_sections = [section for section, exists in sections.items() if not exists]
                logger.info(f"Missing CSS sections: {', '.join(missing_sections)}")
                
                # Build the sections to add
                additions = []
                
                if 'variables' not in found_sections:
                    additions.append("""
/* Variables */
:root {
  --color-primary: #3f51b5;
  --color-secondary: #f50057;
  --color-text: #333333;
  --color-bg: #ffffff;
  --font-family: 'Arial', sans-serif;
  --spacing-unit: 16px;
}
""")
                
                if 'reset' not in found_sections:
                    additions.append("""
/* Reset */
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}
""")
                
                if 'base' not in found_sections:
                    additions.append("""
/* Base */
body {
  font-family: var(--font-family);
  color: var(--color-text);
  background-color: var(--color-bg);
  padding: var(--spacing-unit);
}
""")
                
                if 'media_queries' not in found_sections:
                    additions.append("""
/* Media Queries */
@media (min-width: 768px) {
  .container {
    padding: calc(var(--spacing-unit) * 2);
  }
}
""")
                
                # Combine the original CSS with the additions
                enhanced_css = css_content.strip() + "\n" + "".join(additions)
                logger.info(f"Added {len(additions)} missing sections to CSS")
                return enhanced_css
            
            # If all sections exist, return the original
            logger.info("All required CSS sections present")
            return css_content
            
        except Exception as e:
            logger.error(f"Error ensuring CSS sections: {str(e)}")
            # In case of error, return the original content
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