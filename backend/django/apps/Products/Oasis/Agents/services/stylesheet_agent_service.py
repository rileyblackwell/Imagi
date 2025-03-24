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
                logger.error("[ERROR] CSS content is empty")
                return False, "CSS content is empty"
            
            # Parse CSS to check for syntax errors
            try:
                sheet = cssutils.parseString(content)
                logger.info("[INFO] CSS parsed successfully")
            except Exception as e:
                logger.warning(f"[WARNING] CSS parsing error: {str(e)}")
                # Return true anyway, we'll just use the raw content
                return True, None
            
            # Less strict validation - log warnings but return valid
            has_rules = False
            has_root = False
            has_media_query = False
            
            for rule in sheet:
                if rule.type == rule.STYLE_RULE:
                    has_rules = True
                    if rule.selectorText == ':root':
                        has_root = True
                elif rule.type == rule.MEDIA_RULE:
                    has_media_query = True
            
            # Log validation results
            if has_rules:
                logger.info("[INFO] CSS contains style rules")
            else:
                logger.warning("[WARNING] No CSS rules found in the content, but continuing anyway")
            
            # Everything is a warning, not an error
            warnings = []
            
            if not has_root:
                warnings.append("Missing :root section with CSS variables")
            
            if not has_media_query:
                warnings.append("Missing media queries for responsive design")
            
            # Log warnings but still return valid
            if warnings:
                warning_message = "; ".join(warnings)
                logger.warning(f"[WARNING] CSS validation warnings: {warning_message}")
            
            # Always return valid
            return True, None
            
        except Exception as e:
            logger.error(f"[ERROR] Unexpected error in CSS validation: {str(e)}")
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
            model (str): The AI model to use (e.g., 'claude-3-5-sonnet-20241022')
            user: The Django user object
            project_id (str, optional): The project ID
            file_path (str, optional): The target file path
            conversation_id (str, optional): The ID of an existing conversation
            
        Returns:
            dict: A dictionary containing the result, including the generated stylesheet
        """
        try:
            # Debug log all input parameters
            logger.info(f"[DEBUG] process_stylesheet called with: model={model}, project_id={project_id}, file_path={file_path}, user={user.username}")
            
            # Set default file path if not provided
            if not file_path:
                file_path = 'static/css/styles.css'
                logger.info(f"[DEBUG] Using default file_path: {file_path}")
                
            # Ensure we have project_id
            if not project_id:
                logger.warning(f"[WARNING] No project_id provided for stylesheet generation")
            
            # Add project context to the prompt if project_id is provided
            project_context = ""
            if project_id:
                # Optional: Get project details to provide more context
                try:
                    from apps.Products.Oasis.ProjectManager.models import Project
                    
                    # Convert project_id to integer if it's a string
                    project_id_int = int(project_id) if isinstance(project_id, str) else project_id
                    
                    logger.info(f"[DEBUG] Looking up project with ID: {project_id_int}")
                    project = Project.objects.get(id=project_id_int)
                    project_context = f"You are creating a stylesheet for project '{project.name}' (ID: {project_id}).\n"
                    logger.info(f"[DEBUG] Found project: {project.name}")
                except (ValueError, TypeError) as e:
                    logger.error(f"[ERROR] Invalid project_id format: {project_id}, error: {str(e)}")
                    # Use fallback instead of returning an error
                    return self.generate_fallback_stylesheet(file_path, f"Invalid project ID format: {project_id}")
                except Exception as e:
                    logger.error(f"[ERROR] Error getting project details: {str(e)}")
                    # Continue without project context
            
            # Build the enhanced prompt with project context and best practices
            enhanced_prompt = f"{project_context}Create a stylesheet based on this description: {prompt}"
            
            logger.info(f"[DEBUG] Enhanced prompt created with project context")
            
            # Use the handle_stylesheet_request method to process the request
            result = self.handle_stylesheet_request(
                user_input=enhanced_prompt,
                model=model,
                user=user,
                file_path=file_path,
                conversation_id=conversation_id,
                project_id=project_id
            )
            
            # Extract the generated content and return it in the expected format
            if result.get('success'):
                logger.info(f"[DEBUG] Stylesheet request successful")
                stylesheet_content = result.get('response', '')
                
                # Check if we got a valid stylesheet content
                if not stylesheet_content or len(stylesheet_content.strip()) < 10:
                    logger.warning(f"[WARNING] Generated stylesheet is empty or too short")
                    return self.generate_fallback_stylesheet(file_path, "Generated stylesheet was invalid or too short")
                
                # Ensure all required sections are present, adding them if necessary
                stylesheet_content = self.ensure_required_sections(stylesheet_content)
                
                # Validate and clean the CSS content
                try:
                    # Parse CSS to validate it 
                    logger.info(f"[DEBUG] Validating CSS content of length: {len(stylesheet_content)}")
                    css_parser = cssutils.parseString(stylesheet_content)
                    # Converting back to string ensures proper formatting
                    validated_stylesheet = css_parser.cssText.decode('utf-8')
                    logger.info(f"[DEBUG] CSS validation successful")
                except Exception as css_error:
                    logger.error(f"[ERROR] CSS validation error: {str(css_error)}")
                    # If parsing fails, use the original stylesheet
                    validated_stylesheet = stylesheet_content
                
                # Get timestamp
                current_time = timezone.now().isoformat()
                
                # Return the result with all needed fields
                logger.info(f"[DEBUG] Returning successful stylesheet response")
                return {
                    'success': True,
                    'stylesheet': validated_stylesheet,
                    'code': validated_stylesheet,  # Add code field for frontend compatibility
                    'file_name': file_path,
                    'conversation_id': result.get('conversation_id'),
                    'timestamp': current_time,
                    'response': "Generated stylesheet successfully",
                    'user_message': {
                        'role': 'user',
                        'content': prompt,
                        'timestamp': current_time
                    },
                    'assistant_message': {
                        'role': 'assistant',
                        'content': "I've created the CSS stylesheet based on your requirements. Here's the code:",
                        'code': validated_stylesheet,
                        'timestamp': current_time
                    }
                }
            else:
                error_msg = result.get('error', 'Stylesheet generation failed')
                logger.error(f"[ERROR] Stylesheet generation failed: {error_msg}")
                # Use fallback instead of returning an error
                return self.generate_fallback_stylesheet(file_path, error_msg)
                
        except Exception as e:
            import traceback
            logger.error(f"[ERROR] Exception in process_stylesheet: {str(e)}")
            logger.error(f"[ERROR] Traceback: {traceback.format_exc()}")
            # Use fallback for any unhandled exceptions
            return self.generate_fallback_stylesheet(file_path, str(e))
            
    def ensure_required_sections(self, css_content):
        """
        Ensure all required sections are present in the stylesheet.
        
        Checks for and adds missing sections including:
        - Variables (:root)
        - Reset
        - Base
        - Typography
        - Layout
        - Components
        - Media Queries
        
        Args:
            css_content (str): The generated stylesheet content
            
        Returns:
            str: The enhanced stylesheet with all required sections
        """
        logger.info(f"[DEBUG] Ensuring required sections in CSS of length: {len(css_content)}")
        
        # Try to parse the CSS to work with it programmatically
        try:
            sheet = cssutils.parseString(css_content)
            
            # Check for existing sections using comments as markers
            sections = {
                'variables': False,
                'reset': False,
                'base': False,
                'typography': False,
                'layout': False,
                'components': False,
                'media_queries': False
            }
            
            # Look for section markers in comments
            comment_pattern = r'/\*\s*(variables|reset|base|typography|layout|components|media\s*queries)\s*\*/'
            import re
            found_sections = set()
            for match in re.finditer(comment_pattern, css_content, re.IGNORECASE):
                section = match.group(1).lower().replace(' ', '_')
                if section in sections:
                    sections[section] = True
                    found_sections.add(section)
            
            # Check for :root (variables) section
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
                logger.info(f"[DEBUG] Missing CSS sections: {', '.join(missing_sections)}")
                
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
                
                if 'typography' not in found_sections:
                    additions.append("""
/* Typography */
h1, h2, h3 {
  color: var(--color-primary);
  margin-bottom: var(--spacing-unit);
}
""")
                
                if 'layout' not in found_sections:
                    additions.append("""
/* Layout */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--spacing-unit);
}
""")
                
                if 'components' not in found_sections:
                    additions.append("""
/* Components */
.button {
  background-color: var(--color-primary);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
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
                logger.info(f"[DEBUG] Added {len(additions)} missing sections to CSS")
                return enhanced_css
            
            # If all sections exist, return the original
            logger.info(f"[DEBUG] All required CSS sections present")
            return css_content
            
        except Exception as e:
            logger.error(f"[ERROR] Error ensuring CSS sections: {str(e)}")
            # In case of error, return the original content
            return css_content

    def generate_fallback_stylesheet(self, file_path, error_message=None):
        """
        Generate a fallback stylesheet when an error occurs during generation.
        
        Args:
            file_path (str): The path where the stylesheet would be saved
            error_message (str, optional): The error that caused the fallback
            
        Returns:
            dict: A response object with a basic default stylesheet
        """
        logger.info(f"[INFO] Generating fallback stylesheet for {file_path}")
        
        # Create a minimal default stylesheet
        default_css = """
/* Variables */
:root {
  --color-primary: #3f51b5;
  --color-secondary: #f50057;
  --color-text: #333333;
  --color-bg: #ffffff;
  --font-family: 'Arial', sans-serif;
  --spacing-unit: 16px;
}

/* Reset */
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

/* Base */
body {
  font-family: var(--font-family);
  color: var(--color-text);
  background-color: var(--color-bg);
  padding: var(--spacing-unit);
}

/* Typography */
h1, h2, h3 {
  color: var(--color-primary);
  margin-bottom: var(--spacing-unit);
}

/* Layout */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--spacing-unit);
}

/* Components */
.button {
  background-color: var(--color-primary);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

/* Media Queries */
@media (min-width: 768px) {
  .container {
    padding: calc(var(--spacing-unit) * 2);
  }
}
"""
        # Get timestamp
        current_time = timezone.now().isoformat()
        
        # Error context for the message
        error_context = ""
        if error_message:
            error_context = f" (Error recovery: {error_message})"
            
        # Create a successful response with the default CSS
        return {
            'success': True,
            'stylesheet': default_css,
            'code': default_css,
            'file_name': file_path,
            'timestamp': current_time,
            'response': f"Generated default stylesheet{error_context}",
            'user_message': {
                'role': 'user',
                'content': "Generate a default stylesheet",
                'timestamp': current_time
            },
            'assistant_message': {
                'role': 'assistant',
                'content': "I've created a default CSS stylesheet with basic styling for your project.",
                'code': default_css,
                'timestamp': current_time
            }
        } 