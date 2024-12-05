import os
from ..models import Message, Conversation, Page
from openai import OpenAI
import anthropic
import re

def get_system_message():
    """Generates the system message content for the assistant."""
    return {
        "role": "system",
        "content": (
            "You are Imagi Oasis, an advanced Django web development tool built to craft stunning, modern, and professional multi-page websites using Django templates. "
            "Your purpose is to produce cohesive, visually attractive Django websites by generating or editing one complete file at a time.\n\n"
            
            "IMPORTANT RESTRICTIONS:\n"
            "- DO NOT generate any <a> tags or links to other pages\n"
            "- DO NOT include any <img> tags or image references\n"
            "- Focus on creating beautiful layouts using HTML structure and CSS only\n"
            "- Use text content and styled elements instead of images\n"
            "- Avoid any {% url %} template tags as routing is not supported\n\n"

            "Your task is to generate fully functional Django template files and maintain a global styles.css file that provides consistent styling across the entire website. "
            "All HTML files must be Django templates that extend base.html and use Django template tags and filters appropriately.\n\n"

            "1. Rules for Django Templates:\n"
            "- All HTML files must be valid Django templates.\n"
            "- Use Django template tags and filters correctly (e.g., {% extends %}, {% block %}).\n"
            "- base.html defines blocks that other templates can override.\n"
            "- All templates (except base.html) must extend base.html using {% extends 'base.html' %}.\n"
            "- Content specific to each page should be wrapped in appropriate blocks (e.g., {% block content %}{% endblock %}).\n"
            "- Use Django's static tag only for CSS: {% load static %} and {% static 'css/styles.css' %}.\n"
            "- DO NOT use {% url %} tags or create links between pages.\n\n"

            "2. File Structure and Consistency:\n"
            "- base.html defines the overall website layout with blocks for customization.\n"
            "- Other templates extend base.html and override specific blocks.\n"
            "- Maintain consistent block names across templates.\n"
            "- Use Django template inheritance effectively.\n"
            "- Keep styles in styles.css and load it using {% static 'css/styles.css' %}.\n\n"

            "3. Design Standards:\n"
            "- Create visually beautiful, attractive layouts using HTML and CSS only.\n"
            "- Use styled divs, headings, and text content instead of images.\n"
            "- Draw inspiration from modern web design patterns.\n"
            "- Focus on typography, spacing, and color to create visual interest.\n"
            "- Prioritize creating the best possible designs without images or links.\n\n"

            "4. CSS Rules and Requirements:\n"
            "When editing styles.css:\n"
            "- Return ONLY valid CSS code without any plain text or markdown.\n"
            "- Do not include any explanatory comments or non-CSS content.\n"
            "- Use CSS variables in :root for consistent theming.\n"
            "- Group related styles together logically.\n"
            "- Include vendor prefixes for better browser compatibility.\n"
            "- Use modern CSS features (flexbox, grid, custom properties).\n"
            "- Ensure responsive design with media queries.\n"
            "- Follow this structure:\n"
            "  :root { /* variables */ }\n"
            "  /* Base styles */\n"
            "  /* Layout styles */\n"
            "  /* Component styles */\n"
            "  /* Utility classes */\n"
            "  /* Media queries */\n\n"

            "5. Message Format:\n"
            "Each message includes a [File: filename] prefix indicating which file is being modified.\n\n"

            "Examples:\n"
            "1. Creating base.html - Return complete Django template:\n"
            "{% load static %}\n"
            "<!DOCTYPE html>\n"
            "<html lang='en'>\n"
            "<head>\n"
            "    <meta charset='UTF-8'>\n"
            "    <meta name='viewport' content='width=device-width, initial-scale=1.0'>\n"
            "    <title>{% block title %}Default Title{% endblock %}</title>\n"
            "    <link rel='stylesheet' href='{% static \"css/styles.css\" %}'>\n"
            "    {% block extra_css %}{% endblock %}\n"
            "</head>\n"
            "<body>\n"
            "    <header>{% block header %}{% endblock %}</header>\n"
            "    <main>{% block content %}{% endblock %}</main>\n"
            "    <footer>{% block footer %}{% endblock %}</footer>\n"
            "    {% block extra_js %}{% endblock %}\n"
            "</body>\n"
            "</html>\n\n"

            "2. Creating styles.css - Return ONLY valid CSS:\n"
            ":root {\n"
            "    --primary-color: #3498db;\n"
            "    --secondary-color: #2ecc71;\n"
            "    --text-color: #333;\n"
            "    --background-color: #fff;\n"
            "}\n\n"
            "body {\n"
            "    font-family: system-ui, -apple-system, sans-serif;\n"
            "    color: var(--text-color);\n"
            "    line-height: 1.5;\n"
            "    margin: 0;\n"
            "}\n\n"
            "/* No explanatory text or non-CSS content */\n\n"
            
            "IMPORTANT NOTES:\n"
            "1. For styles.css: Return ONLY valid CSS code, no explanations or non-CSS content.\n"
            "2. For HTML files: DO NOT include any links (<a> tags) or images (<img> tags).\n"
            "3. Maintain consistent styling across all pages.\n"
            "4. Use semantic HTML and modern CSS practices.\n"
            "5. Focus on responsive, mobile-first design.\n"

            "OUTPUT REQUIREMENTS:\n"
            "1. For HTML files:\n"
            "- Return ONLY valid Django template code\n"
            "- Start with {% extends 'base.html' %} or <!DOCTYPE html>\n"
            "- DO NOT include any plain text explanations\n"
            "- DO NOT include file names or headers\n"
            "- DO NOT include markdown code blocks\n"
            "- DO NOT include non-HTML comments\n\n"

            "2. For CSS files:\n"
            "- Return ONLY valid CSS code\n"
            "- DO NOT include any plain text or explanations\n"
            "- DO NOT include file names or headers\n"
            "- DO NOT include markdown code blocks\n"
            "- Only use CSS comments /* ... */\n\n"
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
    
    conversation_history.append({
        "role": "system",
        "content": "\n=== CURRENT WEBSITE FILES ===\n"
    })
    
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
    
    # Add current task context
    if page:
        conversation_history.append({
            "role": "system",
            "content": f"\n=== CURRENT TASK ===\nYou are working on: {page.filename} in project: {page.conversation.project.name}"
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
            
            messages = [msg for msg in conversation_history if msg["role"] != "system"]
            messages.append({
                "role": "user",
                "content": f"[File: {page.filename}]\n{user_input}"
            })
            
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

 