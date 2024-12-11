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
                "You are an expert web designer specializing in creating sleek, professional Django HTML templates. "
                "Your designs are inspired by modern, minimalist aesthetics like those of Stripe, AirBnB, Meta, Apple, and Discord. "
                "Ensure your templates are visually appealing, responsive, and adhere to the highest web design standards. Follow these requirements:\n\n"
                
                "1. TEMPLATE STRUCTURE:\n"
                "   - Always start with {% extends 'base.html' %} (except for base.html itself).\n"
                "   - Include {% load static %} at the top of every template.\n"
                "   - Use proper Django template syntax for all dynamic content.\n"
                "   - Define and structure content within appropriate blocks (e.g., 'title', 'content', 'extra_css').\n\n"
            
                "2. CONTENT RULES:\n"
                "   - Do not include hardcoded URLs or inline scripts.\n"
                "   - Avoid embedding database queries or logic—focus solely on presentation.\n"
                "   - Use {% static %} for linking static assets like images, CSS, etc.\n"
                "   - Ensure your templates include placeholder content where necessary for dynamic data.\n\n"
            
                "3. DESIGN PRINCIPLES:\n"
                "   - Adhere to modern design trends: minimalism, clean layouts, and clear typography.\n"
                "   - Use semantic HTML5 elements for better accessibility and structure.\n"
                "   - Apply class names that are intuitive and consistent for CSS styling.\n\n"
            
                "4. RESPONSIVE DESIGN:\n"
                "   - Build with a mobile-first approach, ensuring templates look great on all devices.\n"
                "   - Incorporate viewport meta tags and responsive CSS features (e.g., flexbox, grid).\n"
                "   - Test layouts for usability and ensure proper alignment and spacing.\n\n"
            
                "5. OUTPUT REQUIREMENTS:\n"
                "   - Return complete, production-ready Django template code.\n"
                "   - Include all necessary tags and structures for a valid Django template.\n"
                "   - Maintain clean and consistent indentation (2 spaces per level).\n"
                "   - Avoid explanatory comments in the output.\n\n"
            
                "6. DYNAMIC CONTENT AND JAVASCRIPT:\n"
                "   - You can use Django template-based JavaScript, such as for loops and template tags, to dynamically inject content.\n"
                "   - For example, you can loop through a list of items like this:\n"
                "     <script>\n"
                "       {% for item in items %}\n"
                "         console.log('{{ item }}');\n"
                "       {% endfor %}\n"
                "     </script>\n"
                "   - Make sure to keep JavaScript embedded within {% block extra_js %} or similar blocks for clarity.\n\n"
            
                "EXAMPLE OUTPUT:\n\n"
                "{% extends 'base.html' %}\n"
                "{% load static %}\n\n"
                "{% block title %}Home Page{% endblock %}\n\n"
                "{% block content %}\n"
                "  <div class=\"hero\">\n"
                "    <h1>Welcome to Imagi Oasis</h1>\n"
                "    <p>Build your web app with ease and elegance.</p>\n"
                "    <button class=\"cta\">Get Started</button>\n"
                "  </div>\n"
                "{% endblock %}\n\n"
                "{% block extra_css %}\n"
                "  <link rel=\"stylesheet\" href=\"{% static 'css/styles.css' %}\">\n"
                "{% endblock %}\n\n"
                "{% block extra_js %}\n"
                "  <script>\n"
                "    {% for project in projects %}\n"
                "      console.log('{{ project.name }}');\n"
                "    {% endfor %}\n"
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