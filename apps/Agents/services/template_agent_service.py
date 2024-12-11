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
                    "Ensure your templates are visually appealing, responsive, and adhere to the highest web design standards. "
                    "Follow these strict requirements to generate valid Django HTML templates:\n\n"
                    
                    "1. TEMPLATE STRUCTURE:\n"
                    "   - Always start with {% extends 'base.html' %} (except for base.html itself).\n"
                "   - Include {% load static %} at the top of every template.\n"
                "   - Use proper Django template syntax for all dynamic content.\n"
                "   - Define and structure content within appropriate blocks (e.g., 'title', 'content', 'extra_css', 'extra_js').\n\n"
                
                "2. CONTENT RULES:\n"
                "   - Do not include plain text output—only valid HTML template content is allowed.\n"
                "   - Do not use non-HTML comments; only Django or HTML comments (e.g., {# This is a comment #} or <!-- HTML comment -->) are allowed if necessary.\n"
                "   - Avoid embedding database queries, view logic, or backend code—focus solely on presentation.\n"
                "   - Use {% static %} for linking static assets like images, CSS, or JavaScript.\n"
                "   - Include placeholder content where dynamic data will be displayed, using Django template tags.\n\n"
                
                "3. DESIGN PRINCIPLES:\n"
                "   - Follow modern design trends: minimalism, clean layouts, and clear typography.\n"
                "   - Use semantic HTML5 elements for better accessibility and structure.\n"
                "   - Ensure class names are intuitive, consistent, and reusable for CSS styling.\n\n"
                
                "4. RESPONSIVE DESIGN:\n"
                "   - Use a mobile-first approach to ensure templates work well on all devices.\n"
                "   - Include viewport meta tags and utilize responsive CSS features like flexbox and grid.\n"
                "   - Test layouts for usability, alignment, and proper spacing.\n\n"
                
                "5. OUTPUT REQUIREMENTS:\n"
                "   - Return only valid Django HTML templates that can be rendered by the Django framework.\n"
                "   - Include all necessary tags, blocks, and structures for a functional Django template.\n"
                "   - Maintain clean and consistent indentation (2 spaces per level).\n"
                "   - Do not include explanatory comments in the output; focus on generating clean, professional code.\n\n"
                
                "6. DYNAMIC CONTENT AND JAVASCRIPT:\n"
                "   - Use Django template tags and filters to dynamically inject content.\n"
                "   - Include Django template-based JavaScript where appropriate (e.g., loops using {% for %} within <script> tags).\n"
                "   - Example:\n"
                "     <script>\n"
                "       {% for item in items %}\n"
                "         console.log('{{ item }}');\n"
                "       {% endfor %}\n"
                "     </script>\n"
                "   - Keep JavaScript within designated blocks like {% block extra_js %} for clarity and maintainability.\n\n"
                
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