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
    """Builds the conversation history with the complete website context.
    
    Structure:
    1. Current state of all HTML and CSS files
    2. Conversation history for the current file
    """
    conversation_history = []
    
    # 1. Add current state of ALL files
    if os.path.exists(output_dir):
        # First add all HTML files
        html_files = [f for f in os.listdir(output_dir) if f.endswith('.html')]
        html_files.sort()
        
        # Ensure index.html is first
        if 'index.html' in html_files:
            html_files.remove('index.html')
            html_files.insert(0, 'index.html')
        
        # Add all HTML files (including the current one)
        for filename in html_files:
            file_path = os.path.join(output_dir, filename)
            try:
                with open(file_path, 'r') as f:
                    file_content = f.read()
                    conversation_history.append({
                        "role": "assistant",
                        "content": f"[File: {filename}]\nCurrent HTML content:\n{file_content}"
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
                        "content": f"[File: styles.css]\nCurrent CSS content:\n{css_content}"
                    })
            except FileNotFoundError:
                pass
    
    # 2. Add conversation history for the current file
    current_file_messages = page.messages.all().order_by('created_at')
    for msg in current_file_messages:
        # Ensure all messages are properly tagged with the file context
        content = msg.content
        if msg.role == "user" and not content.startswith("[File:"):
            content = f"[File: {page.filename}]\n{content}"
        
        conversation_history.append({
            "role": msg.role,
            "content": content
        })
    
    return conversation_history


def process_user_input(user_input, model, conversation, page):
    """Processes user input for a specific page."""
    try:
        # Get system message
        system_msg = get_system_message()
        
        # Set up output directory - ensure it exists
        base_dir = os.path.dirname(__file__)
        output_dir = ensure_website_directory(os.path.join(base_dir, '..'))
        
        # Build conversation history - this should only read files, never delete them
        conversation_history = build_conversation_history(system_msg, page, output_dir)
        
        # Add the current file context
        file_context = get_file_context(page.filename)
        
        # Create the complete messages array with proper structure
        complete_messages = [
            # 1. System prompt
            {"role": "system", "content": system_msg["content"]},
            
            # 2. Current state of all website files (from conversation_history)
            *conversation_history,
            
            # 3. File context (which file we're editing)
            {"role": "system", "content": file_context},
            
            # 4. Current user request
            {"role": "user", "content": f"[File: {page.filename}]\n{user_input}"}
        ]

        # Store the full conversation for logging
        full_conversation = {
            "model": model,
            "messages": complete_messages,
            "system": system_msg["content"]
        }

        try:
            if model == 'claude-sonnet':
                # For Claude, we'll use the same structure but format slightly differently
                system_content = (
                    f"{system_msg['content']}\n\n"
                    f"CURRENT TASK: You are editing {page.filename}\n\n"
                    f"IMPORTANT: Return only the complete, valid file content for {page.filename}."
                )
                
                # Use the same messages as GPT, but exclude the system messages from the messages array
                claude_messages = [
                    msg for msg in complete_messages[1:]  # Skip the first system message
                    if msg["role"] != "system"  # Skip any other system messages
                ]
                
                completion = anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=2048,
                    system=system_content,
                    messages=claude_messages
                )
                assistant_response = completion.content[0].text
            else:
                # For OpenAI, use the complete messages array as is
                completion = openai_client.chat.completions.create(
                    model=model,
                    messages=complete_messages
                )
                assistant_response = completion.choices[0].message.content

        except Exception as e:
            raise ValueError(f"API error: {str(e)}")

        # Validate and clean the response based on file type
        if page.filename.endswith('.html'):
            # For vague requests, try to get the existing file content first
            if user_input.lower().strip() in ['update this webpage', 'update webpage', 'update this page', 'update page']:
                try:
                    with open(os.path.join(output_dir, page.filename), 'r') as f:
                        existing_content = f.read()
                        if existing_content and '<!DOCTYPE html>' in existing_content:
                            assistant_response = existing_content
                except FileNotFoundError:
                    pass

            # For HTML files, first try to extract HTML content if it's wrapped in other text
            html_match = re.search(r'(?s)<!DOCTYPE html>.*?</html>', assistant_response)
            if html_match:
                assistant_response = html_match.group(0)
            else:
                print("Error: Response does not contain a complete HTML document")
                print("Response received:", assistant_response)
                raise ValueError(
                    "Response must be a complete HTML document starting with <!DOCTYPE html> "
                    "and containing all required tags (<html>, <head>, <meta>, <title>, <link>, <body>)"
                )
            
            # Then validate the HTML content
            cleaned_response = test_html(assistant_response)
            if not cleaned_response:
                print("Error: HTML validation failed")
                print("HTML content:", assistant_response)
                raise ValueError(
                    "Invalid HTML content. Response must be a complete HTML document "
                    "with all required tags and proper structure."
                )
                
        elif page.filename == 'styles.css':
            # For CSS files, just remove any markdown code block indicators if present
            cleaned_response = assistant_response.replace('```css', '').replace('```', '').strip()
            
            # Basic check to ensure we're not getting HTML or other content
            if '<!DOCTYPE' in cleaned_response or '<html' in cleaned_response:
                raise ValueError("Response contains HTML instead of CSS")
        else:
            cleaned_response = assistant_response

        # Add debug print for successful validation
        print(f"Successfully validated {page.filename}")
        print(f"First 200 chars of cleaned response: {cleaned_response[:200]}...")

        # Save only the current file being edited
        output_path = os.path.join(output_dir, page.filename)
        with open(output_path, 'w') as f:
            f.write(cleaned_response)

        # Save the conversation
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

        # For CSS updates, also return the current index.html content
        if page.filename == 'styles.css':
            index_path = os.path.join(output_dir, 'index.html')
            try:
                with open(index_path, 'r') as f:
                    index_content = f.read()
                return {
                    'html': index_content, 
                    'css': cleaned_response,
                    'conversation_history': full_conversation
                }
            except FileNotFoundError:
                return {
                    'html': '', 
                    'css': cleaned_response,
                    'conversation_history': full_conversation
                }

        return {
            'html': cleaned_response,
            'conversation_history': full_conversation
        }

    except Exception as e:
        print(f"Error in process_user_input: {str(e)}")
        raise ValueError(str(e))


def undo_last_action(conversation, page):
    """Removes the last user-assistant exchange from the specific page."""
    messages = page.messages.order_by('-created_at')
    total_messages = messages.count()

    if total_messages >= 2:
        # Get the previous content (before the last change)
        previous_content = messages[2].content if total_messages > 2 else ''
        
        # Delete only the last exchange (last two messages)
        latest_two = messages[:2]
        Message.objects.filter(id__in=[msg.id for msg in latest_two]).delete()

        # For styles.css, we need to ensure we return valid CSS
        if page.filename == 'styles.css':
            # Just return the previous content without validation
            if not previous_content:
                # If no previous CSS exists, return empty string but don't delete file
                return '', 'No previous CSS version available.'
        else:
            previous_content = test_html(previous_content) if previous_content else ''

        return previous_content, 'Last action undone successfully.'
    else:
        # Don't delete all messages for styles.css when there's not enough history
        if page.filename == 'styles.css':
            return '', 'Not enough history to undo last action.'
        else:
            messages.all().delete()
            return '', 'Not enough history to undo last action; page history cleared.'
