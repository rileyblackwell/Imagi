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
import re

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
            logger.info(f"StylesheetAgentService handling request for file: {file_path}")
            
            # Process the conversation using the parent class method
            result = self.process_conversation(
                user_input=user_input,
                model=model,
                user=user,
                conversation_id=conversation_id,
                project_id=project_id,
                file_path=file_path
            )
            
            # Extract CSS content if successful
            if result.get('success', False):
                css_content = self.extract_css_from_response(result['response'])
                enhanced_css = self.ensure_required_sections(css_content)
                result['response'] = enhanced_css
            
            return result
            
        except Exception as e:
            logger.error(f"Error in handle_stylesheet_request: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': str(e)
            }

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
            
            return result
            
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
        Ensure the CSS content has all the required sections.
        
        Args:
            css_content (str): The CSS content to enhance
            
        Returns:
            str: The enhanced CSS content
        """
        # Check if :root section exists
        if ':root' not in css_content:
            # Add :root section with common variables
            root_section = """
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
"""
            css_content = root_section + css_content
        
        # Check if reset section exists
        if '*::before' not in css_content and '*::after' not in css_content:
            # Add basic reset
            reset_section = """
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}
"""
            # Find position to insert (after :root section)
            root_end = css_content.find('}', css_content.find(':root'))
            if root_end > -1:
                css_content = css_content[:root_end+1] + reset_section + css_content[root_end+1:]
            else:
                css_content = reset_section + css_content
        
        # Check if body styles exist
        if 'body {' not in css_content:
            # Add basic body styles
            body_section = """
body {
  font-family: var(--font-family);
  color: var(--color-text);
  background-color: var(--color-background);
  line-height: 1.5;
  font-size: var(--font-size-base);
}
"""
            # Find position to insert (after reset section)
            reset_end = css_content.find('}', css_content.find('*::after')) if '*::after' in css_content else css_content.find('}', css_content.find('box-sizing')) if 'box-sizing' in css_content else -1
            if reset_end > -1:
                css_content = css_content[:reset_end+1] + body_section + css_content[reset_end+1:]
            else:
                css_content += body_section
        
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