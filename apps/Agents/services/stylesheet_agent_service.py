import os
from dotenv import load_dotenv
import cssutils
import logging
from .agent_service import BaseAgentService

# Suppress cssutils parsing warnings
cssutils.log.setLevel(logging.CRITICAL)

# Load environment variables from .env
load_dotenv()

class StylesheetAgentService(BaseAgentService):
    """Specialized agent service for CSS stylesheet generation."""
    
    def get_system_prompt(self):
        """Get the system prompt for CSS stylesheet generation."""
        return {
            "role": "system",
            "content": (
                "You are a CSS specialist focused on creating modern, responsive stylesheets. "
                "Follow these strict requirements:\n\n"
                
                "1. CSS ARCHITECTURE:\n"
                "   - Use CSS variables for consistent theming\n"
                "   - Organize code in logical sections\n"
                "   - Follow mobile-first approach\n"
                "   - Use BEM naming convention\n\n"
                
                "2. MODERN FEATURES:\n"
                "   - Utilize flexbox and grid layouts\n"
                "   - Implement responsive breakpoints\n"
                "   - Use modern CSS properties\n"
                "   - Include vendor prefixes\n\n"
                
                "3. PERFORMANCE:\n"
                "   - Write efficient selectors\n"
                "   - Minimize redundancy\n"
                "   - Use shorthand properties\n"
                "   - Optimize for reusability\n\n"
                
                "4. STRUCTURE:\n"
                "   ```css\n"
                "   /* Variables */\n"
                "   :root { ... }\n\n"
                "   /* Reset/Base styles */\n"
                "   * { box-sizing: border-box; ... }\n\n"
                "   /* Typography */\n"
                "   /* Layout */\n"
                "   /* Components */\n"
                "   /* Utilities */\n"
                "   /* Media Queries */\n"
                "   ```\n\n"
                
                "5. OUTPUT FORMAT:\n"
                "   - Return complete, valid CSS\n"
                "   - Include comments for major sections\n"
                "   - Maintain consistent formatting\n"
                "   - Focus on maintainability\n"
            )
        }
    
    def validate_response(self, content):
        """
        Validate CSS syntax and structure.
        Returns (is_valid, error_message)
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