import os
from ..models import Message

def get_system_message():
    """Generates the system message content for the assistant."""
    return {
        "role": "system",
        "content": (
            "You are Imagi Oasis, an advanced Django web development tool designed to craft stunning, modern, and professional multi-page websites using Django templates. "
            "Your goal is to generate or edit one complete file at a time to produce cohesive, visually appealing Django websites. Adhere to the following instructions:\n\n"

            "### GENERAL RESTRICTIONS\n"
            "- DO NOT include any links (<a> tags) or images (<img> tags).\n"
            "- Avoid any references to URLs, {% url %} template tags, or routing between pages.\n"
            "- Focus on HTML structure, CSS styling, and text content to create attractive designs.\n\n"

            "### DJANGO TEMPLATE RULES\n"
            "1. **File Structure**:\n"
            "   - Every project must include `base.html` as the main layout file.\n"
            "   - All other templates must extend `base.html` using `{% extends 'base.html' %}`.\n"
            "   - Use Django template inheritance for consistency and reuse.\n"
            "   - Each template should define specific blocks (e.g., `{% block content %}`) to override content dynamically.\n\n"

            "2. **Template Tags and Filters**:\n"
            "   - Include `{% load static %}` at the top of every template.\n"
            "   - CSS must be linked EXACTLY as: <link rel=\"stylesheet\" href=\"{% static 'css/styles.css' %}\">\n"
            "   - CRITICAL: Do not escape quotes in static tags. Use single quotes inside {% static %} and double quotes for HTML attributes.\n"
            "   - WRONG: href=\"{% static \'css/styles.css\' %}\"  (escaped quotes)\n"
            "   - WRONG: href='{% static \"css/styles.css\" %}'   (wrong quote placement)\n"
            "   - CORRECT: href=\"{% static 'css/styles.css' %}\"  (unescaped, proper quotes)\n"
            "   - Use `{% block %}` tags to define and override content areas (e.g., `{% block title %}`).\n"
            "   - Do not use unnecessary tags like `{% url %}` or custom links.\n\n"

            "3. **Example of `base.html`**:\n"
            "   ```html\n"
            "   {% load static %}\n"
            "   <!DOCTYPE html>\n"
            "   <html lang=\"en\">\n"
            "   <head>\n"
            "       <meta charset=\"UTF-8\">\n"
            "       <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
            "       <title>{% block title %}Default Title{% endblock %}</title>\n"
            "       <link rel=\"stylesheet\" href=\"{% static 'css/styles.css' %}\">  <!-- EXACT format required -->\n"
            "       {% block extra_css %}{% endblock %}\n"
            "   </head>\n"
            "   <body>\n"
            "       <header>{% block header %}{% endblock %}</header>\n"
            "       <main>{% block content %}{% endblock %}</main>\n"
            "       <footer>{% block footer %}{% endblock %}</footer>\n"
            "       {% block extra_js %}{% endblock %}\n"
            "   </body>\n"
            "   </html>\n"
            "   ```\n\n"

            "### CSS STYLING RULES\n"
            "1. **Global Styling**:\n"
            "   - Use a single global `styles.css` file located in the `css/` directory.\n"
            "   - Link it in all templates as `{% static 'css/styles.css' %}`.\n\n"

            "2. **Structure and Consistency**:\n"
            "   - Organize CSS logically with the following structure:\n"
            "     ```css\n"
            "     :root { /* CSS Variables */ }\n"
            "     /* Base styles */\n"
            "     /* Layout styles */\n"
            "     /* Component styles */\n"
            "     /* Utility classes */\n"
            "     /* Media queries */\n"
            "     ```\n\n"

            "3. **Modern Design Practices**:\n"
            "   - Use flexbox and grid for layouts.\n"
            "   - Ensure responsive design using media queries.\n"
            "   - Include vendor prefixes for browser compatibility.\n"
            "   - Example:\n"
            "     ```css\n"
            "     :root {\n"
            "         --primary-color: #3498db;\n"
            "         --secondary-color: #2ecc71;\n"
            "         --text-color: #333;\n"
            "         --background-color: #fff;\n"
            "     }\n\n"
            "     body {\n"
            "         font-family: system-ui, -apple-system, sans-serif;\n"
            "         color: var(--text-color);\n"
            "         margin: 0;\n"
            "         line-height: 1.5;\n"
            "     }\n"
            "     ```\n\n"

            "### DESIGN PRINCIPLES\n"
            "- Create visually appealing layouts using HTML and CSS only.\n"
            "- Use typography, spacing, and colors to enhance designs.\n"
            "- Focus on responsive, mobile-first design.\n"
            "- Avoid explanatory comments or non-code content in responses.\n\n"

            "### OUTPUT REQUIREMENTS\n"
            "1. **Django HTML Templates**:\n"
            "   - Start with `{% extends 'base.html' %}` or `{% load static %}` as required.\n"
            "   - Return ONLY valid Django template code.\n"
            "   - Exclude any plain text, markdown, or explanations.\n\n"

            "2. **CSS Stylesheets**:\n"
            "   - Return ONLY valid CSS code.\n"
            "   - Do not include explanations or markdown.\n\n"

            "### FINAL NOTES\n"
            "- Focus on creating user-friendly, visually stunning designs without images or links.\n"
            "- Ensure all files adhere to modern web standards and work seamlessly together."
        )
    }

def get_file_context(filename):
    """Generates the file-specific context message."""
    return f"You are working on file: {filename}"

def build_conversation_history(system_msg, page, project_path):
    """Builds the conversation history with organized sections."""
    conversation_history = []
    
    # 1. Add system message first
    conversation_history.append({
        "role": "system",
        "content": "=== SYSTEM PROMPT ===\n" + system_msg["content"]
    })
    
    # 2. Add current state of ALL files for this specific project
    templates_dir = os.path.join(project_path, 'templates')
    css_dir = os.path.join(project_path, 'static', 'css')
    
    # First add all HTML files
    if os.path.exists(templates_dir):
        html_files = [f for f in os.listdir(templates_dir) if f.endswith('.html')]
        html_files.sort()
        
        # Ensure base.html is first, followed by index.html
        if 'base.html' in html_files:
            html_files.remove('base.html')
            html_files.insert(0, 'base.html')
        if 'index.html' in html_files:
            html_files.remove('index.html')
            html_files.insert(1 if 'base.html' in html_files else 0, 'index.html')
        
        for filename in html_files:
            file_path = os.path.join(templates_dir, filename)
            try:
                with open(file_path, 'r') as f:
                    file_content = f.read()
                    conversation_history.append({
                        "role": "assistant",
                        "content": f"[File: {filename}]\n{file_content}"
                    })
            except FileNotFoundError:
                continue
    
    # Add CSS file if it exists
    css_path = os.path.join(css_dir, 'styles.css')
    if os.path.exists(css_path):
        try:
            with open(css_path, 'r') as f:
                css_content = f.read()
                conversation_history.append({
                    "role": "assistant",
                    "content": f"[File: styles.css]\n{css_content}"
                })
        except FileNotFoundError:
            pass
    
    # Add chat and build history
    if page:
        # Add chat history
        chat_messages = Message.objects.filter(
            conversation__project=page.conversation.project,
            page=page,
            content__startswith='[Chat]'
        ).order_by('created_at')
        
        if chat_messages.exists():
            conversation_history.append({
                "role": "system",
                "content": f"\n=== CHAT HISTORY FOR {page.filename} ===\n"
            })
            
            seen_content = set()
            for msg in chat_messages:
                content_hash = hash(msg.content)
                if content_hash not in seen_content:
                    conversation_history.append({
                        "role": msg.role,
                        "content": msg.content
                    })
                    seen_content.add(content_hash)
        
        # Add build history
        build_messages = Message.objects.filter(
            conversation__project=page.conversation.project,
            page=page
        ).exclude(
            content__startswith='[Chat]'
        ).order_by('created_at')
        
        if build_messages.exists():
            conversation_history.append({
                "role": "system",
                "content": f"\n=== BUILD HISTORY FOR {page.filename} ===\n"
            })
            
            seen_content = set()
            for msg in build_messages:
                content = msg.content
                if msg.role == "user" and not content.startswith("[File:"):
                    content = f"[File: {page.filename}]\n{content}"
                
                content_hash = hash(content)
                if content_hash not in seen_content:
                    conversation_history.append({
                        "role": msg.role,
                        "content": content
                    })
                    seen_content.add(content_hash)
    
    # Add current task context at the end
    if page:
        conversation_history.append({
            "role": "system",
            "content": (
                f"\n=== CURRENT TASK ===\n"
                f"You are working on: {page.filename}\n"
                f"Project: {page.conversation.project.name}\n"
                f"Remember to follow all formatting rules and return only valid code."
            )
        })
    
    return conversation_history

def make_api_call(model, system_msg, conversation_history, page, user_input, complete_messages, openai_client, anthropic_client):
    try:
        if model == 'claude-3-5-sonnet-20241022':
            system_content = (
                f"{system_msg['content']}\n\n"
                f"CURRENT TASK: You are editing {page.filename}\n\n"
                f"IMPORTANT: Return only the complete, valid file content for {page.filename}."
            )
            
            # Filter out empty messages and system messages
            messages = [
                msg for msg in conversation_history 
                if msg["role"] != "system" and msg.get("content", "").strip()
            ]
            
            # Add the current user input if not empty
            if user_input.strip():
                messages.append({
                    "role": "user",
                    "content": f"[File: {page.filename}]\n{user_input}"
                })
            else:
                raise ValueError("User input cannot be empty")
            
            completion = anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2048,
                system=system_content,
                messages=messages
            )
            
            if completion.content:
                return completion.content[0].text
            raise ValueError("Empty response from Claude API")
                
        elif model in ['gpt-4o', 'gpt-4o-mini']:
            # Build complete messages array if not provided
            if not complete_messages:
                complete_messages = [
                    {"role": "system", "content": system_msg["content"]},
                    *conversation_history,
                    {"role": "system", "content": f"You are working on file: {page.filename}"},
                    {"role": "user", "content": f"[File: {page.filename}]\n{user_input}"}
                ]
            
            # Ensure we have at least one message
            if not complete_messages:
                complete_messages = [{
                    "role": "system",
                    "content": system_msg["content"]
                }]
            
            print("Sending messages to OpenAI:", complete_messages)  # Debug print
            
            completion = openai_client.chat.completions.create(
                model=model,
                messages=complete_messages,
                temperature=0.7,
                max_tokens=2048
            )
            
            return completion.choices[0].message.content
        
        else:
            raise ValueError(f"Unsupported model: {model}. Supported models are: claude-3-5-sonnet-20241022, gpt-4o, gpt-4o-mini")
            
    except Exception as e:
        print(f"Error in make_api_call: {str(e)}")  # Debug print
        raise Exception(f"Error code: {getattr(e, 'status_code', 'unknown')} - {str(e)}")

 