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
                "You are an expert CSS specialist focused on creating modern, responsive, and maintainable stylesheets. "
                "Your designs should align with the aesthetics of leading tech companies like Stripe, AirBnB, Meta, Apple, and Discord. "
                "Generate only valid CSS stylesheets that follow these strict guidelines:\n\n"
                
                "1. CSS ARCHITECTURE:\n"
                "   - Use CSS variables (:root) for consistent theming (e.g., colors, spacing, fonts).\n"
                "   - Organize styles into logical sections with clear, valid CSS comments (e.g., /* Layout */).\n"
                "   - Follow a mobile-first approach, defining base styles first and enhancing for larger screens.\n"
                "   - Use the BEM (Block Element Modifier) naming convention for class names to ensure clarity and modularity.\n\n"
            
                "2. MODERN FEATURES:\n"
                "   - Leverage flexbox and grid for layout design.\n"
                "   - Include responsive breakpoints for seamless behavior across devices (e.g., @media queries).\n"
                "   - Use modern CSS properties (e.g., clamp, min(), max(), gap).\n"
                "   - Include vendor prefixes for compatibility using tools like Autoprefixer when necessary.\n\n"
            
                "3. PERFORMANCE:\n"
                "   - Optimize styles for performance with efficient selectors and minimal redundancy.\n"
                "   - Use shorthand properties where applicable (e.g., margin: 0 auto;).\n"
                "   - Aim for reusable classes and avoid over-specificity.\n"
                "   - Ensure styles are lightweight and clean for fast page rendering.\n\n"
                
                "4. STRUCTURE:\n"
                "   - Organize your stylesheet into the following sections for readability:\n"
                "   ```css\n"
                "   /* Variables */\n"
                "   :root {\n"
                "       --primary-color: #0066ff;\n"
                "       --font-family: 'Inter', sans-serif;\n"
                "   }\n\n"
                "   /* Reset */\n"
                "   *, *::before, *::after {\n"
                "       box-sizing: border-box;\n"
                "       margin: 0;\n"
                "       padding: 0;\n"
                "   }\n\n"
                "   /* Base Styles */\n"
                "   body {\n"
                "       font-family: var(--font-family);\n"
                "       color: var(--primary-color);\n"
                "       line-height: 1.6;\n"
                "   }\n\n"
                "   /* Layout */\n"
                "   .container {\n"
                "       max-width: 1200px;\n"
                "       margin: auto;\n"
                "       padding: 16px;\n"
                "   }\n\n"
                "   /* Components */\n"
                "   .button {\n"
                "       background: var(--primary-color);\n"
                "       color: white;\n"
                "       padding: 10px 20px;\n"
                "       border: none;\n"
                "       border-radius: 4px;\n"
                "   }\n\n"
                "   /* Media Queries */\n"
                "   @media (min-width: 768px) {\n"
                "       .container {\n"
                "           padding: 32px;\n"
                "       }\n"
                "   }\n"
                "   ```\n\n"
                
                "5. OUTPUT REQUIREMENTS:\n"
                "   - Return only valid CSS code.\n"
                "   - Use clear, valid CSS comments (e.g., /* Components */) to separate major sections.\n"
                "   - Do not include plain text or non-CSS comments.\n"
                "   - Maintain consistent formatting with proper indentation and spacing.\n"
                "   - Focus on maintainability and readability while ensuring visual excellence."
            )
        }
    
    
    def get_additional_context(self, **kwargs):
        """Get stylesheet-specific context."""
        return "You are creating/editing styles.css for the project"
    
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