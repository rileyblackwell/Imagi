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
import time
from functools import wraps
import random
import traceback

# Load environment variables from .env
load_dotenv()
openai_key = os.getenv('OPENAI_KEY')
anthropic_key = os.getenv('ANTHROPIC_KEY')

openai_client = OpenAI(api_key=openai_key)
anthropic_client = anthropic.Anthropic(api_key=anthropic_key)

def retry_on_error(max_retries=3, initial_delay=1, max_delay=8, exponential_base=2):
    """
    Decorator that implements exponential backoff retry logic
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            
            for retry in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    error_str = str(e).lower()
                    
                    if 'overloaded' in error_str or '429' in error_str or '529' in error_str:
                        if retry < max_retries - 1:
                            jitter = random.uniform(0, 0.1 * delay)
                            sleep_time = min(delay + jitter, max_delay)
                            time.sleep(sleep_time)
                            delay *= exponential_base
                    else:
                        raise
            
            raise last_exception
        return wrapper
    return decorator

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
    
    # 3. Add file-specific history if page is provided
    if page:
        # Get all messages for this specific page and project
        all_messages = Message.objects.filter(
            conversation__project=page.conversation.project,  # Filter by project
            page=page
        ).order_by('created_at')
        
        # Separate chat and build messages
        chat_messages = [msg for msg in all_messages if msg.content.startswith('[Chat]')]
        build_messages = [msg for msg in all_messages if not msg.content.startswith('[Chat]')]
        
        # Add chat history section if there are chat messages
        if chat_messages:
            conversation_history.append({
                "role": "system",
                "content": f"\n=== CHAT HISTORY FOR {page.filename} ===\n"
            })
            
            for msg in chat_messages:
                conversation_history.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        # Add build history section if there are build messages
        if build_messages:
            conversation_history.append({
                "role": "system",
                "content": f"\n=== BUILD HISTORY FOR {page.filename} ===\n"
            })
            
            for msg in build_messages:
                content = msg.content
                if msg.role == "user" and not content.startswith("[File:"):
                    content = f"[File: {page.filename}]\n{content}"
                
                conversation_history.append({
                    "role": msg.role,
                    "content": content
                })
    
    # 4. Add current file context at the end
    if page:
        conversation_history.append({
            "role": "system",
            "content": f"\n=== CURRENT TASK ===\nYou are working on: {page.filename} in project: {page.conversation.project.name}"
        })
    
    return conversation_history

@retry_on_error(max_retries=3, initial_delay=1, max_delay=8)
def make_api_call(model, system_msg, conversation_history, page, user_input, complete_messages):
    print(f"\n=== make_api_call START ===")
    print(f"Model: {model}")
    print(f"Page: {page.filename}")
    
    try:
        if model == 'claude-3-5-sonnet-20241022':
            print("Using Claude 3.5 Sonnet model")
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
            
            print("Sending request to Claude API...")
            completion = anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2048,
                system=system_content,
                messages=messages
            )
            
            print("Claude API Response received")
            print(f"Response type: {type(completion)}")
            print(f"Response content type: {type(completion.content)}")
            
            if completion.content:
                response_text = completion.content[0].text
                print(f"Response text type: {type(response_text)}")
                return response_text
            raise ValueError("Empty response from Claude API")
                
        elif model in ['gpt-4o', 'gpt-4o-mini']:
            print(f"Using OpenAI model: {model}")
            print("Sending request to OpenAI API...")
            
            completion = openai_client.chat.completions.create(
                model=model,
                messages=complete_messages,
                temperature=0.7,
                max_tokens=2048
            )
            
            print("OpenAI API Response received")
            print(f"Response type: {type(completion)}")
            response = completion.choices[0].message.content
            print(f"Response content type: {type(response)}")
            return response
                
    except Exception as e:
        print(f"\n=== API Error Details ===")
        print(f"Error type: {type(e)}")
        print(f"Error message: {str(e)}")
        if 'completion' in locals():
            print(f"Response structure: {completion}")
        raise
        
    print("=== make_api_call END ===\n")

def process_user_input(user_input, model, conversation, page):
    """Processes user input for a specific page."""
    print(f"\n=== process_user_input START ===")
    print(f"Processing input for page: {page.filename}")
    print(f"Project: {conversation.project.name}")
    print(f"Model: {model}")
    print(f"Input length: {len(user_input)}")
    
    try:
        system_msg = get_system_message()
        base_dir = os.path.dirname(__file__)
        
        # Ensure we're using the project-specific directory
        output_dir = ensure_website_directory(
            os.path.join(base_dir, '..'), 
            conversation.project.id
        )
        print(f"Using project directory: {output_dir}")
        
        print("Building conversation history...")
        conversation_history = build_conversation_history(system_msg, page, output_dir)
        print(f"Conversation history length: {len(conversation_history)}")
        
        file_context = get_file_context(page.filename)
        complete_messages = [
            {"role": "system", "content": system_msg["content"]},
            *conversation_history,
            {"role": "system", "content": file_context},
            {"role": "user", "content": f"[File: {page.filename}]\n{user_input}"}
        ]
        
        print("Making API call...")
        assistant_response = make_api_call(
            model=model,
            system_msg=system_msg,
            conversation_history=conversation_history,
            page=page,
            user_input=user_input,
            complete_messages=complete_messages
        )
        
        print(f"API response received, type: {type(assistant_response)}")
        print(f"Response length: {len(str(assistant_response))}")

        if not assistant_response:
            raise ValueError("Empty response from AI service")

        # Process response based on file type
        if page.filename.endswith('.html'):
            print("Processing HTML response...")
            html_match = re.search(r'(?s)<!DOCTYPE html>.*?</html>', assistant_response)
            if html_match:
                assistant_response = html_match.group(0)
            else:
                raise ValueError("Response must be a complete HTML document")
                
            cleaned_response = test_html(assistant_response)
            if not cleaned_response:
                raise ValueError("Invalid HTML content")
                
        elif page.filename == 'styles.css':
            print("Processing CSS response...")
            cleaned_response = assistant_response.replace('```css', '').replace('```', '').strip()
            
            if '<!DOCTYPE' in cleaned_response or '<html' in cleaned_response:
                raise ValueError("Response contains HTML instead of CSS")
        else:
            cleaned_response = assistant_response

        # Save the file
        output_path = os.path.join(output_dir, page.filename)
        with open(output_path, 'w') as f:
            f.write(cleaned_response)
        print(f"File saved: {output_path}")

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
        print("Messages saved to database")

        if page.filename == 'styles.css':
            index_path = os.path.join(output_dir, 'index.html')
            try:
                with open(index_path, 'r') as f:
                    index_content = f.read()
                return {'html': index_content, 'css': cleaned_response}
            except FileNotFoundError:
                return {'html': '', 'css': cleaned_response}

        print("=== process_user_input END ===\n")
        return cleaned_response

    except Exception as e:
        print(f"\n=== Error in process_user_input ===")
        print(f"Error type: {type(e)}")
        print(f"Error message: {str(e)}")
        print(f"Error traceback: {traceback.format_exc()}")
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

def process_chat_input(user_input, model, conversation, conversation_history, file_name):
    """Processes chat input without generating website files."""
    try:
        print(f"\n=== process_chat_input START ===")
        print(f"Project: {conversation.project.name}")
        print(f"File: {file_name}")
        
        system_msg = get_system_message()
        base_dir = os.path.dirname(__file__)
        
        # Ensure we're using the project-specific directory
        output_dir = ensure_website_directory(
            os.path.join(base_dir, '..'), 
            conversation.project.id
        )
        
        # Get or create the page for this file
        page = Page.objects.get_or_create(
            conversation=conversation,
            filename=file_name
        )[0]
        
        # Build conversation history with project context
        conversation_history = build_conversation_history(system_msg, page, output_dir)
        
        try:
            if model == 'claude-3-5-sonnet-20241022':  # Updated model name
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
                
                # Simplified response handling
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
            print(f"API Error in process_chat_input: {str(e)}")
            raise ValueError(f"API error: {str(e)}")

    except Exception as e:
        print(f"Error in process_chat_input: {str(e)}")
        raise ValueError(str(e))
