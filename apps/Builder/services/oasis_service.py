# builder/services/oasis_service.py

import os
import re
from dotenv import load_dotenv
from openai import OpenAI
import anthropic
from ..models import Message, Conversation, Page
from .utils import (
    get_system_message, 
    get_file_context,
    build_conversation_history,
    make_api_call
)
from apps.ProjectManager.services import DevServerManager

# Load environment variables from .env
load_dotenv()
openai_key = os.getenv('OPENAI_KEY')
anthropic_key = os.getenv('ANTHROPIC_KEY')

openai_client = OpenAI(api_key=openai_key)
anthropic_client = anthropic.Anthropic(api_key=anthropic_key)

def get_active_conversation(user):
    """Retrieve the active conversation for the user."""
    conversation = Conversation.objects.filter(
        user=user,
        project__isnull=False
    ).select_related('project').order_by('-project__updated_at').first()
    
    if not conversation:
        raise ValueError('No active project found. Please select or create a project first.')
    
    return conversation

def clean_response(page_filename, assistant_response):
    """Cleans the assistant response based on the file type."""
    try:
        # Remove any markdown code block markers
        content = assistant_response.replace('```html', '').replace('```css', '').replace('```', '').strip()
        
        # Remove any file headers/names that might be present
        if '[File:' in content:
            content = re.sub(r'\[File:.*?\]', '', content, flags=re.MULTILINE).strip()
            
        # Remove any non-code text at the start of the file
        if page_filename.endswith('.html'):
            # Find the start of actual HTML content
            html_start = content.find('{% extends') if '{% extends' in content else content.find('<!DOCTYPE')
            if html_start == -1:
                raise ValueError("Response must start with {% extends %} or <!DOCTYPE html>")
            content = content[html_start:].strip()
            
            # Validate Django template
            if not ('{% extends' in content or '<!DOCTYPE html>' in content):
                raise ValueError("Response must be a complete Django template")
                
            # Ensure {% load static %} is present if needed
            if '{% static' in content and '{% load static %}' not in content:
                if '{% extends' in content:
                    # Add after extends tag
                    extends_end = content.find('%}', content.find('{% extends')) + 2
                    content = content[:extends_end] + '\n{% load static %}' + content[extends_end:]
                else:
                    # Add at the start for base.html
                    content = '{% load static %}\n' + content
            
            # Ensure CSS is loaded with static tag
            if '<link' in content and 'stylesheet' in content:
                if 'href="css/' in content or "href='css/" in content:
                    content = re.sub(
                        r'href=[\'"]css/([^\'"]+)[\'"]',
                        r'href="{% static \'css/\1\' %}"',
                        content
                    )
            
        elif page_filename.endswith('.css'):
            # Find the start of actual CSS content
            css_start = content.find('{')
            if css_start != -1:
                # Look backwards from { to find the selector
                selector_start = content[:css_start].rstrip().rfind('\n')
                if selector_start != -1:
                    content = content[selector_start + 1:].strip()
                else:
                    content = content.strip()
            
            # Basic CSS validation
            if '{' not in content or '}' not in content:
                raise ValueError("Invalid CSS content")
            
            # Remove any non-CSS comments
            content = re.sub(r'//.*?\n', '\n', content)  # Remove single-line comments
            content = re.sub(r'[^/\*]#.*?\n', '\n', content)  # Remove hash comments
            
        return content
        
    except Exception as e:
        print(f"Error cleaning response: {str(e)}")
        raise ValueError(f"Invalid {page_filename} content: {str(e)}")

def process_builder_mode_input_service(user_input, model, file_name, user):
    """
    Handles all business logic for processing user input and generating website content.
    """
    try:
        print(f"Processing builder mode input: {user_input}")
        # Validate required fields
        if not user_input:
            raise ValueError('User input is required')
        if not model:
            raise ValueError('Model selection is required')
        if not file_name:
            raise ValueError('File selection is required')

        # Get the active conversation for the specific project
        conversation = get_active_conversation(user)
        
        if not conversation.project.user_project:
            raise ValueError("No associated user project found")
            
        # Get or create the page/file
        page, created = Page.objects.get_or_create(
            conversation=conversation,
            filename=file_name
        )

        # Get system message and build conversation history
        system_msg = get_system_message()
        conversation_history = build_conversation_history(
            system_msg, 
            page, 
            conversation.project.user_project.project_path
        )

        # Build complete messages array
        complete_messages = [
            {"role": "system", "content": system_msg["content"]},
            *conversation_history,
            {"role": "system", "content": f"You are working on file: {page.filename}"},
            {"role": "user", "content": f"[File: {page.filename}]\n{user_input}"}
        ]

        # Make API call to get response
        print(f"Making API call to {model}")
        assistant_response = make_api_call(
            model=model,
            system_msg=system_msg,
            conversation_history=conversation_history,
            page=page,
            user_input=user_input,
            complete_messages=complete_messages,
            openai_client=openai_client,
            anthropic_client=anthropic_client
        )
        
        if not assistant_response:
            raise ValueError("Empty response from AI service")

        # Clean the response
        cleaned_response = clean_response(file_name, assistant_response)

        # Save messages to database
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

        # Return the content in a consistent format
        return {
            'success': True,
            'response': cleaned_response,
            'file': file_name
        }
            
    except Exception as e:
        print(f"Error in process_builder_mode_input_service: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

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
        
        # Get the project path and determine the correct output directory
        project_path = conversation.project.user_project.project_path
        if page_name.endswith('.html'):
            output_dir = os.path.join(project_path, 'templates')
        elif page_name.endswith('.css'):
            output_dir = os.path.join(project_path, 'static', 'css')
        else:
            return None, 'Invalid file type', 400
            
        # Write the previous content to file
        output_path = os.path.join(output_dir, page_name)
        with open(output_path, 'w') as f:
            f.write(previous_content)
        
        # For CSS files, we need to return the HTML content to re-render the page
        if page_name == 'styles.css':
            try:
                index_path = os.path.join(project_path, 'templates', 'index.html')
                with open(index_path, 'r') as f:
                    html_content = f.read()
                return html_content, 'Previous version restored', 200
            except FileNotFoundError:
                return previous_content, 'Previous version restored', 200
        else:
            return previous_content, 'Previous version restored', 200
            
    except Exception as e:
        print(f"Error in undo_last_action_service: {str(e)}")
        return None, 'Nothing to undo', 200

def process_chat_mode_input_service(user_input, model, conversation, conversation_history, file_name):
    """Processes chat input without generating website files."""
    try:
        # Set up the system message
        system_msg = get_system_message()
        
        # Get the project path
        project_path = conversation.project.user_project.project_path
        
        # Get or create the page for this file
        page, created = Page.objects.get_or_create(
            conversation=conversation,
            filename=file_name
        )
        
        # Build conversation history using the project's directories
        conversation_history = build_conversation_history(system_msg, page, project_path)
        
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
