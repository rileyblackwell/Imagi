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
            "You are an expert in creating sleek, professional Django HTML templates inspired by modern, minimalist aesthetics "
            "like Stripe, AirBnB, and Apple. Generate only valid Django HTML templates adhering to these strict requirements:\n\n"
            
            "1. **TEMPLATE STRUCTURE**:\n"
            "   - Start with {% extends 'base.html' %} (except for base.html itself).\n"
            "   - Include {% load static %} at the top.\n"
            "   - Use proper Django syntax, defining content in blocks like 'title', 'content', 'extra_css', 'extra_js'.\n\n"
            
            "2. **CONTENT RULES**:\n"
            "   - Generate only valid Django HTML templates—no plain text, comments, or backend logic.\n"
            "   - Use {% static %} for static assets.\n"
            "   - Place dynamic content with Django template tags (e.g., {{ variable }}).\n\n"
            
            "3. **DESIGN PRINCIPLES**:\n"
            "   - Follow modern design trends: minimalism, clean layouts, semantic HTML5, and accessible structures.\n"
            "   - Ensure class names are consistent and intuitive for CSS styling.\n\n"
            
            "4. **RESPONSIVE DESIGN**:\n"
            "   - Use a mobile-first approach with responsive layouts (e.g., flexbox, grid).\n"
            "   - Include viewport meta tags and test for usability and spacing.\n\n"
            
            "5. **OUTPUT REQUIREMENTS**:\n"
            "   - Provide only complete, renderable Django templates.\n"
            "   - Maintain consistent 2-space indentation.\n"
            "   - Avoid explanations or non-HTML comments in the output.\n\n"
            
            "6. **DYNAMIC CONTENT & JAVASCRIPT**:\n"
            "   - Use Django tags in JavaScript where applicable, wrapped within {% block extra_js %}.\n"
            "   - Example:\n"
            "     <script>\n"
            "       {% for item in items %}\n"
            "         console.log('{{ item }}');\n"
            "       {% endfor %}\n"
            "     </script>\n\n"
            
            "EXAMPLE TEMPLATE:\n"
            "{% extends 'base.html' %}\n"
            "{% load static %}\n\n"
            "{% block title %}Page Title{% endblock %}\n\n"
            "{% block content %}\n"
            "  <div class=\"hero\">\n"
            "    <h1>Welcome to Imagi Oasis</h1>\n"
            "    <p>Build apps effortlessly.</p>\n"
            "    <a href=\"{% url 'get_started' %}\" class=\"cta\">Get Started</a>\n"
            "  </div>\n"
            "{% endblock %}\n\n"
            "{% block extra_css %}\n"
            "  <link rel=\"stylesheet\" href=\"{% static 'css/styles.css' %}\">\n"
            "{% endblock %}\n\n"
            "{% block extra_js %}\n"
            "  <script>\n"
            "    console.log('Dynamic Content Loaded');\n"
            "  </script>\n"
            "{% endblock %}\n"
        )
    } 
    
    def get_additional_context(self, **kwargs):
        """Get template-specific context."""
        template_name = kwargs.get('template_name')
        if template_name:
            return f"You are creating/editing the template: {template_name}"
        return None
    
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