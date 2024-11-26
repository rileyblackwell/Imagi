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
            "You are Imagi Oasis, an advanced web development tool built to craft stunning, modern, and professional multi-page websites from natural language descriptions. "
            "Your purpose is to produce cohesive, visually attractive websites by generating or editing one complete file at a time, such as an HTML or CSS file.\n\n"
            
            "Your task is to generate fully functional HTML files and maintain a global styles.css file that provides consistent styling across the entire website. "
            "All HTML files must be linked to each other and the shared global stylesheet to ensure a unified design.\n\n"

            "1. Rules for Editing Files (HTML or CSS):\n"
            "- Always return the complete updated file (HTML or CSS).\n"
            "- For HTML, include <!DOCTYPE html> and all required tags: <html>, <head>, <meta>, <title>, <link>, <body>.\n"
            "- Make requested changes (e.g., add a contact form, modify a color) and ensure they integrate seamlessly.\n"
            "- Preserve existing content unless explicitly instructed to remove it.\n"
            "- Ensure proper formatting, structure, and valid syntax.\n"
            "- Return only the file content without explanations or markdown.\n"
            "- Do not include images in the generated content, as images are not supported right now.\n\n"

            "2. File Consistency:\n"
            "- Do not provide partial updates; always generate the complete file.\n"
            "- If other files exist in the conversation history, treat them as the most recent version and ensure designs and styles are consistent across all webpages.\n"
            "- Incorporate relevant information from other files to maintain a cohesive and unified design.\n\n"

            "3. Design Standards:\n"
            "- Create visually beautiful, attractive, and professional websites.\n"
            "- Draw inspiration from leading companies like Stripe, Airbnb, Twilio, Apple, and OpenAI.\n"
            "- Prioritize creating the best websites and designs possible, focusing on elegance, clarity, and responsiveness.\n\n"

            "4. CSS Specific Requirements:\n"
            "- Group related styles together for better organization.\n"
            "- Use CSS variables in :root {} for consistent theming.\n\n"

            "5. Message Format:\n"
            "Each message includes a [File: filename] prefix indicating which file is being modified.\n\n"

            "Examples:\n"
            "1. Creating index.html - Return complete HTML:\n"
            "<!DOCTYPE html>\n"
            "<html>\n"
            "<head>\n"
            "    <meta charset='UTF-8'>\n"
            "    <meta name='viewport' content='width=device-width, initial-scale=1.0'>\n"
            "    <title>Page Title</title>\n"
            "    <link rel='stylesheet' href='styles.css'>\n"
            "</head>\n"
            "<body>\n"
            "    <!-- Content here -->\n"
            "</body>\n"
            "</html>\n\n"

            "2. Creating styles.css - Return complete CSS:\n"
            "/* Global Variables */\n"
            ":root {\n"
            "    --primary-color: #3498db;\n"
            "}\n\n"
            "/* Base Styles */\n"
            "body {\n"
            "    font-family: 'Open Sans', sans-serif;\n"
            "    color: #333;\n"
            "}\n\n"
        )
    }

def get_file_context(filename):
    """Generates the file-specific context message."""
    return f"You are working on file: {filename}"

def ensure_website_directory(base_dir):
    """
    Ensures the website directory exists and returns its path.
    
    Args:
        base_dir (str): The base directory path where the website directory should be created
        
    Returns:
        str: The path to the website directory
    """
    # Create website directory directly under base_dir
    output_dir = os.path.join(base_dir, 'website')
    
    # Create the directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    return output_dir

def build_conversation_history(system_msg, page, output_dir):
    """Builds the conversation history with organized sections."""
    conversation_history = []
    
    # 1. Add system message first
    conversation_history.append({
        "role": "system",
        "content": "=== SYSTEM PROMPT ===\n" + system_msg["content"]
    })
    
    # 2. Add current state of ALL files for this specific project
    if output_dir and os.path.exists(output_dir):
        conversation_history.append({
            "role": "system",
            "content": "\n=== CURRENT WEBSITE FILES ===\n"
        })
        
        # First add all HTML files
        html_files = [f for f in os.listdir(output_dir) if f.endswith('.html')]
        html_files.sort()
        
        # Ensure index.html is first
        if 'index.html' in html_files:
            html_files.remove('index.html')
            html_files.insert(0, 'index.html')
        
        # Add all HTML files
        for filename in html_files:
            file_path = os.path.join(output_dir, filename)
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
        css_path = os.path.join(output_dir, 'styles.css')
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
    
    # 3. Add chat history for this specific page
    if page:
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
            
            # Track seen content to avoid duplicates
            seen_content = set()
            
            for msg in chat_messages:
                content = msg.content
                content_hash = hash(content)
                if content_hash not in seen_content:
                    conversation_history.append({
                        "role": msg.role,
                        "content": content
                    })
                    seen_content.add(content_hash)
    
    # 4. Add file-specific build history if page is provided
    if page:
        # Get all messages for this specific page, excluding chat messages
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
            
            # Track seen content to avoid duplicates
            seen_content = set()
            
            for msg in build_messages:
                content = msg.content
                # For user messages, ensure they have the file prefix
                if msg.role == "user" and not content.startswith("[File:"):
                    content = f"[File: {page.filename}]\n{content}"
                
                # Only add if we haven't seen this exact content before
                content_hash = hash(content)
                if content_hash not in seen_content:
                    conversation_history.append({
                        "role": msg.role,
                        "content": content
                    })
                    seen_content.add(content_hash)
    
    # 5. Add current file context at the end
    if page:
        conversation_history.append({
            "role": "system",
            "content": f"\n=== CURRENT TASK ===\nYou are working on: {page.filename} in project: {page.conversation.project.name}"
        })
    
    return conversation_history

def make_api_call(model, system_msg, conversation_history, page, user_input, complete_messages, openai_client, anthropic_client):
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
        completion = openai_client.chat.completions.create(
            model=model,
            messages=complete_messages,
            temperature=0.7,
            max_tokens=2048
        )
        
        return completion.choices[0].message.content
    
    else:
        raise ValueError(f"Unsupported model: {model}. Supported models are: claude-3-5-sonnet-20241022, gpt-4o, gpt-4o-mini")

 