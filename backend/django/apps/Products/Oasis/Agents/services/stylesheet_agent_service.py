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
            if not content.strip():
                return False, "CSS content is empty"
                
            # Parse CSS to check for syntax errors
            sheet = cssutils.parseString(content)
            
            # Check for required sections using comments
            required_sections = [
                'Variables', 'Reset', 'Base', 'Typography', 
                'Layout', 'Components', 'Media'
            ]
            found_sections = []
            
            for rule in sheet:
                if rule.type == rule.COMMENT:
                    comment = rule.cssText.lower()
                    for section in required_sections:
                        if section.lower() in comment:
                            found_sections.append(section)
            
            missing_sections = [s for s in required_sections if s not in found_sections]
            if missing_sections:
                return False, f"Missing sections: {', '.join(missing_sections)}"
                
            # Check for root variables
            has_root = False
            for rule in sheet:
                if rule.type == rule.STYLE_RULE:
                    if rule.selectorText == ':root':
                        has_root = True
                        break
            
            if not has_root:
                return False, "Missing :root section with CSS variables"
                
            # Check for media queries
            has_media_query = False
            for rule in sheet:
                if rule.type == rule.MEDIA_RULE:
                    has_media_query = True
                    break
                    
            if not has_media_query:
                return False, "Missing media queries for responsive design"
            
            return True, None
            
        except Exception as e:
            return False, f"CSS validation error: {str(e)}"

    def handle_stylesheet_request(self, user_input, model, user, file_path, conversation_id=None):
        """
        Handle a complete stylesheet generation request, including conversation management.
        
        Args:
            user_input (str): The user's message
            model (str): The AI model to use
            user: The Django user object
            file_path (str): The path to the stylesheet file
            conversation_id (int, optional): The ID of an existing conversation
            
        Returns:
            dict: The result of the operation, including success status and response
        """
        try:
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
            
            # Process stylesheet generation
            result = self.process_conversation(
                user_input=user_input,
                model=model,
                user=user,
                file_name=file_path,
                conversation=conversation
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
            print(f"Error in handle_stylesheet_request: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            } 

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
            # Set default file path if not provided
            if not file_path:
                file_path = 'static/css/styles.css'
            
            # Call the existing method to handle the stylesheet request
            result = self.handle_stylesheet_request(
                user_input=prompt,
                model=model,
                user=user,
                file_path=file_path,
                conversation_id=conversation_id
            )
            
            # Extract the generated content and return it in the expected format
            if result.get('success'):
                stylesheet_content = result.get('response', '')
                
                # Validate and clean the CSS content
                try:
                    # Parse CSS to validate it 
                    css_parser = cssutils.parseString(stylesheet_content)
                    # Converting back to string ensures proper formatting
                    validated_stylesheet = css_parser.cssText.decode('utf-8')
                except:
                    # If parsing fails, use the original stylesheet
                    validated_stylesheet = stylesheet_content
                
                # Return the result with all needed fields
                return {
                    'success': True,
                    'stylesheet': validated_stylesheet,
                    'file_name': file_path,
                    'conversation_id': result.get('conversation_id'),
                    'timestamp': result.get('timestamp')
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Stylesheet generation failed')
                }
                
        except Exception as e:
            print(f"Error in process_stylesheet: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            } 