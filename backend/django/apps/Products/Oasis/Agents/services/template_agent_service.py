from dotenv import load_dotenv
import re
from .agent_service import BaseAgentService

# Load environment variables from .env
load_dotenv()

class TemplateAgentService(BaseAgentService):
    """Specialized agent service for Django template generation."""
    
    def __init__(self):
        super().__init__()
        self.current_template_name = None

    def get_system_prompt(self):
        """Get the optimized system prompt for Django template generation."""
        return {
            "role": "system",
            "content": (
                "You are an expert web designer specializing in creating professional, sleek, and visually stunning Django HTML templates. "
                "You work iteratively with users to create templates that meet their specific requirements. "
                "The tool you are supporting is called Imagi Oasis, a cutting-edge platform that translates user input into Django HTML template code.\n\n"
                
                "Your responsibilities:\n"
                "1. Generate **only complete Django HTML templates** in response to user messages.\n"
                "2. Never include plain text, explanations, non-Django HTML comments, links (e.g., <a> tags), or images (e.g., <img> tags) in your responses.\n"
                "3. Work interactively with the user by interpreting their natural language messages to refine templates and meet their needs.\n\n"
                
                "Key requirements for template generation:\n"
                "1. **TEMPLATE STRUCTURE**:\n"
                "   - For non-base templates, ALWAYS start with {% extends 'base.html' %} as the FIRST line.\n"
                "   - Then include {% load static %} as the SECOND line (never before extends).\n"
                "   - Use the stylesheet located at `static/css/styles.css` by linking it within {% block extra_css %}.\n"
                "   - Define content within Django blocks: 'title', 'content', 'extra_css', and 'extra_js'.\n\n"
                
                "2. **CONTENT RULES**:\n"
                "   - Provide only valid, renderable Django HTML templates.\n"
                "   - Use {% static %} for referencing static assets (e.g., {% static 'css/styles.css' %}).\n"
                "   - Dynamically include content using Django template tags (e.g., {{ variable }}).\n"
                "   - Do not include any links (<a> tags) or images (<img> tags) in the templates, as they are not currently supported.\n\n"
                
                "3. **DESIGN PRINCIPLES**:\n"
                "   - Follow modern design trends inspired by companies like Stripe, AirBnB, Apple, and Google.\n"
                "   - Use minimalist, accessible, and semantic HTML5 structures.\n"
                "   - Ensure all class names are consistent and intuitive for CSS styling.\n\n"
                
                "4. **RESPONSIVE DESIGN**:\n"
                "   - Use a mobile-first approach with responsive layouts (e.g., flexbox, grid).\n"
                "   - Include <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"> for responsive scaling.\n"
                "   - Ensure all elements adapt elegantly to various screen sizes.\n\n"
                
                "5. **OUTPUT REQUIREMENTS**:\n"
                "   - Maintain consistent 2-space indentation for readability.\n"
                "   - Provide only the complete HTML template without additional comments or explanations.\n\n"
                
                "6. **DYNAMIC CONTENT & JAVASCRIPT**:\n"
                "   - Use Django template tags within JavaScript blocks when applicable, wrapped inside {% block extra_js %}.\n"
                "   - Example:\n"
                "     <script>\n"
                "       {% for item in items %}\n"
                "         console.log('{{ item }}');\n"
                "       {% endfor %}\n"
                "     </script>\n\n"
                
                "EXAMPLE TEMPLATE:\n"
                "{% extends 'base.html' %}\n"
                "{% load static %}\n\n"
                "{% block title %}Welcome to Imagi Oasis{% endblock %}\n\n"
                "{% block content %}\n"
                "  <div class=\"hero-section\">\n"
                "    <h1>Transform Your Ideas Into Reality</h1>\n"
                "    <p>Build world-class web apps effortlessly with Imagi Oasis.</p>\n"
                "    <button class=\"cta-button\">Start Now</button>\n"
                "  </div>\n"
                "{% endblock %}\n\n"
                "{% block extra_css %}\n"
                "  <link rel=\"stylesheet\" href=\"{% static 'css/styles.css' %}\">\n"
                "{% endblock %}\n\n"
                "{% block extra_js %}\n"
                "  <script>\n"
                "    console.log('Welcome to Imagi Oasis!');\n"
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
    
    def fix_template_issues(self, content, template_name):
        """Fix common template issues and ensure proper tag order."""
        # Add missing DOCTYPE and basic HTML structure for base.html
        if template_name == 'base.html' and '<!DOCTYPE html>' not in content:
            return (
                "<!DOCTYPE html>\n"
                '<html lang="en">\n'
                "<head>\n"
                '    <meta charset="UTF-8">\n'
                '    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
                "    <title>{% block title %}{% endblock %}</title>\n"
                "    {% load static %}\n"
                "    {% block extra_css %}{% endblock %}\n"
                "</head>\n"
                "<body>\n"
                "    {% block content %}{% endblock %}\n"
                "    {% block extra_js %}{% endblock %}\n"
                "</body>\n"
                "</html>"
            )
        
        # For non-base templates, ensure proper tag order
        if template_name != 'base.html':
            # Remove existing tags
            content = re.sub(r'{%\s*extends.*?%}', '', content)
            content = re.sub(r'{%\s*load\s+static\s*%}', '', content)
            
            # Add tags in correct order (extends must come first)
            content = (
                "{% extends 'base.html' %}\n"
                "{% load static %}\n\n"
            ) + content.lstrip()
            
            # If somehow load static got added before extends, fix it
            if re.search(r'{%\s*load\s+static\s*%}\s*{%\s*extends', content):
                content = re.sub(
                    r'{%\s*load\s+static\s*%}\s*({%\s*extends.*?%})',
                    r'\1\n{% load static %}',
                    content
                )
        
        return content

    def validate_response(self, content):
        """
        Validate Django template syntax and structure.
        Returns (is_valid, error_message)
        """
        # Get the current template name
        template_name = self.current_template_name
        
        # Define checks based on template type
        if template_name == 'base.html':
            checks = [
                (r"{%\s*load\s+static\s*%}", "Missing {% load static %} tag"),
                (r"<!DOCTYPE\s+html>", "Missing DOCTYPE declaration"),
                (r"<html.*?>", "Missing <html> tag"),
                (r"<head>.*?</head>", "Missing <head> section", re.DOTALL),
                (r"<body>.*?</body>", "Missing <body> section", re.DOTALL),
                (r'<meta\s+name="viewport"', "Missing viewport meta tag"),
            ]
        else:
            # For non-base templates, first check if extends comes before load static
            if re.search(r'{%\s*load\s+static\s*%}\s*{%\s*extends', content):
                return False, "{% extends 'base.html' %} must come before {% load static %}"
            
            # Then check for the presence of both tags
            checks = [
                (r"{%\s*extends\s+'base\.html'\s*%}", "Missing {% extends 'base.html' %} tag"),
                (r"{%\s*load\s+static\s*%}", "Missing {% load static %} tag"),
            ]
        
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

    def process_conversation(self, user_input, model, user, **kwargs):
        """Process a conversation with the template agent."""
        # Store the current template name
        self.current_template_name = kwargs.get('template_name')
        
        # Get the response from the parent class
        result = super().process_conversation(user_input, model, user, **kwargs)
        
        if result.get('success'):
            # Fix any template issues
            fixed_content = self.fix_template_issues(result['response'], self.current_template_name)
            
            # Validate the fixed content
            is_valid, error_msg = self.validate_response(fixed_content)
            
            if is_valid:
                result['response'] = fixed_content
            else:
                result['success'] = False
                result['error'] = error_msg
                result['original_response'] = result['response']
                result['response'] = fixed_content
        
        return result