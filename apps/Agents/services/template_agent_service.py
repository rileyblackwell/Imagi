import os
from dotenv import load_dotenv
import re
from .agent_service import BaseAgentService

# Load environment variables from .env
load_dotenv()

class TemplateAgentService(BaseAgentService):
    """Specialized agent service for Django template generation."""
    
    def get_system_prompt(self):
        """Get the system prompt for Django template generation."""
        return {
            "role": "system",
            "content": (
                "You are a Django template specialist focused on creating modern, responsive HTML templates. "
                "Follow these strict requirements:\n\n"
                
                "1. TEMPLATE STRUCTURE:\n"
                "   - Always start with {% extends 'base.html' %} (except for base.html)\n"
                "   - Include {% load static %} at the top\n"
                "   - Define appropriate blocks (content, title, etc.)\n"
                "   - Use proper Django template syntax\n\n"
                
                "2. CONTENT RULES:\n"
                "   - NO hardcoded URLs or links\n"
                "   - NO database queries or view logic\n"
                "   - Use {% static %} for assets\n"
                "   - Focus on structure and presentation\n\n"
                
                "3. STYLING:\n"
                "   - Link to styles.css: <link rel=\"stylesheet\" href=\"{% static 'css/styles.css' %}\">\n"
                "   - Use semantic HTML5 elements\n"
                "   - Add appropriate class names for styling\n\n"
                
                "4. RESPONSIVE DESIGN:\n"
                "   - Use flexbox/grid layouts\n"
                "   - Include viewport meta tag\n"
                "   - Structure content for mobile-first design\n\n"
                
                "5. OUTPUT FORMAT:\n"
                "   - Return complete, valid Django template code\n"
                "   - Include all required template tags\n"
                "   - Maintain proper indentation\n"
                "   - No explanatory comments in the output\n"
            )
        }
    
    def validate_response(self, content):
        """
        Validate Django template syntax and structure.
        Returns (is_valid, error_message)
        """
        # Check for basic required elements
        checks = [
            (r"{%\s*load\s+static\s*%}", "Missing {% load static %} tag"),
            (r"<!DOCTYPE\s+html>", "Missing DOCTYPE declaration"),
            (r"<html.*?>", "Missing <html> tag"),
            (r"<head>.*?</head>", "Missing <head> section", re.DOTALL),
            (r"<body>.*?</body>", "Missing <body> section", re.DOTALL),
            (r'<meta\s+name="viewport"', "Missing viewport meta tag"),
        ]
        
        # Special check for non-base templates
        if "base.html" not in content.lower():
            checks.append(
                (r"{%\s*extends\s+'base.html'\s*%}", "Missing {% extends 'base.html' %} tag")
            )
        
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