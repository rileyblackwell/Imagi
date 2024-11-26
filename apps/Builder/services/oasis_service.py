# builder/services/oasis_service.py

import os
import re
from dotenv import load_dotenv
from openai import OpenAI
import anthropic
from ..models import Message, Conversation, Page
from .utils import (
    test_html, 
    get_system_message, 
    get_file_context,
    ensure_website_directory
)

# Load environment variables from .env
load_dotenv()
openai_key = os.getenv('OPENAI_KEY')
anthropic_key = os.getenv('ANTHROPIC_KEY')

openai_client = OpenAI(api_key=openai_key)
anthropic_client = anthropic.Anthropic(api_key=anthropic_key)

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

def make_api_call(model, system_msg, conversation_history, page, user_input, complete_messages):
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

def process_user_input(user_input, model, conversation, page):
    """Processes user input for a specific page."""
    try:
        system_msg = get_system_message()
        base_dir = os.path.dirname(__file__)
        output_dir = ensure_website_directory(
            os.path.join(base_dir, '..')
        )
        
        conversation_history = build_conversation_history(system_msg, page, output_dir)
        file_context = get_file_context(page.filename)
        
        complete_messages = [
            {"role": "system", "content": system_msg["content"]},
            *conversation_history,
            {"role": "system", "content": file_context},
            {"role": "user", "content": f"[File: {page.filename}]\n{user_input}"}
        ]
        
        assistant_response = make_api_call(
            model=model,
            system_msg=system_msg,
            conversation_history=conversation_history,
            page=page,
            user_input=user_input,
            complete_messages=complete_messages
        )

        if not assistant_response:
            raise ValueError("Empty response from AI service")

        # Process response based on file type
        if page.filename.endswith('.html'):
            html_match = re.search(r'(?s)<!DOCTYPE html>.*?</html>', assistant_response)
            if html_match:
                assistant_response = html_match.group(0)
            else:
                raise ValueError("Response must be a complete HTML document")
                
            cleaned_response = test_html(assistant_response)
            if not cleaned_response:
                raise ValueError("Invalid HTML content")
            
            # Ensure proper CSS linking
            if '<link rel="stylesheet" href="styles.css">' in cleaned_response:
                cleaned_response = cleaned_response.replace(
                    '<link rel="stylesheet" href="styles.css">',
                    '<link rel="stylesheet" href="/builder/oasis/styles.css">'
                )
                
        elif page.filename == 'styles.css':
            # Clean CSS content - remove any file prefix and only keep CSS content
            css_content = assistant_response
            if '[File: styles.css]' in css_content:
                css_content = css_content.split('[File: styles.css]')[1].strip()
            
            # Remove any markdown code block markers if present
            css_content = css_content.replace('```css', '').replace('```', '').strip()
            
            # Validate that it looks like CSS (basic check)
            if '{' not in css_content or '}' not in css_content:
                raise ValueError("Invalid CSS content")
                
            cleaned_response = css_content
        else:
            cleaned_response = assistant_response

        # Save the file
        output_path = os.path.join(output_dir, page.filename)
        with open(output_path, 'w') as f:
            f.write(cleaned_response)

        # Save messages
        Message.objects.create(
            conversation=conversation,
            page=page,
            role="user",
            content=user_input
        )

        Message.objects.create(
            conversation=conversation,
            page=page,
            role="assistant",
            content=cleaned_response
        )

        if page.filename == 'styles.css':
            index_path = os.path.join(output_dir, 'index.html')
            try:
                with open(index_path, 'r') as f:
                    index_content = f.read()
                return {'html': index_content, 'css': cleaned_response}
            except FileNotFoundError:
                return {'html': '', 'css': cleaned_response}

        return cleaned_response

    except Exception as e:
        raise ValueError(str(e))

def undo_last_action_service(user, page_name):
    """
    Service function to handle the business logic for undoing the last action.
    Returns a tuple of (content, message, status_code)
    """
    try:
        # Get the active conversation
        conversation = Conversation.objects.filter(
            user=user,
            project__isnull=False
        ).order_by('-created_at').first()
        
        if not conversation or not page_name:
            return None, 'Nothing to undo', 200
            
        # Try to get the page
        try:
            page = Page.objects.get(conversation=conversation, filename=page_name)
        except Page.DoesNotExist:
            return None, 'Nothing to undo', 200
        
        # Get previous content
        messages = Message.objects.filter(
            conversation=conversation,
            page=page,
            role='assistant'
        ).order_by('-created_at')
        
        if messages.count() < 2:
            return None, 'Nothing to undo', 200
        
        # Get the previous version (second most recent)
        previous_content = messages[1].content if messages.count() > 1 else ''
        
        if not previous_content:
            return None, 'Nothing to undo', 200
        
        # Delete the most recent version
        messages[0].delete()
        
        # Get the output directory and write the previous content to file
        output_dir = ensure_website_directory(os.path.dirname(os.path.dirname(__file__)))
        output_path = os.path.join(output_dir, page_name)
        
        with open(output_path, 'w') as f:
            f.write(previous_content)
        
        # For CSS files, we need to return the HTML content to re-render the page
        if page_name == 'styles.css':
            try:
                with open(os.path.join(output_dir, 'index.html'), 'r') as f:
                    html_content = f.read()
                return html_content, 'Previous version restored', 200
            except FileNotFoundError:
                return previous_content, 'Previous version restored', 200
        else:
            return previous_content, 'Previous version restored', 200
            
    except Exception as e:
        print(f"Error in undo_last_action_service: {str(e)}")
        return None, 'Nothing to undo', 200

def process_chat_input(user_input, model, conversation, conversation_history, file_name):
    """Processes chat input without generating website files."""
    try:
        system_msg = get_system_message()
        base_dir = os.path.dirname(__file__)
        output_dir = ensure_website_directory(
            os.path.join(base_dir, '..')
        )
        
        page = Page.objects.get_or_create(
            conversation=conversation,
            filename=file_name
        )[0]
        
        conversation_history = build_conversation_history(system_msg, page, output_dir)
        
        if model == 'claude-3-5-sonnet-20241022':
            system_content = (
                f"{system_msg['content']}\n\n"
                f"CURRENT TASK: You are in chat mode discussing {file_name}. "
                "Provide helpful responses about website development and design. "
                "You can reference the current content of the file and suggest improvements "
                "or explain concepts, but do not generate actual code updates.\n\n"
                f"CONTEXT: The conversation is about {file_name}"
            )
            
            messages = [msg for msg in conversation_history if msg["role"] != "system"]
            messages.append({
                "role": "user", 
                "content": f"[Chat][File: {file_name}]\n{user_input}"
            })
            
            completion = anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2048,
                system=system_content,
                messages=messages
            )
            
            if completion.content:
                response = completion.content[0].text
            else:
                raise ValueError("Empty response from Claude API")
            
        else:
            messages = [
                {"role": "system", "content": system_msg["content"]},
                {"role": "system", "content": f"You are discussing {file_name}"},
                *conversation_history,
                {"role": "user", "content": f"[Chat][File: {file_name}]\n{user_input}"}
            ]
            
            completion = openai_client.chat.completions.create(
                model=model,
                messages=messages
            )
            response = completion.choices[0].message.content

        # Save the chat messages to the conversation
        Message.objects.create(
            conversation=conversation,
            page=page,
            role="user",
            content=f"[Chat][File: {file_name}]\n{user_input}"
        )

        Message.objects.create(
            conversation=conversation,
            page=page,
            role="assistant",
            content=f"[Chat][File: {file_name}]\n{response}"
        )

        return response

    except Exception as e:
        raise ValueError(str(e))
