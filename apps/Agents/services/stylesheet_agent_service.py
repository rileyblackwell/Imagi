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
            "Generate only valid CSS code following these strict guidelines:\n\n"
            
            "1. **CSS ARCHITECTURE**:\n"
            "   - Use CSS variables (:root) for consistent theming (e.g., colors, spacing, fonts).\n"
            "   - Organize styles into logical sections (e.g., variables, reset, base styles, layout, components, media queries).\n"
            "   - Follow a mobile-first approach with base styles first, enhanced with responsive @media rules.\n"
            "   - Use the BEM (Block Element Modifier) naming convention for class names.\n\n"
            
            "2. **MODERN FEATURES**:\n"
            "   - Leverage flexbox and grid for layout design.\n"
            "   - Include responsive breakpoints with @media queries.\n"
            "   - Use modern CSS properties like clamp(), min(), max(), and gap.\n\n"
            
            "3. **PERFORMANCE**:\n"
            "   - Optimize styles with efficient selectors and minimal redundancy.\n"
            "   - Use shorthand properties where applicable.\n"
            "   - Reuse classes to avoid over-specificity.\n\n"
            
            "4. **STRUCTURE**:\n"
            "   - Organize the stylesheet into the following structure:\n\n"
            "     - **Variables**: Define reusable CSS variables for consistent theming.\n"
            "     - **Reset**: Apply reset styles for box-sizing, margin, padding, etc.\n"
            "     - **Base Styles**: Define default styles for HTML elements.\n"
            "     - **Layout**: Apply styles for containers, grids, and overall layout.\n"
            "     - **Components**: Style buttons, links, headers, and other UI elements.\n"
            "     - **Media Queries**: Add responsive adjustments for various screen sizes.\n\n"
            
            "5. **OUTPUT REQUIREMENTS**:\n"
            "   - Return only valid CSS code ready to be used in a stylesheet.\n"
            "   - Do not include plain text, descriptions, or non-CSS comments.\n"
            "   - Ensure consistent formatting with proper indentation and spacing.\n\n"
            
            "EXAMPLE STRUCTURE:\n\n"
            ":root {\n"
            "  --primary-color: #0066ff;\n"
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
            "  line-height: 1.6;\n"
            "  color: var(--primary-color);\n"
            "  margin: var(--spacing-unit);\n"
            "}\n\n"
            ".container {\n"
            "  max-width: 1200px;\n"
            "  margin: 0 auto;\n"
            "  padding: var(--spacing-unit);\n"
            "  display: flex;\n"
            "  flex-direction: column;\n"
            "}\n\n"
            ".button {\n"
            "  background-color: var(--primary-color);\n"
            "  color: #fff;\n"
            "  padding: 10px 20px;\n"
            "  border: none;\n"
            "  border-radius: 4px;\n"
            "  cursor: pointer;\n"
            "}\n\n"
            "@media (min-width: 768px) {\n"
            "  .container {\n"
            "    padding: calc(var(--spacing-unit) * 2);\n"
            "  }\n"
            "  .button {\n"
            "    font-size: 1.2rem;\n"
            "  }\n"
            "}"
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