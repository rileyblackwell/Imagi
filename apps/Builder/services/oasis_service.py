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
    ensure_website_directory,
    build_conversation_history,
    make_api_call
)

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
    if page_filename.endswith('.html'):
        html_match = re.search(r'(?s)<!DOCTYPE html>.*?</html>', assistant_response)
        if html_match:
            return html_match.group(0)
        raise ValueError("Response must be a complete HTML document")
        
    elif page_filename == 'styles.css':
        # Clean CSS content - remove any file prefix and only keep CSS content
        css_content = assistant_response
        if '[File: styles.css]' in css_content:
            css_content = css_content.split('[File: styles.css]')[1].strip()
        
        # Remove any markdown code block markers if present
        css_content = css_content.replace('```css', '').replace('```', '').strip()
        
        # Validate that it looks like CSS (basic check)
        if '{' not in css_content or '}' not in css_content:
            raise ValueError("Invalid CSS content")
        
        return css_content
    
    return assistant_response  # For other file types, return the response as is

def process_builder_mode_input_service(user_input, model, file_name, user):
    """
    Handles all business logic for processing user input and generating website content.
    
    Args:
        user_input (str): The input from the user
        model (str): The AI model to use
        file_name (str): The name of the file being edited
        user: The user making the request
        
    Returns:
        dict: Response containing generated content and any error messages
    """
    try:
        # Validate required fields
        if not user_input:
            raise ValueError('User input is required')
        if not model:
            raise ValueError('Model selection is required')
        if not file_name:
            raise ValueError('File selection is required')

        # Get the active conversation for the specific project
        conversation = get_active_conversation(user)
        project = conversation.project
        
        if not project.project_path:
            raise ValueError("Project path not found. Please ensure the project is properly set up.")
        
        # Determine the output directory based on file type
        if file_name.endswith('.html'):
            output_dir = os.path.join(project.project_path, 'templates')
        elif file_name.endswith('.css'):
            output_dir = os.path.join(project.project_path, 'static', 'css')
        else:
            raise ValueError(f"Unsupported file type: {file_name}")
        
        os.makedirs(output_dir, exist_ok=True)
            
        print(f"Processing input for project: {conversation.project.name} (ID: {conversation.project.id})")
        
        # Get or create the page/file
        page, created = Page.objects.get_or_create(
            conversation=conversation,
            filename=file_name
        )

        # Set up the system message and directories
        system_msg = get_system_message()
        base_dir = os.path.dirname(__file__)
        output_dir = ensure_website_directory(
            os.path.join(base_dir, '..')
        )
        
        # Build conversation history and context
        conversation_history = build_conversation_history(system_msg, page, output_dir)
        file_context = get_file_context(page.filename)
        
        complete_messages = [
            {"role": "system", "content": system_msg["content"]},
            *conversation_history,
            {"role": "system", "content": file_context},
            {"role": "user", "content": f"[File: {page.filename}]\n{user_input}"}
        ]
        
        # Make API call to get response
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

        # Use the new helper function to clean the response
        cleaned_response = clean_response(page.filename, assistant_response)

        # Save the file to the project directory
        output_path = os.path.join(output_dir, file_name)
        with open(output_path, 'w') as f:
            f.write(cleaned_response)

        # Also save to Imagi's website directory for the builder interface
        imagi_output_dir = ensure_website_directory(os.path.dirname(os.path.dirname(__file__)))
        imagi_output_path = os.path.join(imagi_output_dir, file_name)
        with open(imagi_output_path, 'w') as f:
            f.write(cleaned_response)

        # Save user message
        Message.objects.create(
            conversation=conversation,
            page=page,
            role="user",
            content=user_input
        )

        # Save assistant message
        Message.objects.create(
            conversation=conversation,
            page=page,
            role="assistant",
            content=cleaned_response
        )

        # Handle special case for CSS files
        if page.filename == 'styles.css':
            index_path = os.path.join(output_dir, 'index.html')
            try:
                with open(index_path, 'r') as f:
                    index_content = f.read()
                response_content = {'html': index_content, 'css': cleaned_response}
            except FileNotFoundError:
                response_content = {'html': '', 'css': cleaned_response}
        else:
            response_content = cleaned_response

        # Format the response based on the type of content
        if isinstance(response_content, dict):
            return {
                'success': True,
                'response': response_content,
                'type': 'dict'
            }
        else:
            return {
                'success': True,
                'response': {'html': response_content},
                'type': 'str'
            }
            
    except ValueError as e:
        return {
            'success': False,
            'error': str(e),
            'detail': 'ValueError occurred during processing'
        }
        
    except Exception as e:
        print(f"Error in process_input_service: {str(e)}")
        return {
            'success': False,
            'error': 'An unexpected error occurred',
            'detail': str(e)
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

def process_chat_mode_input_service(user_input, model, conversation, conversation_history, file_name):
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
